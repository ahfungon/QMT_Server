"""
策略服务模块

此模块提供策略相关的业务逻辑处理
"""

import logging
from typing import List, Dict, Any, Optional
from ..models import db
from ..models.stock import StockStrategy
from ai_robot import create_ai_processor

logger = logging.getLogger(__name__)

class StrategyService:
    """策略服务类"""
    
    def __init__(self):
        """初始化AI处理器"""
        self.ai_processor = create_ai_processor()
    
    def analyze_strategy(self, strategy_text: str) -> Dict[str, Any]:
        """分析策略文本"""
        try:
            return self.ai_processor.process_strategy(strategy_text)
        except Exception as e:
            logger.error(f"策略分析失败: {str(e)}", exc_info=True)
            raise
    
    def get_all_strategies(self, sort_by: str = 'updated_at', order: str = 'desc') -> List[Dict[str, Any]]:
        """
        获取所有策略
        
        Args:
            sort_by: 排序字段，可选值: updated_at, created_at
            order: 排序方式，可选值: desc, asc
            
        Returns:
            List[Dict[str, Any]]: 策略列表
        """
        try:
            query = StockStrategy.query
            
            # 添加排序
            if sort_by == 'created_at':
                query = query.order_by(StockStrategy.created_at.desc() if order == 'desc' else StockStrategy.created_at.asc())
            else:  # 默认按更新时间
                query = query.order_by(StockStrategy.updated_at.desc() if order == 'desc' else StockStrategy.updated_at.asc())
            
            strategies = query.all()
            return [strategy.to_dict() for strategy in strategies]
        except Exception as e:
            logger.error(f"获取策略列表失败: {str(e)}", exc_info=True)
            raise
    
    def create_strategy(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """创建新策略"""
        try:
            strategy = StockStrategy(**data)
            db.session.add(strategy)
            db.session.commit()
            return strategy.to_dict()
        except Exception as e:
            db.session.rollback()
            logger.error(f"创建策略失败: {str(e)}", exc_info=True)
            raise
    
    def update_strategy(self, strategy_id: int, data: Dict[str, Any]) -> Dict[str, Any]:
        """更新策略"""
        try:
            strategy = StockStrategy.query.get_or_404(strategy_id)
            for key, value in data.items():
                setattr(strategy, key, value)
            db.session.commit()
            return strategy.to_dict()
        except Exception as e:
            db.session.rollback()
            logger.error(f"更新策略失败: {str(e)}", exc_info=True)
            raise
    
    def check_strategy_exists(self, stock_name: str, stock_code: str, action: str) -> Optional[Dict[str, Any]]:
        """检查策略是否存在"""
        try:
            strategy = StockStrategy.query.filter_by(
                stock_name=stock_name,
                stock_code=stock_code,
                action=action,
                is_active=True
            ).first()
            return strategy.to_dict() if strategy else None
        except Exception as e:
            logger.error(f"检查策略失败: {str(e)}", exc_info=True)
            raise
    
    def update_strategy_by_key(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """根据关键字段更新策略"""
        try:
            strategy = StockStrategy.query.filter_by(
                stock_name=data['stock_name'],
                stock_code=data['stock_code'],
                action=data['action'],
                is_active=True
            ).first()
            
            if not strategy:
                raise ValueError('未找到匹配的策略')
            
            # 更新策略字段
            has_updates = False
            update_fields = [
                'position_ratio', 'price_min', 'price_max',
                'take_profit_price', 'stop_loss_price',
                'other_conditions', 'reason'
            ]
            
            for field in update_fields:
                if field in data and getattr(strategy, field) != data[field]:
                    setattr(strategy, field, data[field])
                    has_updates = True
            
            if has_updates:
                db.session.commit()
                
            return strategy.to_dict()
        except Exception as e:
            db.session.rollback()
            logger.error(f"更新策略失败: {str(e)}", exc_info=True)
            raise
    
    def deactivate_strategy(self, strategy_id: int) -> Dict[str, Any]:
        """设置策略为失效"""
        try:
            strategy = StockStrategy.query.get_or_404(strategy_id)
            strategy.is_active = False
            db.session.commit()
            return strategy.to_dict()
        except Exception as e:
            db.session.rollback()
            logger.error(f"设置策略失效失败: {str(e)}", exc_info=True)
            raise 