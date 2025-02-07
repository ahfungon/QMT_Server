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
from app import create_app
from app.models import db

def init_database():
    """初始化数据库"""
    print("正在初始化数据库...")
    
    # 加载环境变量
    load_dotenv()
    
    # 创建应用
    app = create_app()
    
    # 创建数据库表
    with app.app_context():
        db.create_all()
        print("数据库表创建成功！")

if __name__ == '__main__':
    init_database() 