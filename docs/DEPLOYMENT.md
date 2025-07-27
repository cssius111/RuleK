# 部署指南

本文档介绍如何将规则怪谈管理者部署到生产环境。

## 📋 部署前准备

### 系统要求

- Ubuntu 20.04+ / CentOS 8+ / Debian 10+
- Python 3.10+
- Node.js 18+
- Nginx
- Docker & Docker Compose（可选）

### 域名和SSL证书

- 准备域名（例如：rulek.example.com）
- 获取SSL证书（推荐 Let's Encrypt）

## 🚀 部署方式

### 方式一：Docker部署（推荐）

#### 1. 准备环境变量

创建 `.env.production` 文件：

```bash
# API配置
DEEPSEEK_API_KEY=your_production_api_key
LOG_LEVEL=WARNING  # 也可以使用數字值，例如 30
DEBUG=False

# 数据库配置（如果使用）
DATABASE_URL=postgresql://user:password@localhost/rulek

# Redis配置（如果使用）
REDIS_URL=redis://localhost:6379/0

# 其他配置
SECRET_KEY=your-secret-key-here
ALLOWED_HOSTS=rulek.example.com
```

#### 2. 构建镜像

```bash
# 构建生产镜像
docker build -t rulek:latest .

# 或使用docker-compose
docker-compose -f docker-compose.yml build
```

#### 3. 启动服务

```bash
# 使用docker-compose启动
docker-compose --profile prod up -d

# 查看日志
docker-compose logs -f
```

### 方式二：传统部署

#### 1. 安装系统依赖

```bash
# Ubuntu/Debian
sudo apt update
sudo apt install python3-pip python3-venv nginx redis-server supervisor

# CentOS
sudo yum install python3-pip nginx redis supervisor
```

#### 2. 创建应用用户

```bash
sudo useradd -m -s /bin/bash rulek
sudo su - rulek
```

#### 3. 部署后端

```bash
# 克隆代码
git clone https://github.com/yourusername/rulek.git
cd rulek

# 创建虚拟环境
python3 -m venv venv
source venv/bin/activate

# 安装依赖
pip install -r requirements.txt

# 运行数据库迁移（如果有）
# python manage.py migrate
```

#### 4. 构建前端

```bash
cd web/frontend
npm install
npm run build
```

#### 5. 配置Supervisor

创建 `/etc/supervisor/conf.d/rulek.conf`：

```ini
[program:rulek-backend]
command=/home/rulek/rulek/venv/bin/python /home/rulek/rulek/web/backend/app.py
directory=/home/rulek/rulek
user=rulek
autostart=true
autorestart=true
redirect_stderr=true
stdout_logfile=/var/log/rulek/backend.log
environment=PATH="/home/rulek/rulek/venv/bin",PYTHONPATH="/home/rulek/rulek"
```

启动服务：

```bash
sudo supervisorctl reread
sudo supervisorctl update
sudo supervisorctl start rulek-backend
```

#### 6. 配置Nginx

创建 `/etc/nginx/sites-available/rulek`：

```nginx
server {
    listen 80;
    server_name rulek.example.com;
    return 301 https://$server_name$request_uri;
}

server {
    listen 443 ssl http2;
    server_name rulek.example.com;

    ssl_certificate /etc/letsencrypt/live/rulek.example.com/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/rulek.example.com/privkey.pem;
    ssl_protocols TLSv1.2 TLSv1.3;
    
    root /home/rulek/rulek/web/frontend/dist;
    index index.html;

    # 前端静态文件
    location / {
        try_files $uri $uri/ /index.html;
        expires 1d;
        add_header Cache-Control "public, immutable";
    }

    # API代理
    location /api {
        proxy_pass http://127.0.0.1:8000;
        proxy_http_version 1.1;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }

    # WebSocket代理
    location /ws {
        proxy_pass http://127.0.0.1:8000;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
        proxy_set_header Host $host;
        proxy_read_timeout 86400;
    }
}
```

启用站点：

```bash
sudo ln -s /etc/nginx/sites-available/rulek /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl reload nginx
```

## 🔒 安全加固

### 1. 防火墙配置

```bash
# UFW (Ubuntu)
sudo ufw allow 22/tcp
sudo ufw allow 80/tcp
sudo ufw allow 443/tcp
sudo ufw enable

# Firewalld (CentOS)
sudo firewall-cmd --permanent --add-service=ssh
sudo firewall-cmd --permanent --add-service=http
sudo firewall-cmd --permanent --add-service=https
sudo firewall-cmd --reload
```

### 2. 应用安全

- 使用强密码
- 定期更新依赖
- 启用HTTPS
- 配置CORS白名单
- 使用环境变量管理敏感信息

### 3. 数据备份

```bash
# 创建备份脚本
cat > /home/rulek/backup.sh << 'EOF'
#!/bin/bash
BACKUP_DIR="/home/rulek/backups"
DATE=$(date +%Y%m%d_%H%M%S)

# 备份数据
tar -czf $BACKUP_DIR/rulek_data_$DATE.tar.gz /home/rulek/rulek/data/

# 保留最近7天的备份
find $BACKUP_DIR -name "rulek_data_*.tar.gz" -mtime +7 -delete
EOF

chmod +x /home/rulek/backup.sh

# 添加到crontab
crontab -e
# 0 2 * * * /home/rulek/backup.sh
```

## 📊 监控和日志

### 1. 应用监控

使用 Prometheus + Grafana：

```yaml
# docker-compose.monitoring.yml
version: '3.8'

services:
  prometheus:
    image: prom/prometheus
    volumes:
      - ./prometheus.yml:/etc/prometheus/prometheus.yml
      - prometheus-data:/prometheus
    ports:
      - "9090:9090"

  grafana:
    image: grafana/grafana
    ports:
      - "3000:3000"
    volumes:
      - grafana-data:/var/lib/grafana

volumes:
  prometheus-data:
  grafana-data:
```

### 2. 日志管理

配置集中日志：

```python
# 在应用中配置日志
LOGGING = {
    'version': 1,
    'handlers': {
        'file': {
            'class': 'logging.handlers.RotatingFileHandler',
            'filename': '/var/log/rulek/app.log',
            'maxBytes': 10485760,  # 10MB
            'backupCount': 10,
        },
    },
    'root': {
        'level': 'INFO',
        'handlers': ['file'],
    },
}
```

## 🔄 更新流程

### 1. 备份数据

```bash
./backup.sh
```

### 2. 拉取更新

```bash
cd /home/rulek/rulek
git pull origin main
```

### 3. 更新依赖

```bash
source venv/bin/activate
pip install -r requirements.txt

cd web/frontend
npm install
npm run build
```

### 4. 重启服务

```bash
sudo supervisorctl restart rulek-backend
# 或
docker-compose restart
```

## 🚨 故障排查

### 常见问题

1. **502 Bad Gateway**
   - 检查后端服务是否运行
   - 查看 Nginx 错误日志

2. **WebSocket连接失败**
   - 确认 Nginx 配置正确
   - 检查防火墙设置

3. **性能问题**
   - 启用 Redis 缓存
   - 增加工作进程数
   - 使用 CDN 加速静态资源

### 日志位置

- 应用日志：`/var/log/rulek/`
- Nginx日志：`/var/log/nginx/`
- 系统日志：`/var/log/syslog`

## 📞 支持

如遇到部署问题，请：

1. 查看[常见问题](docs/FAQ.md)
2. 提交 [Issue](https://github.com/yourusername/rulek/issues)
3. 联系技术支持

---

祝部署顺利！🚀
