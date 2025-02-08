"""
装饰器工具模块

此模块提供各种装饰器功能
"""

import logging
from functools import wraps
from flask import jsonify

logger = logging.getLogger(__name__)

def handle_exceptions(func):
    """
    异常处理装饰器
    
    捕获并处理路由函数中的异常，返回统一的错误响应格式
    """
    @wraps(func)
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except ValueError as e:
            logger.warning(f"参数验证错误: {str(e)}")
            return jsonify({
                'code': 400,
                'message': str(e),
                'data': None
            }), 400
        except Exception as e:
            logger.error(f"服务器错误: {str(e)}", exc_info=True)
            return jsonify({
                'code': 500,
                'message': f"服务器内部错误: {str(e)}",
                'data': None
            }), 500
    return wrapper 