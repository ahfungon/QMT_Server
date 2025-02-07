"""
基础配置类模块

此模块定义了所有环境通用的基础配置
"""

import os
from datetime import timedelta

class BaseConfig:
    """基础配置类"""
    # Flask配置
    JSON_AS_ASCII = False
    
    # 数据库配置
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_DATABASE_URI = (
        f"mysql+pymysql://{os.getenv('MYSQL_USER')}:{os.getenv('MYSQL_PASSWORD')}@"
        f"{os.getenv('MYSQL_HOST')}:{os.getenv('MYSQL_PORT', '3306')}/"
        f"{os.getenv('MYSQL_DATABASE')}"
    )
    
    # 日志配置
    LOG_LEVEL = 'INFO'
    LOG_FORMAT = '%(asctime)s [%(levelname)s] %(message)s'
    LOG_FILE = 'api.log'
    
    # 时区配置
    TIMEZONE = 'Asia/Shanghai'
    
    # AI配置
    AI_TYPE = os.getenv('AI_TYPE', 'zhipu')
    
    @staticmethod
    def init_app(app):
        """初始化应用"""
        pass 