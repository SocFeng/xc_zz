import time
import threading
from datetime import datetime
from comment import RedisConn  # 你的生产连接

# 自定义起始时间点（2026-01-01 00:00:00）
BEGIN_TIMESTAMP = int(datetime(2026, 1, 1).timestamp())
COUNT_BITS = 32  # 序列号占 32 位

def generate_long_id() -> int:
    with RedisConn() as r:
        # 当前秒级时间戳
        now_second = int(time.time())
        timestamp = now_second - BEGIN_TIMESTAMP

        # 高并发安全：Redis 原子自增
        seq = r.incr("order:id:sequence")

        # 溢出保护（32位最大 4294967295）
        if seq >= (1 << COUNT_BITS):
            r.set("order:id:sequence", 0)
            seq = r.incr("order:id:sequence")

        # 拼接唯一ID
        return (timestamp << COUNT_BITS) | seq


# ==============================
# 🔥 超级高并发测试（核心）
# 100 个线程，每个生成 1000 个 ID
# 总共 100,000 个 ID，测试是否重复！
# ==============================
def test_task(ids_set, lock):
    for _ in range(2000):
        new_id = generate_long_id()
        with lock:
            ids_set.add(new_id)  # 线程安全加入集合


def high_concurrency_test():
    print("🚀 开始高并发测试（100线程 × 1000次 = 100万ID）...")

    ids_set = set()
    lock = threading.Lock()
    thread_count = 100  # 100线程并发
    threads = []

    # 启动多线程
    for i in range(thread_count):
        t = threading.Thread(target=test_task, args=(ids_set, lock))
        threads.append(t)
        t.start()

    # 等待全部结束
    for t in threads:
        t.join()

    # 结果校验
    print(f"✅ 预期生成数量：{thread_count * 2000}")
    print(f"✅ 实际去重数量：{len(ids_set)}")

    if len(ids_set) == thread_count * 2000:
        print("🎉 测试成功：无重复ID，高并发安全！")
    else:
        print("❌ 测试失败：出现重复！")


if __name__ == "__main__":
    high_concurrency_test()