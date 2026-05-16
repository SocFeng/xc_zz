# Flask + Redis 实战案例
# 包含：发送验证码、验证码校验登录、用户认证拦截、用户限流

import uuid
import time
from functools import wraps

from flask import Flask, request, jsonify
from comment import RedisConn

app = Flask(__name__)


# ============================================================
# 1. 发送验证码
# ============================================================

def generate_code(length=6):
    """生成6位数字验证码"""
    import random
    return "".join([str(random.randint(0, 9)) for _ in range(length)])


@app.route("/api/send_code", methods=["POST"])
def send_code():
    """
    发送验证码
    请求体: {"phone": "13800138000"}
    流程: 生成验证码 -> 存入Redis(5分钟过期) -> 模拟发送短信
    """
    data = request.get_json()
    phone = data.get("phone")
    if not phone:
        return jsonify({"code": 400, "msg": "手机号不能为空"}), 400

    with RedisConn() as r:
        # 防刷限制：60秒内不能重复发送
        rate_key = f"sms:rate:{phone}"
        if r.exists(rate_key):
            ttl = r.ttl(rate_key)
            return jsonify({"code": 429, "msg": f"请等待{ttl}秒后再发送"}), 429

        # 生成验证码并存入Redis，5分钟过期
        code = generate_code()
        r.setex(f"sms:code:{phone}", 300, code)

        # 设置60秒防刷标记
        r.setex(rate_key, 60, 1)

    # 模拟发送短信（实际项目中调用短信服务商API）
    print(f"[模拟短信] 发送验证码 {code} 到 {phone}")
    return jsonify({"code": 200, "msg": "验证码发送成功", "data": {"code": code}})


# ============================================================
# 2. 验证码校验与登录
# ============================================================

@app.route("/api/login", methods=["POST"])
def login():
    """
    验证码登录
    请求体: {"phone": "13800138000", "code": "123456"}
    流程: 校验验证码 -> 生成token -> 存入Redis -> 返回token
    """
    data = request.get_json()
    phone = data.get("phone")
    code = data.get("code")

    if not phone or not code:
        return jsonify({"code": 400, "msg": "手机号和验证码不能为空"}), 400

    with RedisConn() as r:
        saved_code = r.get(f"sms:code:{phone}")
        if saved_code is None:
            return jsonify({"code": 400, "msg": "验证码已过期，请重新发送"}), 400
        if saved_code != code:
            return jsonify({"code": 400, "msg": "验证码错误"}), 400

        # 验证通过，删除验证码
        r.delete(f"sms:code:{phone}")

        # 生成token，存入Redis，有效期2小时
        token = uuid.uuid4().hex
        r.setex(f"user:token:{token}", 7200, phone)

    return jsonify({
        "code": 200,
        "msg": "登录成功",
        "data": {"token": token, "phone": phone}
    })


# ============================================================
# 3. 用户认证拦截
# ============================================================

def login_required(f):
    """
    登录认证装饰器
    从请求头中获取token，校验Redis中是否存在
    """

    @wraps(f)
    def decorated(*args, **kwargs):
        token = request.headers.get("Authorization", "").replace("Bearer ", "")
        if not token:
            return jsonify({"code": 401, "msg": "未登录，请先登录"}), 401

        with RedisConn() as r:
            phone = r.get(f"user:token:{token}")
            if phone is None:
                return jsonify({"code": 401, "msg": "token无效或已过期，请重新登录"}), 401

            # 续期：每次访问自动续期2小时
            r.expire(f"user:token:{token}", 7200)
            # 将用户信息注入请求上下文
            request.phone = phone

        return f(*args, **kwargs)

    return decorated


@app.route("/api/user/info", methods=["GET"])
@login_required
def user_info():
    """获取用户信息（需要登录认证）"""
    return jsonify({
        "code": 200,
        "msg": "获取成功",
        "data": {"phone": request.phone, "nickname": f"用户{request.phone[-4:]}"}
    })


@app.route("/api/logout", methods=["POST"])
@login_required
def logout():
    """退出登录，删除Redis中的token"""
    token = request.headers.get("Authorization", "").replace("Bearer ", "")
    with RedisConn() as r:
        r.delete(f"user:token:{token}")
    return jsonify({"code": 200, "msg": "退出成功"})


# ============================================================
# 4. 用户限流
# ============================================================

def rate_limit(max_requests=10, window=60):
    """
    基于IP的限流装饰器
    使用Redis INCR + EXPIRE实现滑动窗口限流
    :param max_requests: 时间窗口内最大请求数
    :param window: 时间窗口（秒）
    """

    def decorator(f):
        @wraps(f)
        def decorated(*args, **kwargs):
            ip = request.remote_addr
            key = f"rate:limit:{ip}:{f.__name__}"

            with RedisConn() as r:
                current = r.incr(key)
                if current == 1:
                    # 第一次请求，设置过期时间
                    r.expire(key, window)

                if current > max_requests:
                    ttl = r.ttl(key)
                    return jsonify({
                        "code": 429,
                        "msg": f"请求过于频繁，请{ttl}秒后再试",
                        "data": {"retry_after": ttl}
                    }), 429

            return f(*args, **kwargs)

        return decorated

    return decorator


@app.route("/api/limited_resource", methods=["GET"])
@rate_limit(max_requests=5, window=60)
def limited_resource():
    """限流接口示例：同一IP 60秒内最多请求5次"""
    return jsonify({
        "code": 200,
        "msg": "请求成功",
        "data": {"content": "这是一个受限流保护的资源"}
    })


# ============================================================
# 综合示例：需要登录 + 限流
# ============================================================

@app.route("/api/order/list", methods=["GET"])
@login_required
@rate_limit(max_requests=20, window=60)
def order_list():
    """查询订单列表（需要登录 + 限流保护）"""
    return jsonify({
        "code": 200,
        "msg": "获取成功",
        "data": {
            "phone": request.phone,
            "orders": [
                {"id": 1, "name": "商品A", "price": 99.9},
                {"id": 2, "name": "商品B", "price": 199.9},
            ]
        }
    })


# 缓存数据
@app.route("/api/user/cache", methods=["POST"])
def user_data():
    """
    模拟缓存数据的方式！
    :return:
    """
    data = request.get_json()
    id = data.get("id")

    allData = [{"id": "001", "name": "张三", "age": 24, "sex": "男", "phone": "13800138000"},
               {"id": "002", "name": "李四", "age": 25, "sex": "女", "phone": "13900139000"},
               {"id": "003", "name": "王五", "age": 26, "sex": "男", "phone": "13600136000"},
               {"id": "004", "name": "赵六", "age": 27, "sex": "女", "phone": "13700137000"},
               {"id": "005", "name": "孙七", "age": 28, "sex": "男", "phone": "13800138008"},
               {"id": "006", "name": "周八", "age": 29, "sex": "女", "phone": "13900139009"},
               ]
    # 1 先查询缓存中是否有数据有数据直接返回
    with RedisConn() as r:
        is_has_key = r.exists(f"user:cache:{id}")
        if is_has_key:
            data = r.hgetall(f"user:cache:{id}")
            return jsonify({"code": 200, "msg": "获取成功 -- 这是缓存中拿到的数据", "data": data})
    # 2 查数据库有没有数据，有数据先缓存再返回
    for data in allData:
        if data["id"] == id:
            with RedisConn() as r:
                r.hmset(f"user:cache:{id}", mapping=data)
            return jsonify({"code": 200, "msg": "获取成功  -- 这是数据库中找的数据，但是已经缓存下来了", "data": data})
    # 3 都没有数据，那就找不到
    return jsonify({"code": 404, "msg": "获取失败", "data": None})


# ============================================================
# 5. 布隆过滤器 - 防止缓存穿透
# ============================================================

# 模拟数据库
ALL_PRODUCTS = [
    {"id": "1001", "name": "iPhone 16", "price": 7999},
    {"id": "1002", "name": "小米14", "price": 3999},
    {"id": "1003", "name": "华为 Mate70", "price": 5999},
    {"id": "1004", "name": "OPPO Find X8", "price": 4999},
    {"id": "1005", "name": "vivo X200", "price": 4599},
]


def my_hash(s, seed):
    """简单的哈希函数，用于布隆过滤器的多个哈希函数"""
    h = seed
    for ch in s:
        h = (h * 31 + ord(ch)) % (1 << 16)  # 取模到 65536 位的位数组
    return h


def bloom_filter_add(r, key, value):
    """
    向布隆过滤器中添加一个元素
    使用3个不同种子的哈希函数，将对应bit位设为1
    :param r: Redis连接
    :param key: 布隆过滤器的key
    :param value: 要添加的值
    """
    for seed in [17, 31, 61]:
        bit_offset = my_hash(value, seed)
        r.setbit(key, bit_offset, 1)


def bloom_filter_exists(r, key, value):
    """
    检查布隆过滤器中是否存在某个元素
    3个哈希函数对应的bit位全部为1才认为"可能存在"
    只要有一个bit位为0，就一定不存在（100%准确）
    :return: True=可能存在, False=一定不存在
    """
    for seed in [17, 31, 61]:
        bit_offset = my_hash(value, seed)
        if not r.getbit(key, bit_offset):
            return False
    return True


@app.route("/api/product/bloom", methods=["POST"])
def product_bloom():
    """
    布隆过滤器防缓存穿透

    请求体: {"id": "1001"}
    流程: 布隆过滤器判断key是否存在 -> 不存在直接返回 -> 存在则查缓存/数据库

    布隆过滤器特点：
    - 判断"不存在"是100%准确的
    - 判断"可能存在"有极小概率误判（误判时多查一次数据库，可以接受）
    - 用极小的内存空间（几KB）过滤掉大量不存在的请求

    测试用例：
    {"id": "1001"} -> 可能存在 -> 查缓存/数据库 -> 返回数据
    {"id": "9999"} -> 一定不存在 -> 直接返回 -> 不查数据库
    """
    data = request.get_json()
    product_id = data.get("id")

    with RedisConn() as r:
        bloom_key = "bloom:product"

        # 首次访问时，初始化布隆过滤器（将数据库中存在的id全部加入）
        # 实际项目中在数据写入数据库时同步添加到布隆过滤器
        if not r.exists(bloom_key):
            for p in ALL_PRODUCTS:
                bloom_filter_add(r, bloom_key, p["id"])
            print("[布隆过滤器] 初始化完成，已添加所有商品ID")

        # 第一步：布隆过滤器判断key是否存在
        if not bloom_filter_exists(r, bloom_key, product_id):
            # 不存在 -> 100%确定数据库没有 -> 直接返回，不查数据库
            return jsonify({"code": 404, "msg": "布隆过滤器判定不存在，拦截请求（未查数据库）", "data": None})

        # 第二步：可能存在 -> 查缓存
        cached = r.get(f"product:bloom:{product_id}")
        if cached:
            return jsonify({"code": 200, "msg": "缓存命中", "data": {"id": product_id, "info": cached}})

    # 第三步：缓存未命中 -> 查数据库
    for p in ALL_PRODUCTS:
        if p["id"] == product_id:
            with RedisConn() as r:
                r.setex(f"product:bloom:{product_id}", 3600, p["name"])
            return jsonify({"code": 200, "msg": "数据库查询并缓存", "data": p})

    # 布隆过滤器误判的情况（说可能存在但数据库实际没有）
    return jsonify({"code": 404, "msg": "布隆过滤器误判，数据库中不存在", "data": None})


# ============================================================
# 6. 缓存空值 - 防止缓存穿透
# ============================================================

@app.route("/api/product/null_cache", methods=["POST"])
def product_null_cache():
    """
    缓存空值防缓存穿透

    请求体: {"id": "1001"}
    流程: 查缓存 -> 命中空值标记直接返回 -> 命中正常数据返回 -> 未命中查数据库
         -> 数据库有 -> 缓存数据并返回
         -> 数据库没有 -> 缓存空值标记（短过期时间）并返回

    核心思想：
    数据库不存在的数据，也缓存一个特殊标记（如"NULL"），
    下次查询时直接命中这个空值缓存返回，避免再次打到数据库。

    测试用例：
    {"id": "1001"} -> 第一次查数据库 -> 缓存结果 -> 第二次直接命中缓存
    {"id": "9999"} -> 第一次查数据库 -> 没有 -> 缓存空值 -> 第二次命中空值缓存，不查数据库
    """
    data = request.get_json()
    product_id = data.get("id")

    # 第一步：查缓存
    with RedisConn() as r:
        cached = r.get(f"product:null:{product_id}")
        if cached is not None:
            # 命中空值标记 -> 数据库查过确实不存在，直接返回
            if cached == "NULL":
                return jsonify({"code": 404, "msg": "命中空值缓存，数据库无此数据（未查数据库）", "data": None})
            # 命中正常数据 -> 直接返回
            return jsonify({"code": 200, "msg": "缓存命中", "data": {"id": product_id, "info": cached}})

    # 第二步：缓存未命中 -> 查数据库
    for p in ALL_PRODUCTS:
        if p["id"] == product_id:
            # 数据库查到了 -> 缓存正常数据，过期时间较长
            with RedisConn() as r:
                r.setex(f"product:null:{product_id}", 3600, p["name"])
            return jsonify({"code": 200, "msg": "数据库查询并缓存", "data": p})

    # 第三步：数据库也没有 -> 缓存空值，过期时间短（防止长期占用内存）
    with RedisConn() as r:
        r.setex(f"product:null:{product_id}", 60, "NULL")
    return jsonify({"code": 404, "msg": "数据库无此数据，已缓存空值（60秒过期）", "data": None})


# ============================================================
# 7. 加互斥锁 - 防止缓存击穿
# ============================================================

@app.route("/api/product/mutex", methods=["POST"])
def product_mutex():
    """
    互斥锁防缓存击穿

    请求体: {"id": "1001"}
    流程: 查缓存 -> 命中直接返回
         -> 未命中 -> 尝试获取互斥锁(SETNX)
             -> 获取成功 -> 查数据库 -> 写缓存 -> 释放锁 -> 返回
             -> 获取失败 -> 等待一小段时间 -> 重试查缓存 -> 命中则返回

    缓存击穿场景：
    某个热点key（如秒杀商品）过期的瞬间，大量并发请求同时涌入，
    如果不加锁，所有请求都会打到数据库，导致数据库压力骤增。

    互斥锁原理：
    只允许一个线程去查数据库并回填缓存，其他线程等待，
    等第一个线程完成后，其他线程直接从缓存获取数据。

    测试方法（模拟并发击穿）：
    同时发起多个请求到此接口，观察只有一个请求查了数据库，
    其他请求都是从缓存拿的数据。
    """
    data = request.get_json()
    product_id = data.get("id")
    cache_key = f"product:mutex:{product_id}"
    lock_key = f"lock:product:{product_id}"

    # 第一步：查缓存
    with RedisConn() as r:
        cached = r.get(cache_key)
        if cached:
            return jsonify({"code": 200, "msg": "缓存命中", "data": {"id": product_id, "info": cached}})

    # 第二步：缓存未命中 -> 尝试获取互斥锁
    with RedisConn() as r:
        # SET key value NX EX 10：如果key不存在才设置成功，10秒自动释放（防止死锁）
        locked = r.set(lock_key, "1", nx=True, ex=10)

        if locked:
            # 获取锁成功 -> 只有这一个线程能查数据库
            try:
                print(f"[互斥锁] 线程获取锁成功，开始查数据库 product_id={product_id}")
                time.sleep(0.5)  # 模拟数据库查询耗时

                # 查数据库
                for p in ALL_PRODUCTS:
                    if p["id"] == product_id:
                        # 回填缓存
                        r.setex(cache_key, 3600, p["name"])
                        return jsonify({
                            "code": 200,
                            "msg": "获取锁成功 -> 查数据库 -> 写缓存",
                            "data": p
                        })

                # 数据库没有
                return jsonify({"code": 404, "msg": "数据库中不存在", "data": None})
            finally:
                # 无论成功失败，都要释放锁
                r.delete(lock_key)
                print(f"[互斥锁] 锁已释放 product_id={product_id}")
        else:
            # 获取锁失败 -> 其他线程正在查数据库，等待后重试查缓存
            print(f"[互斥锁] 获取锁失败，等待其他线程加载缓存 product_id={product_id}")
            time.sleep(0.6)  # 等待第一个线程完成数据库查询和缓存回填

            with RedisConn() as r2:
                cached = r2.get(cache_key)
                if cached:
                    return jsonify({"code": 200, "msg": "等待后从缓存获取", "data": {"id": product_id, "info": cached}})

            # 等待超时仍未加载成功
            return jsonify({"code": 503, "msg": "系统繁忙，请稍后重试", "data": None})


if __name__ == '__main__':
    app.run(debug=True, port=5000)
