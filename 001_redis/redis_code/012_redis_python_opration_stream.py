# python 操作 redis - Stream 数据类型
import time
import threading

from comment import RedisConn


# ============================================================
# 基础操作
# ============================================================

def redis_pool_xadd_about():
    """
    xadd 的使用：向 stream 中添加消息
    :return:
    """
    with RedisConn() as r:
        r.delete("redis-stream-about-key")
        # * 表示自动生成消息ID（时间戳-序号）
        msg_id_1 = r.xadd("redis-stream-about-key", {"name": "张三", "age": "24"})
        msg_id_2 = r.xadd("redis-stream-about-key", {"name": "李四", "age": "25"})
        msg_id_3 = r.xadd("redis-stream-about-key", {"name": "王五", "age": "26"})
        print("添加的消息ID：", msg_id_1, msg_id_2, msg_id_3)

        # 指定 MAXLEN，近似裁剪，保留最新的1000条
        r.xadd("redis-stream-about-key", {"name": "赵六", "age": "27"}, maxlen=1000, approximate=True)


def redis_pool_xlen_about():
    """
    xlen 的使用：获取 stream 中消息数量
    :return:
    """
    with RedisConn() as r:
        print("stream 中的消息数量：", r.xlen("redis-stream-about-key"))


def redis_pool_xrange_about():
    """
    xrange 的使用：获取指定范围的消息（正序）
    :return:
    """
    with RedisConn() as r:
        # 获取所有消息（- 最小，+ 最大）
        print("所有消息（正序）：")
        for msg_id, data in r.xrange("redis-stream-about-key", "-", "+"):
            print(f"  ID: {msg_id}, 数据: {data}")

        # 获取前2条消息
        print("前2条消息：")
        for msg_id, data in r.xrange("redis-stream-about-key", "-", "+", count=2):
            print(f"  ID: {msg_id}, 数据: {data}")


def redis_pool_xrevrange_about():
    """
    xrevrange 的使用：获取指定范围的消息（倒序）
    :return:
    """
    with RedisConn() as r:
        # 注意：倒序时 start 放大的，end 放小的
        print("所有消息（倒序）：")
        for msg_id, data in r.xrevrange("redis-stream-about-key", "+", "-", count=3):
            print(f"  ID: {msg_id}, 数据: {data}")


def redis_pool_xread_about():
    """
    xread 的使用：独立消费者读取新消息
    :return:
    """
    with RedisConn() as r:
        # 从头开始读取所有消息
        print("从头读取所有消息：")
        result = r.xread({"redis-stream-about-key": "0"}, count=10, block=1000)
        if result:
            for stream_name, messages in result:
                for msg_id, data in messages:
                    print(f"  Stream: {stream_name}, ID: {msg_id}, 数据: {data}")


def redis_pool_xdel_about():
    """
    xdel 的使用：删除指定消息
    :return:
    """
    with RedisConn() as r:
        # 先获取一条消息的 ID
        all_msgs = r.xrange("redis-stream-about-key", "-", "+", count=1)
        if all_msgs:
            msg_id = all_msgs[0][0]
            print(f"删除消息 ID: {msg_id}")
            print("删除数量：", r.xdel("redis-stream-about-key", msg_id))
            print("删除后消息数量：", r.xlen("redis-stream-about-key"))


# ============================================================
# 消费组操作
# ============================================================

def redis_pool_xgroup_about():
    """
    xgroup 的使用：创建/管理消费组
    :return:
    """
    with RedisConn() as r:
        # 先清理旧的消费组
        try:
            r.xgroup_destroy("redis-stream-about-key", "group1")
        except Exception:
            pass

        # 创建消费组，从头开始消费（0）
        created = r.xgroup_create("redis-stream-about-key", "group1", id="0")
        print("创建消费组 group1：", created)

        # 创建消费组，只消费新消息（$）
        try:
            r.xgroup_destroy("redis-stream-about-key", "group2")
        except Exception:
            pass
        created = r.xgroup_create("redis-stream-about-key", "group2", id="$")
        print("创建消费组 group2（只消费新消息）：", created)


def redis_pool_xreadgroup_about():
    """
    xreadgroup 的使用：消费组读取消息
    :return:
    """
    with RedisConn() as r:
        # consumer1 读取新消息（> 表示未被消费组消费过的消息）
        print("consumer1 读取新消息：")
        result = r.xreadgroup("group1", "consumer1", {"redis-stream-about-key": ">"}, count=2)
        if result:
            for stream_name, messages in result:
                for msg_id, data in messages:
                    print(f"  ID: {msg_id}, 数据: {data}")

        # consumer2 读取剩余的新消息
        print("consumer2 读取剩余消息：")
        result = r.xreadgroup("group1", "consumer2", {"redis-stream-about-key": ">"}, count=10)
        if result:
            for stream_name, messages in result:
                for msg_id, data in messages:
                    print(f"  ID: {msg_id}, 数据: {data}")

        # 读取 consumer1 已消费但未确认的消息（pending）
        print("consumer1 的 pending 消息：")
        result = r.xreadgroup("group1", "consumer1", {"redis-stream-about-key": "0"})
        if result:
            for stream_name, messages in result:
                for msg_id, data in messages:
                    print(f"  ID: {msg_id}, 数据: {data}")


def redis_pool_xack_about():
    """
    xack 的使用：确认消息已处理
    :return:
    """
    with RedisConn() as r:
        # 先获取 consumer1 的 pending 消息
        result = r.xreadgroup("group1", "consumer1", {"redis-stream-about-key": "0"})
        if result:
            for stream_name, messages in result:
                for msg_id, data in messages:
                    # 确认消息
                    acked = r.xack("redis-stream-about-key", "group1", msg_id)
                    print(f"确认消息 {msg_id}：{acked}")


def redis_pool_xpending_about():
    """
    xpending 的使用：查看未确认消息
    :return:
    """
    with RedisConn() as r:
        # 添加几条新消息
        r.xadd("redis-stream-about-key", {"name": "pending测试1", "age": "30"})
        r.xadd("redis-stream-about-key", {"name": "pending测试2", "age": "31"})

        # consumer1 消费但不确认
        r.xreadgroup("group1", "consumer1", {"redis-stream-about-key": ">"})

        # 查看 pending 概览
        pending_info = r.xpending("redis-stream-about-key", "group1")
        print("pending 概览：", pending_info)

        # 查看 pending 详细列表
        pending_range = r.xpending_range("redis-stream-about-key", "group1", min="-", max="+", count=10)
        print("pending 详情：")
        for item in pending_range:
            print(f"  消息ID: {item['message_id']}, 消费者: {item['consumer']}, 空闲: {item['time_since_delivered']}ms")

        # 确认这些消息
        for item in pending_range:
            r.xack("redis-stream-about-key", "group1", item['message_id'])


def redis_pool_xclaim_about():
    """
    xclaim 的使用：将 pending 消息转交给其他消费者
    :return:
    """
    with RedisConn() as r:
        # 添加一条消息，让 consumer1 消费但不确认
        new_id = r.xadd("redis-stream-about-key", {"name": "claim测试", "age": "32"})
        r.xreadgroup("group1", "consumer1", {"redis-stream-about-key": ">"})

        # 查看 consumer1 的 pending 消息
        pending = r.xpending_range("redis-stream-about-key", "group1", min="-", max="+", count=10)
        print("consumer1 的 pending 消息：", [p['message_id'] for p in pending])

        # 模拟空闲时间（实际中需要等待 min_idle_time）
        time.sleep(0.1)

        # 将消息转交给 consumer2（idle_time_ms=0 强制转交）
        for item in pending:
            claimed = r.xclaim("redis-stream-about-key", "group1", "consumer2", min_idle_time=0,
                               message_ids=[item['message_id']])
            print(f"转交消息 {item['message_id']} 给 consumer2：{len(claimed)} 条")

        # 查看 consumer2 的 pending 消息
        pending2 = r.xpending_range("redis-stream-about-key", "group1", min="-", max="+", consumername="consumer2")
        print("consumer2 的 pending 消息：", [p['message_id'] for p in pending2])

        # 清理：确认所有消息
        for item in pending2:
            r.xack("redis-stream-about-key", "group1", item['message_id'])


def redis_pool_xtrim_about():
    """
    xtrim 的使用：修剪消息流
    :return:
    """
    with RedisConn() as r:
        # 添加多条消息
        for i in range(10):
            r.xadd("redis-stream-about-key", {"name": f"trim测试{i}", "age": str(20 + i)})

        before = r.xlen("redis-stream-about-key")
        print(f"裁剪前消息数量：{before}")

        # 近似裁剪，保留最新 5 条
        trimmed = r.xtrim("redis-stream-about-key", maxlen=5, approximate=True)
        print(f"被裁剪的消息数量：{trimmed}")

        after = r.xlen("redis-stream-about-key")
        print(f"裁剪后消息数量：{after}")


def redis_pool_xinfo_about():
    """
    xinfo 的使用：查看流和消费组信息
    :return:
    """
    with RedisConn() as r:
        # 查看 stream 信息
        stream_info = r.xinfo_stream("redis-stream-about-key")
        print("stream 信息：")
        print(f"  消息总数: {stream_info['length']}")
        print(f"  消费组数量: {stream_info['groups']}")
        print(f"  最后生成的ID: {stream_info['last-generated-id']}")

        # 查看消费组信息
        groups_info = r.xinfo_groups("redis-stream-about-key")
        print("消费组信息：")
        for group in groups_info:
            print(f"  组名: {group['name']}, 消费者数: {group['consumers']}, pending数: {group['pending']}")

        # 查看消费者信息
        consumers_info = r.xinfo_consumers("redis-stream-about-key", "group1")
        print("消费者信息：")
        for consumer in consumers_info:
            print(f"  消费者: {consumer['name']}, pending数: {consumer['pending']}, 空闲: {consumer['idle']}ms")


# ============================================================
# 综合示例：模拟生产者消费者
# ============================================================

def redis_pool_stream_producer_consumer_demo():
    """
    模拟生产者消费者的完整流程
    :return:
    """
    print("\n===== 生产者消费者演示 =====")
    with RedisConn() as r:
        # 清理环境
        r.delete("redis-stream-demo")
        try:
            r.xgroup_destroy("redis-stream-demo", "order_group")
        except Exception:
            pass

        # 创建 stream 和消费组
        r.xadd("redis-stream-demo", {"type": "init", "data": "stream已创建"})
        r.xgroup_create("redis-stream-demo", "order_group", id="0")
        print("[准备] stream 和消费组已创建")

    def producer():
        """生产者：模拟产生订单消息"""
        with RedisConn() as r:
            for i in range(5):
                msg_id = r.xadd("redis-stream-demo", {"order_id": f"ORD{1000 + i}", "amount": str(100 + i * 50)})
                print(f"[生产者] 发送消息: order_id=ORD{1000+i}, ID={msg_id}")
                time.sleep(0.2)

    def consumer(name):
        """消费者：从消费组中消费消息"""
        with RedisConn() as r:
            while True:
                result = r.xreadgroup("order_group", name, {"redis-stream-demo": ">"}, count=1, block=3000)
                if not result:
                    print(f"[{name}] 没有更多消息，退出")
                    break
                for stream_name, messages in result:
                    for msg_id, data in messages:
                        print(f"[{name}] 消费消息: ID={msg_id}, 数据={data}")
                        # 模拟业务处理
                        time.sleep(0.3)
                        # 确认消息
                        r.xack("redis-stream-demo", "order_group", msg_id)
                        print(f"[{name}] 确认消息: ID={msg_id}")

    # 启动生产者和消费者
    producer_thread = threading.Thread(target=producer)
    consumer1_thread = threading.Thread(target=consumer, args=("worker-1",))
    consumer2_thread = threading.Thread(target=consumer, args=("worker-2",))

    producer_thread.start()
    consumer1_thread.start()
    consumer2_thread.start()

    producer_thread.join()
    consumer1_thread.join()
    consumer2_thread.join()

    # 查看最终状态
    with RedisConn() as r:
        pending_info = r.xpending("redis-stream-demo", "order_group")
        print(f"\n[最终状态] pending 总数: {pending_info['pending']}")
        print(f"[最终状态] stream 消息总数: {r.xlen('redis-stream-demo')}")


if __name__ == '__main__':
    # 基础操作
    redis_pool_xadd_about()
    redis_pool_xlen_about()
    redis_pool_xrange_about()
    redis_pool_xrevrange_about()
    redis_pool_xread_about()
    redis_pool_xdel_about()

    # 消费组操作
    redis_pool_xgroup_about()
    redis_pool_xreadgroup_about()
    redis_pool_xack_about()
    redis_pool_xpending_about()
    # redis_pool_xclaim_about()

    # 裁剪和信息查看
    redis_pool_xtrim_about()
    redis_pool_xinfo_about()

    # 生产者消费者演示
    redis_pool_stream_producer_consumer_demo()
