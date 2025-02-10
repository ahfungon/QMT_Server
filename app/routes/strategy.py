"""
策略路由模块

此模块定义了所有与策略相关的路由
"""

import logging
from flask import Blueprint, request, render_template, jsonify
from ..services.strategy import StrategyService
from ..utils.response import success_response, error_response
from ..utils.decorators import handle_exceptions
from ..models import StockStrategy

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
@handle_exceptions
def get_strategies():
    """获取策略列表"""
    try:
        log_request_info(request)
        
        # 获取排序参数，默认按更新时间降序
        sort_by = request.args.get('sort_by', 'updated_at')  # 可选值: updated_at, created_at
        order = request.args.get('order', 'desc')  # 可选值: desc, asc
        
        # 获取策略列表
        strategies = strategy_service.get_all_strategies(sort_by, order)
        
        # 记录详细日志
        logger.info("获取所有策略列表（排序规则：1.是否有效 2.更新时间 3.创建时间）:")
        logger.info("-"*50)
        for strategy in strategies:
            logger.info(
                f"ID: {strategy['id']:3d} | "
                f"名称: {strategy['stock_name']:10s} | "
                f"代码: {strategy['stock_code']:6s} | "
                f"是否有效: {'是' if strategy['is_active'] else '否'} | "
                f"创建时间: {strategy['created_at']} | "
                f"更新时间: {strategy['updated_at']}"
            )
        logger.info("-"*50)
        logger.info(f"共获取到 {len(strategies)} 条记录")
        logger.info("="*50)
        
        response_data = {
            'code': 200,
            'message': 'success',
            'data': strategies
        }
        return jsonify(response_data)
        
    except Exception as e:
        error_data = {
            'code': 500,
            'message': str(e),
            'data': None
        }
        logger.error(f"获取策略列表失败: {str(e)}", exc_info=True)
        return jsonify(error_data), 500

@strategy_bp.route('/strategies', methods=['POST'])
def create_strategy():
    """创建策略"""
    try:
        log_request_info(request)
        
        data = request.get_json()
        
        # 验证必要字段
        if not data.get('action'):
            response = error_response('交易动作不能为空', 400)
            log_response_info(response.get_json())
            return response
            
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
        if not data:
            response_data = {
                'code': 400,
                'message': '请求数据为空',
                'data': None
            }
            log_response_info(response_data)
            return jsonify(response_data), 400
            
        strategy = strategy_service.update_strategy(id, data)
        response_data = {
            'code': 200,
            'message': '策略更新成功',
            'data': strategy
        }
        log_response_info(response_data)
        return jsonify(response_data)
        
    except ValueError as e:
        response_data = {
            'code': 400,
            'message': str(e),
            'data': None
        }
        log_response_info(response_data)
        return jsonify(response_data), 400
        
    except Exception as e:
        response_data = {
            'code': 500,
            'message': f'更新策略失败: {str(e)}',
            'data': None
        }
        logger.error(f"更新策略失败: {str(e)}", exc_info=True)
        log_response_info(response_data)
        return jsonify(response_data), 500

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

@strategy_bp.route('/strategies/<int:id>/activate', methods=['POST'])
def activate_strategy(id):
    """设置策略为有效"""
    try:
        log_request_info(request)
        
        strategy = strategy_service.activate_strategy(id)
        response = success_response(strategy, '策略已设置为有效')
        log_response_info(response.get_json())
        return response
        
    except Exception as e:
        response = error_response(f'设置策略有效失败: {str(e)}', 500)
        log_response_info(response.get_json())
        return response

@strategy_bp.route('/strategies/search', methods=['GET'])
def search_strategies():
    """高级查询策略列表"""
    try:
        log_request_info(request)
        
        # 获取查询参数
        params = {
            'start_time': request.args.get('start_time'),
            'end_time': request.args.get('end_time'),
            'stock_code': request.args.get('stock_code'),
            'stock_name': request.args.get('stock_name'),
            'action': request.args.get('action'),
            'sort_by': request.args.get('sort_by', 'updated_at'),
            'order': request.args.get('order', 'desc'),
            'is_active': None if request.args.get('is_active') is None else request.args.get('is_active').lower() == 'true'
        }
        
        # 调用服务层方法
        strategies = strategy_service.search_strategies(**params)
        
        response = success_response(strategies)
        log_response_info(response.get_json())
        return response
        
    except Exception as e:
        response = error_response(f'查询策略列表失败: {str(e)}', 500)
        log_response_info(response.get_json())
        return response

@strategy_bp.route('/strategies/<int:id>', methods=['GET'])
@handle_exceptions
def get_strategy(id):
    """获取单个策略"""
    try:
        strategy = StockStrategy.query.get_or_404(id)
        return success_response(strategy.to_dict())
    except Exception as e:
        logger.error(f"获取策略失败: {str(e)}", exc_info=True)
        return error_response("获取策略失败", code=500) 