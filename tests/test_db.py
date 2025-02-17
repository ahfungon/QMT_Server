"""
数据库连接测试程序
"""

import os
from pathlib import Path
from dotenv import load_dotenv
import pymysql
from sqlalchemy import create_engine, text
from sqlalchemy.exc import SQLAlchemyError

# 获取项目根目录
ROOT_DIR = Path(__file__).resolve().parent.parent
env_path = ROOT_DIR / '.env'

# 加载环境变量
print(f"\n=== 加载环境变量 ===")
print(f"尝试加载环境变量文件：{env_path}")
if env_path.exists():
    load_dotenv(env_path, override=True)
    print("环境变量加载成功！")
else:
    print("警告：找不到 .env 文件！")

# 打印所有当前环境变量
print("\n=== 当前所有环境变量 ===")
for key, value in os.environ.items():
    if 'MYSQL' in key:
        print(f"{key}: {value}")

# 在加载环境变量之后添加
print(f"\n=== 文件路径信息 ===")
print(f"当前文件: {__file__}")
print(f"当前目录: {os.getcwd()}")
print(f"环境变量文件路径: {env_path}")
print(f"环境变量文件是否存在: {env_path.exists()}")

if env_path.exists():
    print("\n=== 环境变量文件内容 ===")
    with open(env_path, 'r', encoding='utf-8') as f:
        print(f.read())

def test_pymysql_connection():
    """测试 PyMySQL 直接连接"""
    print("\n=== 测试 PyMySQL 直接连接 ===")
    try:
        # 获取环境变量
        host = os.getenv('MYSQL_HOST')
        port = int(os.getenv('MYSQL_PORT', 3306))
        user = os.getenv('MYSQL_USER')
        password = os.getenv('MYSQL_PASSWORD')
        database = os.getenv('MYSQL_DATABASE')
        
        print(f"连接信息:")
        print(f"- HOST: {host}")
        print(f"- PORT: {port}")
        print(f"- USER: {user}")
        print(f"- DATABASE: {database}")
        print(f"- PASSWORD: {'*' * len(str(password)) if password else 'None'}")
        
        # 创建连接
        conn = pymysql.connect(
            host=host,
            port=port,
            user=user,
            password=password,
            database=database
        )
        
        print("PyMySQL 连接成功!")
        
        # 测试查询
        with conn.cursor() as cursor:
            cursor.execute("SELECT VERSION()")
            version = cursor.fetchone()
            print(f"MySQL 版本: {version[0]}")
            
            # 获取用户认证方式
            cursor.execute("SELECT user, host, plugin FROM mysql.user WHERE user = %s", (user,))
            user_info = cursor.fetchone()
            if user_info:
                print(f"用户认证方式: {user_info[2]}")
        
        conn.close()
        
    except pymysql.Error as e:
        print(f"PyMySQL 连接失败: {str(e)}")
        # 打印更详细的错误信息
        import traceback
        print("\n=== 详细错误信息 ===")
        print(traceback.format_exc())

def test_sqlalchemy_connection():
    """测试 SQLAlchemy 连接"""
    print("\n=== 测试 SQLAlchemy 连接 ===")
    try:
        # 获取环境变量
        host = os.getenv('MYSQL_HOST')
        port = os.getenv('MYSQL_PORT', 3306)
        user = os.getenv('MYSQL_USER')
        password = os.getenv('MYSQL_PASSWORD')
        database = os.getenv('MYSQL_DATABASE')
        
        # 构建连接 URL
        url = f"mysql+pymysql://{user}:{password}@{host}:{port}/{database}"
        print(f"连接URL: {url}")
        
        # 创建引擎
        engine = create_engine(url)
        
        # 测试连接
        with engine.connect() as conn:
            print("SQLAlchemy 连接成功!")
            result = conn.execute(text("SELECT VERSION()")).fetchone()
            print(f"MySQL 版本: {result[0]}")
            
    except SQLAlchemyError as e:
        print(f"SQLAlchemy 连接失败: {str(e)}")

if __name__ == "__main__":
    # 打印环境变量
    print("=== 环境变量信息 ===")
    print(f"MYSQL_HOST: {os.getenv('MYSQL_HOST')}")
    print(f"MYSQL_PORT: {os.getenv('MYSQL_PORT')}")
    print(f"MYSQL_USER: {os.getenv('MYSQL_USER')}")
    print(f"MYSQL_DATABASE: {os.getenv('MYSQL_DATABASE')}")
    
    # 测试连接
    test_pymysql_connection()
    test_sqlalchemy_connection() 