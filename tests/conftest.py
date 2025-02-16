"""
测试配置模块

此模块提供测试所需的fixture和配置
"""

import os
import sys
from pathlib import Path
import pytest
from dotenv import load_dotenv

# 添加项目根目录到 Python 路径
project_root = Path(__file__).parent.parent
sys.path.append(str(project_root))

# 加载环境变量
env_path = project_root / '.env'
load_dotenv(env_path, override=True)

from app import create_app
from app.models import db as _db

@pytest.fixture(scope='session')
def app():
    """创建测试应用"""
    os.environ['FLASK_CONFIG'] = 'development'  # 使用开发环境配置
    app = create_app()
    
    # 创建数据库表
    with app.app_context():
        _db.create_all()
        
    return app

@pytest.fixture(scope='session')
def client(app):
    """创建测试客户端"""
    return app.test_client()

@pytest.fixture(scope='session')
def db(app):
    """提供数据库会话"""
    return _db

@pytest.fixture(scope='function')
def session(db):
    """提供数据库事务"""
    connection = db.engine.connect()
    transaction = connection.begin()
    
    session = db.create_scoped_session(
        options={"bind": connection, "binds": {}}
    )
    db.session = session
    
    yield session
    
    # 回滚事务而不是提交，这样不会影响数据库
    transaction.rollback()
    connection.close()
    session.remove() 