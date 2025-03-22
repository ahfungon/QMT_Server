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
import re

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# 获取项目根目录
ROOT_DIR = Path(__file__).resolve().parent.parent
env_path = ROOT_DIR / '.env'
sql_script_path = Path(__file__).resolve().parent / 'database.sql'

# 加载环境变量
print(f"\n=== 加载环境变量 ===")
print(f"尝试加载环境变量文件：{env_path}")
if env_path.exists():
    load_dotenv(env_path, override=True)
    print("环境变量加载成功！")
else:
    print("警告：找不到 .env 文件！")
    sys.exit(1)

# 检查SQL脚本是否存在
print(f"\n=== 检查SQL脚本 ===")
print(f"SQL脚本路径：{sql_script_path}")
if not sql_script_path.exists():
    print(f"错误：SQL脚本文件 '{sql_script_path}' 不存在！")
    sys.exit(1)
print("SQL脚本文件存在！")

# 获取数据库连接参数
MYSQL_HOST = os.getenv('MYSQL_HOST', 'localhost')
MYSQL_PORT = int(os.getenv('MYSQL_PORT', '3306'))
MYSQL_USER = os.getenv('MYSQL_USER', 'root')
MYSQL_PASSWORD = os.getenv('MYSQL_PASSWORD', '')
MYSQL_DATABASE = os.getenv('MYSQL_DATABASE', 'stock_strategy')  # 默认名称设为stock_strategy

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

def execute_sql_statements(connection, statements):
    """执行SQL语句列表"""
    with connection.cursor() as cursor:
        for statement in statements:
            if statement.strip():
                try:
                    cursor.execute(statement)
                    connection.commit()
                except Exception as e:
                    print(f"执行SQL语句时出错: {e}")
                    print(f"问题语句: {statement[:100]}...")
                    raise

# 分割SQL脚本成单独的语句
def split_sql_script(script):
    """将SQL脚本分割为单独的语句"""
    # 移除注释
    script = re.sub(r'--.*?$', '', script, flags=re.MULTILINE)
    # 按分号分割语句（但要注意处理引号内的分号）
    statements = []
    statement = ""
    in_quotes = False
    quote_char = None
    
    for char in script:
        statement += char
        
        if char in ('"', "'"):
            if not in_quotes:
                in_quotes = True
                quote_char = char
            elif char == quote_char:
                in_quotes = False
                quote_char = None
        
        if char == ';' and not in_quotes:
            statements.append(statement.strip())
            statement = ""
    
    # 添加最后一个语句（如果没有以分号结尾）
    if statement.strip():
        statements.append(statement.strip())
    
    return statements

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
    
    # 执行SQL脚本创建数据库和表
    print(f"\n=== 执行SQL脚本 ===")
    print(f"正在执行SQL脚本 '{sql_script_path}'...")
    
    # 读取SQL脚本内容
    with open(sql_script_path, 'r', encoding='utf-8') as f:
        sql_script = f.read()
    
    # 分割SQL脚本
    sql_statements = split_sql_script(sql_script)
    print(f"SQL脚本已分割为 {len(sql_statements)} 个语句")
    
    # 执行创建数据库语句
    create_db_statements = [stmt for stmt in sql_statements if 'CREATE DATABASE' in stmt.upper()]
    if not create_db_statements:
        # 如果脚本中没有创建数据库的语句，我们自己添加一个
        create_db_stmt = f"CREATE DATABASE IF NOT EXISTS {MYSQL_DATABASE} DEFAULT CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;"
        execute_sql_statements(conn, [create_db_stmt])
        print(f"数据库 '{MYSQL_DATABASE}' 已创建")
    else:
        execute_sql_statements(conn, create_db_statements)
        print(f"已执行数据库创建语句")
    
    # 关闭不带数据库的连接
    conn.close()
    
    # 连接到新创建的数据库
    conn = pymysql.connect(
        host=MYSQL_HOST,
        port=MYSQL_PORT,
        user=MYSQL_USER,
        password=MYSQL_PASSWORD,
        database=MYSQL_DATABASE
    )
    
    # 执行其余语句
    remaining_statements = [stmt for stmt in sql_statements if 'CREATE DATABASE' not in stmt.upper() and 
                            'USE' not in stmt.upper().split()]
    
    print(f"执行剩余的 {len(remaining_statements)} 个SQL语句...")
    execute_sql_statements(conn, remaining_statements)
    print("所有SQL语句执行成功！")
    
    # 验证数据库和表是否创建成功
    print(f"\n=== 验证数据库 ===")
    with conn.cursor() as cursor:
        # 检查表是否存在
        cursor.execute("SHOW TABLES")
        tables = cursor.fetchall()
        print(f"数据库 '{MYSQL_DATABASE}' 中的表：")
        for table in tables:
            print(f"- {table[0]}")
    
    conn.close()
    print("数据库连接已关闭")
    
    print("\n数据库重置和初始化完成！\n")
    
except Exception as e:
    print(f"\n错误: {e}")
    sys.exit(1) 