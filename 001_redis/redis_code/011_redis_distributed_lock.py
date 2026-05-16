# Redis 分布式锁完整实现
# 支持：自动过期、锁续期、可重入、阻塞等待、Redlock高可用

import uuid
import time
import threading
from functools import wraps
from typing import Optional, List

import redis
from comment import RedisConn

# ============================================================
# Lua 脚本（保证原子性）
# ============================================================

# 释放锁：只有持有者才能释放（先比较 value，再删除）
# 返回 1 表示释放成功，0 表示锁已被别人持有或已过期
UNLOCK_SCRIPT = """
if redis.call("GET", KEYS[1]) == ARGV[1] then
    return redis.call("DEL", KEYS[1])
else
    return 0
end
"""

# 续期锁：只有持有者才能续期（先比较 value，再重设过期时间）
# 返回 1 表示续期成功，0 表示锁已被别人持有或已过期
RENEW_SCRIPT = """
if redis.call("GET", KEYS[1]) == ARGV[1] then
    return redis.call("EXPIRE", KEYS[1], ARGV[2])
else
    return 0
end
"""

# 可重入锁：加锁（value 中嵌套计数器）
# KEYS[1]=锁key, ARGV[1]=持有者唯一标识, ARGV[2]=过期时间, ARGV[3]=当前线程标识
REENTRANT_LOCK_SCRIPT = """
local current = redis.call("GET", KEYS[1])
if current == false then
    -- 锁不存在，直接加锁，计数=1
    redis.call("SET", KEYS[1], ARGV[1] .. ":1", "EX", tonumber(ARGV[2]))
    return 1
elseif string.find(current, ARGV[1] .. ":") == 1 then
    -- 锁被当前持有者持有，计数+1
    local count = tonumber(string.sub(current, #ARGV[1] + 2))
    redis.call("SET", KEYS[1], ARGV[1] .. ":" .. (count + 1), "EX", tonumber(ARGV[2]))
    return count + 1
else
    -- 锁被其他人持有
    return 0
end
"""

# 可重入锁：解锁
REENTRANT_UNLOCK_SCRIPT = """
local current = redis.call("GET", KEYS[1])
if current == false then
    return -1
elseif string.find(current, ARGV[1] .. ":") == 1 then
    local count = tonumber(string.sub(current, #ARGV[1] + 2))
    if count <= 1 then
        redis.call("DEL", KEYS[1])
        return 0
    else
        redis.call("SET", KEYS[1], ARGV[1] .. ":" .. (count - 1), "EX", tonumber(ARGV[2]))
        return count - 1
    end
else
    return -2
end
"""


# ============================================================
# 1. 基础分布式锁（单Redis节点）
# ============================================================

class RedisDistributedLock:
    """
    基于 Redis 的分布式锁

    特性：
    - 原子加锁：SET NX EX（一条命令完成）
    - 安全释放：Lua 脚本保证只有持有者能释放（先比对 value 再删除）
    - 自动过期：防止持有者崩溃导致死锁
    - 锁续期：后台线程自动续期（看门狗机制），防止业务执行时间过长导致锁过期
    - 阻塞获取：支持最大等待时间

    用法：
        lock = RedisDistributedLock("order:123", expire=30)
        if lock.acquire():
            try:
                # 业务逻辑
                pass
            finally:
                lock.release()

        # 或者用 with 语句
        with RedisDistributedLock("order:123") as lock:
            if lock.locked:
                # 业务逻辑
                pass
    """

    def __init__(self, key: str, expire: int = 30, retry_interval: float = 0.1,
                 wait_timeout: float = 10):
        """
        :param key: 锁的名称
        :param expire: 锁的过期时间（秒），防止持有者崩溃导致死锁
        :param retry_interval: 获取锁失败时的重试间隔（秒）
        :param wait_timeout: 获取锁的最大等待时间（秒），0 表示不等待
        """
        self.key = f"lock:{key}"
        self.value = f"{uuid.uuid4().hex}:{threading.current_thread().ident}"
        self.expire = expire
        self.retry_interval = retry_interval
        self.wait_timeout = wait_timeout
        self._locked = False
        self._renew_thread: Optional[threading.Thread] = None
        self._renew_stop = threading.Event()

    @property
    def locked(self) -> bool:
        return self._locked

    def acquire(self, wait_timeout: Optional[float] = None) -> bool:
        """
        获取锁
        :param wait_timeout: 最大等待时间（秒），None 使用初始化时的值
        :return: True=获取成功, False=获取失败
        """
        if wait_timeout is None:
            wait_timeout = self.wait_timeout

        deadline = time.time() + wait_timeout

        while True:
            with RedisConn() as r:
                # SET key value NX EX expire —— 原子操作
                acquired = r.set(self.key, self.value, nx=True, ex=self.expire)

            if acquired:
                self._locked = True
                self._start_renew()
                return True

            # 不等待直接返回
            if wait_timeout <= 0:
                return False

            # 超时
            if time.time() >= deadline:
                return False

            # 等待后重试
            time.sleep(self.retry_interval)

    def release(self) -> bool:
        """
        释放锁（Lua脚本保证原子性：先比较value，再删除）
        :return: True=释放成功, False=锁已被别人持有或已过期
        """
        self._stop_renew()
        with RedisConn() as r:
            result = r.eval(UNLOCK_SCRIPT, 1, self.key, self.value)
        self._locked = False
        return result == 1

    def _start_renew(self):
        """启动后台续期线程（看门狗）"""
        self._renew_stop.clear()
        self._renew_thread = threading.Thread(target=self._renew_loop, daemon=True)
        self._renew_thread.start()

    def _stop_renew(self):
        """停止后台续期线程"""
        self._renew_stop.set()

    def _renew_loop(self):
        """
        看门狗线程：每隔 expire/3 续期一次
        例如 expire=30秒，则每10秒续期一次
        """
        interval = max(self.expire / 3, 1)
        while not self._renew_stop.wait(interval):
            with RedisConn() as r:
                r.eval(RENEW_SCRIPT, 1, self.key, self.value, self.expire)

    def __enter__(self):
        self.acquire()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.release()
        return False


# ============================================================
# 2. 可重入分布式锁
# ============================================================

class RedisReentrantLock:
    """
    可重入分布式锁

    同一个线程可以多次获取同一把锁，每次 unlock 对应一次 unlock
    内部用 value 中嵌套计数器实现：value = "{uuid}:{thread_id}:{count}"

    用法：
        lock = RedisReentrantLock("resource")
        with lock:
            with lock:  # 可以重入
                pass
    """

    def __init__(self, key: str, expire: int = 30):
        self.key = f"lock:reentrant:{key}"
        self.owner = f"{uuid.uuid4().hex}:{threading.current_thread().ident}"
        self.expire = expire
        self._local_count = 0  # 本地计数器（线程内）
        self._locked = False

    @property
    def locked(self) -> bool:
        return self._locked

    def acquire(self) -> bool:
        with RedisConn() as r:
            result = r.eval(REENTRANT_LOCK_SCRIPT, 1, self.key, self.owner, self.expire)
        if result:
            self._local_count += 1
            self._locked = True
            return True
        return False

    def release(self) -> bool:
        if self._local_count <= 0:
            return False
        with RedisConn() as r:
            result = r.eval(REENTRANT_UNLOCK_SCRIPT, 1, self.key, self.owner, self.expire)
        if result >= 0:
            self._local_count -= 1
            if self._local_count == 0:
                self._locked = False
            return True
        return False

    def __enter__(self):
        self.acquire()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.release()
        return False


# ============================================================
# 3. Redlock 高可用分布式锁（多Redis节点）
# ============================================================

class Redlock:
    """
    Redlock 算法 —— 多节点 Redis 分布式锁

    核心思想：
    在 N 个独立的 Redis 节点上同时加锁，
    当超过半数（N/2+1）节点加锁成功且总耗时 < 锁过期时间时，
    认为获取锁成功。

    即使部分 Redis 节点宕机，只要多数节点存活，锁仍然可用。

    用法：
        lock = Redlock(
            redis_nodes=[
                {"host": "127.0.0.1", "port": 6379},
                {"host": "127.0.0.1", "port": 6380},
                {"host": "127.0.0.1", "port": 6381},
            ],
            expire=30
        )
        if lock.acquire("order:123"):
            try:
                pass
            finally:
                lock.release("order:123")
    """

    def __init__(self, redis_nodes: List[dict], expire: int = 30, retry_count: int = 3,
                 retry_delay: float = 0.2):
        """
        :param redis_nodes: Redis 节点列表，每个元素如 {"host": "x", "port": 6379}
        :param expire: 锁过期时间（毫秒）
        :param retry_count: 获取锁失败时的重试次数
        :param retry_delay: 重试间隔（秒）
        """
        self.expire = expire
        self.retry_count = retry_count
        self.retry_delay = retry_delay
        self.quorum = len(redis_nodes) // 2 + 1  # 多数派数量
        self.nodes: List[redis.Redis] = []
        for node_cfg in redis_nodes:
            pool = redis.ConnectionPool(
                host=node_cfg.get("host", "127.0.0.1"),
                port=node_cfg.get("port", 6379),
                db=node_cfg.get("db", 0),
                password=node_cfg.get("password"),
                decode_responses=True,
                socket_timeout=node_cfg.get("timeout", 2),
            )
            self.nodes.append(redis.Redis(connection_pool=pool))

    def acquire(self, key: str) -> Optional[str]:
        """
        获取分布式锁
        :param key: 锁的名称
        :return: 锁的唯一标识（释放时需要），None 表示获取失败
        """
        lock_key = f"redlock:{key}"
        value = f"{uuid.uuid4().hex}:{threading.current_thread().ident}"

        for attempt in range(self.retry_count):
            start_time = time.time()
            acquired_count = 0

            # 向所有节点尝试加锁
            for node in self.nodes:
                try:
                    if node.set(lock_key, value, nx=True, px=self.expire):
                        acquired_count += 1
                except redis.RedisError:
                    continue

            elapsed = time.time() - start_time

            # 多数派加锁成功，且总耗时 < 锁过期时间，认为成功
            if acquired_count >= self.quorum and (elapsed * 1000) < self.expire:
                return value

            # 加锁失败，释放已获取的锁
            self._release_nodes(lock_key, value)

            if attempt < self.retry_count - 1:
                time.sleep(self.retry_delay)

        return None

    def release(self, key: str, value: str) -> bool:
        """
        释放分布式锁
        :param key: 锁的名称
        :param value: acquire 返回的唯一标识
        :return: True=释放成功
        """
        return self._release_nodes(f"redlock:{key}", value)

    def _release_nodes(self, lock_key: str, value: str) -> bool:
        """在所有节点上释放锁（Lua脚本保证原子性）"""
        success = False
        for node in self.nodes:
            try:
                if node.eval(UNLOCK_SCRIPT, 1, lock_key, value):
                    success = True
            except redis.RedisError:
                continue
        return success


# ============================================================
# 装饰器：用分布式锁保护函数
# ============================================================

def distributed_lock(key: str, expire: int = 30, wait_timeout: float = 10):
    """
    分布式锁装饰器
    用法：
        @distributed_lock("order:process", expire=30)
        def process_order(order_id):
            pass
    """
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            # 支持动态key：如果函数第一个参数是字符串，拼接到锁key中
            lock_key = key
            if args and isinstance(args[0], str):
                lock_key = f"{key}:{args[0]}"

            with RedisDistributedLock(lock_key, expire=expire, wait_timeout=wait_timeout) as lock:
                if not lock.locked:
                    return {"code": 429, "msg": "获取锁失败，系统繁忙"}
                return func(*args, **kwargs)
        return wrapper
    return decorator


# ============================================================
# 测试用例
# ============================================================

def test_basic_lock():
    """测试基础锁：加锁 -> 释放"""
    print("\n===== 测试1: 基础分布式锁 =====")
    lock = RedisDistributedLock("test:basic", expire=10, wait_timeout=5)

    print(f"  尝试获取锁...")
    if lock.acquire():
        print(f"  获取成功, value={lock.value}")
        print(f"  执行业务逻辑...")
        time.sleep(1)
        released = lock.release()
        print(f"  释放锁: {released}")
    else:
        print("  获取失败")


def test_with_statement():
    """测试 with 语句自动加锁释放"""
    print("\n===== 测试2: with 语句 =====")
    with RedisDistributedLock("test:with", expire=10) as lock:
        if lock.locked:
            print("  锁已获取，执行业务逻辑")
            time.sleep(1)
        print("  退出 with，锁自动释放")


def test_concurrent_acquire():
    """测试并发竞争：多个线程同时抢锁"""
    print("\n===== 测试3: 并发竞争锁 =====")
    results = []

    def worker(worker_id):
        lock = RedisDistributedLock("test:concurrent", expire=10, wait_timeout=8)
        if lock.acquire():
            results.append(f"  Worker-{worker_id} 获取锁成功")
            time.sleep(0.5)  # 模拟业务处理
            lock.release()
        else:
            results.append(f"  Worker-{worker_id} 获取锁失败")

    threads = [threading.Thread(target=worker, args=(i,)) for i in range(5)]
    for t in threads:
        t.start()
    for t in threads:
        t.join()

    for r in results:
        print(r)


def test_reentrant_lock():
    """测试可重入锁"""
    print("\n===== 测试4: 可重入锁 =====")
    lock = RedisReentrantLock("test:reentrant", expire=10)

    print(f"  第一次加锁: {lock.acquire()}  (计数={lock._local_count})")
    print(f"  第二次加锁: {lock.acquire()}  (计数={lock._local_count})")
    print(f"  第三次加锁: {lock.acquire()}  (计数={lock._local_count})")
    print(f"  第一次释放: {lock.release()}  (计数={lock._local_count})")
    print(f"  第二次释放: {lock.release()}  (计数={lock._local_count})")
    print(f"  第三次释放: {lock.release()}  (计数={lock._local_count})")


def test_renew():
    """测试锁续期：看门狗自动续期"""
    print("\n===== 测试5: 锁续期（看门狗） =====")
    lock = RedisDistributedLock("test:renew", expire=5)

    if lock.acquire():
        print("  锁已获取，过期时间=5秒，看门狗每~1.7秒续期一次")
        for i in range(8):
            time.sleep(1)
            with RedisConn() as r:
                ttl = r.ttl(lock.key)
            print(f"  第{i + 1}秒，剩余TTL={ttl}秒")
        lock.release()
        print("  锁已释放")


def test_lock_timeout():
    """测试获取锁超时"""
    print("\n===== 测试6: 获取锁超时 =====")

    # 线程A持有锁不释放
    def holder():
        lock = RedisDistributedLock("test:timeout", expire=20)
        lock.acquire()
        time.sleep(5)
        lock.release()

    t = threading.Thread(target=holder)
    t.start()
    time.sleep(0.2)  # 确保 holder 先拿到锁

    # 线程B尝试获取，等待超时
    lock_b = RedisDistributedLock("test:timeout", wait_timeout=2)
    print(f"  尝试获取锁（最多等待2秒）...")
    start = time.time()
    result = lock_b.acquire()
    elapsed = time.time() - start
    print(f"  结果: {result}, 耗时: {elapsed:.1f}秒")

    t.join()


def test_decorated_function():
    """测试装饰器"""
    print("\n===== 测试7: 装饰器保护函数 =====")

    @distributed_lock("task:process", expire=10)
    def process_task(task_id):
        print(f"  处理任务 {task_id}")
        time.sleep(1)
        return {"code": 200, "msg": f"任务{task_id}完成"}

    result = process_task("A001")
    print(f"  结果: {result}")


if __name__ == '__main__':
    test_basic_lock()
    test_with_statement()
    test_concurrent_acquire()
    test_reentrant_lock()
    test_renew()
    test_lock_timeout()
    test_decorated_function()
