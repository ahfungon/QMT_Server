"""
应用入口模块

此模块是应用的启动入口
"""

import os
from pathlib import Path
from dotenv import load_dotenv
from app import create_app

# 获取项目根目录
ROOT_DIR = Path(__file__).resolve().parent
env_path = ROOT_DIR / '.env'

# 加载环境变量
print(f"\n=== 加载环境变量 ===")
print(f"尝试加载环境变量文件：{env_path}")
if env_path.exists():
    load_dotenv(env_path, override=True)
    print("环境变量加载成功！")
else:
    print("警告：找不到 .env 文件！")

app = create_app()

if __name__ == '__main__':
    debug = os.getenv('FLASK_DEBUG', '0') == '1'
    port = int(os.getenv('FLASK_RUN_PORT', '5000'))  # 默认使用5000端口
    host = os.getenv('FLASK_RUN_HOST', '0.0.0.0')    # 默认监听所有网络接口
    
    print("="*50)
    print("正在启动服务...")
    print(f"调试模式: {'开启' if debug else '关闭'}")
    print(f"监听地址: {host}")
    print(f"服务端口: {port}")
    print(f"静态文件路径: {app.static_folder}")
    print(f"模板文件路径: {app.template_folder}")
    print("="*50)
    
    # 添加 host 参数，允许外部访问
    app.run(host=host, debug=debug, port=port) 