"""
持仓相关路由模块

此模块提供持仓查询和更新的API接口
"""

from flask import Blueprint, jsonify, request, current_app
from ..models import StockPosition, db
from ..services.position import PositionService
from ..utils.logger import setup_logger
from datetime import datetime

position_bp = Blueprint('position', __name__, url_prefix='/api/v1')
logger = setup_logger('position')
position_service = PositionService()

@position_bp.route('/positions', methods=['GET'])
def get_positions():
    """
    获取所有持仓信息
    
    Returns:
        JSON响应，包含所有持仓信息
    """
    try:
        logger.info("【前端触发】开始获取所有持仓信息...")
        # 获取并更新所有持仓信息
        positions = position_service.update_all_positions()
        
        logger.info(f"【前端触发】成功获取并更新 {len(positions)} 条持仓记录")
        return jsonify({
            'code': 200,
            'message': 'success',
            'data': positions
        })
        
    except Exception as e:
        logger.error(f"【前端触发】获取持仓列表失败: {str(e)}")
        return jsonify({
            'code': 500,
            'message': f'获取持仓列表失败: {str(e)}',
            'data': None
        }), 500

@position_bp.route('/positions/<stock_code>', methods=['GET'])
def get_position(stock_code: str):
    """
    获取指定股票的持仓信息
    
    Args:
        stock_code: 股票代码
        
    Returns:
        JSON响应，包含指定股票的持仓信息
    """
    try:
        logger.info(f"【前端触发】开始获取股票 {stock_code} 的持仓信息...")
        position = StockPosition.query.filter_by(stock_code=stock_code).first()
        if not position:
            logger.warning(f"【前端触发】未找到股票代码为 {stock_code} 的持仓记录")
            return jsonify({
                'code': 404,
                'message': f'未找到股票代码为 {stock_code} 的持仓记录',
                'data': None
            }), 404
            
        # 更新市值信息
        latest_price = position_service.get_real_time_price(stock_code)
        if latest_price:
            position.update_market_value(latest_price)
            db.session.commit()
            logger.info(f"【前端触发】成功更新股票 {stock_code} 的最新价格: {latest_price}")
        
        logger.info(f"【前端触发】成功获取股票 {stock_code} 的持仓信息")
        return jsonify({
            'code': 200,
            'message': 'success',
            'data': position.to_dict()
        })
        
    except Exception as e:
        logger.error(f"【前端触发】获取股票 {stock_code} 的持仓信息失败: {str(e)}")
        return jsonify({
            'code': 500,
            'message': f'获取持仓信息失败: {str(e)}',
            'data': None
        }), 500

@position_bp.route('/positions/<stock_code>/market_value', methods=['PUT'])
def update_market_value(stock_code):
    """更新持仓市值
    
    Args:
        stock_code (str): 股票代码
        
    Returns:
        dict: 更新结果
    """
    try:
        data = request.get_json()
        if not data or 'latest_price' not in data:
            return jsonify({
                'code': 400,
                'message': '缺少必要的参数: latest_price'
            }), 400
            
        position = StockPosition.query.filter_by(stock_code=stock_code).first()
        if not position:
            return jsonify({
                'code': 404,
                'message': f'未找到股票代码为 {stock_code} 的持仓'
            }), 404
            
        position.latest_price = data['latest_price']
        position.market_value = position.total_volume * position.latest_price
        position.floating_profit = position.market_value - position.total_amount
        position.floating_profit_ratio = position.floating_profit / position.total_amount
        position.updated_at = datetime.now()
        
        db.session.commit()
        
        return jsonify({
            'code': 200,
            'message': '更新市值成功',
            'data': position.to_dict()
        })
        
    except Exception as e:
        current_app.logger.error(f'更新市值失败: {str(e)}')
        return jsonify({
            'code': 500,
            'message': f'更新市值失败: {str(e)}'
        }), 500 