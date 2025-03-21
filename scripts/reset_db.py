"""
数据库重置脚本

此脚本用于重置数据库，删除并重新创建数据库及所有表
"""

import os
import sys
from pathlib import Path
from dotenv import load_dotenv
import pymysql
import logging
from sqlalchemy import create_engine, text

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

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
    sys.exit(1)

# 获取数据库连接参数
MYSQL_HOST = os.getenv('MYSQL_HOST', 'localhost')
MYSQL_PORT = int(os.getenv('MYSQL_PORT', '3306'))
MYSQL_USER = os.getenv('MYSQL_USER', 'root')
MYSQL_PASSWORD = os.getenv('MYSQL_PASSWORD', '')
MYSQL_DATABASE = os.getenv('MYSQL_DATABASE', '')

print(f"\n=== 数据库重置 ===")
print(f"主机: {MYSQL_HOST}")
print(f"端口: {MYSQL_PORT}")
print(f"用户: {MYSQL_USER}")
print(f"数据库: {MYSQL_DATABASE}")

# 确认操作
confirm = input("\n警告：此操作将删除并重新创建数据库 '{}'。是否继续？(y/n): ".format(MYSQL_DATABASE))
if confirm.lower() != 'y':
    print("操作已取消")
    sys.exit(0)

try:
    # 连接到MySQL（不指定数据库）
    print(f"\n正在连接到MySQL服务器...")
    conn = pymysql.connect(
        host=MYSQL_HOST,
        port=MYSQL_PORT,
        user=MYSQL_USER,
        password=MYSQL_PASSWORD
    )
    
    print("连接成功！")
    
    # 获取游标
    with conn.cursor() as cursor:
        # 检查数据库是否存在
        cursor.execute(f"SHOW DATABASES LIKE '{MYSQL_DATABASE}'")
        db_exists = cursor.fetchone() is not None
        
        if db_exists:
            print(f"正在删除数据库 '{MYSQL_DATABASE}'...")
            cursor.execute(f"DROP DATABASE {MYSQL_DATABASE}")
            print(f"数据库 '{MYSQL_DATABASE}' 已删除")
        
        # 创建数据库
        print(f"正在创建数据库 '{MYSQL_DATABASE}'...")
        cursor.execute(
            f"CREATE DATABASE {MYSQL_DATABASE} "
            "DEFAULT CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci"
        )
        print(f"数据库 '{MYSQL_DATABASE}' 创建成功！")
    
    conn.close()
    print("MySQL连接已关闭")
    
    # 现在启动应用来创建表
    print("\n=== 初始化数据库表 ===")
    print("注意：请回到项目根目录运行 'python run.py' 来创建表")
    
    print("\n数据库重置完成！\n")
    
except Exception as e:
    print(f"\n错误: {e}")
    sys.exit(1) 