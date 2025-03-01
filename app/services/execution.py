"""
策略执行记录服务模块

此模块提供策略执行记录相关的业务逻辑处理
"""

import logging
from typing import List, Dict, Any, Optional
from datetime import datetime
from ..models import db
from ..models.execution import StrategyExecution
from ..models.stock import StockStrategy
from .position import PositionService

logger = logging.getLogger(__name__)

class ExecutionService:
    """策略执行记录服务类"""
    
    def __init__(self):
        """初始化持仓服务"""
        self.position_service = PositionService()
    
    def create_execution(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        创建策略执行记录
        
        Args:
            data: 执行记录数据，包含以下字段：
                - strategy_id: 策略ID
                - execution_price: 执行价格
                - volume: 交易量（可选，如果不提供则根据策略计算）
                - strategy_status: 策略执行状态（'partial' 或 'completed'）
                - remarks: 备注说明（可选）
            
        Returns:
            Dict[str, Any]: 创建的执行记录
        """
        try:
            # 验证必要字段
            required_fields = ['strategy_id', 'execution_price', 'strategy_status']
            for field in required_fields:
                if field not in data or data[field] is None:
                    raise ValueError(f"缺少必要字段: {field}")
            
            # 验证策略状态参数
            if data['strategy_status'] not in ['partial', 'completed']:
                raise ValueError("策略状态必须是 'partial' 或 'completed'")
            
            # 验证策略ID并获取策略信息
            strategy = db.session.get(StockStrategy, data['strategy_id'])
            if not strategy:
                raise ValueError(f"策略ID {data['strategy_id']} 不存在")
            
            # 根据操作类型计算交易量（如果未提供）
            volume = data.get('volume')
            if volume is None:
                # 根据不同操作类型计算交易量
                volume = self._calculate_trade_volume(strategy, data['execution_price'])
                
                # 如果是持有操作，则不需要交易
                if strategy.action == 'hold':
                    volume = 0
            
            # 自动填充策略相关信息
            execution_data = {
                'strategy_id': data['strategy_id'],
                'stock_code': strategy.stock_code,
                'stock_name': strategy.stock_name,
                'action': strategy.action,
                'execution_price': data['execution_price'],
                'volume': volume,
                'position_ratio': strategy.position_ratio,
                'original_position_ratio': strategy.original_position_ratio,
                'execution_result': 'success',  # 默认执行成功
                'remarks': data.get('remarks', '')
            }
            
            # 创建执行记录
            execution = StrategyExecution(**execution_data)
            db.session.add(execution)
            
            # 更新策略执行状态
            strategy.execution_status = data['strategy_status']
            logger.info(f"策略 {strategy.id} 状态更新为: {data['strategy_status']}")
            
            # 如果是持有操作，则不更新持仓
            if strategy.action == 'hold':
                logger.info(f"策略 {strategy.id} 是持有操作，不更新持仓")
                db.session.commit()
                return execution.to_dict()
            
            # 更新持仓信息
            try:
                position = self.position_service.update_position(
                    stock_code=strategy.stock_code,
                    stock_name=strategy.stock_name,
                    volume=volume,
                    price=data['execution_price'],
                    action=strategy.action,
                    position_ratio=strategy.position_ratio,
                    original_position_ratio=strategy.original_position_ratio
                )
                logger.info(f"持仓更新成功: {position}")
                
                # 更新账户资金
                if strategy.action in ['buy', 'add']:
                    # 买入/加仓操作需要扣除资金
                    total_cost = volume * data['execution_price']
                    from ..services.account import AccountService
                    account_service = AccountService()
                    account = account_service.get_account_funds()
                    
                    # 检查资金是否足够
                    if account['available_funds'] < total_cost:
                        logger.error(f"可用资金不足: 需要 {total_cost}，当前可用 {account['available_funds']}")
                        raise ValueError(f"可用资金不足: 需要 {total_cost}，当前可用 {account['available_funds']}")
                    
                    # 更新账户资金
                    new_available_funds = account['available_funds'] - total_cost
                    account_service.update_funds(
                        available_funds=new_available_funds,
                        frozen_funds=account['frozen_funds']
                    )
                    logger.info(f"账户资金更新成功: 扣除 {total_cost}，剩余可用资金 {new_available_funds}")
                elif strategy.action in ['sell', 'trim']:
                    # 卖出/减仓操作需要增加资金
                    total_income = volume * data['execution_price']
                    from ..services.account import AccountService
                    account_service = AccountService()
                    account = account_service.get_account_funds()
                    
                    # 更新账户资金
                    new_available_funds = account['available_funds'] + total_income
                    account_service.update_funds(
                        available_funds=new_available_funds,
                        frozen_funds=account['frozen_funds']
                    )
                    logger.info(f"账户资金更新成功: 增加 {total_income}，可用资金增加到 {new_available_funds}")
            except Exception as e:
                logger.error(f"持仓或资金更新失败: {str(e)}")
                raise
            
            db.session.commit()
            return execution.to_dict()
        except Exception as e:
            db.session.rollback()
            logger.error(f"创建执行记录失败: {str(e)}", exc_info=True)
            raise
    
    def _calculate_trade_volume(self, strategy: StockStrategy, price: float) -> int:
        """
        根据策略类型计算交易量
        
        Args:
            strategy: 策略对象
            price: 交易价格
            
        Returns:
            int: 计算得到的交易量
        """
        # 获取账户资金信息
        from ..services.account import AccountService
        account_service = AccountService()
        account = account_service.get_account_funds()
        
        # 获取持仓信息
        position = StockPosition.query.filter_by(stock_code=strategy.stock_code).first()
        
        # 根据不同操作类型计算交易量
        if strategy.action in ['buy', 'add']:
            # 买入/加仓：根据总资产和仓位比例计算
            trade_amount = account['total_assets'] * strategy.position_ratio / 100
            volume = int(trade_amount / price)
            logger.info(f"买入/加仓交易量计算: 总资产={account['total_assets']}, "
                        f"仓位比例={strategy.position_ratio}%, 价格={price}, 计算得到交易量={volume}")
            return volume
            
        elif strategy.action == 'sell':
            # 卖出：根据持仓数量和仓位比例计算
            if not position:
                logger.warning(f"没有持仓，无法执行卖出操作")
                return 0
                
            volume = int(position.total_volume * strategy.position_ratio / 100)
            logger.info(f"卖出交易量计算: 持仓数量={position.total_volume}, "
                        f"卖出比例={strategy.position_ratio}%, 计算得到交易量={volume}")
            return volume
            
        elif strategy.action == 'trim':
            # 减仓：根据持仓数量、原始仓位和目标减仓比例计算
            if not position:
                logger.warning(f"没有持仓，无法执行减仓操作")
                return 0
                
            if not position.original_position_ratio or position.original_position_ratio <= 0:
                logger.warning(f"原始仓位比例无效，使用当前持仓全部数量作为基准")
                # 如果没有原始仓位比例记录，则按照sell逻辑处理
                volume = int(position.total_volume * strategy.position_ratio / 100)
            else:
                # 减仓特殊计算逻辑：
                # 交易量 = 当前持股数量 × (目标减仓比例 ÷ 原始买入仓位比例)
                volume = int(position.total_volume * (strategy.position_ratio / position.original_position_ratio))
                
            logger.info(f"减仓交易量计算: 持仓数量={position.total_volume}, "
                        f"原始仓位比例={position.original_position_ratio}%, "
                        f"目标减仓比例={strategy.position_ratio}%, 计算得到交易量={volume}")
            return volume
            
        else:  # 包括 'hold' 操作
            # 持有操作不涉及实际交易
            return 0
    
    def get_execution(self, execution_id: int) -> Optional[Dict[str, Any]]:
        """
        获取单个执行记录
        
        Args:
            execution_id: 执行记录ID
            
        Returns:
            Optional[Dict[str, Any]]: 执行记录信息
        """
        try:
            execution = db.session.get(StrategyExecution, execution_id)
            return execution.to_dict() if execution else None
        except Exception as e:
            logger.error(f"获取执行记录失败: {str(e)}", exc_info=True)
            raise
    
    def get_executions(self, 
        strategy_id: int = None,
        stock_code: str = None,
        start_time: str = None,
        end_time: str = None,
        action: str = None,
        result: str = None,
        sort_by: str = 'execution_time',
        order: str = 'desc',
        limit: int = None
    ) -> List[Dict[str, Any]]:
        """
        查询执行记录列表
        
        Args:
            strategy_id: 策略ID
            stock_code: 股票代码
            start_time: 开始时间
            end_time: 结束时间
            action: 执行操作
            result: 执行结果
            sort_by: 排序字段
            order: 排序方式
            limit: 限制返回数量
            
        Returns:
            List[Dict[str, Any]]: 执行记录列表
        """
        try:
            # 构建查询
            query = db.select(StrategyExecution)
            
            # 添加过滤条件
            if strategy_id:
                query = query.filter(StrategyExecution.strategy_id == strategy_id)
            if stock_code:
                query = query.filter(StrategyExecution.stock_code.like(f'%{stock_code}%'))
            if start_time:
                query = query.filter(StrategyExecution.execution_time >= start_time)
            if end_time:
                query = query.filter(StrategyExecution.execution_time <= end_time)
            if action:
                query = query.filter(StrategyExecution.action == action)
            if result:
                query = query.filter(StrategyExecution.execution_result == result)
            
            # 添加排序
            if sort_by == 'created_at':
                query = query.order_by(
                    StrategyExecution.created_at.desc() if order == 'desc' else StrategyExecution.created_at.asc()
                )
            else:  # 默认按执行时间
                query = query.order_by(
                    StrategyExecution.execution_time.desc() if order == 'desc' else StrategyExecution.execution_time.asc()
                )
            
            # 添加限制
            if limit:
                query = query.limit(limit)
            
            # 执行查询
            executions = db.session.execute(query).scalars().all()
            return [execution.to_dict() for execution in executions]
            
        except Exception as e:
            logger.error(f"查询执行记录列表失败: {str(e)}", exc_info=True)
            raise
    
    def update_execution(self, execution_id: int, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        更新执行记录
        
        Args:
            execution_id: 执行记录ID
            data: 更新数据
            
        Returns:
            Dict[str, Any]: 更新后的执行记录
        """
        try:
            execution = db.session.get(StrategyExecution, execution_id)
            if not execution:
                raise ValueError(f"执行记录不存在，ID: {execution_id}")
            
            # 更新字段
            for key, value in data.items():
                if hasattr(execution, key):
                    setattr(execution, key, value)
            
            # 如果更新了执行量，需要重新计算策略执行状态
            if 'volume' in data:
                strategy = db.session.get(StockStrategy, execution.strategy_id)
                if strategy:
                    # 获取该策略的所有执行记录
                    query = db.select(StrategyExecution).filter_by(strategy_id=strategy.id)
                    all_executions = db.session.execute(query).scalars().all()
                    
                    # 计算已执行的总量
                    total_executed_volume = sum(e.volume for e in all_executions)
                    
                    # 计算策略需要执行的总量
                    # 这里需要根据实际业务逻辑调整计算方式
                    target_volume = 100  # 这里需要根据实际业务逻辑计算目标数量
                    
                    # 更新策略状态
                    if total_executed_volume >= target_volume:
                        strategy.execution_status = 'completed'
                        logger.info(f"策略 {strategy.id} 已全部执行完成")
                    else:
                        strategy.execution_status = 'partial'
                        logger.info(f"策略 {strategy.id} 部分执行，已执行量: {total_executed_volume}")
            
            db.session.commit()
            return execution.to_dict()
        except Exception as e:
            db.session.rollback()
            logger.error(f"更新执行记录失败: {str(e)}", exc_info=True)
            raise
    
    def delete_execution(self, execution_id: int) -> bool:
        """
        删除执行记录
        
        Args:
            execution_id: 执行记录ID
            
        Returns:
            bool: 是否删除成功
        """
        try:
            execution = db.session.get(StrategyExecution, execution_id)
            if not execution:
                raise ValueError(f"执行记录不存在，ID: {execution_id}")
            
            # 获取策略信息
            strategy = db.session.get(StockStrategy, execution.strategy_id)
            if strategy:
                # 删除当前执行记录后重新计算策略执行状态
                db.session.delete(execution)
                db.session.flush()  # 刷新会话，使删除生效但不提交
                
                # 获取剩余的执行记录
                query = db.select(StrategyExecution).filter_by(strategy_id=strategy.id)
                remaining_executions = db.session.execute(query).scalars().all()
                
                # 计算剩余执行量
                total_executed_volume = sum(e.volume for e in remaining_executions)
                
                # 计算策略需要执行的总量
                # 这里需要根据实际业务逻辑调整计算方式
                target_volume = 100  # 这里需要根据实际业务逻辑计算目标数量
                
                # 更新策略状态
                if not remaining_executions:
                    strategy.execution_status = 'pending'
                    logger.info(f"策略 {strategy.id} 所有执行记录已删除，状态更新为未执行")
                elif total_executed_volume >= target_volume:
                    strategy.execution_status = 'completed'
                    logger.info(f"策略 {strategy.id} 删除执行记录后仍然全部执行完成")
                else:
                    strategy.execution_status = 'partial'
                    logger.info(f"策略 {strategy.id} 删除执行记录后部分执行，剩余执行量: {total_executed_volume}")
            
            db.session.commit()
            return True
        except Exception as e:
            db.session.rollback()
            logger.error(f"删除执行记录失败: {str(e)}", exc_info=True)
            raise 