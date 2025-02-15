"""
主页路由模块

此模块提供主页相关的路由
"""

import logging
from flask import Blueprint, render_template, current_app
from ..services.strategy import StrategyService

logger = logging.getLogger(__name__)

# 创建蓝图
home_bp = Blueprint('home', __name__)

@home_bp.route('/')
def index():
    """渲染主页"""
    try:
        # 获取策略列表
        strategy_service = StrategyService()
        strategies = strategy_service.get_all_strategies()
        
        # 渲染模板
        return render_template('index.html', strategies=strategies)
    except Exception as e:
        logger.error(f"渲染主页失败: {str(e)}")
        return render_template('error.html', error=str(e)), 500

@home_bp.app_errorhandler(403)
def forbidden(e):
    """403错误处理"""
    current_app.logger.warning(f"403错误: {str(e)}")
    return render_template('error.html', error="您没有访问权限"), 403

@home_bp.app_errorhandler(404)
def not_found(e):
    """404错误处理"""
    current_app.logger.warning(f"404错误: {str(e)}")
    return render_template('error.html', error="页面不存在"), 404

@home_bp.app_errorhandler(500)
def internal_server_error(e):
    """500错误处理"""
    current_app.logger.error(f"500错误: {str(e)}", exc_info=True)
    return render_template('error.html', error="服务器内部错误"), 500 