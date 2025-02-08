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
from flask_cors import CORS
from datetime import timedelta

# 加载环境变量（确保最先加载）
env_path = Path(__file__).parent.parent / '.env'
load_dotenv(env_path, override=True)

def create_app(config_name=None):
    """
    创建并配置Flask应用
    """
    if config_name is None:
        config_name = os.getenv('FLASK_CONFIG', 'development')
        
    # 创建Flask应用实例
    app = Flask(__name__,
                static_folder=os.path.join(os.path.dirname(os.path.dirname(__file__)), 'app', 'static'),
                template_folder=os.path.join(os.path.dirname(os.path.dirname(__file__)), 'app', 'templates'))
    
    # 加载配置
    app.config.from_object(config[config_name])
    config[config_name].init_app(app)
    
    # 配置CORS
    CORS(app, resources={
        r"/*": {
            "origins": ["http://localhost:5000"],
            "methods": ["GET", "POST", "PUT", "DELETE", "OPTIONS"],
            "allow_headers": ["Content-Type"]
        }
    })
    
    # 设置安全头部
    @app.after_request
    def add_security_headers(response):
        response.headers['X-Content-Type-Options'] = 'nosniff'
        response.headers['X-Frame-Options'] = 'SAMEORIGIN'
        response.headers['X-XSS-Protection'] = '1; mode=block'
        return response
    
    # 初始化日志
    setup_logger(app)
    
    # 初始化扩展
    db.init_app(app)
    
    # 创建数据库表
    with app.app_context():
        db.create_all()
    
    # 注册蓝图
    from .routes import strategy_bp, execution_bp, home_bp
    app.register_blueprint(home_bp)
    app.register_blueprint(strategy_bp, url_prefix='/api/v1')
    app.register_blueprint(execution_bp, url_prefix='/api/v1')
    
    return app 