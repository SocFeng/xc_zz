# Docker 在 Linux 中的安装指南

## 为什么选择 Docker？

Docker 提供了轻量级的虚拟化解决方案，具有以下优势：
- 环境统一：开发、测试、生产环境一致性
- 版本隔离：不同版本软件互不干扰
- 快速部署：一键启动复杂应用
- 资源占用少：比传统虚拟机更高效
- 易于管理：丰富的命令行工具和生态系统

## 安装前准备

### 检查系统要求
确保你的 Linux 系统满足以下条件：
- 64位系统架构
- Linux 内核版本不低于 3.10（推荐 3.10+）
- 至少 4GB RAM

检查内核版本：
```bash
uname -r
```

### 移除旧版本（如有）

某些旧版可能被命名为 `docker`, `docker-engine`, `docker.io`, 或 `containerd`。

Ubuntu/Debian:
```bash
sudo apt-get remove docker docker-engine docker.io containerd runc
```

CentOS/RHEL/Fedora:
```bash
sudo yum remove docker \
                  docker-client \
                  docker-client-latest \
                  docker-common \
                  docker-latest \
                  docker-latest-logrotate \
                  docker-logrotate \
                  docker-selinux \
                  docker-engine-selinux \
                  docker-engine
```

## 安装方式

### 方式一：使用官方仓库安装（推荐）

#### Ubuntu/Debian 系统

1. 更新包索引：
```bash
sudo apt-get update
```

2. 安装必要的包以支持 HTTPS：
```bash
sudo apt-get install ca-certificates curl gnupg lsb-release
```

3. 添加 Docker 的官方 GPG 密钥：
```bash
sudo mkdir -p /etc/apt/keyrings
curl -fsSL https://download.docker.com/linux/ubuntu/gpg | sudo gpg --dearmor -o /etc/apt/keyrings/docker.gpg
```

4. 设置仓库：
```bash
echo \
  "deb [arch=$(dpkg --print-architecture) signed-by=/etc/apt/keyrings/docker.gpg] https://download.docker.com/linux/ubuntu \
  $(lsb_release -cs) stable" | sudo tee /etc/apt/sources.list.d/docker.list > /dev/null
```

5. 更新包索引并安装 Docker Engine：
```bash
sudo apt-get update
sudo apt-get install docker-ce docker-ce-cli containerd.io docker-compose-plugin
```

#### CentOS/RHEL/Fedora 系统

1. 安装 dnf-utils（如果未安装）：
```bash
sudo dnf install dnf-utils
```

2. 添加 Docker 仓库：
```bash
sudo dnf config-manager --add-repo https://download.docker.com/linux/centos/docker-ce.repo
```

3. 安装 Docker Engine：
```bash
sudo dnf install docker-ce docker-ce-cli containerd.io docker-buildx-plugin docker-compose-plugin
```

### 方式二：使用便捷脚本安装

Docker 官方提供了一个便捷的安装脚本：

```bash
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh
```

### 方式三：手动下载安装包

1. 访问 Docker 发布页面：https://download.docker.com/linux/ubuntu/dists/
2. 选择你的发行版名称和架构
3. 下载 `.deb`（Ubuntu/Debian）或 `.rpm`（CentOS/RHEL/Fedora）文件
4. 使用包管理器安装

## 启动 Docker 服务

安装完成后，需要启动 Docker 服务并设置为开机自启：

```bash
# 启动 Docker 服务
sudo systemctl start docker

# 设置开机自启
sudo systemctl enable docker

# 验证 Docker 是否正确安装
sudo docker run hello-world
```

## 用户权限配置

默认情况下，只有 root 用户或 docker 组成员可以运行 Docker 命令。

添加当前用户到 docker 组：
```bash
sudo usermod -aG docker $USER
```

注销并重新登录，或运行以下命令刷新组权限：
```bash
newgrp docker
```

验证是否可以不使用 sudo 运行 Docker：
```bash
docker run hello-world
```

## Docker Compose 安装

Docker Compose 是用于定义和运行多容器 Docker 应用程序的工具。

### 方法一：从 GitHub 下载（推荐）
```bash
# 查看最新版本
LATEST_VERSION=$(curl -s https://api.github.com/repos/docker/compose/releases/latest | grep '"tag_name"' | cut -d '"' -f 4)
sudo curl -L "https://github.com/docker/compose/releases/download/${LATEST_VERSION}/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
sudo chmod +x /usr/local/bin/docker-compose
```

### 方法二：通过包管理器
Ubuntu/Debian:
```bash
sudo apt-get install docker-compose-plugin
```

CentOS/RHEL/Fedora:
```bash
sudo dnf install docker-compose-plugin
```

## 常见配置选项

### 修改 Docker 数据存储路径

1. 创建新的数据目录：
```bash
sudo mkdir -p /new/path/docker
```

2. 停止 Docker 服务：
```bash
sudo systemctl stop docker
```

3. 编辑 Docker 配置文件：
```bash
sudo nano /etc/docker/daemon.json
```

4. 添加以下内容：
```json
{
  "data-root": "/new/path/docker"
}
```

5. 重启 Docker 服务：
```bash
sudo systemctl start docker
```

### 配置镜像加速器

在中国大陆地区，访问 Docker Hub 可能较慢，可以通过配置镜像加速器提升速度。

编辑配置文件：
```bash
sudo nano /etc/docker/daemon.json
```

添加加速器地址（可选择一个或多个）：
```json
{
  "registry-mirrors": [
    "https://docker.mirrors.ustc.edu.cn",
    "https://hub-mirror.c.163.com",
    "https://mirror.baidubce.com"
  ]
}
```

重启 Docker 服务使配置生效：
```bash
sudo systemctl restart docker
```

## 常见问题与解决方案

### 1. 权限错误
**问题：** `Got permission denied while trying to connect to the Docker daemon socket...`
**解决：** 将用户添加到 docker 组，参考前面的用户权限配置部分

### 2. 内存不足
**问题：** 容器启动失败，提示内存不足
**解决：** 
- 检查系统可用内存
- 限制容器使用的内存：`docker run -m 512m image_name`

### 3. 端口冲突
**问题：** 容器无法绑定到指定端口
**解决：** 
- 检查端口是否已被其他服务占用：`netstat -tulpn | grep :port`
- 更改容器端口映射

### 4. Docker 服务启动失败
**检查日志：**
```bash
sudo journalctl -u docker.service
```

**重启服务：**
```bash
sudo systemctl daemon-reload
sudo systemctl restart docker
```

### 5. 镜像拉取缓慢
**解决方案：** 配置镜像加速器，参考前面的相关部分

### 6. 磁盘空间不足
**清理 Docker 资源：**
```bash
# 清理所有未使用的资源（容器、网络、镜像、构建缓存）
docker system prune -a

# 只清理构建缓存
docker builder prune

# 查看磁盘使用情况
docker system df
```

### 7. DNS 解析问题
**在容器中设置 DNS：**
```bash
docker run --dns 8.8.8.8 image_name
```

或者修改 Docker daemon 配置：
```json
{
  "dns": ["8.8.8.8", "8.8.4.4"]
}
```

## 常用命令

### 基础命令
```bash
# 查看 Docker 版本信息
docker version

# 查看 Docker 系统信息
docker info

# 查看 Docker 磁盘使用情况
docker system df
```

### 镜像管理
```bash
# 拉取镜像
docker pull image_name

# 查看本地镜像
docker images

# 删除镜像
docker rmi image_name

# 构建镜像
docker build -t image_name .

# 查看镜像历史
docker history image_name
```

### 容器管理
```bash
# 运行容器
docker run -it image_name /bin/bash

# 查看运行中的容器
docker ps

# 查看所有容器（包括停止的）
docker ps -a

# 启动/停止/重启容器
docker start container_name
docker stop container_name
docker restart container_name

# 进入运行中的容器
docker exec -it container_name /bin/bash

# 查看容器日志
docker logs container_name

# 删除容器
docker rm container_name
```

### Docker Compose 命令
```bash
# 启动服务
docker-compose up

# 后台启动服务
docker-compose up -d

# 停止服务
docker-compose down

# 查看服务状态
docker-compose ps

# 查看服务日志
docker-compose logs
```

## 最佳实践

1. **定期更新 Docker**：保持 Docker 引擎的最新版本以获得安全修复和新功能
2. **使用 .dockerignore 文件**：避免将不必要的文件复制到镜像中
3. **优化镜像大小**：使用多阶段构建减少最终镜像体积
4. **使用标签管理镜像**：使用有意义的标签而非 latest
5. **安全性**：定期扫描镜像漏洞，运行非 root 用户的容器
6. **资源限制**：为容器设置适当的 CPU 和内存限制
7. **健康检查**：在 Dockerfile 中添加 HEALTHCHECK 指令