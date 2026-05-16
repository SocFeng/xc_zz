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


# 写入
with RedisConn() as r:
    # r.set("user:1001:name", "张三")
    # r.expire("user:1001:name", 3600)
    # 下面这样是线程安全的
    r.setex("user:1001:name", 3600, "张三")

# 读取
with RedisConn() as r:
    name = r.get("user:1001:name")
    print(name)
