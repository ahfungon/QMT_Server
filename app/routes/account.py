"""
账户资金路由模块

此模块提供账户资金相关的API接口
"""

from flask import Blueprint, jsonify, request, current_app
from ..services.account import AccountService
from ..utils.logger import setup_logger

account_bp = Blueprint('account', __name__)
logger = setup_logger('account')
account_service = AccountService()

@account_bp.route('/account/funds', methods=['GET'])
def get_account_funds():
    """
    获取账户资金信息
    
    Returns:
        JSON响应，包含账户资金信息
    """
    try:
        logger.info("【前端触发】开始获取账户资金信息...")
        funds = account_service.get_account_funds()
        
        logger.info(f"【前端触发】成功获取账户资金信息：{funds}")
        return jsonify({
            'code': 200,
            'message': 'success',
            'data': funds
        })
        
    except Exception as e:
        logger.error(f"【前端触发】获取账户资金信息失败: {str(e)}")
        return jsonify({
            'code': 500,
            'message': f'获取账户资金信息失败: {str(e)}',
            'data': None
        }), 500

@account_bp.route('/account/funds/freeze', methods=['POST'])
def freeze_funds():
    """
    冻结资金
    
    Returns:
        JSON响应，包含更新后的账户资金信息
    """
    try:
        data = request.get_json()
        if not data or 'amount' not in data:
            return jsonify({
                'code': 400,
                'message': '缺少必要的参数: amount',
                'data': None
            }), 400
            
        amount = float(data['amount'])
        logger.info(f"【前端触发】开始冻结资金：{amount}")
        
        funds = account_service.freeze_funds(amount)
        
        logger.info(f"【前端触发】成功冻结资金：{amount}")
        return jsonify({
            'code': 200,
            'message': 'success',
            'data': funds
        })
        
    except ValueError as e:
        logger.error(f"【前端触发】冻结资金失败，参数错误: {str(e)}")
        return jsonify({
            'code': 400,
            'message': str(e),
            'data': None
        }), 400
        
    except Exception as e:
        logger.error(f"【前端触发】冻结资金失败: {str(e)}")
        return jsonify({
            'code': 500,
            'message': f'冻结资金失败: {str(e)}',
            'data': None
        }), 500

@account_bp.route('/account/funds/unfreeze', methods=['POST'])
def unfreeze_funds():
    """
    解冻资金
    
    Returns:
        JSON响应，包含更新后的账户资金信息
    """
    try:
        data = request.get_json()
        if not data or 'amount' not in data:
            return jsonify({
                'code': 400,
                'message': '缺少必要的参数: amount',
                'data': None
            }), 400
            
        amount = float(data['amount'])
        logger.info(f"【前端触发】开始解冻资金：{amount}")
        
        funds = account_service.unfreeze_funds(amount)
        
        logger.info(f"【前端触发】成功解冻资金：{amount}")
        return jsonify({
            'code': 200,
            'message': 'success',
            'data': funds
        })
        
    except ValueError as e:
        logger.error(f"【前端触发】解冻资金失败，参数错误: {str(e)}")
        return jsonify({
            'code': 400,
            'message': str(e),
            'data': None
        }), 400
        
    except Exception as e:
        logger.error(f"【前端触发】解冻资金失败: {str(e)}")
        return jsonify({
            'code': 500,
            'message': f'解冻资金失败: {str(e)}',
            'data': None
        }), 500

@account_bp.route('/account/funds', methods=['PUT'])
def update_funds():
    """
    更新账户资金
    
    Returns:
        JSON响应，包含更新后的账户资金信息
    """
    try:
        data = request.get_json()
        if not data or 'available_funds' not in data or 'frozen_funds' not in data:
            return jsonify({
                'code': 400,
                'message': '缺少必要的参数: available_funds, frozen_funds',
                'data': None
            }), 400
            
        available_funds = float(data['available_funds'])
        frozen_funds = float(data['frozen_funds'])
        
        logger.info(f"【前端触发】开始更新账户资金：可用资金={available_funds}, 冻结资金={frozen_funds}")
        
        funds = account_service.update_funds(available_funds, frozen_funds)
        
        logger.info(f"【前端触发】成功更新账户资金：{funds}")
        return jsonify({
            'code': 200,
            'message': 'success',
            'data': funds
        })
        
    except ValueError as e:
        logger.error(f"【前端触发】更新账户资金失败，参数错误: {str(e)}")
        return jsonify({
            'code': 400,
            'message': str(e),
            'data': None
        }), 400
        
    except Exception as e:
        logger.error(f"【前端触发】更新账户资金失败: {str(e)}")
        return jsonify({
            'code': 500,
            'message': f'更新账户资金失败: {str(e)}',
            'data': None
        }), 500 