"""
数据库初始化脚本

此脚本用于初始化数据库结构
"""

import os
import sys
from pathlib import Path

# 添加项目根目录到 Python 路径
project_root = Path(__file__).parent.parent
sys.path.append(str(project_root))

from dotenv import load_dotenv
import pymysql
from app import create_app
from app.models import db

def init_database():
    """初始化数据库"""
    print("正在初始化数据库...")
    
    # 加载环境变量
    env_path = Path(__file__).parent.parent / '.env'
    load_dotenv(env_path, override=True)
    
    # 打印环境变量和配置信息
    print("\n=== 环境变量信息 ===")
    print(f"MYSQL_HOST: {os.getenv('MYSQL_HOST')}")
    print(f"MYSQL_PORT: {os.getenv('MYSQL_PORT')}")
    print(f"MYSQL_USER: {os.getenv('MYSQL_USER')}")
    print(f"MYSQL_DATABASE: {os.getenv('MYSQL_DATABASE')}")
    print(f"当前工作目录: {os.getcwd()}")
    print(f"环境变量文件路径: {env_path}")
    print(f"环境变量文件是否存在: {env_path.exists()}")
    
    # 创建应用
    app = create_app()
    
    # 打印 SQLAlchemy 配置
    print("\n=== SQLAlchemy 配置 ===")
    print(f"SQLALCHEMY_DATABASE_URI: {app.config['SQLALCHEMY_DATABASE_URI']}")
    
    # 创建数据库表
    with app.app_context():
        db.create_all()
        print("\n数据库表创建成功！")

if __name__ == '__main__':
    init_database() 