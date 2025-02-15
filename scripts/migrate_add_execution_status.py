"""
数据库迁移脚本 - 添加执行状态字段

此脚本用于为 stock_strategies 表添加 execution_status 字段
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

def migrate_database():
    """执行数据库迁移"""
    print("正在执行数据库迁移...")
    
    # 加载环境变量
    env_path = Path(__file__).parent.parent / '.env'
    load_dotenv(env_path, override=True)
    
    try:
        # 连接数据库
        conn = pymysql.connect(
            host=os.getenv('MYSQL_HOST'),
            port=int(os.getenv('MYSQL_PORT', 3306)),
            user=os.getenv('MYSQL_USER'),
            password=os.getenv('MYSQL_PASSWORD'),
            database=os.getenv('MYSQL_DATABASE'),
            charset='utf8mb4'
        )
        
        with conn.cursor() as cursor:
            # 检查字段是否已存在
            cursor.execute("""
                SELECT COUNT(*)
                FROM information_schema.COLUMNS 
                WHERE TABLE_SCHEMA = %s
                AND TABLE_NAME = 'stock_strategies'
                AND COLUMN_NAME = 'execution_status'
            """, (os.getenv('MYSQL_DATABASE'),))
            
            if cursor.fetchone()[0] == 0:
                # 添加执行状态字段
                print("添加 execution_status 字段...")
                cursor.execute("""
                    ALTER TABLE stock_strategies
                    ADD COLUMN execution_status ENUM('pending', 'completed', 'partial')
                    NOT NULL DEFAULT 'pending'
                    COMMENT '执行状态：未执行、已全部执行、已部分执行'
                    AFTER reason
                """)
                
                # 添加索引
                print("添加索引...")
                cursor.execute("""
                    ALTER TABLE stock_strategies
                    ADD INDEX idx_execution_status (execution_status)
                """)
                
                # 更新现有记录的状态
                print("更新现有记录状态...")
                cursor.execute("""
                    UPDATE stock_strategies s
                    LEFT JOIN (
                        SELECT 
                            strategy_id,
                            COUNT(*) as exec_count,
                            SUM(CASE WHEN execution_result = 'success' THEN 1 ELSE 0 END) as success_count,
                            SUM(CASE WHEN execution_result = 'partial' THEN 1 ELSE 0 END) as partial_count
                        FROM strategy_executions
                        GROUP BY strategy_id
                    ) e ON s.id = e.strategy_id
                    SET s.execution_status = 
                        CASE 
                            WHEN e.strategy_id IS NULL THEN 'pending'
                            WHEN e.success_count > 0 THEN 'completed'
                            WHEN e.partial_count > 0 THEN 'partial'
                            ELSE 'pending'
                        END
                """)
                
                conn.commit()
                print("数据库迁移完成！")
            else:
                print("execution_status 字段已存在，无需迁移。")
        
        conn.close()
        
    except Exception as e:
        print(f"迁移过程中出错：{e}")
        return

if __name__ == '__main__':
    migrate_database() 