"""
测试环境配置模块

此模块定义了测试环境特定的配置
"""

from .base import BaseConfig
import os

class TestingConfig(BaseConfig):
    """测试环境配置类"""
    # Flask配置
    TESTING = True
    DEBUG = False
    
    # 使用现有数据库
    SQLALCHEMY_DATABASE_URI = (
        f"mysql+pymysql://{os.getenv('MYSQL_USER')}:{os.getenv('MYSQL_PASSWORD')}@"
        f"{os.getenv('MYSQL_HOST')}:{os.getenv('MYSQL_PORT', '3306')}/"
        f"{os.getenv('MYSQL_DATABASE')}?charset=utf8mb4"
    )
    
    # 日志配置
    LOG_LEVEL = 'DEBUG'
    LOG_FILE = 'test.log' 