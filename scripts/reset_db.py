"""
数据库重置脚本

此脚本用于重置数据库，会删除已存在的数据库并重新执行初始化脚本
"""

import os
import sys
from pathlib import Path

# 添加项目根目录到 Python 路径
project_root = Path(__file__).parent.parent
sys.path.append(str(project_root))

from dotenv import load_dotenv
import pymysql
import logging

# 设置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)
logger = logging.getLogger(__name__)

def reset_database():
    """重置数据库"""
    logger.info("开始重置数据库...")
    
    # 加载环境变量
    env_path = Path(__file__).parent.parent / '.env'
    load_dotenv(env_path, override=True)
    
    conn = None
    try:
        # 连接 MySQL（不指定数据库）
        conn = pymysql.connect(
            host=os.getenv('MYSQL_HOST'),
            port=int(os.getenv('MYSQL_PORT', 3306)),
            user=os.getenv('MYSQL_USER'),
            password=os.getenv('MYSQL_PASSWORD'),
            charset='utf8mb4'
        )
        
        database_name = os.getenv('MYSQL_DATABASE')
        
        with conn.cursor() as cursor:
            # 检查数据库是否存在
            cursor.execute(
                "SELECT SCHEMA_NAME FROM INFORMATION_SCHEMA.SCHEMATA WHERE SCHEMA_NAME = %s",
                (database_name,)
            )
            
            if cursor.fetchone():
                logger.info(f"数据库 {database_name} 已存在，正在删除...")
                cursor.execute(f"DROP DATABASE {database_name}")
                logger.info(f"数据库 {database_name} 删除成功！")
            
            # 读取初始化 SQL 文件
            sql_file_path = project_root / 'scripts' / 'database.sql'
            if not sql_file_path.exists():
                raise FileNotFoundError(f"找不到初始化文件：{sql_file_path}")
            
            logger.info("正在执行数据库初始化脚本...")
            with open(sql_file_path, 'r', encoding='utf-8') as f:
                sql_content = f.read()
            
            # 执行 SQL 脚本
            for statement in sql_content.split(';'):
                statement = statement.strip()
                if statement:  # 忽略空语句
                    try:
                        cursor.execute(statement)
                        conn.commit()
                    except Exception as e:
                        logger.error(f"执行 SQL 语句失败: {statement}")
                        logger.error(f"错误信息: {str(e)}")
                        raise
            
            logger.info("数据库初始化完成！")
            
            # 显示创建的表
            cursor.execute(f"USE {database_name}")
            cursor.execute("SHOW TABLES")
            tables = cursor.fetchall()
            logger.info("创建的表：")
            for table in tables:
                logger.info(f"- {table[0]}")
        
        logger.info("数据库重置成功！")
        
    except Exception as e:
        logger.error(f"重置数据库失败: {str(e)}")
        raise
    finally:
        if conn:
            try:
                conn.close()
            except:
                pass  # 忽略关闭连接时的错误

if __name__ == '__main__':
    reset_database() 