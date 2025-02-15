"""
路由包

此包包含所有路由定义
"""

from .strategy import strategy_bp
from .home import home_bp
from .execution import execution_bp
from .position import position_bp

# 导出所有蓝图
__all__ = ['strategy_bp', 'home_bp', 'execution_bp', 'position_bp'] 