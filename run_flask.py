"""
Flask Web服务器启动脚本
启动HTML前端和REST API服务
"""
import sys
from pathlib import Path

# 添加项目根目录到路径
sys.path.insert(0, str(Path(__file__).resolve().parent))

from backend.api.flask_api import app
from config.settings import OUTPUT_DIR

if __name__ == '__main__':
    # 确保输出目录存在
    OUTPUT_DIR.mkdir(exist_ok=True, parents=True)
    
    print("\n" + "=" * 60)
    print("🏐 排球冒险 - AI训练系统")
    print("=" * 60)
    print(f"📍 前端地址: http://localhost:5000")
    print(f"📍 API地址: http://localhost:5000/api")
    print(f"📁 输出目录: {OUTPUT_DIR}")
    print("=" * 60)
    print("提示: 在浏览器中打开 http://localhost:5000 即可使用")
    print("按 Ctrl+C 停止服务器")
    print("=" * 60 + "\n")
    
    # 启动Flask开发服务器
    app.run(
        host='0.0.0.0', 
        port=5000, 
        debug=True,
        use_reloader=True
    )

