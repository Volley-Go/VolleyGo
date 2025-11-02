# 🚀 启动Web服务器 - 一键指南

## Windows用户 👨‍💻

### 方法1: 双击批处理文件（最简单）
```
双击运行: run_flask.bat
```

### 方法2: 命令行启动
```bash
# 打开命令提示符（CMD）或PowerShell
cd D:\Library\Volleyball
python run_flask.py
```

---

## Linux/Mac用户 🐧🍎

### 方法1: 使用Shell脚本
```bash
chmod +x run_flask.sh
./run_flask.sh
```

### 方法2: 直接运行Python
```bash
cd /path/to/Volleyball
python run_flask.py
```

---

## 📍 访问地址

服务器启动后，在浏览器中打开:

### 🌐 http://localhost:5000

或者使用本机IP地址（局域网访问）:
### 🌐 http://你的IP地址:5000

---

## ✅ 检查服务器状态

### 方法1: 浏览器访问
打开: http://localhost:5000/api/health

应该看到:
```json
{
  "status": "ok",
  "message": "Volleyball AI Training System API is running",
  "version": "1.0.0"
}
```

### 方法2: 命令行测试
```bash
curl http://localhost:5000/api/health
```

---

## 🛑 停止服务器

在启动服务器的终端窗口中按:
```
Ctrl + C
```

---

## 🔧 常见启动问题

### 问题1: 端口5000被占用

**解决方案:**

修改 `backend/api/flask_api.py` 最后几行:
```python
app.run(host='0.0.0.0', port=5001, debug=True)  # 改为5001或其他端口
```

### 问题2: 找不到模块

**解决方案:**
```bash
# 安装依赖
pip install -r requirements.txt

# 或单独安装
pip install Flask Flask-CORS
```

### 问题3: Python版本过低

**要求:** Python 3.8+

**检查版本:**
```bash
python --version
```

如果版本过低，请升级Python。

---

## 📦 首次启动清单

✅ 1. Python 3.8+ 已安装  
✅ 2. 已安装项目依赖 (`pip install -r requirements.txt`)  
✅ 3. FFmpeg已安装（视频处理）  
✅ 4. 端口5000未被占用  
✅ 5. 网络连接正常（Tailwind CSS使用CDN）  

---

## 🎯 启动后做什么？

1. **首次访问**: 会自动显示新手引导（4步）
2. **选择位置**: 选择你的主打位置（主攻、副攻等）
3. **开始训练**: 上传视频，获得AI分析
4. **学习战术**: 完成战术测试，获得星星和经验
5. **查看进度**: 在个人资料中查看你的成长

---

## 📊 服务器终端显示

正常启动后，你应该看到:

```
============================================================
🏐 排球冒险 - AI训练系统
============================================================
📍 前端地址: http://localhost:5000
📍 API地址: http://localhost:5000/api
📁 输出目录: D:\Library\Volleyball\output
============================================================
提示: 在浏览器中打开 http://localhost:5000 即可使用
按 Ctrl+C 停止服务器
============================================================

 * Serving Flask app 'flask_api'
 * Debug mode: on
WARNING: This is a development server...
 * Running on all addresses (0.0.0.0)
 * Running on http://127.0.0.1:5000
 * Running on http://192.168.x.x:5000
```

---

## 🎨 界面截图说明

当你看到以下界面时，说明启动成功：

1. **顶部**: 橙色渐变背景，显示用户信息
2. **中间**: 排球场位置可视化
3. **底部**: 战术学习和AI教练标签
4. **最底部**: 导航栏（主页、排行榜、我的、设置）

---

## 💻 开发者模式

如果你是开发者，想要修改代码并实时查看效果:

1. Flask 自动重载已启用（debug=True）
2. 修改HTML/JS/CSS后，刷新浏览器即可
3. 修改Python后端代码，Flask会自动重启

---

## 📞 需要帮助？

- 查看 `QUICK_START_WEB.md` - 详细使用指南
- 查看 `WEB_VERSION_README.md` - 功能说明
- 查看 `frontend/README.md` - 前端文档

---

**现在就开始你的排球冒险之旅吧！🚀**

