# python 操作 redis - Hash 数据类型
from comment import RedisConn


def redis_pool_hset_hget_about():
    """
    hset/hget 的使用
    :return:
    """
    with RedisConn() as r:
        r.hset(name="redis-hash-about-key", mapping={"name": "张三", "age": 18})
        print("获取到的数据是：", r.hget(name="redis-hash-about-key", key="name"))
        print("获取到的数据是：", r.hget(name="redis-hash-about-key", key="age"))


def redis_pool_hmset_hmget_about():
    """
    hmset/hmget 的使用
    :return:
    """
    with RedisConn() as r:
        r.hset(name="redis-hash-about-key", mapping={"city": "北京", "score": 99.5})
        print("获取到的数据是：", r.hmget(name="redis-hash-about-key", keys=["name", "age", "city", "score"]))


def redis_pool_hgetall_about():
    """
    hgetall 的使用
    :return:
    """
    with RedisConn() as r:
        print("获取所有字段和值：", r.hgetall(name="redis-hash-about-key"))


def redis_pool_hkeys_hvals_about():
    """
    hkeys/hvals 的使用
    :return:
    """
    with RedisConn() as r:
        print("获取所有字段名：", r.hkeys(name="redis-hash-about-key"))
        print("获取所有值：", r.hvals(name="redis-hash-about-key"))


def redis_pool_hincrby_about():
    """
    hincrby 的使用
    :return:
    """
    with RedisConn() as r:
        r.hincrby(name="redis-hash-about-key", key="age", amount=10)
        print("获取到的数据是：", r.hget(name="redis-hash-about-key", key="age"))


def redis_pool_hsetnx_about():
    """
    hsetnx 的使用
    :return:
    """
    with RedisConn() as r:
        print("hsetnx 设置不存在的字段：", r.hsetnx(name="redis-hash-about-key", key="phone", value="123456789"))
        print("hsetnx 设置已存在的字段：", r.hsetnx(name="redis-hash-about-key", key="name", value="李四"))
        print("获取到的数据是：", r.hget(name="redis-hash-about-key", key="phone"))


def redis_pool_hdel_about():
    """
    hdel 的使用
    :return:
    """
    with RedisConn() as r:
        print("删除字段 phone：", r.hdel("redis-hash-about-key", "phone"))
        print("获取到的数据是：", r.hget(name="redis-hash-about-key", key="phone"))


def redis_pool_hexists_about():
    """
    hexists 的使用
    :return:
    """
    with RedisConn() as r:
        print("字段 name 是否存在：", r.hexists(name="redis-hash-about-key", key="name"))
        print("字段 phone 是否存在：", r.hexists(name="redis-hash-about-key", key="phone"))


def redis_pool_hlen_about():
    """
    hlen 的使用
    :return:
    """
    with RedisConn() as r:
        print("hash 键值对数量：", r.hlen(name="redis-hash-about-key"))


if __name__ == '__main__':
    redis_pool_hset_hget_about()
    redis_pool_hmset_hmget_about()
    redis_pool_hgetall_about()
    redis_pool_hkeys_hvals_about()
    redis_pool_hincrby_about()
    redis_pool_hsetnx_about()
    redis_pool_hdel_about()
    redis_pool_hexists_about()
    redis_pool_hlen_about()
