"""
数据模型包

此包包含所有数据库模型定义
"""

from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

from .stock import StockStrategy 