# python 操作 redis - List 数据类型
from comment import RedisConn


def redis_pool_lpush_rpush_about():
    """
    lpush/rpush 的使用
    :return:
    """
    with RedisConn() as r:
        r.delete("redis-list-about-key")
        r.lpush("redis-list-about-key", "a", "b", "c")
        print("lpush 后的列表：", r.lrange("redis-list-about-key", 0, -1))
        r.rpush("redis-list-about-key", "d", "e", "f")
        print("rpush 后的列表：", r.lrange("redis-list-about-key", 0, -1))


def redis_pool_lpop_rpop_about():
    """
    lpop/rpop 的使用
    :return:
    """
    with RedisConn() as r:
        print("lpop 取出左侧元素：", r.lpop("redis-list-about-key"))
        print("rpop 取出右侧元素：", r.rpop("redis-list-about-key"))
        print("当前列表：", r.lrange("redis-list-about-key", 0, -1))


def redis_pool_lrange_about():
    """
    lrange 的使用
    :return:
    """
    with RedisConn() as r:
        print("获取所有元素：", r.lrange("redis-list-about-key", 0, -1))
        print("获取前两个元素：", r.lrange("redis-list-about-key", 0, 1))


def redis_pool_lindex_about():
    """
    lindex 的使用
    :return:
    """
    with RedisConn() as r:
        print("获取索引为0的元素：", r.lindex("redis-list-about-key", 0))
        print("获取索引为100的元素：", r.lindex("redis-list-about-key", 100))


def redis_pool_linsert_about():
    """
    linsert 的使用
    :return:
    """
    with RedisConn() as r:
        r.linsert("redis-list-about-key", "BEFORE", "b", "before_b")
        print("在 b 前面插入后：", r.lrange("redis-list-about-key", 0, -1))
        r.linsert("redis-list-about-key", "AFTER", "b", "after_b")
        print("在 b 后面插入后：", r.lrange("redis-list-about-key", 0, -1))


def redis_pool_lrem_about():
    """
    lrem 的使用
    :return:
    """
    with RedisConn() as r:
        r.rpush("redis-list-about-key", "x", "x", "x")
        print("添加 x 后：", r.lrange("redis-list-about-key", 0, -1))
        print("删除 2 个 x：", r.lrem("redis-list-about-key", 2, "x"))
        print("删除后：", r.lrange("redis-list-about-key", 0, -1))


def redis_pool_ltrim_about():
    """
    ltrim 的使用
    :return:
    """
    with RedisConn() as r:
        r.delete("redis-list-trim-key")
        r.rpush("redis-list-trim-key", "1", "2", "3", "4", "5")
        print("ltrim 前：", r.lrange("redis-list-trim-key", 0, -1))
        r.ltrim("redis-list-trim-key", 1, 3)
        print("ltrim 后（保留索引1-3）：", r.lrange("redis-list-trim-key", 0, -1))


def redis_pool_llen_about():
    """
    llen 的使用
    :return:
    """
    with RedisConn() as r:
        print("列表长度：", r.llen("redis-list-about-key"))


def redis_pool_lset_about():
    """
    lset 的使用
    :return:
    """
    with RedisConn() as r:
        print("lset 前：", r.lrange("redis-list-about-key", 0, -1))
        r.lset("redis-list-about-key", 0, "changed_value")
        print("lset 后（索引0修改）：", r.lrange("redis-list-about-key", 0, -1))


def redis_pool_rpoplpush_about():
    """
    rpoplpush 的使用
    :return:
    """
    with RedisConn() as r:
        r.delete("redis-list-about-key-2")
        print("list1：", r.lrange("redis-list-about-key", 0, -1))
        result = r.rpoplpush("redis-list-about-key", "redis-list-about-key-2")
        print("rpoplpush 取出的元素：", result)
        print("list1：", r.lrange("redis-list-about-key", 0, -1))
        print("list2：", r.lrange("redis-list-about-key-2", 0, -1))


if __name__ == '__main__':
    redis_pool_lpush_rpush_about()
    redis_pool_lpop_rpop_about()
    redis_pool_lrange_about()
    redis_pool_lindex_about()
    redis_pool_linsert_about()
    redis_pool_lrem_about()
    redis_pool_ltrim_about()
    redis_pool_llen_about()
    redis_pool_lset_about()
    redis_pool_rpoplpush_about()
