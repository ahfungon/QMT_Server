"""
数据库模型包

此包包含所有数据库模型定义
"""

from flask_sqlalchemy import SQLAlchemy

# 初始化数据库
db = SQLAlchemy()

# 导入所有模型
from .stock import StockStrategy
from .execution import StrategyExecution

# 导出所有模型
__all__ = ['db', 'StockStrategy', 'StrategyExecution'] 