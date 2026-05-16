## Python_Redis

在python代码中操作Redis数据库，对一些功能实现

### 安装Redis包
```shell
pip install redis
```

### 基础连接和使用
```python
# 连接redis数据库


import redis

r = redis.Redis(
    host='127.0.0.1',
    port=6379,
    db=0,
    # 如果有用户和密码
    # username='xxx',
    # password='xxx'

)
# 测试是否连接成功

print("查看是否连接成功：",r.ping())
```
### 基础连接池
```python
# 连接redis数据库的连接池
import threading

import redis

from redis.connection import ConnectionPool

# 创建全局唯一连接池（单例）
pool = ConnectionPool(
    host="127.0.0.1",
    port=6379,
    password=None,  # 无密码则为 None
    db=0,
    decode_responses=True,  # 自动把 bytes 转 str
    max_connections=10,  # 最大连接数
)


# 获取 Redis 连接
def get_redis():
    return redis.Redis(connection_pool=pool)


# 关闭连接池（程序退出时调用）
def close_pool():
    pool.disconnect()


r = get_redis()
print("查看是否连接成功：", r.ping())

r.set("name", "张三")
print(r.get("name"))


# 每个线程自己拿连接！！！（关键）
def task():
    # 每个线程内部获取新连接
    r = redis.Redis(connection_pool=pool)
    r.set("key", "value")
    print(r.get("key"))

# 多线程并发
threads = [threading.Thread(target=task) for _ in range(10)]
for t in threads:
    t.start()
for t in threads:
    t.join()

```

### 连接池的创建与使用

使用连接池管理Redis连接，支持多线程并发访问。核心代码在 `redis_code/comment.py` 中：

```python
import redis
import threading
import os
from contextlib import contextmanager


class RedisPool:
    """双重检查锁单例连接池"""
    _pool: redis.ConnectionPool | None = None
    _lock = threading.Lock()

    @classmethod
    def get_pool(cls) -> redis.ConnectionPool:
        if cls._pool is None:
            with cls._lock:
                if cls._pool is None:
                    cls._pool = redis.ConnectionPool(
                        host=os.getenv("REDIS_HOST", "127.0.0.1"),
                        port=int(os.getenv("REDIS_PORT", 6379)),
                        password=os.getenv("REDIS_PASSWORD", None),
                        db=int(os.getenv("REDIS_DB", 0)),
                        decode_responses=True,
                        max_connections=50,
                        socket_timeout=30,
                        socket_connect_timeout=30,
                        health_check_interval=30,
                        retry_on_timeout=True,
                    )
        return cls._pool


class RedisClient:
    _client: redis.Redis | None = None
    _lock = threading.Lock()

    @classmethod
    def get_client(cls) -> redis.Redis:
        if cls._client is None:
            with cls._lock:
                if cls._client is None:
                    cls._client = redis.Redis(connection_pool=RedisPool.get_pool())
        return cls._client


@contextmanager
def RedisConn():
    """生产级 Redis 连接上下文"""
    client = RedisClient.get_client()
    try:
        yield client
    except redis.exceptions.ConnectionError as e:
        raise RuntimeError(f"Redis 连接失败: {e}") from e
    except redis.exceptions.TimeoutError as e:
        raise RuntimeError(f"Redis 命令超时: {e}") from e
    except redis.exceptions.RedisError as e:
        raise RuntimeError(f"Redis 异常: {e}") from e
```

使用方式：通过 `with RedisConn() as r:` 上下文管理器获取连接，自动处理异常。

---

### String 类型操作

代码文件：`redis_code/004_redis_python_opration_string.py`

| 方法 | 说明 |
|------|------|
| `set / get` | 设置/获取字符串值，支持 `ex` 设置过期时间 |
| `keys` | 按模式匹配获取所有key |
| `mset / mget` | 批量设置/获取多个key |
| `incr / incrby / incrbyfloat` | 自增操作（整数/浮点数） |
| `setnx / setex` | 不存在时设置 / 设置带过期时间 |
| `strlen` | 获取字符串长度 |
| `getrange` | 获取子字符串 |
| `getset` | 设置新值并返回旧值 |

---

### Hash 类型操作

代码文件：`redis_code/005_redis_python_opration_hash.py`

| 方法 | 说明 |
|------|------|
| `hset / hget` | 设置/获取hash字段值 |
| `hmget` | 批量获取多个字段值 |
| `hgetall` | 获取所有字段和值 |
| `hkeys / hvals` | 获取所有字段名 / 所有值 |
| `hincrby` | 对字段值增加指定数量 |
| `hsetnx` | 字段不存在时才设置 |
| `hdel` | 删除指定字段 |
| `hexists` | 判断字段是否存在 |
| `hlen` | 获取字段数量 |

---

### List 类型操作

代码文件：`redis_code/006_redis_python_opration_list.py`

| 方法 | 说明 |
|------|------|
| `lpush / rpush` | 从左/右添加元素 |
| `lpop / rpop` | 从左/右取出元素 |
| `lrange` | 获取指定区间元素 |
| `lindex` | 获取指定索引元素 |
| `linsert` | 在指定元素前/后插入 |
| `lrem` | 删除指定数量的指定元素 |
| `ltrim` | 截取指定区间，只保留截取部分 |
| `llen` | 获取列表长度 |
| `lset` | 修改指定索引位置的元素 |
| `rpoplpush` | 从一个列表右侧取出，放入另一个列表左侧 |

---

### Set 类型操作

代码文件：`redis_code/007_redis_python_opration_set.py`

| 方法 | 说明 |
|------|------|
| `sadd / srem` | 添加/删除集合元素 |
| `scard` | 获取集合元素个数 |
| `sismember` | 判断元素是否在集合中 |
| `smembers` | 获取集合所有元素 |
| `spop` | 随机移除并返回一个元素 |
| `srandmember` | 随机获取指定个数元素（不移除） |
| `smove` | 将元素从一个集合移动到另一个集合 |
| `sinter / sunion / sdiff` | 交集/并集/差集 |
| `sinterstore / sunionstore / sdiffstore` | 交集/并集/差集并存储到新集合 |

---

### Sorted Set 类型操作

代码文件：`redis_code/008_redis_python_opration_sorted_set.py`

| 方法 | 说明 |
|------|------|
| `zadd` | 添加元素并指定分数 |
| `zrem` | 删除指定元素 |
| `zscore` | 获取指定元素的分数 |
| `zrange` | 按排名区间获取元素，支持 `withscores` |
| `zrank` | 获取元素排名（从0开始） |
| `zcard` | 获取元素总个数 |
| `zcount` | 获取指定分数区间的元素个数 |
| `zincrby` | 对指定元素的分数增加指定值 |
| `zrangebyscore` | 按分数区间获取元素 |
