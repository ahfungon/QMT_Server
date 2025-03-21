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
import logging
from sqlalchemy import text

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
    
    # 配置CORS - 使用最简单的配置
    CORS(app)
    
    # 设置安全头部
    @app.after_request
    def add_security_headers(response):
        response.headers['Access-Control-Allow-Origin'] = '*'
        response.headers['Access-Control-Allow-Methods'] = 'GET, POST, PUT, DELETE, OPTIONS'
        response.headers['Access-Control-Allow-Headers'] = 'Content-Type'
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
        try:
            # 获取数据库连接参数（直接从环境变量获取，避免通过配置读取）
            MYSQL_HOST = os.getenv('MYSQL_HOST', 'localhost')
            MYSQL_PORT = os.getenv('MYSQL_PORT', '3306')
            MYSQL_USER = os.getenv('MYSQL_USER', 'root')
            MYSQL_PASSWORD = os.getenv('MYSQL_PASSWORD', '')
            MYSQL_DATABASE = os.getenv('MYSQL_DATABASE', '')
            
            # 打印一下环境变量检查
            logging.info(f"数据库连接参数: HOST={MYSQL_HOST}, PORT={MYSQL_PORT}, USER={MYSQL_USER}, DB={MYSQL_DATABASE}")
            
            # 尝试创建数据库（如果不存在）
            database_name = MYSQL_DATABASE
            
            # 创建到 MySQL 服务器的连接（不指定数据库）
            base_url = f"mysql+pymysql://{MYSQL_USER}:{MYSQL_PASSWORD}@{MYSQL_HOST}:{MYSQL_PORT}"
            logging.info(f"基础连接URL: {base_url}")
            engine_without_db = db.create_engine(base_url)
            
            # 检查数据库是否存在
            with engine_without_db.connect() as conn:
                # 使用 text() 包装 SQL 语句
                result = conn.execute(text(
                    f"SELECT SCHEMA_NAME FROM INFORMATION_SCHEMA.SCHEMATA WHERE SCHEMA_NAME = '{database_name}'"
                ))
                database_exists = result.scalar() is not None
                
                # 只有在数据库不存在时才创建
                if not database_exists:
                    logging.info(f"数据库 {database_name} 不存在，正在创建...")
                    conn.execute(text(
                        f"CREATE DATABASE IF NOT EXISTS {database_name} "
                        "DEFAULT CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci"
                    ))
                    conn.commit()
                    logging.info(f"数据库 {database_name} 创建成功！")
                else:
                    logging.info(f"数据库 {database_name} 已存在，跳过创建步骤。")
            
            # 关闭不带数据库的连接
            engine_without_db.dispose()
            
            # 创建或更新表结构
            db.create_all()
            logging.info("数据库表结构检查/更新完成！")
            
        except Exception as e:
            logging.error(f"数据库初始化失败: {str(e)}")
            raise
    
    # 注册蓝图
    from .routes import strategy_bp, execution_bp, home_bp, position_bp, account_bp, health_bp, root_health_bp
    app.register_blueprint(home_bp)
    app.register_blueprint(strategy_bp, url_prefix='/api/v1')
    app.register_blueprint(execution_bp, url_prefix='/api/v1')
    app.register_blueprint(position_bp, url_prefix='/api/v1')
    app.register_blueprint(account_bp, url_prefix='/api/v1')
    app.register_blueprint(health_bp)
    app.register_blueprint(root_health_bp)
    
    # 启动股价自动更新
    from .tasks.price_updater import PriceUpdater
    price_updater = PriceUpdater(app=app)  # 移除固定的interval参数，使用自动调整的更新间隔
    price_updater.start()
    app.price_updater = price_updater  # 保存到应用实例中，方便后续管理
    
    return app 