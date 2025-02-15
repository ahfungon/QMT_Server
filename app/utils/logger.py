"""
日志工具模块

此模块提供日志相关的工具函数
"""

import os
import logging
from logging.handlers import RotatingFileHandler
from pathlib import Path

def setup_logger(name_or_app, level=logging.INFO):
    """
    设置日志记录器
    
    Args:
        name_or_app: 日志记录器名称或 Flask 应用实例
        level: 日志级别，默认为 INFO
        
    Returns:
        logging.Logger: 配置好的日志记录器
    """
    # 如果传入的是 Flask 应用实例，从配置中获取日志级别
    if hasattr(name_or_app, 'config'):
        app = name_or_app
        name = app.import_name
        level = getattr(logging, app.config.get('LOG_LEVEL', 'INFO'))
    else:
        name = name_or_app
    
    # 创建日志记录器
    logger = logging.getLogger(name)
    logger.setLevel(level)
    
    # 如果已经有处理器，说明已经配置过，直接返回
    if logger.handlers:
        return logger
    
    # 创建日志目录
    log_dir = Path(__file__).parent.parent.parent / 'logs'
    log_dir.mkdir(exist_ok=True)
    
    # 创建文件处理器
    log_file = log_dir / f'{name}.log'
    file_handler = RotatingFileHandler(
        log_file,
        maxBytes=10 * 1024 * 1024,  # 10MB
        backupCount=5,
        encoding='utf-8'
    )
    
    # 创建控制台处理器
    console_handler = logging.StreamHandler()
    
    # 设置日志格式
    formatter = logging.Formatter(
        '%(asctime)s [%(levelname)s] %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    
    # 应用格式化器
    file_handler.setFormatter(formatter)
    console_handler.setFormatter(formatter)
    
    # 添加处理器
    logger.addHandler(file_handler)
    logger.addHandler(console_handler)
    
    return logger 