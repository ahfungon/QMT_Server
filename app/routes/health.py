"""
健康检查路由模块

此模块提供健康检查相关的API接口
"""

from flask import Blueprint, jsonify, current_app
from datetime import datetime, timedelta
import time
import platform
import os

# 记录服务启动时间
START_TIME = time.time()
VERSION = "1.0.0"  # 服务版本号

# 创建两个蓝图，一个用于API路径，一个用于根路径
health_bp = Blueprint('health', __name__, url_prefix='/api/v1')
root_health_bp = Blueprint('root_health', __name__)

@health_bp.route('/health', methods=['GET'])
def health_check():
    """
    健康检查接口
    
    Returns:
        JSON响应，包含服务状态信息
    """
    # 计算服务运行时间
    uptime_seconds = time.time() - START_TIME
    uptime_delta = timedelta(seconds=int(uptime_seconds))
    
    # 格式化运行时间为 "XXh XXm XXs" 格式
    hours, remainder = divmod(uptime_delta.total_seconds(), 3600)
    minutes, seconds = divmod(remainder, 60)
    uptime_str = f"{int(hours)}h {int(minutes)}m {int(seconds)}s"
    
    # 获取当前时间的ISO格式
    current_time = datetime.utcnow().strftime('%Y-%m-%dT%H:%M:%SZ')
    
    # 构建响应数据
    response_data = {
        "status": "ok",
        "version": VERSION,
        "uptime": uptime_str,
        "timestamp": current_time,
        "system_info": {
            "python_version": platform.python_version(),
            "platform": platform.platform(),
            "process_id": os.getpid()
        }
    }
    
    return jsonify(response_data), 200

@health_bp.route('/ping', methods=['GET'])
def ping():
    """
    简单的ping接口
    
    Returns:
        JSON响应，包含pong消息和时间戳
    """
    current_time = datetime.utcnow().strftime('%Y-%m-%dT%H:%M:%SZ')
    
    return jsonify({
        "message": "pong",
        "timestamp": current_time
    }), 200

# 添加根路径的健康检查接口
@root_health_bp.route('/health', methods=['GET'])
def root_health_check():
    """
    根路径的健康检查接口
    
    Returns:
        JSON响应，包含服务状态信息
    """
    return health_check()

@root_health_bp.route('/ping', methods=['GET'])
def root_ping():
    """
    根路径的ping接口
    
    Returns:
        JSON响应，包含pong消息和时间戳
    """
    return ping()

@root_health_bp.route('/', methods=['GET'])
def root():
    """
    根路径接口
    
    Returns:
        简单的JSON响应，表示服务正在运行
    """
    return jsonify({
        "status": "running",
        "message": "QMT Server is running",
        "timestamp": datetime.utcnow().strftime('%Y-%m-%dT%H:%M:%SZ')
    }), 200 