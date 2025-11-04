# 🔧 环境变量配置指南

本指南说明如何使用环境变量配置 API Key，避免将敏感信息直接写在代码中。

---

## 📋 快速开始

### 1. 复制配置模板

项目根目录下有一个 `.env.example` 文件，这是配置模板。您需要将其复制为 `.env` 文件：

**Windows (PowerShell):**
```powershell
Copy-Item .env.example .env
```

**Windows (CMD):**
```cmd
copy .env.example .env
```

**Linux/Mac:**
```bash
cp .env.example .env
```

### 2. 编辑 .env 文件

使用文本编辑器打开 `.env` 文件，填入您的实际 API Key：

```env
# OpenAI API 配置
# 请复制此文件为 .env 并填入您的实际 API Key

# OpenAI API Key（必填）
# 从 https://platform.openai.com/api-keys 获取
OPENAI_API_KEY=your_api_key_here

# OpenAI API Base URL（可选，默认使用官方API）
# 如果使用代理服务，请修改为代理地址
OPENAI_BASE_URL=https://api.chatanywhere.tech
```

将 `your_api_key_here` 替换为您的实际 API Key。

### 3. 安装依赖

确保已安装 `python-dotenv` 包：

```bash
pip install -r requirements.txt
```

这会自动安装 `python-dotenv>=1.0.0`。

### 4. 启动应用

配置完成后，正常启动应用即可：

```bash
python run_flask.py
```

或

```bash
streamlit run app.py
```
