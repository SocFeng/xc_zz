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
