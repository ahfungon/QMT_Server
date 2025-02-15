"""
配置加载模块

此模块负责加载不同环境的配置
"""

from .development import DevelopmentConfig
from .production import ProductionConfig
from .testing import TestingConfig

# 配置映射字典
config = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'testing': TestingConfig,
    'default': DevelopmentConfig
} 