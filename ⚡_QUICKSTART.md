# ⚡ 三步启动 - 最简版

## 第一步：安装依赖 📦
```bash
pip install -r requirements.txt
```

## 第二步：启动服务器 🚀
```bash
run_flask.bat
```

## 第三步：打开浏览器 🌐
```
http://localhost:5000
```

---

## ✅ 就这么简单！

**接下来你会看到：**
1. 新手引导页面（首次访问）
2. 选择你的位置
3. 进入主页面
4. 开始训练！

---

## 🎯 核心功能试用

### AI动作识别（必试！）
1. 点击 **"AI 教练"** 标签
2. 点击 **"开始咨询 AI 教练"**
3. 上传你的排球训练视频
4. 选择 **"单帧快速分析"**
5. 点击 **"开始AI分析"**
6. 查看AI评分和反馈！

---

## 🐛 遇到问题？

### 端口被占用
修改 `backend/api/flask_api.py` 最后一行:
```python
app.run(host='0.0.0.0', port=5001, debug=True)  # 改成5001
```

### 找不到Flask
```bash
pip install Flask Flask-CORS
```

### 其他问题
查看: `QUICK_START_WEB.md`

---

**立即开始！🏐**

