# 排球冒险 - Web前端说明

## 🎯 概述

基于Figma设计稿实现的HTML + Tailwind CSS前端界面，对接Flask REST API后端。

## 📁 文件结构

```
frontend/
├── index.html          # 主HTML文件
├── js/
│   ├── app.js         # 主应用逻辑
│   ├── api.js         # API通信模块
│   └── components.js  # UI组件库
└── README.md          # 本文件
```

## 🚀 启动方式

### 1. 安装依赖

```bash
pip install -r requirements.txt
```

### 2. 启动Flask服务器

**Windows:**
```bash
run_flask.bat
```

**Linux/Mac:**
```bash
chmod +x run_flask.sh
./run_flask.sh
```

**或直接运行Python:**
```bash
python run_flask.py
```

### 3. 访问应用

在浏览器中打开: `http://localhost:5000`

## 🎨 功能特性

### ✅ 已实现功能

1. **新手引导流程** (4步)
   - 欢迎页面
   - 核心功能介绍
   - 位置选择
   - 进阶路线预览

2. **主页面**
   - 用户信息栏（等级、经验、段位）
   - 排球场位置可视化
   - 战术学习标签页
   - AI教练标签页

3. **AI动作识别**
   - 视频上传（拖拽/点击）
   - 分析模式选择（单帧/序列）
   - 实时AI分析
   - 评分结果展示（总分、分项得分）
   - 姿态检测可视化
   - 运动轨迹分析
   - 改进建议反馈

4. **战术学习**
   - 战术卡片列表
   - 难度分级（初级/中级/高级）
   - 解锁机制
   - 奖励系统

5. **底部导航**
   - 主页
   - 排行榜
   - 个人资料
   - 设置

### 🚧 待完善功能

1. **战术测试题库** - 实现完整的问答流程
2. **排行榜** - 展示用户排名
3. **个人资料** - 段位进阶、统计数据、成就系统
4. **设置** - 通知、音效、深色模式等

## 🔧 API接口

### 视频分析
```
POST /api/analyze/video
Content-Type: multipart/form-data

参数:
- video: 视频文件
- mode: 'single' | 'sequence'

返回:
{
  "success": true,
  "score": {
    "total_score": 85.5,
    "arm_score": 90,
    "body_score": 85,
    "position_score": 82,
    "stability_score": 85,
    "feedback": [...]
  },
  "pose_image_base64": "...",
  "trajectory_plot_base64": "..."
}
```

### 战术题库
```
GET /api/tactics/questions

返回:
{
  "questions": [...],
  "categories": [...],
  "difficulty_levels": [...]
}
```

## 🎨 设计要点

### 颜色方案
- 主橙色: `#FF6900` (volleyball-orange)
- 深橙色: `#F54900` (volleyball-dark-orange)
- 浅橙色: `#FE9A00` (volleyball-light-orange)
- 绿色: `#00C950` (volleyball-green)
- 蓝色: `#155DFC` (volleyball-blue)
- 紫色: `#AD46FF` (volleyball-purple)

### 组件风格
- 圆角: 大圆角设计（rounded-2xl, rounded-3xl）
- 阴影: 多层次阴影效果
- 渐变: 线性渐变背景
- 动画: 平滑的hover和transition效果

### 响应式设计
- 移动端优先
- 平板适配
- 桌面端优化

## 💡 开发建议

### 调试
在浏览器开发者工具中查看:
- Console: JavaScript日志和错误
- Network: API请求和响应
- Application: LocalStorage数据

### 自定义
修改 `tailwind.config` 在 `index.html` 中自定义主题颜色和样式。

### 扩展
在 `components.js` 中添加新的可复用组件。

## 📝 注意事项

1. **CORS设置**: Flask API已配置CORS，允许跨域请求
2. **文件大小限制**: 视频文件最大50MB
3. **支持格式**: MP4, AVI, MOV, MKV
4. **浏览器兼容**: 推荐使用Chrome、Edge或Firefox最新版本

## 🐛 常见问题

### 问题1: 视频分析失败
- 检查视频格式是否支持
- 确认视频中有清晰的人体姿态
- 查看浏览器Console错误信息

### 问题2: API连接失败
- 确认Flask服务器已启动
- 检查端口5000是否被占用
- 查看Network标签页中的请求状态

### 问题3: 页面显示异常
- 清除浏览器缓存
- 检查Tailwind CSS CDN是否加载成功
- 查看Console中的JavaScript错误

## 📞 技术支持

如有问题，请检查:
1. Flask服务器日志
2. 浏览器开发者工具
3. 项目根目录的其他文档

