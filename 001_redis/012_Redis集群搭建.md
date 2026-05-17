# Redis 三大核心架构完整搭建文档（主从、哨兵、分片集群）

## 文档说明

本文档基于 **Linux CentOS、Redis 6\.2\+、yum 默认安装（/usr/bin/redis\-server）** 环境，统一适配单机器多实例部署，包含**主从架构、哨兵架构、分片集群**三种核心架构的从零搭建、配置、验证、启停、报错解决方案，所有配置无冗余注释、可直接复制落地，适配学习与测试场景。

统一端口规划（单机多实例隔离）：

- 主从架构：主6379、从6380、从6381

- 哨兵架构：基于一主两从，新增哨兵26379、26380、26381

- 分片集群：6个节点（7000\-7006），3主3从

# 第一章：Redis 一主两从架构搭建

## 一、架构原理

主从复制是Redis最基础的架构，一个主节点（Master）负责读写，多个从节点（Slave）实时同步主节点数据，从节点默认只读，实现数据备份、读写分离，**无自动故障转移能力**。

## 二、环境准备

### 1、创建多实例隔离目录

```bash
# 配置文件目录
mkdir -p /etc/redis/6379
mkdir -p /etc/redis/6380
mkdir -p /etc/redis/6381

# 数据、日志存放目录
mkdir -p /var/lib/redis/6379
mkdir -p /var/lib/redis/6380
mkdir -p /var/lib/redis/6381
```

### 2、统一权限授权（解决权限报错）

```bash
sudo chown -R redis:redis /etc/redis
sudo chown -R redis:redis /var/lib/redis
sudo chmod -R 755 /etc/redis
sudo chmod -R 755 /var/lib/redis
```

## 三、核心配置文件（无密码纯净版）

### 1、主节点 6379（无需任何主从配置）

沿用系统原生主节点，无需修改业务配置，仅优化基础参数

```ini
port 6379
bind 0.0.0.0
daemonize yes
protected-mode no
appendonly yes
dir /var/lib/redis/6379
logfile /var/lib/redis/6379/redis.log
pidfile /var/run/redis_6379.pid
```

### 2、从节点 6380

```ini
port 6380
bind 0.0.0.0
daemonize yes
protected-mode no
appendonly yes
dir /var/lib/redis/6380
logfile /var/lib/redis/6380/redis.log
pidfile /var/run/redis_6380.pid
replicaof 127.0.0.1 6379
```

### 3、从节点 6381

```ini
port 6381
bind 0.0.0.0
daemonize yes
protected-mode no
appendonly yes
dir /var/lib/redis/6381
logfile /var/lib/redis/6381/redis.log
pidfile /var/run/redis_6381.pid
replicaof 127.0.0.1 6379
```

**关键规则**：主节点无密码时，从节点无需配置`requirepass`、`masterauth`；主节点有密码，从节点必须配置 `masterauth 主节点密码`。

## 四、启动与验证

### 1、启动所有实例

```bash
/usr/bin/redis-server /etc/redis/6379/redis.conf
/usr/bin/redis-server /etc/redis/6380/redis.conf
/usr/bin/redis-server /etc/redis/6381/redis.conf
```

### 2、查看进程

```bash
ps -ef | grep redis-server
```

出现6379、6380、6381三个服务进程即为启动成功。

### 3、主从状态验证

主节点执行：

```redis
INFO replication
```

正常返回：`role:master`、`connected\_slaves:2`

从节点执行：

```redis
INFO replication
```

正常返回：`role:slave`、`master\_link\_status:up`

### 4、数据同步测试

主节点写入数据，从节点可查询；从节点禁止写入，符合读写分离机制。

## 五、启停命令

```bash
# 停止
redis-cli -p 6379 shutdown
redis-cli -p 6380 shutdown
redis-cli -p 6381 shutdown

# 重启
/usr/bin/redis-server /etc/redis/6379/redis.conf
/usr/bin/redis-server /etc/redis/6380/redis.conf
/usr/bin/redis-server /etc/redis/6381/redis.conf
```

# 第二章：Redis 哨兵高可用架构搭建

## 一、架构原理

哨兵（Sentinel）基于主从架构，解决**主节点故障无法自动切换**的问题。通过3个哨兵节点监控主从节点，主节点宕机后，自动投票选举新主节点，实现故障自动转移、高可用。

架构组成：1主2从 \+ 3哨兵

## 二、前置条件

确保第一章**一主两从架构正常运行**，主从同步状态正常（master\_link\_status:up）。

## 三、哨兵配置搭建

### 1、创建哨兵目录

```bash
mkdir -p /etc/redis/sentinel26379
mkdir -p /etc/redis/sentinel26380
mkdir -p /etc/redis/sentinel26381
```

### 2、哨兵统一配置（三份仅端口不同）

哨兵26379配置：/etc/redis/sentinel26379/sentinel\.conf

```ini
port 26379
bind 0.0.0.0
daemonize yes
protected-mode no
logfile /var/lib/redis/sentinel26379.log
sentinel monitor mymaster 127.0.0.1 6379 2
sentinel down-after-milliseconds mymaster 3000
sentinel failover-timeout mymaster 10000
sentinel parallel-syncs mymaster 1
```

哨兵26380、26381仅修改端口和日志路径，其余配置完全一致。

**核心参数解释**：

- `sentinel monitor mymaster 127\.0\.0\.1 6379 2`：监控主节点，2个哨兵判定宕机则触发故障转移

- `down\-after\-milliseconds 3000`：3秒未响应判定节点主观下线

- `failover\-timeout 10000`：故障转移超时时间10秒

## 四、启动哨兵集群

```bash
redis-sentinel /etc/redis/sentinel26379/sentinel.conf
redis-sentinel /etc/redis/sentinel26380/sentinel.conf
redis-sentinel /etc/redis/sentinel26381/sentinel.conf
```

## 五、哨兵状态验证

### 1、查看哨兵信息

```bash
redis-cli -p 26379
127.0.0.1:26379> INFO sentinel
```

正常显示监控的主节点、从节点、哨兵节点数量。

### 2、故障转移测试

手动关闭主节点6379，哨兵会自动选举6380/6381为新主节点，重启旧主后自动变为从节点。

## 六、哨兵启停命令

```bash
# 停止哨兵
redis-cli -p 26379 shutdown
redis-cli -p 26380 shutdown
redis-cli -p 26381 shutdown

# 启动哨兵
redis-sentinel /etc/redis/sentinel26379/sentinel.conf
redis-sentinel /etc/redis/sentinel26380/sentinel.conf
redis-sentinel /etc/redis/sentinel26381/sentinel.conf
```

# 第三章：Redis 分片集群（Cluster）搭建

## 一、架构原理

Redis Cluster 分片集群实现**数据分片存储 \+ 高可用**，无中心节点，将数据分为16384个哈希槽，分散到多个主节点，从节点备份对应主节点数据，支持横向扩容、海量数据存储，是生产主流分布式架构。

本次搭建：**3主3从 6节点集群**，端口7000、7001、7002（主），7003、7004、7005（从）

## 二、环境准备

### 1、创建6个节点目录

```bash
for port in {7000..7005};do
mkdir -p /etc/redis/$port
mkdir -p /var/lib/redis/$port
done
```

### 2、批量授权

```bash
sudo chown -R redis:redis /etc/redis /var/lib/redis
sudo chmod -R 755 /etc/redis /var/lib/redis
```

## 三、集群节点统一配置

所有6个节点配置格式一致，仅端口不同，以7000为例：/etc/redis/7000/redis\.conf

```ini
port 7000
bind 0.0.0.0
daemonize yes
protected-mode no
dir /var/lib/redis/7000
logfile /var/lib/redis/7000/redis.log
pidfile /var/run/redis_7000.pid
appendonly yes
# 集群核心配置
cluster-enabled yes
cluster-config-file nodes-7000.conf
cluster-node-timeout 15000
```

其余7001\-7005节点，仅修改端口、日志、pid、集群配置文件名即可。

## 四、启动所有集群节点

```bash
for port in {7000..7005};do
/usr/bin/redis-server /etc/redis/$port/redis.conf
done
```

## 五、创建集群（核心步骤）

Redis6\.0\+ 无需ruby环境，直接执行集群创建命令，自动分配哈希槽和主从关系

```bash
redis-cli --cluster create \
127.0.0.1:7000 \
127.0.0.1:7001 \
127.0.0.1:7002 \
127.0.0.1:7003 \
127.0.0.1:7004 \
127.0.0.1:7005 \
--cluster-replicas 1
```

执行后输入 `yes` 确认创建，自动完成3主3从分配。

## 六、集群验证

### 1、进入集群客户端（必须带\-c参数）

```bash
redis-cli -p 7000 -c
```

### 2、查看集群状态

```redis
cluster info
cluster nodes
```

正常显示3个master、3个slave，集群状态 `cluster\_state:ok`

### 3、数据测试

写入数据自动跳转对应哈希槽节点，集群正常读写，节点宕机后从节点自动顶替。

## 七、集群启停命令

```bash
# 停止所有集群节点
for port in {7000..7005};do
redis-cli -p $port shutdown
done

# 重启所有集群节点
for port in {7000..7005};do
/usr/bin/redis-server /etc/redis/$port/redis.conf
done
```

# 第四章：三大架构对比与核心注意事项

## 一、架构功能对比

|架构类型|核心能力|故障转移|数据分片|适用场景|
|---|---|---|---|---|
|主从架构|数据备份、读写分离|不支持|不支持|简单备份、读写分离、学习测试|
|哨兵架构|主从高可用、自动故障转移|支持|不支持|中小型项目、高可用需求、数据量不大|
|分片集群|分布式存储、分片\+高可用、横向扩容|支持|支持|大型项目、海量数据、高并发场景|

## 二、通用避坑注意事项

1. **端口冲突问题**：单机多实例必须端口隔离，启动新架构前，停止旧架构所有redis进程，避免端口占用

2. **密码配置规则**：主节点无密码，从节点/哨兵无需密码配置；主节点有密码，从节点必须配置masterauth，哨兵必须配置sentinel auth\-pass

3. **配置文件规范**：禁止配置行尾加注释，会导致启动报错

4. **集群连接规范**：操作分片集群必须加 `\-c` 参数，否则数据跳转报错

5. **权限问题**：所有实例目录必须授权redis用户，避免日志、文件读写权限拒绝

## 三、常见通用报错解决

- Permission denied：执行文档内chown、chmod授权命令

- master\_link\_status:down：检查bind绑定、端口通断、主从密码一致性

- 集群创建失败：清空所有节点nodes配置文件、重启节点后重新创建

- 哨兵监控异常：确认主从架构正常、防火墙放行端口、配置文件参数正确

> （注：文档部分内容可能由 AI 生成）
