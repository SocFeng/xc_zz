## 汇总docker compose 一键启动多个服务命令
```yaml
version: '3.8'
services:
  ###########################
  # 一、独立组件
  ###########################
  redis:
    image: redis:7-alpine
    container_name: redis
    restart: always
    ports:
      - "6379:6379"
    volumes:
      - redis-data:/data
    networks:
      - my-network

  mysql:
    image: mysql:8.0
    container_name: mysql
    restart: always
    environment:
      MYSQL_ROOT_PASSWORD: 123456
      MYSQL_DATABASE: test
    ports:
      - "3306:3306"
    volumes:
      - mysql-data:/var/lib/mysql
    networks:
      - my-network

  rabbitmq:
    image: rabbitmq:3-management
    container_name: rabbitmq
    restart: always
    ports:
      - "5672:5672"
      - "15672:15672"
    environment:
      RABBITMQ_DEFAULT_USER: admin
      RABBITMQ_DEFAULT_PASS: 123456
    volumes:
      - rabbitmq-data:/var/lib/rabbitmq
    networks:
      - my-network

  zookeeper:
    image: zookeeper:3.8
    container_name: zookeeper
    restart: always
    ports:
      - "2181:2181"
    volumes:
      - zookeeper-data:/data
    networks:
      - my-network

  ###########################
  # 二、OpenSearch 检索套件
  ###########################
  opensearch:
    image: opensearch:2.11.0
    container_name: opensearch
    restart: always
    environment:
      - discovery.type=single-node
      - "OPENSEARCH_JAVA_OPTS=-Xms512m -Xmx512m"
      - bootstrap.memory_lock=true
    ulimits:
      memlock:
        soft: -1
        hard: -1
    ports:
      - "9200:9200"
      - "9600:9600"
    volumes:
      - opensearch-data:/usr/share/opensearch/data
    networks:
      - my-network

  opensearch-dashboard:
    image: opensearch-dashboards:2.11.0
    container_name: opensearch-dashboard
    restart: always
    ports:
      - "5601:5601"
    environment:
      OPENSEARCH_HOSTS: '["http://opensearch:9200"]'
    depends_on:
      - opensearch
    networks:
      - my-network

  ###########################
  # 三、Kafka 消息队列套件
  ###########################
  kafka:
    image: confluentinc/cp-kafka:7.5.0
    container_name: kafka
    restart: always
    ports:
      - "9092:9092"
    environment:
      KAFKA_BROKER_ID: 1
      KAFKA_ZOOKEEPER_CONNECT: zookeeper:2181
      KAFKA_ADVERTISED_LISTENERS: PLAINTEXT://kafka:29092,PLAINTEXT_HOST://localhost:9092
      KAFKA_LISTENER_SECURITY_PROTOCOL_MAP: PLAINTEXT:PLAINTEXT,PLAINTEXT_HOST:PLAINTEXT
      KAFKA_INTER_BROKER_LISTENER_NAME: PLAINTEXT
      KAFKA_OFFSETS_TOPIC_REPLICATION_FACTOR: 1
    depends_on:
      - zookeeper
    networks:
      - my-network

  kafka-ui:
    image: provectuslabs/kafka-ui:latest
    container_name: kafka-ui
    restart: always
    ports:
      - "8080:8080"
    environment:
      KAFKA_CLUSTERS_0_NAME: local
      KAFKA_CLUSTERS_0_BOOTSTRAPSERVERS: kafka:29092
    depends_on:
      - kafka
    networks:
      - my-network

  ###########################
  # 四、Nacos 注册/配置中心套件
  ###########################
  nacos-mysql:
    image: mysql:8.0
    container_name: nacos-mysql
    restart: always
    environment:
      MYSQL_ROOT_PASSWORD: 123456
      MYSQL_DATABASE: nacos
    volumes:
      - nacos-mysql-data:/var/lib/mysql
    networks:
      - my-network

  nacos:
    image: nacos/nacos-server:v2.2.3
    container_name: nacos
    restart: always
    ports:
      - "8848:8848"
      - "9848:9848"
    environment:
      MODE: standalone
      SPRING_DATASOURCE_PLATFORM: mysql
      MYSQL_SERVICE_HOST: nacos-mysql
      MYSQL_SERVICE_DB_NAME: nacos
      MYSQL_SERVICE_USER: root
      MYSQL_SERVICE_PASSWORD: 123456
    depends_on:
      - nacos-mysql
    networks:
      - my-network

  ###########################
  # 五、Prometheus + Grafana 监控套件
  ###########################
  prometheus:
    image: prom/prometheus:v2.47.0
    container_name: prometheus
    restart: always
    ports:
      - "9090:9090"
    volumes:
      - prometheus-data:/prometheus
    networks:
      - my-network

  grafana:
    image: grafana/grafana:10.1.5
    container_name: grafana
    restart: always
    ports:
      - "3000:3000"
    volumes:
      - grafana-data:/var/lib/grafana
    depends_on:
      - prometheus
    networks:
      - my-network

networks:
  my-network:
    driver: bridge

volumes:
  redis-data:
  mysql-data:
  rabbitmq-data:
  zookeeper-data:
  opensearch-data:
  nacos-mysql-data:
  prometheus-data:
  grafana-data:

```

## 启动和查看服务
```bash
# 1. 启动所有服务
docker-compose up -d

# 2. 查看服务状态
docker-compose ps

# 3. 查看所有日志
docker-compose logs -f
```


### 数据整理
| 组件 | 访问地址 | 默认账号 | 默认密码 |
|------|----------|----------|----------|
| Redis | `localhost:6379` | - | 无密码（如需可自行修改配置） |
| MySQL | `localhost:3306` | `root` | `123456` |
| RabbitMQ | `http://localhost:15672` | `admin` | `123456` |
| OpenSearch Dashboard | `http://localhost:5601` | - | 默认无密码 |
| Kafka UI | `http://localhost:8080` | - | 默认无密码 |
| Nacos | `http://localhost:8848/nacos` | `nacos` | `nacos` |
| Prometheus | `http://localhost:9090` | - | 默认无密码 |
| Grafana | `http://localhost:3000` | `admin` | `admin` |
