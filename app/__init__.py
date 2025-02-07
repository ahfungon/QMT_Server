"""
应用初始化模块

此模块负责初始化Flask应用
"""

import os
from pathlib import Path
from flask import Flask
from dotenv import load_dotenv
from config import config
from .models import db
from .utils.logger import setup_logger

# 加载环境变量（确保最先加载）
env_path = Path(__file__).parent.parent / '.env'
load_dotenv(env_path, override=True)

def create_app(config_name=None):
    """创建Flask应用"""
    if config_name is None:
        config_name = os.getenv('FLASK_CONFIG', 'development')
        
    app = Flask(__name__)
    app.config.from_object(config[config_name])
    config[config_name].init_app(app)
    
    # 初始化日志
    setup_logger(app)
    
    # 初始化扩展
    db.init_app(app)
    
    # 创建数据库表
    with app.app_context():
        db.create_all()
    
    # 注册蓝图
    from .routes import strategy_bp, home_bp
    # 注册主页路由
    app.register_blueprint(home_bp)
    # 注册API路由（使用不同的名称）
    app.register_blueprint(strategy_bp, url_prefix='/api/v1', name='api_strategy')
    
    return app 