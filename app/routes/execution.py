"""
策略执行记录路由模块

此模块提供策略执行记录相关的API路由
"""

import logging
from flask import Blueprint, request, jsonify, current_app
from typing import Dict, Any
from ..services.execution import ExecutionService
from ..utils.response import success_response, error_response
from ..utils.decorators import handle_exceptions
from ..models import db, StrategyExecution

# 创建蓝图
execution_bp = Blueprint('execution', __name__)
execution_service = ExecutionService()
logger = logging.getLogger(__name__)


@execution_bp.route('/executions', methods=['POST'])
@handle_exceptions
def create_execution():
    """创建策略执行记录"""
    try:
        data = request.get_json()
        result = execution_service.create_execution(data)
        return success_response(data=result, message="创建执行记录成功")
    except ValueError as e:
        return error_response(str(e), code=400)
    except Exception as e:
        logger.error(f"创建执行记录失败: {str(e)}", exc_info=True)
        return error_response("创建执行记录失败", code=500)


@execution_bp.route('/executions/<int:execution_id>', methods=['GET'])
@handle_exceptions
def get_execution(execution_id: int):
    """获取单个执行记录"""
    try:
        result = execution_service.get_execution(execution_id)
        if result is None:
            return error_response("执行记录不存在", code=404)
        return success_response(data=result)
    except Exception as e:
        logger.error(f"获取执行记录失败: {str(e)}", exc_info=True)
        return error_response("获取执行记录失败", code=500)


@execution_bp.route('/executions', methods=['GET'])
@handle_exceptions
def get_executions():
    """查询执行记录列表"""
    try:
        # 获取查询参数
        strategy_id = request.args.get('strategy_id', type=int)
        stock_code = request.args.get('stock_code', type=str)
        start_time = request.args.get('start_time', type=str)
        end_time = request.args.get('end_time', type=str)
        action = request.args.get('action', type=str)
        result = request.args.get('result', type=str)
        sort_by = request.args.get('sort_by', 'execution_time', type=str)
        order = request.args.get('order', 'desc', type=str)
        
        results = execution_service.get_executions(
            strategy_id=strategy_id,
            stock_code=stock_code,
            start_time=start_time,
            end_time=end_time,
            action=action,
            result=result,
            sort_by=sort_by,
            order=order
        )
        return success_response(data=results)
    except Exception as e:
        logger.error(f"查询执行记录列表失败: {str(e)}", exc_info=True)
        return error_response("查询执行记录列表失败", code=500)


@execution_bp.route('/executions/<int:execution_id>', methods=['PUT'])
@handle_exceptions
def update_execution(execution_id: int):
    """更新执行记录"""
    try:
        data = request.get_json()
        result = execution_service.update_execution(execution_id, data)
        return success_response(data=result, message="更新执行记录成功")
    except Exception as e:
        logger.error(f"更新执行记录失败: {str(e)}", exc_info=True)
        return error_response("更新执行记录失败", code=500)


@execution_bp.route('/executions/<int:execution_id>', methods=['DELETE'])
@handle_exceptions
def delete_execution(execution_id: int):
    """删除执行记录"""
    try:
        execution_service.delete_execution(execution_id)
        return success_response(message="删除执行记录成功")
    except Exception as e:
        logger.error(f"删除执行记录失败: {str(e)}", exc_info=True)
        return error_response("删除执行记录失败", code=500)


@execution_bp.route('/executions/batch', methods=['POST'])
def batch_get_executions():
    """
    批量获取多个策略的执行记录
    
    请求参数：
    - strategy_ids: list[int] 策略ID列表
    - limit: int 可选，每个策略返回的记录数限制
    
    返回数据：
    {
        strategy_id: [
            {
                execution_id: int,
                strategy_id: int,
                execution_time: str,
                execution_price: float,
                volume: int,
                execution_result: str,
                created_at: str
            },
            ...
        ],
        ...
    }
    """
    try:
        data = request.get_json()
        if not data or 'strategy_ids' not in data:
            return jsonify({
                'code': 400,
                'message': '缺少必要的参数：strategy_ids'
            })
        
        strategy_ids = data.get('strategy_ids', [])
        limit = data.get('limit')
        
        if not isinstance(strategy_ids, list):
            return jsonify({
                'code': 400,
                'message': 'strategy_ids必须是一个列表'
            })
        
        result = {}
        for strategy_id in strategy_ids:
            query = db.session.query(StrategyExecution).filter(
                StrategyExecution.strategy_id == strategy_id
            ).order_by(StrategyExecution.execution_time.desc())
            
            if limit:
                query = query.limit(limit)
            
            executions = query.all()
            result[strategy_id] = [
                {
                    'execution_id': execution.execution_id,
                    'strategy_id': execution.strategy_id,
                    'execution_time': execution.execution_time.strftime('%Y-%m-%d %H:%M:%S'),
                    'execution_price': execution.execution_price,
                    'volume': execution.volume,
                    'execution_result': execution.execution_result,
                    'created_at': execution.created_at.strftime('%Y-%m-%d %H:%M:%S')
                }
                for execution in executions
            ]
        
        return jsonify({
            'code': 200,
            'message': '获取成功',
            'data': result
        })
        
    except Exception as e:
        current_app.logger.error(f'批量获取执行记录失败：{str(e)}')
        return jsonify({
            'code': 500,
            'message': f'服务器错误：{str(e)}'
        }) 