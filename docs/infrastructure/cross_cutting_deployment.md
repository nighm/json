# 横切关注点层部署运维文档

## 概述

本文档详细描述了横切关注点层的部署、配置、监控和运维方案，确保系统在生产环境中的稳定运行。

## 部署架构

### 系统架构图
```
┌─────────────────────────────────────────────────────────────┐
│                    应用层 (Application Layer)                │
├─────────────────────────────────────────────────────────────┤
│                  横切关注点层 (Cross-cutting Layer)          │
│  ┌─────────────┬─────────────┬─────────────┬─────────────┐  │
│  │   日志模块   │   配置模块   │   安全模块   │   缓存模块   │  │
│  └─────────────┴─────────────┴─────────────┴─────────────┘  │
│  ┌─────────────┬─────────────┬─────────────┬─────────────┐  │
│  │ 异常处理模块 │   验证模块   │ 统计分析模块 │ 国际化模块   │  │
│  └─────────────┴─────────────┴─────────────┴─────────────┘  │
├─────────────────────────────────────────────────────────────┤
│                    基础设施层 (Infrastructure Layer)         │
└─────────────────────────────────────────────────────────────┘
```

### 部署模式
- **单体部署**：适用于中小型应用
- **微服务部署**：适用于大型分布式系统
- **容器化部署**：使用Docker容器化部署

## 环境要求

### 系统要求
- **操作系统**：Linux (Ubuntu 20.04+ / CentOS 8+) 或 Windows Server 2019+
- **Python版本**：3.8+
- **内存**：最小2GB，推荐4GB+
- **存储**：最小10GB可用空间
- **网络**：支持HTTP/HTTPS访问

### 依赖组件
```bash
# Python依赖包
pip install -r requirements.txt

# 系统依赖
apt-get update && apt-get install -y \
    python3-dev \
    python3-pip \
    build-essential \
    libssl-dev \
    libffi-dev
```

### 配置文件结构
```
config/
├── cross_cutting/
│   ├── logging.yaml          # 日志配置
│   ├── cache.yaml           # 缓存配置
│   ├── security.yaml        # 安全配置
│   └── i18n.yaml           # 国际化配置
├── environment/
│   ├── development.yaml     # 开发环境配置
│   ├── staging.yaml        # 测试环境配置
│   └── production.yaml     # 生产环境配置
└── application.yaml        # 应用主配置
```

## 部署步骤

### 1. 环境准备

#### 创建虚拟环境
```bash
# 创建Python虚拟环境
python3 -m venv venv
source venv/bin/activate  # Linux/Mac
# 或
venv\Scripts\activate     # Windows

# 安装依赖
pip install -r requirements.txt
```

#### 创建必要目录
```bash
# 创建日志目录
mkdir -p /var/log/cross_cutting
chmod 755 /var/log/cross_cutting

# 创建缓存目录
mkdir -p /var/cache/cross_cutting
chmod 755 /var/cache/cross_cutting

# 创建配置目录
mkdir -p /etc/cross_cutting
chmod 644 /etc/cross_cutting
```

### 2. 配置文件部署

#### 日志配置 (logging.yaml)
```yaml
logging:
  level: INFO
  format: "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
  handlers:
    file:
      enabled: true
      path: /var/log/cross_cutting/app.log
      max_size: 100MB
      backup_count: 10
    console:
      enabled: true
      level: INFO
  loggers:
    security:
      level: WARNING
    cache:
      level: DEBUG
```

#### 缓存配置 (cache.yaml)
```yaml
cache:
  type: memory  # memory, redis, memcached
  memory:
    max_size: 1000
    ttl: 3600
  redis:
    host: localhost
    port: 6379
    db: 0
    password: ""
  memcached:
    servers: ["localhost:11211"]
```

#### 安全配置 (security.yaml)
```yaml
security:
  password:
    algorithm: bcrypt
    rounds: 12
  encryption:
    algorithm: AES-256-GCM
    key_rotation: true
  session:
    timeout: 3600
    secure: true
```

#### 国际化配置 (i18n.yaml)
```yaml
i18n:
  default_language: zh_CN
  supported_languages: ["zh_CN", "en_US", "ja_JP"]
  fallback_language: en_US
  resource_path: /etc/cross_cutting/i18n
```

### 3. 应用部署

#### 使用Docker部署
```dockerfile
# Dockerfile
FROM python:3.9-slim

WORKDIR /app

# 安装系统依赖
RUN apt-get update && apt-get install -y \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# 复制应用代码
COPY src/ ./src/
COPY config/ ./config/
COPY requirements.txt .

# 安装Python依赖
RUN pip install --no-cache-dir -r requirements.txt

# 创建必要目录
RUN mkdir -p /var/log/cross_cutting /var/cache/cross_cutting

# 设置环境变量
ENV PYTHONPATH=/app
ENV CONFIG_PATH=/app/config

# 暴露端口
EXPOSE 8000

# 启动命令
CMD ["python", "-m", "src.main"]
```

#### Docker Compose配置
```yaml
# docker-compose.yml
version: '3.8'

services:
  cross-cutting:
    build: .
    ports:
      - "8000:8000"
    volumes:
      - ./config:/app/config
      - ./logs:/var/log/cross_cutting
      - ./cache:/var/cache/cross_cutting
    environment:
      - ENVIRONMENT=production
      - LOG_LEVEL=INFO
    depends_on:
      - redis
    restart: unless-stopped

  redis:
    image: redis:6-alpine
    ports:
      - "6379:6379"
    volumes:
      - redis_data:/data
    restart: unless-stopped

volumes:
  redis_data:
```

### 4. 服务启动

#### 系统服务配置 (systemd)
```ini
# /etc/systemd/system/cross-cutting.service
[Unit]
Description=Cross-cutting Concerns Service
After=network.target

[Service]
Type=simple
User=cross-cutting
Group=cross-cutting
WorkingDirectory=/opt/cross-cutting
Environment=PYTHONPATH=/opt/cross-cutting
Environment=CONFIG_PATH=/opt/cross-cutting/config
ExecStart=/opt/cross-cutting/venv/bin/python -m src.main
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

#### 启动服务
```bash
# 启用并启动服务
sudo systemctl enable cross-cutting
sudo systemctl start cross-cutting

# 检查服务状态
sudo systemctl status cross-cutting

# 查看日志
sudo journalctl -u cross-cutting -f
```

## 配置管理

### 环境变量配置
```bash
# 应用配置
export ENVIRONMENT=production
export LOG_LEVEL=INFO
export CONFIG_PATH=/etc/cross_cutting

# 数据库配置
export DB_HOST=localhost
export DB_PORT=5432
export DB_NAME=cross_cutting
export DB_USER=cross_cutting
export DB_PASSWORD=secure_password

# 缓存配置
export REDIS_HOST=localhost
export REDIS_PORT=6379
export REDIS_PASSWORD=

# 安全配置
export SECRET_KEY=your-secret-key-here
export ENCRYPTION_KEY=your-encryption-key-here
```

### 配置验证
```python
# config_validator.py
from src.infrastructure.cross_cutting import get_validator, get_config

def validate_configuration():
    """验证配置文件的正确性"""
    validator = get_validator()
    
    # 验证必要配置
    required_configs = [
        "logging.level",
        "cache.type",
        "security.password.algorithm",
        "i18n.default_language"
    ]
    
    for config_key in required_configs:
        value = get_config(config_key)
        if value is None:
            raise ValueError(f"缺少必要配置: {config_key}")
    
    print("配置验证通过")

if __name__ == "__main__":
    validate_configuration()
```

## 监控方案

### 1. 日志监控

#### 日志收集
```python
# log_monitor.py
import logging
from src.infrastructure.cross_cutting import get_logger

class LogMonitor:
    def __init__(self):
        self.logger = get_logger("monitor")
        
    def monitor_error_rate(self):
        """监控错误率"""
        # 实现错误率监控逻辑
        pass
        
    def monitor_performance(self):
        """监控性能指标"""
        # 实现性能监控逻辑
        pass
```

#### ELK Stack集成
```yaml
# logstash.conf
input {
  file {
    path => "/var/log/cross_cutting/*.log"
    type => "cross-cutting"
  }
}

filter {
  if [type] == "cross-cutting" {
    grok {
      match => { "message" => "%{TIMESTAMP_ISO8601:timestamp} - %{DATA:logger} - %{LOGLEVEL:level} - %{GREEDYDATA:message}" }
    }
  }
}

output {
  elasticsearch {
    hosts => ["localhost:9200"]
    index => "cross-cutting-logs-%{+YYYY.MM.dd}"
  }
}
```

### 2. 性能监控

#### 应用性能监控
```python
# performance_monitor.py
import time
from functools import wraps
from src.infrastructure.cross_cutting import get_logger, get_cache

def monitor_performance(func_name):
    """性能监控装饰器"""
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            start_time = time.time()
            try:
                result = func(*args, **kwargs)
                execution_time = time.time() - start_time
                
                # 记录性能指标
                cache = get_cache()
                cache.set(f"perf:{func_name}:avg", execution_time, ttl=3600)
                
                return result
            except Exception as e:
                execution_time = time.time() - start_time
                logger = get_logger("performance")
                logger.error(f"函数 {func_name} 执行失败，耗时: {execution_time:.3f}s", exc_info=True)
                raise
        return wrapper
    return decorator
```

#### Prometheus指标
```python
# metrics.py
from prometheus_client import Counter, Histogram, Gauge
from src.infrastructure.cross_cutting import get_logger

# 定义指标
REQUEST_COUNT = Counter('cross_cutting_requests_total', 'Total requests', ['module', 'method'])
REQUEST_DURATION = Histogram('cross_cutting_request_duration_seconds', 'Request duration', ['module', 'method'])
CACHE_HIT_RATIO = Gauge('cross_cutting_cache_hit_ratio', 'Cache hit ratio', ['cache_type'])
ERROR_COUNT = Counter('cross_cutting_errors_total', 'Total errors', ['module', 'error_type'])

class MetricsCollector:
    def __init__(self):
        self.logger = get_logger("metrics")
    
    def record_request(self, module, method, duration):
        """记录请求指标"""
        REQUEST_COUNT.labels(module=module, method=method).inc()
        REQUEST_DURATION.labels(module=module, method=method).observe(duration)
    
    def record_cache_hit(self, cache_type, hit_ratio):
        """记录缓存命中率"""
        CACHE_HIT_RATIO.labels(cache_type=cache_type).set(hit_ratio)
    
    def record_error(self, module, error_type):
        """记录错误指标"""
        ERROR_COUNT.labels(module=module, error_type=error_type).inc()
```

### 3. 健康检查

#### 健康检查接口
```python
# health_check.py
from src.infrastructure.cross_cutting import get_logger, get_cache, get_config

class HealthChecker:
    def __init__(self):
        self.logger = get_logger("health")
    
    def check_system_health(self):
        """检查系统健康状态"""
        health_status = {
            "status": "healthy",
            "timestamp": time.time(),
            "checks": {}
        }
        
        # 检查缓存服务
        try:
            cache = get_cache()
            cache.set("health_check", "ok", ttl=60)
            health_status["checks"]["cache"] = "healthy"
        except Exception as e:
            health_status["checks"]["cache"] = "unhealthy"
            health_status["status"] = "degraded"
        
        # 检查配置服务
        try:
            config = get_config("logging.level")
            health_status["checks"]["config"] = "healthy"
        except Exception as e:
            health_status["checks"]["config"] = "unhealthy"
            health_status["status"] = "degraded"
        
        return health_status
```

## 运维操作

### 1. 服务管理

#### 启动服务
```bash
# 启动服务
sudo systemctl start cross-cutting

# 检查服务状态
sudo systemctl status cross-cutting

# 查看实时日志
sudo journalctl -u cross-cutting -f
```

#### 停止服务
```bash
# 优雅停止
sudo systemctl stop cross-cutting

# 强制停止
sudo systemctl kill cross-cutting
```

#### 重启服务
```bash
# 重启服务
sudo systemctl restart cross-cutting

# 重新加载配置
sudo systemctl reload cross-cutting
```

### 2. 日志管理

#### 日志轮转
```bash
# logrotate配置
# /etc/logrotate.d/cross-cutting
/var/log/cross_cutting/*.log {
    daily
    missingok
    rotate 30
    compress
    delaycompress
    notifempty
    create 644 cross-cutting cross-cutting
    postrotate
        systemctl reload cross-cutting
    endscript
}
```

#### 日志清理
```bash
# 清理30天前的日志
find /var/log/cross_cutting -name "*.log.*" -mtime +30 -delete

# 清理压缩日志
find /var/log/cross_cutting -name "*.log.*.gz" -mtime +90 -delete
```

### 3. 备份恢复

#### 配置备份
```bash
#!/bin/bash
# backup_config.sh

BACKUP_DIR="/backup/cross_cutting/$(date +%Y%m%d)"
mkdir -p $BACKUP_DIR

# 备份配置文件
cp -r /etc/cross_cutting $BACKUP_DIR/

# 备份日志文件
cp -r /var/log/cross_cutting $BACKUP_DIR/

# 压缩备份
tar -czf $BACKUP_DIR.tar.gz $BACKUP_DIR
rm -rf $BACKUP_DIR

echo "配置备份完成: $BACKUP_DIR.tar.gz"
```

#### 数据恢复
```bash
#!/bin/bash
# restore_config.sh

BACKUP_FILE=$1
RESTORE_DIR="/tmp/restore_$(date +%Y%m%d_%H%M%S)"

if [ -z "$BACKUP_FILE" ]; then
    echo "请指定备份文件"
    exit 1
fi

# 解压备份
tar -xzf $BACKUP_FILE -C /tmp
RESTORE_PATH=$(find /tmp -name "cross_cutting" -type d | head -1)

if [ -z "$RESTORE_PATH" ]; then
    echo "备份文件格式错误"
    exit 1
fi

# 停止服务
sudo systemctl stop cross-cutting

# 恢复配置
sudo cp -r $RESTORE_PATH/* /etc/cross_cutting/

# 启动服务
sudo systemctl start cross-cutting

# 清理临时文件
rm -rf /tmp/restore_*

echo "配置恢复完成"
```

### 4. 故障排查

#### 常见问题排查
```bash
# 1. 检查服务状态
sudo systemctl status cross-cutting

# 2. 检查日志
sudo journalctl -u cross-cutting --since "1 hour ago"

# 3. 检查端口占用
sudo netstat -tlnp | grep :8000

# 4. 检查磁盘空间
df -h /var/log/cross_cutting

# 5. 检查内存使用
free -h

# 6. 检查进程
ps aux | grep cross-cutting
```

#### 性能问题排查
```bash
# 1. 检查CPU使用率
top -p $(pgrep -f cross-cutting)

# 2. 检查内存使用
cat /proc/$(pgrep -f cross-cutting)/status | grep VmRSS

# 3. 检查网络连接
ss -tlnp | grep :8000

# 4. 检查文件描述符
lsof -p $(pgrep -f cross-cutting) | wc -l
```

## 安全考虑

### 1. 访问控制
```bash
# 设置文件权限
sudo chown -R cross-cutting:cross-cutting /etc/cross_cutting
sudo chmod 600 /etc/cross_cutting/*.yaml
sudo chmod 755 /var/log/cross_cutting
sudo chmod 755 /var/cache/cross_cutting
```

### 2. 网络安全
```yaml
# 防火墙配置
# /etc/ufw/applications.d/cross-cutting
[Cross-cutting]
title=Cross-cutting Concerns Service
description=Cross-cutting concerns layer service
ports=8000/tcp
```

### 3. 数据加密
```python
# 敏感数据加密
from src.infrastructure.cross_cutting import get_security_provider

security = get_security_provider()

# 加密敏感配置
encrypted_password = security.encrypt("sensitive_password")
decrypted_password = security.decrypt(encrypted_password)
```

## 总结

本文档提供了横切关注点层的完整部署运维方案，包括：

1. **部署架构**：清晰的系统架构和部署模式
2. **环境配置**：详细的环境要求和配置说明
3. **监控方案**：全面的监控和告警机制
4. **运维操作**：日常运维操作指南
5. **安全考虑**：安全配置和最佳实践

通过遵循本文档的指导，可以确保横切关注点层在生产环境中的稳定运行和高效维护。 