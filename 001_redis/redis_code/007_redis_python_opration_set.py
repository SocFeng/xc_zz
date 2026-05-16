# python 操作 redis - Set 数据类型
from comment import RedisConn


def redis_pool_sadd_srem_about():
    """
    sadd/srem 的使用
    :return:
    """
    with RedisConn() as r:
        r.delete("redis-set-about-key-1", "redis-set-about-key-2")
        r.sadd("redis-set-about-key-1", "A", "B", "C", "D", "E")
        print("添加后的集合：", r.smembers("redis-set-about-key-1"))
        r.sadd("redis-set-about-key-2", "C", "D", "F", "G", "1", "2")
        print("set2：", r.smembers("redis-set-about-key-2"))
        r.srem("redis-set-about-key-1", "A")
        print("删除 A 后：", r.smembers("redis-set-about-key-1"))


def redis_pool_scard_about():
    """
    scard 的使用
    :return:
    """
    with RedisConn() as r:
        print("集合元素个数：", r.scard("redis-set-about-key-1"))


def redis_pool_sismember_about():
    """
    sismember 的使用
    :return:
    """
    with RedisConn() as r:
        print("B 是否在集合中：", r.sismember("redis-set-about-key-1", "B"))
        print("X 是否在集合中：", r.sismember("redis-set-about-key-1", "X"))


def redis_pool_smembers_about():
    """
    smembers 的使用
    :return:
    """
    with RedisConn() as r:
        print("获取集合所有元素：", r.smembers("redis-set-about-key-1"))


def redis_pool_spop_about():
    """
    spop 的使用
    :return:
    """
    with RedisConn() as r:
        result = r.spop("redis-set-about-key-1")
        print("随机移除的元素：", result)
        print("移除后：", r.smembers("redis-set-about-key-1"))


def redis_pool_srandmember_about():
    """
    srandmember 的使用
    :return:
    """
    with RedisConn() as r:
        print("随机获取 2 个元素（不移除）：", r.srandmember("redis-set-about-key-1", 2))
        print("集合不变：", r.smembers("redis-set-about-key-1"))


def redis_pool_smove_about():
    """
    smove 的使用
    :return:
    """
    with RedisConn() as r:
        print("移动前 set1：", r.smembers("redis-set-about-key-1"))
        print("移动前 set2：", r.smembers("redis-set-about-key-2"))
        r.smove("redis-set-about-key-1", "redis-set-about-key-2", "B")
        print("移动 B 后 set1：", r.smembers("redis-set-about-key-1"))
        print("移动 B 后 set2：", r.smembers("redis-set-about-key-2"))


def redis_pool_sinter_sunion_sdiff_about():
    """
    sinter/sunion/sdiff 的使用
    :return:
    """
    with RedisConn() as r:
        print("交集：", r.sinter(["redis-set-about-key-1", "redis-set-about-key-2"]))
        print("并集：", r.sunion(["redis-set-about-key-1", "redis-set-about-key-2"]))
        print("差集（set1 - set2）：", r.sdiff(["redis-set-about-key-1", "redis-set-about-key-2"]))


def redis_pool_sinterstore_sunionstore_sdiffstore_about():
    """
    sinterstore/sunionstore/sdiffstore 的使用
    :return:
    """
    with RedisConn() as r:
        r.sinterstore("redis-set-inter", ["redis-set-about-key-1", "redis-set-about-key-2"])
        print("交集存储结果：", r.smembers("redis-set-inter"))
        r.sunionstore("redis-set-union", ["redis-set-about-key-1", "redis-set-about-key-2"])
        print("并集存储结果：", r.smembers("redis-set-union"))
        r.sdiffstore("redis-set-diff", ["redis-set-about-key-1", "redis-set-about-key-2"])
        print("差集存储结果：", r.smembers("redis-set-diff"))


if __name__ == '__main__':
    redis_pool_sadd_srem_about()
    redis_pool_scard_about()
    redis_pool_sismember_about()
    redis_pool_smembers_about()
    redis_pool_spop_about()
    redis_pool_srandmember_about()
    redis_pool_smove_about()
    redis_pool_sinter_sunion_sdiff_about()
    redis_pool_sinterstore_sunionstore_sdiffstore_about()
