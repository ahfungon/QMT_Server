"""
开发环境配置模块

此模块定义了开发环境特定的配置
"""

from .base import BaseConfig

class DevelopmentConfig(BaseConfig):
    """开发环境配置类"""
    # Flask配置
    DEBUG = True
    TESTING = False
    
    # 日志配置
    LOG_LEVEL = 'DEBUG'
    LOG_FILE = 'dev.log' 