"""
策略路由模块

此模块定义了所有与策略相关的路由
"""

import logging
from flask import Blueprint, request, render_template, jsonify
from ..services.strategy import StrategyService
from ..utils.response import success_response, error_response

# 创建蓝图
strategy_bp = Blueprint('strategy', __name__)
strategy_service = StrategyService()
logger = logging.getLogger(__name__)

def log_request_info(request):
    """记录请求信息"""
    logger.info("="*50)
    logger.info(f"请求路径: {request.path}")
    logger.info(f"请求方法: {request.method}")
    logger.info(f"请求头: {dict(request.headers)}")
    if request.is_json:
        logger.info(f"请求体: {request.get_json()}")
    logger.info("-"*50)

def log_response_info(response_data):
    """记录响应信息"""
    # 如果是获取列表的接口，只记录数量
    if isinstance(response_data.get('data'), list):
        log_data = {
            'code': response_data['code'],
            'message': response_data['message'],
            'data_count': len(response_data['data'])
        }
        logger.info(f"响应数据: 状态码={log_data['code']}, 消息={log_data['message']}, 数据条数={log_data['data_count']}")
    else:
        # 其他接口记录完整信息，但不包含具体数据
        log_data = {
            'code': response_data['code'],
            'message': response_data['message'],
            'has_data': response_data.get('data') is not None
        }
        logger.info(f"响应数据: {log_data}")
    logger.info("="*50)

@strategy_bp.route('/analyze_strategy', methods=['POST'])
def analyze_strategy():
    """分析策略接口"""
    try:
        log_request_info(request)
        
        data = request.get_json()
        if not data or 'strategy_text' not in data:
            response_data = {
                'code': 400,
                'message': '缺少策略文本',
                'data': None
            }
            log_response_info(response_data)
            return jsonify(response_data), 400

        result = strategy_service.analyze_strategy(data['strategy_text'])
        
        # 如果返回错误信息，直接返回
        if 'error' in result:
            response_data = {
                'code': 400,
                'message': result['error'],
                'data': None
            }
            log_response_info(response_data)
            return jsonify(response_data), 400
            
        response_data = {
            'code': 200,
            'message': '策略分析成功',
            'data': result
        }
        log_response_info(response_data)
        return jsonify(response_data)
        
    except Exception as e:
        error_response = {
            'code': 500,
            'message': f'策略分析失败: {str(e)}',
            'data': None
        }
        logger.error(f"策略分析失败: {str(e)}", exc_info=True)
        log_response_info(error_response)
        return jsonify(error_response), 500

@strategy_bp.route('/strategies', methods=['GET'])
def get_strategies():
    """获取策略列表"""
    try:
        log_request_info(request)
        
        strategies = strategy_service.get_all_strategies()
        response = success_response(strategies)
        log_response_info(response.get_json())
        return response
        
    except Exception as e:
        response = error_response(str(e))
        log_response_info(response.get_json())
        return response

@strategy_bp.route('/strategies', methods=['POST'])
def create_strategy():
    """创建策略"""
    try:
        log_request_info(request)
        
        data = request.get_json()
        strategy = strategy_service.create_strategy(data)
        response = success_response(strategy)
        log_response_info(response.get_json())
        return response
        
    except Exception as e:
        response = error_response(str(e))
        log_response_info(response.get_json())
        return response

@strategy_bp.route('/strategies/<int:id>', methods=['PUT'])
def update_strategy(id):
    """更新策略"""
    try:
        log_request_info(request)
        
        data = request.get_json()
        strategy = strategy_service.update_strategy(id, data)
        response = success_response(strategy)
        log_response_info(response.get_json())
        return response
        
    except Exception as e:
        response = error_response(str(e))
        log_response_info(response.get_json())
        return response

@strategy_bp.route('/strategies/check', methods=['POST'])
def check_strategy():
    """检查策略是否存在"""
    try:
        log_request_info(request)
        
        data = request.get_json()
        if not all(k in data for k in ['stock_name', 'stock_code', 'action']):
            return error_response('缺少必要参数', 400)

        strategy = strategy_service.check_strategy_exists(
            data['stock_name'],
            data['stock_code'],
            data['action']
        )
        
        response = success_response(strategy)
        log_response_info(response.get_json())
        return response
        
    except Exception as e:
        response = error_response(f'检查策略失败: {str(e)}', 500)
        log_response_info(response.get_json())
        return response

@strategy_bp.route('/strategies/update', methods=['POST'])
def update_strategy_by_key():
    """根据关键字段更新策略"""
    try:
        log_request_info(request)
        
        data = request.get_json()
        if not all(k in data for k in ['stock_name', 'stock_code', 'action']):
            return error_response('缺少必要参数', 400)

        strategy = strategy_service.update_strategy_by_key(data)
        response = success_response(strategy, '策略更新成功')
        log_response_info(response.get_json())
        return response
        
    except ValueError as e:
        response = error_response(str(e), 404)
        log_response_info(response.get_json())
        return response
    except Exception as e:
        response = error_response(f'更新策略失败: {str(e)}', 500)
        log_response_info(response.get_json())
        return response

@strategy_bp.route('/strategies/<int:id>/deactivate', methods=['POST'])
def deactivate_strategy(id):
    """设置策略为失效"""
    try:
        log_request_info(request)
        
        strategy = strategy_service.deactivate_strategy(id)
        response = success_response(strategy, '策略已设置为失效')
        log_response_info(response.get_json())
        return response
        
    except Exception as e:
        response = error_response(f'设置策略失效失败: {str(e)}', 500)
        log_response_info(response.get_json())
        return response 