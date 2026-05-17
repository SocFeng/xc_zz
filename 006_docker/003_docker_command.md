## DockerFile

### 是什么
Dockerfile 是一个文本文件，包含了一系列用于构建 Docker 镜像的指令。它定义了镜像的构建步骤和配置。

### 怎么写
Dockerfile 使用特定的指令语法，每条指令都会在镜像中创建一个新的层。

### 有什么作用
- 自动化构建 Docker 镜像
- 定义应用程序的运行环境
- 确保环境的一致性和可重复性
- 简化部署流程

### 常用指令说明

```dockerfile
# 基础镜像
FROM <image>:<tag>

# 维护者信息
MAINTAINER <name>

# 设置工作目录
WORKDIR /path/to/workdir

# 复制文件到镜像
COPY <src> <dest>

# 添加文件到镜像（支持URL和tar包）
ADD <src> <dest>

# 执行命令
RUN <command>

# 设置环境变量
ENV <key>=<value>

# 暴露端口
EXPOSE <port>

# 容器启动时执行的命令
CMD ["executable","param1","param2"]

# 容器启动时执行的命令（可被覆盖）
ENTRYPOINT ["executable","param1","param2"]

# 设置数据卷
VOLUME ["/data"]

# 设置用户
USER <user>[:<group>]
```

## Docker 的基础命令

### 镜像管理

```bash
# 拉取镜像
docker pull <image>:<tag>
# 示例：docker pull nginx:latest

# 查看本地镜像
docker images

# 删除镜像
docker rmi <image>

# 构建镜像
docker build -t <name>:<tag> .
# 示例：docker build -t myapp:v1 .

# 给镜像打标签
docker tag <source> <target>
# 示例：docker tag myapp:v1 myapp:latest

# 保存镜像到文件
docker save -o <file> <image>
# 示例：docker save -o nginx.tar nginx:latest

# 从文件加载镜像
docker load -i <file>
# 示例：docker load -i nginx.tar
```

### 容器管理

```bash
# 运行容器
docker run [options] <image> [command]
# 常用选项：
# -d: 后台运行
# -it: 交互式终端
# -p: 端口映射 (主机端口:容器端口)
# -v: 数据卷挂载
# --name: 容器名称
# 示例：docker run -d -p 80:80 --name web nginx

# 查看运行中的容器
docker ps

# 查看所有容器（包括已停止的）
docker ps -a

# 停止容器
docker stop <container>

# 启动已停止的容器
docker start <container>

# 重启容器
docker restart <container>

# 删除容器
docker rm <container>

# 强制删除运行中的容器
docker rm -f <container>

# 查看容器日志
docker logs <container>

# 进入运行中的容器
docker exec -it <container> /bin/bash
# 示例：docker exec -it web /bin/bash

# 查看容器详细信息
docker inspect <container>

# 查看容器资源使用情况
docker stats
```

### 网络管理

```bash
# 查看网络
docker network ls

# 创建网络
docker network create <network>
# 示例：docker network create mynet

# 连接容器到网络
docker network connect <network> <container>

# 断开容器与网络的连接
docker network disconnect <network> <container>

# 删除网络
docker network rm <network>
```

### 数据卷管理

```bash
# 创建数据卷
docker volume create <volume>

# 查看数据卷
docker volume ls

# 删除数据卷
docker volume rm <volume>

# 查看数据卷详细信息
docker volume inspect <volume>
```

## Docker-compose 作用安装和部署

### 是什么
Docker Compose 是一个用于定义和运行多容器 Docker 应用程序的工具。通过 YAML 文件配置应用程序的服务，然后使用一个命令创建和启动所有服务。

### 如何安装

#### Linux 系统
```bash
# 下载 Docker Compose
sudo curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose

# 添加执行权限
sudo chmod +x /usr/local/bin/docker-compose

# 验证安装
docker-compose --version
```

#### Windows/Mac 系统
Docker Desktop 已包含 Docker Compose，无需单独安装。

### 怎么做

创建 `docker-compose.yml` 文件：

```yaml
version: '3'
services:
  web:
    image: nginx:latest
    ports:
      - "80:80"
    volumes:
      - ./html:/usr/share/nginx/html
    networks:
      - mynet

  db:
    image: mysql:5.7
    environment:
      MYSQL_ROOT_PASSWORD: rootpassword
      MYSQL_DATABASE: mydb
    volumes:
      - dbdata:/var/lib/mysql
    networks:
      - mynet

networks:
  mynet:

volumes:
  dbdata:
```

### 常用命令

```bash
# 启动所有服务
docker-compose up -d

# 停止所有服务
docker-compose down

# 查看服务状态
docker-compose ps

# 查看服务日志
docker-compose logs

# 重新构建服务
docker-compose build

# 启动指定服务
docker-compose up -d <service>
# 示例：docker-compose up -d web

# 停止指定服务
docker-compose stop <service>

# 删除指定服务
docker-compose rm <service>
```

### 能做什么
- 简化多容器应用的部署
- 一键启动/停止整个应用栈
- 统一管理服务配置
- 方便进行开发和测试环境搭建
- 支持服务间的依赖关系
- 实现环境变量和配置的统一管理

## 部署项目

### 示例：部署一个 Web 应用

1. **项目结构**
```
myproject/
├── docker-compose.yml
├── Dockerfile
├── app/
│   └── main.py
└── requirements.txt
```

2. **Dockerfile**
```dockerfile
FROM python:3.9-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY app/ .
CMD ["python", "main.py"]
```

3. **docker-compose.yml**
```yaml
version: '3'
services:
  web:
    build: .
    ports:
      - "5000:5000"
    volumes:
      - ./app:/app
    environment:
      - FLASK_ENV=development
  
  redis:
    image: redis:alpine
    ports:
      - "6379:6379"
```

4. **部署步骤**
```bash
# 构建并启动服务
docker-compose up -d

# 查看服务状态
docker-compose ps

# 查看日志
docker-compose logs -f

# 停止服务
docker-compose down
```