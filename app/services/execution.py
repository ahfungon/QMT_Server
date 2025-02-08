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

logger = logging.getLogger(__name__)

class ExecutionService:
    """策略执行记录服务类"""
    
    def create_execution(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        创建策略执行记录
        
        Args:
            data: 执行记录数据
            
        Returns:
            Dict[str, Any]: 创建的执行记录
        """
        try:
            # 验证必要字段
            required_fields = ['strategy_id', 'execution_price', 'volume']
            for field in required_fields:
                if field not in data or data[field] is None:
                    raise ValueError(f"缺少必要字段: {field}")
            
            # 验证策略ID并获取策略信息
            strategy = StockStrategy.query.get(data['strategy_id'])
            if not strategy:
                raise ValueError(f"策略ID {data['strategy_id']} 不存在")
            
            # 自动填充策略相关信息
            data['stock_code'] = strategy.stock_code
            data['stock_name'] = strategy.stock_name
            data['action'] = strategy.action
            
            # 设置默认的执行结果
            if 'execution_result' not in data or data['execution_result'] is None:
                data['execution_result'] = 'success'
            
            # 设置执行时间
            if 'execution_time' not in data:
                data['execution_time'] = datetime.now()
            
            # 创建执行记录
            execution = StrategyExecution(**data)
            db.session.add(execution)
            db.session.commit()
            
            return execution.to_dict()
        except Exception as e:
            db.session.rollback()
            logger.error(f"创建执行记录失败: {str(e)}", exc_info=True)
            raise
    
    def get_execution(self, execution_id: int) -> Optional[Dict[str, Any]]:
        """
        获取单个执行记录
        
        Args:
            execution_id: 执行记录ID
            
        Returns:
            Optional[Dict[str, Any]]: 执行记录信息
        """
        try:
            execution = StrategyExecution.query.get(execution_id)
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
            query = StrategyExecution.query
            
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
            executions = query.all()
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
            execution = StrategyExecution.query.get_or_404(execution_id)
            
            # 更新字段
            for key, value in data.items():
                if hasattr(execution, key):
                    setattr(execution, key, value)
            
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
            execution = StrategyExecution.query.get_or_404(execution_id)
            db.session.delete(execution)
            db.session.commit()
            return True
        except Exception as e:
            db.session.rollback()
            logger.error(f"删除执行记录失败: {str(e)}", exc_info=True)
            raise 