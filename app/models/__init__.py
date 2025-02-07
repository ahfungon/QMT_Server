"""
数据模型包

此包包含所有数据库模型定义
"""

from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

# 导入所有模型
from .stock import StockStrategy

# 导出所有模型
__all__ = ['db', 'StockStrategy'] 