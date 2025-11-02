#!/bin/bash

echo "================================================"
echo "  排球冒险 - AI训练系统 (Flask Web版本)"
echo "================================================"
echo ""

# 激活虚拟环境(如果存在)
if [ -f "venv/bin/activate" ]; then
    echo "正在激活虚拟环境..."
    source venv/bin/activate
fi

# 启动Flask服务器
echo "正在启动Web服务器..."
python run_flask.py

