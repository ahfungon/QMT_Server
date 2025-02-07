"""
响应格式化工具模块

此模块提供统一的响应格式化功能
"""

from flask import jsonify

def success_response(data=None, message="success", code=200):
    """成功响应"""
    response = {
        "code": code,
        "message": message,
        "data": data
    }
    return jsonify(response)

def error_response(message="error", code=400, data=None):
    """错误响应"""
    response = {
        "code": code,
        "message": message,
        "data": data
    }
    return jsonify(response), code 