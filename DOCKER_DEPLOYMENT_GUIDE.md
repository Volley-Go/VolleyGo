# 🐳 Docker部署到阿里云完整指南

## ⏱️ 预计时间

**对于有基本程序开发和Linux使用经验的开发者：**

- **首次部署：** 2-4小时
  - 阿里云ECS配置：30分钟
  - Docker环境搭建：30分钟
  - 项目配置和测试：1-2小时
  - 域名和SSL配置（可选）：30-60分钟

- **后续部署（已有经验）：** 30-60分钟

---

## 📋 准备工作清单

### 1. 阿里云资源准备

- [ ] **ECS服务器**（推荐配置）
  - CPU: 2核以上
  - 内存: 4GB以上（推荐8GB，视频处理需要）
  - 系统: Ubuntu 20.04 LTS 或 Ubuntu 22.04 LTS
  - 带宽: 5Mbps以上
  - 存储: 40GB以上（视频文件会占用空间）

- [ ] **安全组配置**
  - 开放端口：80 (HTTP), 443 (HTTPS), 22 (SSH), 5000 (应用端口，可选)
  - 端口说明：
    - 22: SSH远程连接
    - 80: HTTP访问
    - 443: HTTPS访问（SSL证书后）
    - 5000: 应用端口（如果需要直连测试）

- [ ] **域名（可选）**
  - 如果不使用域名，直接用IP访问

---

## 🚀 步骤1: 创建并连接ECS服务器

### 1.1 创建ECS实例

1. 登录[阿里云控制台](https://ecs.console.aliyun.com/)
2. 点击"创建实例"
3. 选择配置：
   - **计费方式**：包年包月 或 按量付费
   - **地域**：选择离您最近的区域
   - **实例规格**：ecs.t6-c2m1.large（2核4GB）或更高
   - **镜像**：Ubuntu 20.04 64位 或 Ubuntu 22.04 64位
   - **系统盘**：40GB ESSD云盘
   - **网络**：专有网络VPC
   - **公网IP**：分配公网IP
   - **带宽**：5Mbps

4. **安全组配置**：
   - 新建安全组
   - 添加规则：
     ```
     方向：入方向
     协议：TCP
     端口：22/22
     授权对象：0.0.0.0/0（或您的IP）
     ```
     ```
     方向：入方向
     协议：TCP
     端口：80/80
     授权对象：0.0.0.0/0
     ```
     ```
     方向：入方向
     协议：TCP
     端口：443/443
     授权对象：0.0.0.0/0
     ```

5. 设置**登录密码**（SSH登录用）
6. 创建实例

### 1.2 连接服务器

**Windows用户：**
```bash
# 使用PowerShell或CMD
ssh root@你的公网IP
# 输入密码
```

**Linux/Mac用户：**
```bash
ssh root@你的公网IP
# 输入密码
```

如果无法连接，检查：
- 安全组是否开放22端口
- 密码是否正确
- 服务器是否运行中

---

## 🐳 步骤2: 安装Docker和Docker Compose

### 2.1 更新系统

```bash
apt-get update
apt-get upgrade -y
```

### 2.2 安装Docker

```bash
# 安装必要的依赖
apt-get install -y \
    apt-transport-https \
    ca-certificates \
    curl \
    gnupg \
    lsb-release

# 添加Docker官方GPG密钥
curl -fsSL https://mirrors.aliyun.com/docker-ce/linux/ubuntu/gpg | gpg --dearmor -o /usr/share/keyrings/docker-archive-keyring.gpg

# 添加Docker仓库（使用阿里云镜像加速）
echo \
  "deb [arch=amd64 signed-by=/usr/share/keyrings/docker-archive-keyring.gpg] https://mirrors.aliyun.com/docker-ce/linux/ubuntu \
  $(lsb_release -cs) stable" | tee /etc/apt/sources.list.d/docker.list > /dev/null

# 安装Docker
apt-get update
apt-get install -y docker-ce docker-ce-cli containerd.io

# 启动Docker服务
systemctl start docker
systemctl enable docker

# 验证安装
docker --version
```

### 2.3 配置Docker镜像加速（重要！）

```bash
# 创建或编辑配置文件
mkdir -p /etc/docker
cat > /etc/docker/daemon.json <<EOF
{
  "registry-mirrors": [
    "https://registry.cn-hangzhou.aliyuncs.com",
    "https://docker.mirrors.ustc.edu.cn"
  ]
}
EOF

# 重启Docker服务
systemctl daemon-reload
systemctl restart docker

# 验证配置
docker info | grep -A 10 "Registry Mirrors"
```

### 2.4 安装Docker Compose

```bash
# 下载Docker Compose（使用国内镜像）
curl -L "https://github.com/docker/compose/releases/download/v2.20.0/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose

# 或者使用更快的方式
# curl -L "https://get.daocloud.io/docker/compose/releases/download/v2.20.0/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose

# 添加执行权限
chmod +x /usr/local/bin/docker-compose

# 创建软链接
ln -s /usr/local/bin/docker-compose /usr/bin/docker-compose

# 验证安装
docker-compose --version
```

---

## 📦 步骤3: 上传项目代码

### 方式1: 使用Git（推荐）

```bash
# 安装Git
apt-get install -y git

# 克隆项目（如果是Git仓库）
git clone <你的仓库地址>
cd Volleyball
```

### 方式2: 使用SCP上传（从本地）

**Windows（PowerShell）：**
```powershell
# 在项目根目录执行
scp -r * root@你的公网IP:/root/volleyball
```

**Linux/Mac：**
```bash
scp -r * root@你的公网IP:/root/volleyball
```

**然后在服务器上：**
```bash
cd /root/volleyball
```

### 方式3: 使用压缩包

**本地：**
```bash
# 在项目根目录
tar -czf volleyball.tar.gz --exclude='__pycache__' --exclude='*.pyc' --exclude='output' .
```

**上传到服务器：**
```bash
# Windows PowerShell
scp volleyball.tar.gz root@你的公网IP:/root/

# Linux/Mac
scp volleyball.tar.gz root@你的公网IP:/root/
```

**服务器上解压：**
```bash
cd /root
tar -xzf volleyball.tar.gz
cd volleyball  # 或项目目录名
```

---

## 🐳 步骤4: 创建Docker配置文件

### 4.1 创建Dockerfile

在项目根目录创建 `Dockerfile`：

```dockerfile
FROM python:3.9-slim

# 设置工作目录
WORKDIR /app

# 设置环境变量
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

# 安装系统依赖
RUN apt-get update && apt-get install -y \
    ffmpeg \
    libgl1-mesa-glx \
    libglib2.0-0 \
    libsm6 \
    libxext6 \
    libxrender-dev \
    libgomp1 \
    && rm -rf /var/lib/apt/lists/*

# 复制依赖文件
COPY requirements.txt .

# 安装Python依赖（使用国内镜像加速）
RUN pip install --no-cache-dir -r requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple

# 复制项目文件
COPY . .

# 创建输出目录
RUN mkdir -p /app/output

# 暴露端口
EXPOSE 5000

# 启动命令（使用Gunicorn生产环境）
CMD ["gunicorn", "-w", "4", "-b", "0.0.0.0:5000", "--timeout", "120", "--access-logfile", "-", "--error-logfile", "-", "backend.api.flask_api:app"]
```

### 4.2 创建.dockerignore

创建 `.dockerignore` 文件，排除不必要的文件：

```
__pycache__
*.pyc
*.pyo
*.pyd
.Python
*.so
*.egg
*.egg-info
dist
build
.venv
venv
env
ENV
output/*
*.log
.git
.gitignore
README.md
*.md
.DS_Store
```

### 4.3 创建docker-compose.yml（可选，但推荐）

创建 `docker-compose.yml` 文件：

```yaml
version: '3.8'

services:
  web:
    build: .
    container_name: volleyball-app
    ports:
      - "5000:5000"
    volumes:
      - ./output:/app/output  # 挂载输出目录，方便查看生成的视频
      - ./data:/app/data       # 挂载数据目录
    environment:
      - PYTHONUNBUFFERED=1
    restart: unless-stopped
    # 资源限制（根据服务器配置调整）
    deploy:
      resources:
        limits:
          cpus: '2'
          memory: 4G
        reservations:
          cpus: '1'
          memory: 2G
```

### 4.4 更新requirements.txt（确保包含Gunicorn）

检查 `requirements.txt` 是否包含 `gunicorn`，如果没有则添加：

```bash
# 在服务器上编辑
nano requirements.txt
```

添加：
```
gunicorn>=21.2.0
```

---

## 🔨 步骤5: 构建和运行Docker容器

### 5.1 构建Docker镜像

```bash
# 确保在项目根目录
cd /root/volleyball  # 或你的项目目录

# 构建镜像（首次构建需要下载基础镜像，可能需要10-20分钟）
docker build -t volleyball-ai:latest .

# 查看镜像
docker images
```

**如果构建失败：**
- 检查网络连接
- 确认Docker镜像加速配置正确
- 查看错误日志

### 5.2 运行容器

**方式1: 使用docker命令**
```bash
docker run -d \
  --name volleyball-app \
  -p 5000:5000 \
  -v $(pwd)/output:/app/output \
  -v $(pwd)/data:/app/data \
  --restart unless-stopped \
  volleyball-ai:latest
```

**方式2: 使用docker-compose（推荐）**
```bash
docker-compose up -d
```

### 5.3 查看容器状态

```bash
# 查看运行中的容器
docker ps

# 查看容器日志
docker logs volleyball-app

# 实时查看日志
docker logs -f volleyball-app
```

### 5.4 测试应用

```bash
# 在服务器上测试
curl http://localhost:5000/api/health

# 或访问浏览器（用你的公网IP）
# http://你的公网IP:5000
```

---

## 🌐 步骤6: 配置Nginx反向代理（推荐）

### 6.1 安装Nginx

```bash
apt-get install -y nginx
```

### 6.2 创建Nginx配置

```bash
nano /etc/nginx/sites-available/volleyball
```

添加以下内容：

```nginx
server {
    listen 80;
    server_name 你的域名.com;  # 或直接使用IP，可以留空

    # 客户端上传文件大小限制（视频文件）
    client_max_body_size 100M;
    client_body_buffer_size 128k;

    # 超时设置
    proxy_connect_timeout 300;
    proxy_send_timeout 300;
    proxy_read_timeout 300;
    send_timeout 300;

    location / {
        proxy_pass http://localhost:5000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        
        # WebSocket支持（如果需要）
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
    }

    # 静态文件直接服务（如果前端文件独立）
    location /static {
        alias /app/frontend;
        expires 30d;
        add_header Cache-Control "public, immutable";
    }
}
```

### 6.3 启用配置

```bash
# 创建软链接
ln -s /etc/nginx/sites-available/volleyball /etc/nginx/sites-enabled/

# 删除默认配置（可选）
rm /etc/nginx/sites-enabled/default

# 测试配置
nginx -t

# 重启Nginx
systemctl restart nginx
systemctl enable nginx
```

### 6.4 测试访问

在浏览器访问：`http://你的公网IP`（不需要端口号）

---

## 🔒 步骤7: 配置SSL证书（HTTPS，可选但推荐）

### 使用Let's Encrypt免费证书

```bash
# 安装Certbot
apt-get install -y certbot python3-certbot-nginx

# 申请证书（需要先配置好域名解析）
certbot --nginx -d 你的域名.com

# 或者手动申请
certbot certonly --standalone -d 你的域名.com

# 证书会自动续期（Crontab已配置）
```

### 手动配置SSL

编辑Nginx配置：
```bash
nano /etc/nginx/sites-available/volleyball
```

添加SSL配置：
```nginx
server {
    listen 443 ssl http2;
    server_name 你的域名.com;
    
    ssl_certificate /etc/letsencrypt/live/你的域名.com/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/你的域名.com/privkey.pem;
    
    # SSL优化
    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_ciphers HIGH:!aNULL:!MD5;
    ssl_prefer_server_ciphers on;
    
    # ... 其他配置同上
}

# HTTP重定向到HTTPS
server {
    listen 80;
    server_name 你的域名.com;
    return 301 https://$server_name$request_uri;
}
```

重启Nginx：
```bash
nginx -t
systemctl restart nginx
```

---

## 🔧 步骤8: 配置防火墙

```bash
# Ubuntu 20.04+ 使用ufw
ufw allow 22/tcp
ufw allow 80/tcp
ufw allow 443/tcp
ufw enable

# 查看状态
ufw status
```

---

## 📊 步骤9: 监控和维护

### 查看容器状态

```bash
# 查看容器资源使用
docker stats volleyball-app

# 查看容器日志
docker logs -f volleyball-app

# 进入容器调试
docker exec -it volleyball-app bash
```

### 重启服务

```bash
# 重启容器
docker restart volleyball-app

# 或使用docker-compose
docker-compose restart
```

### 更新部署

```bash
# 停止容器
docker-compose down

# 重新构建（如果有代码更新）
docker-compose build --no-cache

# 启动
docker-compose up -d
```

### 清理资源

```bash
# 清理未使用的镜像
docker image prune -a

# 清理未使用的容器
docker container prune

# 清理所有（谨慎使用）
docker system prune -a
```

---

## 🐛 常见问题排查

### 问题1: 无法访问应用

**检查步骤：**
```bash
# 1. 检查容器是否运行
docker ps

# 2. 检查容器日志
docker logs volleyball-app

# 3. 检查端口是否监听
netstat -tlnp | grep 5000

# 4. 检查防火墙
ufw status

# 5. 检查安全组（阿里云控制台）
```

### 问题2: 视频处理失败

**可能原因：**
- FFmpeg未正确安装
- 内存不足
- 磁盘空间不足

**解决方法：**
```bash
# 进入容器检查FFmpeg
docker exec -it volleyball-app which ffmpeg
docker exec -it volleyball-app ffmpeg -version

# 检查磁盘空间
df -h

# 检查内存
free -h
```

### 问题3: 上传大文件失败

**解决：**
- 增加Nginx `client_max_body_size`
- 增加容器内存限制
- 检查超时设置

### 问题4: API调用失败（ChatGPT API）

**解决：**
- 检查网络连接
- 确认API密钥正确
- 查看容器日志

### 问题5: 容器自动停止

**检查日志：**
```bash
docker logs volleyball-app
# 查看错误信息
```

**常见原因：**
- 内存不足
- 代码错误
- 端口冲突

---

## 💰 成本估算

### 阿里云ECS成本（参考）

- **2核4GB**：约 ¥100-200/月（按量付费更灵活）
- **带宽5Mbps**：约 ¥25/月
- **40GB云盘**：约 ¥10/月

**总计：约 ¥135-235/月**

### 优化建议

1. **使用按量付费**：如果不稳定运行
2. **选择优惠活动**：新用户通常有优惠
3. **带宽按需**：可以动态调整
4. **定时备份**：重要数据定期备份

---

## 📝 部署检查清单

部署完成后，请检查：

- [ ] 服务器可以SSH连接
- [ ] Docker和Docker Compose安装成功
- [ ] 容器运行正常（`docker ps`）
- [ ] 应用可以访问（浏览器测试）
- [ ] API接口正常（`/api/health`）
- [ ] 视频上传功能正常
- [ ] 视频分析功能正常
- [ ] 智能问答功能正常
- [ ] Nginx配置正确（如果使用）
- [ ] SSL证书配置（如果使用HTTPS）
- [ ] 防火墙配置正确
- [ ] 容器自动重启（`restart: unless-stopped`）
- [ ] 日志可以查看
- [ ] 磁盘空间充足

---

## 🎯 下一步优化

### 性能优化

1. **使用Redis缓存**：缓存分析结果
2. **使用消息队列**：异步处理视频分析
3. **CDN加速**：静态资源使用CDN
4. **负载均衡**：多实例部署

### 安全加固

1. **使用非root用户**运行容器
2. **配置fail2ban**防止暴力破解
3. **定期更新**系统和依赖
4. **配置备份**自动化

### 监控告警

1. **使用Prometheus + Grafana**监控
2. **配置告警**（资源不足、服务异常）
3. **日志收集**和分析

---

## 📚 参考资源

- [阿里云ECS文档](https://help.aliyun.com/product/25365.html)
- [Docker官方文档](https://docs.docker.com/)
- [Nginx文档](https://nginx.org/en/docs/)
- [Let's Encrypt文档](https://letsencrypt.org/docs/)

---

## 🆘 获取帮助

如果遇到问题：

1. **查看日志**：`docker logs volleyball-app`
2. **检查配置**：确认所有配置文件正确
3. **网络测试**：`curl http://localhost:5000/api/health`
4. **重新构建**：`docker-compose build --no-cache`

---

**祝部署顺利！🎉**

如果有任何问题，请查看日志并检查以上步骤。

