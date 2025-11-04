# 🏐 排球AI训练系统 v3.0

**AI-Powered Volleyball Training System**

一个基于人工智能的排球垫球动作识别与训练系统，帮助排球爱好者提升技术水平。

---

## ✨ 主要特性

### 🎯 核心功能
- **智能姿态识别**: 基于MediaPipe的33点人体姿态检测
- **多维度评分**: 手臂姿态、身体重心、触球位置、整体稳定性4个维度全面评估
- **双模式分析**: 
  - 单帧快速分析：提取关键帧，3秒出结果
  - 连续帧深度分析：完整动作序列，流畅度、完整性、一致性多维评估
- **智能反馈**: AI精准定位问题，提供个性化改进建议
- **游戏化关卡**: 初级(50分)、中级(70分)、高级(85分)循序渐进

### 🎬 可视化功能
- **骨架叠加**: 在原视频上叠加姿态骨架
- **纯骨架动画**: 白色背景抽象骨架展示
- **左右对比**: 原视频与骨架并排对比
- **轨迹追踪**: 实时绘制关键点运动路径

### 🏗️ 专业架构
- **前后端分离**: 清晰的模块化设计
- **三层架构**: API层、服务层、核心层
- **易于扩展**: 组件化开发，便于维护和升级

---

## 🚀 快速开始

### 环境要求
- Python 3.8+
- pip

### 安装步骤

1. **克隆项目**
```bash
git clone <repository-url>
cd volleyball-ai-training
```

2. **安装依赖**
```bash
pip install -r requirements.txt
```

3. **配置环境变量**（重要！）
   
   项目使用环境变量管理 API Key，避免敏感信息泄露。
   
   ```bash
   # 复制配置模板
   cp .env.example .env
   
   # 编辑 .env 文件，填入您的 API Key
   # Windows: notepad .env
   # Linux/Mac: nano .env
   ```
   
   在 `.env` 文件中设置：
   ```env
   OPENAI_API_KEY=your_api_key_here
   OPENAI_BASE_URL=https://api.chatanywhere.tech
   ```
   
   📖 详细配置说明请查看 [配置指南](CONFIGURATION_GUIDE.md)

4. **启动应用**
```bash
# Flask API 服务器（推荐）
python run_flask.py

# 或 Streamlit 应用
streamlit run app.py
```

5. **访问系统**
   - Flask API: 打开浏览器访问 `http://localhost:5000`
   - Streamlit: 打开浏览器访问 `http://localhost:8501`

---

## 📂 项目结构

```
volleyball-ai-training/
│
├── app.py                      # Streamlit主应用入口
├── requirements.txt            # 项目依赖
├── README.md                   # 项目文档
│
├── backend/                    # 后端代码
│   ├── __init__.py
│   ├── api/                   # API接口层
│   │   ├── __init__.py
│   │   └── volleyball_api.py  # 对外API接口
│   ├── core/                  # 核心功能模块
│   │   ├── __init__.py
│   │   ├── pose_detector.py   # 姿态检测
│   │   ├── video_processor.py # 视频处理
│   │   ├── scorer.py          # 评分算法
│   │   ├── sequence_analyzer.py    # 序列分析
│   │   ├── trajectory_visualizer.py # 轨迹可视化
│   │   └── video_generator.py      # 视频生成
│   ├── services/              # 业务逻辑层
│   │   ├── __init__.py
│   │   └── volleyball_service.py   # 业务服务
│   ├── models/                # 数据模型
│   └── utils/                 # 工具函数
│
├── frontend/                   # 前端代码
│   ├── __init__.py
│   ├── components/            # UI组件
│   │   ├── __init__.py
│   │   ├── header.py         # 页面头部
│   │   ├── score_card.py     # 评分卡片
│   │   └── video_uploader.py # 视频上传
│   ├── pages/                # 页面
│   └── assets/               # 静态资源
│
├── config/                    # 配置文件
│   ├── __init__.py
│   └── settings.py           # 系统配置
│
├── data/                     # 数据目录
│   ├── models/              # 模型文件
│   └── templates/           # 动作模板
│       └── default_template.json
│
├── output/                   # 输出文件
│   └── (生成的视频等)
│
└── tests/                    # 测试代码
    ├── unit/                # 单元测试
    └── integration/         # 集成测试
```

---

## 📖 使用指南

### 1. 动作分析

#### 上传视频
- 支持格式: MP4, AVI, MOV, MKV
- 文件大小: ≤ 50MB
- 视频时长: 3-10秒最佳

#### 选择分析模式
- **🎯 单帧分析（快速）**: 提取关键帧快速评估，适合初学者
- **🎬 连续帧分析（详细）**: 完整动作序列深度分析，提供流畅度等指标

#### 查看结果
- 总分及分项得分
- 雷达图可视化
- 关卡等级评定
- 个性化改进建议

### 2. 视频可视化

#### 生成可视化视频
1. 上传原始视频
2. 选择可视化类型:
   - 🎥 骨架叠加（推荐）
   - 🦴 纯骨架动画
   - 📊 左右对比
   - 📈 轨迹追踪
3. 点击生成按钮
4. 下载生成的视频

### 3. 拍摄技巧

#### 📹 拍摄要求
- **角度**: 正面拍摄，相机与人平行
- **距离**: 全身入镜，从头到脚完整显示
- **光线**: 充足且均匀，避免逆光
- **背景**: 简洁清爽，避免杂乱
- **稳定**: 使用三脚架或稳定设备

#### 👕 服装建议
- 穿着贴身运动服
- 避免过于宽松的衣物
- 颜色与背景有对比度

---

## 📊 评分标准

### 总分构成 (100分)

| 维度 | 分值 | 评分标准 |
|------|------|----------|
| **手臂姿态** | 40分 | 双臂伸直(165°)，夹角<30°，水平对称 |
| **身体重心** | 30分 | 膝盖弯曲60-90°，重心下沉稳定 |
| **触球位置** | 20分 | 接触点在腰腹前方，高度适中(45%身高) |
| **整体稳定** | 10分 | 动作流畅连贯，姿态置信度高 |

### 关卡等级

- 🌱 **初级**: ≥50分 - 基础动作掌握
- 🌟 **中级**: ≥70分 - 标准动作规范  
- 🏆 **高级**: ≥85分 - 专业级别水准

---

## 🔧 技术架构

### 后端技术
- **MediaPipe Pose**: 实时姿态检测（33个关键点）
- **OpenCV**: 视频处理与帧提取
- **NumPy & SciPy**: 数值计算与信号处理
- **Python 3.8+**: 主要开发语言

### 前端技术
- **Streamlit**: Web应用框架
- **Plotly**: 交互式数据可视化
- **CSS3**: 现代化UI样式

### 架构设计
```
┌─────────────────┐
│   Streamlit UI  │  ← 前端展示层
└────────┬────────┘
         │
┌────────▼────────┐
│   API Layer     │  ← 接口层
└────────┬────────┘
         │
┌────────▼────────┐
│ Service Layer   │  ← 业务逻辑层
└────────┬────────┘
         │
┌────────▼────────┐
│   Core Modules  │  ← 核心功能层
│  (Pose, Video,  │
│   Score, etc.)  │
└─────────────────┘
```

---

## 🎯 适用场景

### 👥 目标用户
- **排球初学者**: 学习标准动作，建立正确基础
- **业余爱好者**: 自我训练，提升技术水平
- **体育教练**: 辅助教学，量化评估学员
- **学生研究者**: 姿态识别研究，运动分析

### 💡 应用场景
- 个人训练辅助
- 线上教学工具
- 训练营评估系统
- 体育科研项目

---

## 📝 版本历史

### v3.0.0 (2025-10-31) - 重大重构
- ✨ 全新架构：前后端分离，模块化设计
- 🎨 现代化UI：全新Streamlit界面，参考专业设计
- 📦 三层架构：API层、服务层、核心层清晰分离
- 📚 完整文档：详细的使用指南和技术文档
- 🔧 易于维护：组件化开发，便于扩展和调试

### v2.1.0 (2025-10-28)
- 🎥 新增4种动态视频可视化模式
- 📈 改进轨迹追踪算法

### v2.0.0 (2025-10-25)
- 🎬 新增连续帧分析功能
- 📊 流畅度、完整性、一致性评估

### v1.0.0
- 🎯 基础姿态识别与评分功能

---

## 🛠️ 开发指南

### 安装开发依赖
```bash
pip install -r requirements.txt
```

### 运行测试
```bash
# 单元测试
pytest tests/unit/

# 集成测试
pytest tests/integration/
```

### 代码规范
- 遵循PEP 8规范
- 使用类型注解
- 添加文档字符串
- 保持模块独立性

### 添加新功能
1. 在`backend/core/`添加核心功能模块
2. 在`backend/services/`扩展业务逻辑
3. 在`backend/api/`暴露API接口
4. 在`frontend/components/`创建UI组件
5. 在`app.py`中集成到主应用

---

## 🤝 贡献指南

欢迎提交Issue和Pull Request！

### 贡献流程
1. Fork本项目
2. 创建特性分支 (`git checkout -b feature/AmazingFeature`)
3. 提交更改 (`git commit -m 'Add some AmazingFeature'`)
4. 推送到分支 (`git push origin feature/AmazingFeature`)
5. 开启Pull Request

---

## 📄 许可证

本项目采用 MIT 许可证。详见 [LICENSE](LICENSE) 文件。

---

## 📮 联系方式

如有问题或建议，欢迎联系：
- 📧 Email: your-email@example.com
- 💬 Issues: [GitHub Issues](https://github.com/your-repo/issues)

---

## 🙏 致谢

- [MediaPipe](https://google.github.io/mediapipe/) - 提供强大的姿态识别技术
- [Streamlit](https://streamlit.io/) - 简洁高效的Web框架
- [OpenCV](https://opencv.org/) - 计算机视觉基础库

---

💖 **Made with passion for volleyball training**

🌟 如果这个项目对你有帮助，请给个Star！
