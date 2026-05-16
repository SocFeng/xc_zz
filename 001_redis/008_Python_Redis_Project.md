## Python Redis 实战项目

基于 Flask + Redis 实现的常见业务场景 Demo，代码文件：`redis_code/009_redis_flask_project.py`

### 依赖安装

```shell
pip install flask redis
```

### 项目结构

```
redis_code/
├── comment.py                        # Redis连接池（共用）
├── 009_redis_flask_project.py        # Flask + Redis 实战接口
```

---

### 1. 发送验证码

**接口**：`POST /api/send_code`

**请求体**：

```json
{"phone": "13800138000"}
```

**Redis 设计**：

| Key | 类型 | 值 | 过期时间 | 作用 |
|-----|------|------|---------|------|
| `sms:code:{phone}` | String | 6位验证码 | 300秒(5分钟) | 存储验证码，登录时校验 |
| `sms:rate:{phone}` | String | 1 | 60秒 | 防刷限制，60秒内不能重复发送 |

**流程**：

1. 检查 `sms:rate:{phone}` 是否存在，存在则返回剩余等待时间（防刷）
2. 生成6位随机数字验证码
3. 将验证码存入 `sms:code:{phone}`，设置5分钟过期
4. 设置 `sms:rate:{phone}` 60秒防刷标记
5. 模拟发送短信（返回验证码方便测试）

**测试**：

```shell
curl -X POST http://127.0.0.1:5000/api/send_code \
  -H "Content-Type: application/json" \
  -d '{"phone": "13800138000"}'

# 响应
{"code": 200, "data": {"code": "538921"}, "msg": "验证码发送成功"}

# 60秒内重复发送（防刷）
{"code": 429, "msg": "请等待45秒后再发送"}
```

---

### 2. 验证码校验与登录

**接口**：`POST /api/login`

**请求体**：

```json
{"phone": "13800138000", "code": "538921"}
```

**Redis 设计**：

| Key | 类型 | 值 | 过期时间 | 作用 |
|-----|------|------|---------|------|
| `user:token:{token}` | String | 手机号 | 7200秒(2小时) | 登录态，认证时校验 |

**流程**：

1. 从 Redis 取出 `sms:code:{phone}` 校验验证码是否正确
2. 验证码错误或已过期，返回错误信息
3. 验证通过后，删除验证码（一次性使用）
4. 生成 UUID 作为 token，存入 `user:token:{token}`，有效期2小时
5. 返回 token 给客户端

**测试**：

```shell
# 验证码正确
curl -X POST http://127.0.0.1:5000/api/login \
  -H "Content-Type: application/json" \
  -d '{"phone": "13800138000", "code": "538921"}'

# 响应
{"code": 200, "data": {"phone": "13800138000", "token": "a1b2c3d4..."}, "msg": "登录成功"}

# 验证码错误
{"code": 400, "msg": "验证码错误"}

# 验证码过期
{"code": 400, "msg": "验证码已过期，请重新发送"}
```

---

### 3. 用户认证拦截

使用 `@login_required` 装饰器实现，自动从请求头中读取 token 并校验。

**Token 传递方式**：`Authorization: Bearer {token}`

**核心逻辑**：

```python
def login_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = request.headers.get("Authorization", "").replace("Bearer ", "")
        if not token:
            return jsonify({"code": 401, "msg": "未登录，请先登录"}), 401

        with RedisConn() as r:
            phone = r.get(f"user:token:{token}")
            if phone is None:
                return jsonify({"code": 401, "msg": "token无效或已过期，请重新登录"}), 401
            # 续期：每次访问自动续期2小时
            r.expire(f"user:token:{token}", 7200)
            request.phone = phone

        return f(*args, **kwargs)
    return decorated
```

**关键点**：
- token 不存在或已过期，返回 401
- 每次访问自动续期（sliding expiration），用户活跃就不会掉线
- 用户信息绑定到 `request` 上，方便后续接口使用

**受保护的接口**：

| 接口 | 方法 | 说明 |
|------|------|------|
| `/api/user/info` | GET | 获取用户信息 |
| `/api/logout` | POST | 退出登录，删除 Redis 中的 token |
| `/api/order/list` | GET | 查询订单（同时受限流保护） |

**测试**：

```shell
# 未登录访问（失败）
curl http://127.0.0.1:5000/api/user/info
{"code": 401, "msg": "未登录，请先登录"}

# 带 token 访问（成功）
curl http://127.0.0.1:5000/api/user/info \
  -H "Authorization: Bearer a1b2c3d4..."
{"code": 200, "data": {"phone": "13800138000", "nickname": "用户8000"}, "msg": "获取成功"}

# 退出登录
curl -X POST http://127.0.0.1:5000/api/logout \
  -H "Authorization: Bearer a1b2c3d4..."
{"code": 200, "msg": "退出成功"}

# 退出后再次访问（失败）
curl http://127.0.0.1:5000/api/user/info \
  -H "Authorization: Bearer a1b2c3d4..."
{"code": 401, "msg": "token无效或已过期，请重新登录"}
```

---

### 4. 用户限流

使用 `@rate_limit` 装饰器实现，基于 Redis INCR + EXPIRE 的固定窗口限流。

**Redis 设计**：

| Key | 类型 | 值 | 过期时间 | 作用 |
|-----|------|------|---------|------|
| `rate:limit:{ip}:{func_name}` | String | 请求次数 | 窗口时间 | 计数器，超过阈值则拒绝 |

**核心逻辑**：

```python
def rate_limit(max_requests=10, window=60):
    def decorator(f):
        @wraps(f)
        def decorated(*args, **kwargs):
            ip = request.remote_addr
            key = f"rate:limit:{ip}:{f.__name__}"

            with RedisConn() as r:
                current = r.incr(key)
                if current == 1:
                    r.expire(key, window)

                if current > max_requests:
                    ttl = r.ttl(key)
                    return jsonify({
                        "code": 429,
                        "msg": f"请求过于频繁，请{ttl}秒后再试",
                        "data": {"retry_after": ttl}
                    }), 429

            return f(*args, **kwargs)
        return decorated
    return decorator
```

**关键点**：
- 使用 Redis `INCR` 原子操作计数，天然线程安全
- 第一次请求时 `INCR` 返回1，此时设置过期时间
- 超过阈值返回 429，并告知重试等待时间
- 可组合 `@login_required` + `@rate_limit` 同时使用

**限流接口**：

| 接口 | 方法 | 限制 | 说明 |
|------|------|------|------|
| `/api/limited_resource` | GET | 5次/60秒 | 限流演示接口 |
| `/api/order/list` | GET | 20次/60秒 | 需登录 + 限流 |

**测试**：

```shell
# 前5次正常
for i in $(seq 1 5); do
  curl -s http://127.0.0.1:5000/api/limited_resource
done
{"code": 200, "data": {"content": "这是一个受限流保护的资源"}, "msg": "请求成功"}
...

# 第6次被限流
curl -s http://127.0.0.1:5000/api/limited_resource
{"code": 429, "data": {"retry_after": 55}, "msg": "请求过于频繁，请55秒后再试"}
```

---

### API 总览

| 接口 | 方法 | 需要登录 | 限流 | 说明 |
|------|------|---------|------|------|
| `/api/send_code` | POST | 否 | 60秒防刷 | 发送验证码 |
| `/api/login` | POST | 否 | 否 | 验证码登录 |
| `/api/user/info` | GET | 是 | 否 | 获取用户信息 |
| `/api/logout` | POST | 是 | 否 | 退出登录 |
| `/api/limited_resource` | GET | 否 | 5次/60秒 | 限流演示 |
| `/api/order/list` | GET | 是 | 20次/60秒 | 订单列表（综合示例） |
