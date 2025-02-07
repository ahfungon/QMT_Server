"""
生产环境配置模块

此模块定义了生产环境特定的配置
"""

from .base import BaseConfig

class ProductionConfig(BaseConfig):
    """生产环境配置类"""
    # Flask配置
    DEBUG = False
    TESTING = False
    
    # 日志配置
    LOG_LEVEL = 'INFO'
    LOG_FILE = 'production.log'
    
    # 数据库连接池配置
    SQLALCHEMY_POOL_SIZE = 10
    SQLALCHEMY_MAX_OVERFLOW = 20 