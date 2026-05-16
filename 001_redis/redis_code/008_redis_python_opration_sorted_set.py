# python 操作 redis - Sorted Set 数据类型
from comment import RedisConn


def redis_pool_zadd_about():
    """
    zadd 的使用
    :return:
    """
    with RedisConn() as r:
        r.delete("redis-zset-about-key")
        r.zadd("redis-zset-about-key", {"ls": 87, "ww": 76, "lh": 97, "ml": 23, "zs": 64})
        print("添加后的有序集合：", r.zrange("redis-zset-about-key", 0, -1, withscores=True))


def redis_pool_zrem_about():
    """
    zrem 的使用
    :return:
    """
    with RedisConn() as r:
        r.zrem("redis-zset-about-key", "ls", "lh")
        print("删除 ls lh 后：", r.zrange("redis-zset-about-key", 0, -1, withscores=True))


def redis_pool_zscore_about():
    """
    zscore 的使用
    :return:
    """
    with RedisConn() as r:
        print("ww 的分数：", r.zscore("redis-zset-about-key", "ww"))
        print("不存在的分数：", r.zscore("redis-zset-about-key", "not_exist"))


def redis_pool_zrange_about():
    """
    zrange 的使用
    :return:
    """
    with RedisConn() as r:
        print("所有元素（带分数）：", r.zrange("redis-zset-about-key", 0, -1, withscores=True))
        print("所有元素（不带分数）：", r.zrange("redis-zset-about-key", 0, -1))


def redis_pool_zrank_about():
    """
    zrank 的使用
    :return:
    """
    with RedisConn() as r:
        print("zs 的排名：", r.zrank("redis-zset-about-key", "zs"))
        print("ww 的排名：", r.zrank("redis-zset-about-key", "ww"))


def redis_pool_zcard_about():
    """
    zcard 的使用
    :return:
    """
    with RedisConn() as r:
        print("有序集合元素个数：", r.zcard("redis-zset-about-key"))


def redis_pool_zcount_about():
    """
    zcount 的使用
    :return:
    """
    with RedisConn() as r:
        print("分数在 0-70 之间的元素个数：", r.zcount("redis-zset-about-key", 0, 70))


def redis_pool_zincrby_about():
    """
    zincrby 的使用
    :return:
    """
    with RedisConn() as r:
        print("ml 增长前分数：", r.zscore("redis-zset-about-key", "ml"))
        r.zincrby("redis-zset-about-key", 9, "ml")
        print("ml 增长 9 后分数：", r.zscore("redis-zset-about-key", "ml"))


def redis_pool_zrangebyscore_about():
    """
    zrangebyscore 的使用
    :return:
    """
    with RedisConn() as r:
        print("分数在 60-80 之间的元素：", r.zrangebyscore("redis-zset-about-key", 60, 80))
        print("分数在 60-80 之间的元素（带分数）：", r.zrangebyscore("redis-zset-about-key", 60, 80, withscores=True))


if __name__ == '__main__':
    redis_pool_zadd_about()
    redis_pool_zrem_about()
    redis_pool_zscore_about()
    redis_pool_zrange_about()
    redis_pool_zrank_about()
    redis_pool_zcard_about()
    redis_pool_zcount_about()
    redis_pool_zincrby_about()
    redis_pool_zrangebyscore_about()
