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
    
    # 控制台处理器
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(formatter)
    
    # 配置根日志记录器
    root_logger = logging.getLogger()
    root_logger.setLevel(log_level)
    root_logger.addHandler(file_handler)
    root_logger.addHandler(console_handler)
    
    return root_logger 