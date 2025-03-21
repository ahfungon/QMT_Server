"""
应用入口模块

此模块是应用的启动入口
"""

import os
from pathlib import Path
from dotenv import load_dotenv
import sys
import logging

# 获取项目根目录
ROOT_DIR = Path(__file__).resolve().parent
env_path = ROOT_DIR / '.env'

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# 加载环境变量
print(f"\n=== 加载环境变量 ===")
print(f"尝试加载环境变量文件：{env_path}")
if env_path.exists():
    # 使用override=True确保覆盖任何已存在的环境变量
    load_dotenv(env_path, override=True)
    print("环境变量加载成功！")
    
    # 验证关键环境变量是否存在
    required_vars = ['MYSQL_HOST', 'MYSQL_PORT', 'MYSQL_USER', 'MYSQL_PASSWORD', 'MYSQL_DATABASE']
    missing_vars = [var for var in required_vars if not os.getenv(var)]
    
    if missing_vars:
        print(f"警告：以下环境变量缺失或为空：{', '.join(missing_vars)}")
    else:
        print("所有必要的环境变量已加载")
        # 打印部分环境变量（隐藏密码）
        mysql_host = os.getenv('MYSQL_HOST')
        mysql_port = os.getenv('MYSQL_PORT')
        mysql_user = os.getenv('MYSQL_USER')
        mysql_database = os.getenv('MYSQL_DATABASE')
        print(f"MySQL连接信息: {mysql_user}@{mysql_host}:{mysql_port}/{mysql_database}")
else:
    print("警告：找不到 .env 文件！")
    sys.exit(1)  # 如果没有环境变量文件，直接退出

# 导入应用创建函数
from app import create_app

# 创建应用实例
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