# 排球冒险 - 部署指南

## 📦 项目部署说明

本项目提供两种运行方式：

### 1️⃣ Web版本（推荐）- HTML + Tailwind CSS + Flask

**优势:**
- ✅ 完美遵循Figma设计稿
- ✅ 现代化Web界面
- ✅ RESTful API架构
- ✅ 易于部署和扩展
- ✅ 更好的用户体验

**启动方式:**
```bash
# Windows
run_flask.bat

# Linux/Mac
chmod +x run_flask.sh
./run_flask.sh

# 或直接运行
python run_flask.py
```

**访问地址:** http://localhost:5000

### 2️⃣ Streamlit版本 - 原版本

**优势:**
- ✅ 快速原型开发
- ✅ Python组件化
- ✅ 适合数据展示

**启动方式:**
```bash
# Windows
run.bat

# Linux/Mac
chmod +x run.sh
./run.sh

# 或直接运行
streamlit run app.py
```

**访问地址:** http://localhost:8501

## 🔧 环境配置

### 系统要求
- Python 3.8+
- 4GB+ RAM
- 支持H.264编码的FFmpeg（视频处理）

### 依赖安装

```bash
# 1. 创建虚拟环境（推荐）
python -m venv venv

# 2. 激活虚拟环境
# Windows:
venv\Scripts\activate
# Linux/Mac:
source venv/bin/activate

# 3. 安装依赖
pip install -r requirements.txt
```

### FFmpeg安装

**Windows:**
1. 下载FFmpeg: https://ffmpeg.org/download.html
2. 解压到C盘
3. 添加到环境变量PATH

**Linux:**
```bash
sudo apt-get install ffmpeg
```

**Mac:**
```bash
brew install ffmpeg
```

## 🌐 生产环境部署

### 使用Gunicorn（推荐）

```bash
# 安装Gunicorn
pip install gunicorn

# 启动服务器
gunicorn -w 4 -b 0.0.0.0:5000 'backend.api.flask_api:app'
```

### 使用Docker

创建 `Dockerfile`:
```dockerfile
FROM python:3.9-slim

WORKDIR /app

# 安装系统依赖
RUN apt-get update && apt-get install -y \
    ffmpeg \
    libgl1-mesa-glx \
    libglib2.0-0

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 5000

CMD ["gunicorn", "-w", "4", "-b", "0.0.0.0:5000", "backend.api.flask_api:app"]
```

构建并运行:
```bash
docker build -t volleyball-ai .
docker run -p 5000:5000 volleyball-ai
```

### Nginx反向代理

创建nginx配置:
```nginx
server {
    listen 80;
    server_name your-domain.com;

    location / {
        proxy_pass http://localhost:5000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
    
    # 增大上传文件限制
    client_max_body_size 50M;
}
```

## 📊 性能优化

### 前端优化
1. **使用本地Tailwind CSS** 而不是CDN（生产环境）
2. **压缩JavaScript文件**
3. **启用浏览器缓存**
4. **图片懒加载**

### 后端优化
1. **使用Redis缓存**分析结果
2. **异步任务队列**处理视频分析
3. **CDN加速**静态资源
4. **数据库**持久化用户数据

## 🔒 安全建议

1. **文件上传验证**
   - 限制文件大小
   - 检查文件类型
   - 扫描恶意内容

2. **API安全**
   - 添加认证token
   - 限制请求频率
   - 使用HTTPS

3. **数据安全**
   - 定期备份
   - 加密敏感数据
   - 日志监控

## 📈 监控与日志

### 日志配置

在 `flask_api.py` 中添加:
```python
import logging

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('app.log'),
        logging.StreamHandler()
    ]
)
```

### 监控工具推荐
- **Sentry**: 错误追踪
- **Prometheus**: 性能监控
- **Grafana**: 可视化仪表板

## 🚀 CI/CD流程

### GitHub Actions示例

创建 `.github/workflows/deploy.yml`:
```yaml
name: Deploy

on:
  push:
    branches: [ main ]

jobs:
  deploy:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - name: Set up Python
        uses: actions/setup-python@v2
        with:
          python-version: '3.9'
      - name: Install dependencies
        run: |
          pip install -r requirements.txt
      - name: Run tests
        run: |
          python -m pytest tests/
      - name: Deploy to server
        run: |
          # 部署脚本
```

## 📱 移动端支持

当前Web版本已完全响应式，支持：
- 📱 手机浏览器
- 📋 平板电脑
- 💻 桌面电脑

### PWA支持（可选）

可以将应用打包为PWA，支持离线访问和安装到主屏幕。

## 🔄 数据迁移

### 从Streamlit迁移到Flask

数据库模式（如果使用）保持一致，只需更改API调用方式：

**Streamlit:**
```python
result = api.analyze_uploaded_video(file, mode='single')
```

**Flask:**
```javascript
const result = await api.analyzeVideo(file, 'single');
```

## 📞 技术支持

遇到问题？

1. 查看 `WEB_VERSION_README.md` - Web版本详细说明
2. 查看 `frontend/README.md` - 前端文档
3. 检查后端日志
4. 查看浏览器Console

## 🎯 最佳实践

1. **开发环境**: 使用Flask内置服务器（debug=True）
2. **测试环境**: 使用Gunicorn（4个worker）
3. **生产环境**: Gunicorn + Nginx + 负载均衡
4. **监控**: 配置日志和监控工具
5. **备份**: 定期备份数据和配置

---

**部署愉快！🎉**

