# 排球冒险 - Web版本使用指南

## 🎉 新功能：HTML + Tailwind CSS 前端

根据Figma设计稿，全新打造的Web前端界面，完美对接AI动作识别后端！

## 🚀 快速启动

### 1. 安装依赖

```bash
pip install -r requirements.txt
```

主要新增依赖:
- `Flask>=3.0.0` - Web框架
- `Flask-CORS>=4.0.0` - 跨域支持

### 2. 启动Web服务器

**Windows用户:**
```bash
run_flask.bat
```

**Linux/Mac用户:**
```bash
chmod +x run_flask.sh
./run_flask.sh
```

**或者直接运行:**
```bash
python run_flask.py
```

### 3. 访问应用

在浏览器中打开: **http://localhost:5000**

## 📱 功能特性

### ✨ 新手引导（4步流程）

1. **欢迎页面** - 介绍核心功能
2. **功能介绍** - 基础阶段、专门技能、激励系统
3. **位置选择** - 选择你的主打位置（主攻、副攻、二传、接应、自由人等）
4. **进阶路线** - 查看专属技能树和成长路线

### 🏐 主页面

#### 用户信息栏
- 实时显示等级、经验值（XP）
- 段位展示（青铜→王者）
- 星星收集进度
- 等级进度条

#### 排球场位置可视化
- 6个位置卡片展示
- 每个位置显示星星、等级、经验进度
- 点击位置开始训练

#### 功能标签页

**1. 战术学习标签 📚**
- 6个战术主题卡片
- 难度分级（初级/中级/高级）
- 解锁机制（需要指定星星和等级）
- 完成奖励（星星+经验）
- 点击开始战术测试

**2. AI教练标签 🤖**
- 智能问答服务
- **视频分析核心功能**（重点）

### 🎯 AI动作识别分析（重点功能）

#### 视频上传
- 支持拖拽上传
- 支持点击上传
- 实时预览
- 文件格式验证（MP4, AVI, MOV, MKV）
- 文件大小限制（最大50MB）

#### 分析模式
1. **单帧快速分析** （推荐）
   - 提取关键帧
   - 快速返回结果
   - 适合快速反馈

2. **连续帧深度分析**
   - 分析整个动作序列
   - 提供轨迹分析
   - 更详细的评分

#### 分析结果展示
- ✅ **总分显示**（0-100分，带等级评价）
- ✅ **四项分项得分**:
  - 手臂动作
  - 身体姿态
  - 位置准确
  - 稳定性
- ✅ **姿态检测可视化图**（关键点标注）
- ✅ **运动轨迹分析图**（序列模式）
- ✅ **AI反馈建议**（针对性改进意见）

### 📝 战术测试功能

- 随机抽取5道题目
- 多选题形式
- 实时答案检查
- 正确/错误标注
- 详细答案解析
- 完成奖励（星星+经验）
- 答案回顾功能

### 🏆 底部导航栏

- 主页
- 排行榜（开发中）
- 个人资料（开发中）
- 设置（开发中）

## 🔌 API接口说明

### 1. 视频分析接口

**端点:** `POST /api/analyze/video`

**请求:**
```javascript
FormData {
  video: File,
  mode: 'single' | 'sequence'
}
```

**响应:**
```json
{
  "success": true,
  "score": {
    "total_score": 85.5,
    "arm_score": 90.0,
    "body_score": 85.0,
    "position_score": 82.0,
    "stability_score": 85.0,
    "feedback": ["建议1", "建议2"]
  },
  "pose_image_base64": "...",
  "trajectory_plot_base64": "...",
  "analysis_mode": "single_frame"
}
```

### 2. 战术题库接口

**端点:** `GET /api/tactics/questions`

**响应:**
```json
{
  "questions": [...],
  "categories": [...],
  "difficulty_levels": [...]
}
```

### 3. 健康检查

**端点:** `GET /api/health`

**响应:**
```json
{
  "status": "ok",
  "message": "Volleyball AI Training System API is running",
  "version": "1.0.0"
}
```

## 🎨 设计特点

### UI/UX
- ✨ 遵循Figma设计稿
- 🎨 Tailwind CSS美化
- 📱 响应式设计（移动端友好）
- 🌈 渐变背景和卡片效果
- ⚡ 流畅的动画过渡
- 🎭 悬停效果和反馈

### 颜色方案
- 主色调：橙色系 (#FF6900)
- 辅助色：绿色 (#00C950)、蓝色 (#155DFC)、紫色 (#AD46FF)
- 多层次阴影效果
- 半透明背景

### 交互设计
- 点击即时反馈
- 加载状态提示
- Toast通知
- 平滑页面切换

## 📂 文件结构

```
项目根目录/
├── backend/
│   ├── api/
│   │   ├── flask_api.py      # Flask REST API (新)
│   │   └── volleyball_api.py  # API业务逻辑
│   ├── core/                  # 核心算法
│   │   ├── pose_detector.py   # 姿态检测
│   │   ├── scorer_v2.py       # 评分系统V2
│   │   ├── video_processor.py # 视频处理
│   │   └── ...
│   └── services/              # 业务服务层
│       └── volleyball_service.py
├── frontend/                  # Web前端 (新)
│   ├── index.html            # 主HTML页面
│   ├── js/
│   │   ├── app.js           # 主应用逻辑
│   │   ├── api.js           # API通信
│   │   ├── components.js    # UI组件
│   │   └── tactics.js       # 战术测试模块
│   └── README.md
├── config/
│   └── settings.py            # 配置文件
├── data/
│   ├── tactics_questions.json # 战术题库
│   └── templates/
├── requirements.txt           # 依赖列表 (已更新)
├── run_flask.py              # Flask启动脚本 (新)
├── run_flask.bat             # Windows启动脚本 (新)
├── run_flask.sh              # Linux/Mac启动脚本 (新)
└── WEB_VERSION_README.md     # 本文件
```

## ⚙️ 配置说明

### 环境变量
可以在 `config/settings.py` 中修改:
- `OUTPUT_DIR`: 输出视频目录
- 其他配置参数

### 端口配置
默认端口: `5000`

如需修改，编辑 `backend/api/flask_api.py`:
```python
app.run(host='0.0.0.0', port=5000, debug=True)
```

## 🔍 调试技巧

### 1. 检查API状态
访问: http://localhost:5000/api/health

### 2. 查看浏览器Console
按 `F12` 打开开发者工具，查看:
- Console: JavaScript日志
- Network: API请求和响应
- Application: LocalStorage数据

### 3. 后端日志
Flask服务器会在终端输出详细日志

## 🐛 常见问题

### Q1: 视频上传后无响应
**A:** 
- 检查视频格式（支持MP4, AVI, MOV, MKV）
- 确认文件大小不超过50MB
- 查看浏览器Console错误信息

### Q2: AI分析失败
**A:**
- 确保视频中有清晰的人体姿态
- 尝试使用不同的分析模式
- 检查后端服务器日志

### Q3: 页面样式显示不正常
**A:**
- 检查网络连接（Tailwind CSS使用CDN）
- 清除浏览器缓存
- 尝试使用Chrome或Firefox最新版本

### Q4: CORS错误
**A:**
- 确认Flask-CORS已正确安装
- 检查 `flask_api.py` 中的CORS配置

## 💡 开发建议

### 添加新功能
1. 在 `js/app.js` 中添加新页面渲染函数
2. 在 `js/components.js` 中创建可复用组件
3. 在 `backend/api/flask_api.py` 中添加新API端点

### 修改样式
在 `index.html` 的 `<script>` 标签中修改Tailwind配置

### 扩展题库
编辑 `data/tactics_questions.json` 添加新题目

## 📊 与原Streamlit版本对比

| 特性 | Streamlit版本 | Web版本 |
|------|--------------|---------|
| UI框架 | Streamlit组件 | HTML + Tailwind CSS |
| 设计 | 默认样式 | ✅ 完全遵循Figma设计 |
| 响应式 | 有限 | ✅ 完全响应式 |
| 自定义程度 | 中等 | ✅ 高度自定义 |
| 部署 | Streamlit Cloud | ✅ 任意Web服务器 |
| API方式 | Python函数调用 | ✅ RESTful HTTP API |
| 加载速度 | 中等 | ✅ 更快 |
| 用户体验 | 良好 | ✅ 优秀 |

## 🎯 重点功能：AI动作识别

### 核心流程

1. **用户上传视频**
   - 前端: 文件验证、预览
   - 发送: FormData with video file

2. **后端AI分析**
   - 接收视频文件
   - MediaPipe姿态检测
   - 评分系统计算
   - 生成可视化图像

3. **结果展示**
   - 总分和分项得分
   - 可视化姿态检测图
   - 运动轨迹分析
   - AI反馈建议

### 技术栈

**前端:**
- HTML5
- Tailwind CSS (CDN)
- Vanilla JavaScript
- Fetch API

**后端:**
- Flask (Python Web框架)
- MediaPipe (姿态检测)
- OpenCV (视频处理)
- NumPy (数值计算)

## 📈 下一步开发

- [ ] 完善排行榜功能
- [ ] 实现个人资料页面
- [ ] 添加设置页面
- [ ] 实现用户登录/注册
- [ ] 添加数据持久化（数据库）
- [ ] 实现多人对战模式
- [ ] 添加社交分享功能

## 🙏 致谢

- Figma设计稿提供UI/UX指导
- MediaPipe提供姿态检测能力
- Tailwind CSS提供美观的UI组件

---

**Happy Coding! 🏐**

