# 连接redis数据库


import redis

r = redis.Redis(
    host='127.0.0.1',
    port=6379,
    db=0,
    # 如果有用户和密码
    # username='xxx',
    # password='xxx'

)
# 测试是否连接成功

print("查看是否连接成功：",r.ping())