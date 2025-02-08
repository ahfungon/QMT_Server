"""
日志工具模块

此模块提供日志记录功能
"""

import logging
from logging.handlers import RotatingFileHandler
import os

def setup_logger(app):
    """配置日志记录器"""
    # 确保日志目录存在
    log_dir = 'logs'
    if not os.path.exists(log_dir):
        os.makedirs(log_dir)
    
    # 获取配置
    log_level = app.config.get('LOG_LEVEL', 'INFO')
    log_format = app.config.get('LOG_FORMAT', '%(asctime)s [%(levelname)s] %(message)s')
    log_file = os.path.join(log_dir, app.config.get('LOG_FILE', 'api.log'))
    
    # 配置日志
    formatter = logging.Formatter(log_format)
    
    # 文件处理器
    file_handler = RotatingFileHandler(
        log_file,
        maxBytes=10*1024*1024,  # 10MB
        backupCount=5,
        encoding='utf-8'
    )
    file_handler.setFormatter(formatter)
    file_handler.setLevel(logging.INFO)  # 确保文件处理器记录INFO级别及以上的日志
    
    # 控制台处理器
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(formatter)
    console_handler.setLevel(logging.INFO)  # 确保控制台处理器记录INFO级别及以上的日志
    
    # 配置根日志记录器
    root_logger = logging.getLogger()
    root_logger.setLevel(logging.INFO)  # 设置根日志记录器的级别为INFO
    
    # 移除所有现有的处理器
    for handler in root_logger.handlers[:]:
        root_logger.removeHandler(handler)
    
    # 添加新的处理器
    root_logger.addHandler(file_handler)
    root_logger.addHandler(console_handler)
    
    # 配置 SQLAlchemy 日志
    logging.getLogger('sqlalchemy.engine').setLevel(logging.WARNING)
    
    return root_logger 