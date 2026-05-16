# python 操作redis的方式
import time

from comment import RedisConn


def redis_pool_set_get_about():
    """
    set/get 的使用
    :return:
    """
    with RedisConn() as r:
        r.set(name="redis-set-about-key", value="redis-set-about-value", ex=3600)
        print("获取到的数据是：", r.get(name="redis-set-about-key"))


def redis_pool_keys_about():
    """
    keys 的使用
    :return:
    """
    with RedisConn() as r:
        data = r.keys(pattern="*")
        print("现在所有的key值的列表：", data)
        for key in data:
            print("获取到的数据key是：", key)


def redis_pool_mset_mget_about():
    """
    mset/mget 的使用
    :return:
    """
    with RedisConn() as r:
        r.mset(mapping={"redis-mset-about-key-1": "redis-mset-about-value-1",
                        "redis-mset-about-key-2": 1234,
                        "redis-mset-about-key-3": 123.642})
        print("获取到的数据是：", r.mget(["redis-mset-about-key-1", "redis-mset-about-key-2", "redis-mset-about-key-3"]))


def redis_pool_incr_incrby_incrbyfloat_about():
    """
    incr/incrby_/ncrbyfloat
    :return:
    """
    with RedisConn() as r:
        r.incr(name="redis-mset-about-key-2")
        r.incrby(name="redis-mset-about-key-2", amount=10)
        r.incrbyfloat(name="redis-mset-about-key-3", amount=10.123)

        print("获取到的数据是：", r.mget(["redis-mset-about-key-1", "redis-mset-about-key-2", "redis-mset-about-key-3"]))


def redis_pool_setnx_setex_about():
    """
    setnx/setex 的使用
    :return:
    """

    with RedisConn() as r:
        r.setnx(name="redis-setnx-about-key", value="redis-setnx-about-value")
        print("获取到的数据是：", r.get(name="redis-setnx-about-key"))
        r.setex(name="redis-setex-about-key", time=300, value="redis-setex-about-value")
        print("获取到的数据是：", r.get(name="redis-setex-about-key"))
        time.sleep(1)

        print(r.ttl("redis-setnx-about-key"), r.ttl("redis-setex-about-key"), r.ttl("redis-setex-about-none"))
        # -1 ：长期存活 299 : 剩余存活时间 -2:不存在/已失效


def redis_pool_strlen_about():
    """
    strlen 的使用
    :return:
    """
    with RedisConn() as r:
        r.set(name="redis-strlen-about-key", value="redis-strlen-about-value")
        print("获取到的数据是：", r.get(name="redis-strlen-about-key"))
        print("获取到的数据长度是：", r.strlen(name="redis-strlen-about-key"))


def redis_pool_getrange_about():
    """
    getrange 的使用
    :return:
    """
    with RedisConn() as r:
        r.set(name="redis-getrange-about-key", value="redis-getrange-about-value")
        print("获取到的数据是：", r.get(name="redis-getrange-about-key"))
        print("获取到的数据是：", r.getrange(key="redis-getrange-about-key", start=4, end=-5))


def redis_pool_getset_about():
    """
    getset 的使用
    :return:
    """
    with RedisConn() as r:
        r.set(name="redis-getset-about-key", value="redis-getset-about-value")
        print("获取到的数据是：", r.get(name="redis-getset-about-key"))
        r.getset(name="redis-getset-about-key", value="redis-getset-about-value-2")
        print("获取到的数据是：", r.get(name="redis-getset-about-key"))


if __name__ == '__main__':
    # redis_pool_set_get_about()
    # redis_pool_keys_about()
    # redis_pool_mset_mget_about()
    # redis_pool_incr_incrby_incrbyfloat_about()
    # redis_pool_setnx_setex_about()
    # redis_pool_strlen_about()
    # redis_pool_getrange_about()
    redis_pool_getset_about()
