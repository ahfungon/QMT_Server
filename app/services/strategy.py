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
            # 构建基础查询
            query = StockStrategy.query
            
            # 组合排序条件：1. 是否有效，2. 更新时间，3. 创建时间
            sort_conditions = [
                StockStrategy.is_active.desc(),  # 有效的排在前面
                StockStrategy.updated_at.desc() if order == 'desc' else StockStrategy.updated_at.asc(),
                StockStrategy.created_at.desc() if order == 'desc' else StockStrategy.created_at.asc()
            ]
            
            # 应用排序条件
            query = query.order_by(*sort_conditions)
            
            # 执行查询
            strategies = query.all()
            
            # 记录详细日志
            logger.info("="*50)
            logger.info("获取所有策略列表（排序规则：1.是否有效 2.更新时间 3.创建时间）:")
            logger.info("-"*50)
            for strategy in strategies:
                logger.info(
                    f"ID: {strategy.id:3d} | "
                    f"名称: {strategy.stock_name:10s} | "
                    f"代码: {strategy.stock_code:6s} | "
                    f"是否有效: {'是' if strategy.is_active else '否'} | "
                    f"创建时间: {strategy.created_at.strftime('%Y-%m-%d %H:%M:%S')} | "
                    f"更新时间: {strategy.updated_at.strftime('%Y-%m-%d %H:%M:%S')}"
                )
            logger.info("-"*50)
            logger.info(f"共获取到 {len(strategies)} 条记录")
            logger.info("="*50)
            
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
            strategy = StockStrategy.query.get(strategy_id)
            if not strategy:
                logger.error(f"策略不存在，ID: {strategy_id}")
                raise ValueError(f"策略不存在，ID: {strategy_id}")
                
            # 记录更新前的数据
            logger.info(f"更新策略前的数据: {strategy.to_dict()}")
            logger.info(f"更新的数据: {data}")
            
            # 验证必要字段
            required_fields = ['stock_name', 'stock_code', 'action']
            for field in required_fields:
                if field in data and not data[field]:
                    raise ValueError(f"字段 {field} 不能为空")
            
            # 更新字段
            for key, value in data.items():
                if hasattr(strategy, key):
                    setattr(strategy, key, value)
                else:
                    logger.warning(f"忽略未知字段: {key}")
            
            db.session.commit()
            updated_strategy = strategy.to_dict()
            logger.info(f"策略更新成功: {updated_strategy}")
            return updated_strategy
            
        except ValueError as e:
            db.session.rollback()
            logger.error(f"更新策略参数错误: {str(e)}")
            raise
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
    
    def search_strategies(self, 
        start_time: str = None, 
        end_time: str = None, 
        stock_code: str = None, 
        stock_name: str = None,
        action: str = None,
        sort_by: str = 'updated_at',
        order: str = 'desc',
        is_active: bool = None
    ) -> List[Dict[str, Any]]:
        """
        高级查询策略列表
        
        Args:
            start_time: 开始时间，格式：YYYY-MM-DD HH:mm:ss
            end_time: 结束时间，格式：YYYY-MM-DD HH:mm:ss
            stock_code: 股票代码
            stock_name: 股票名称
            action: 交易动作（buy/sell）
            sort_by: 排序字段，可选值: updated_at, created_at
            order: 排序方式，可选值: desc, asc
            is_active: 是否只查询有效策略，None表示查询所有
            
        Returns:
            List[Dict[str, Any]]: 策略列表
        """
        try:
            # 构建基础查询
            query = StockStrategy.query
            
            # 添加时间范围过滤
            if start_time:
                query = query.filter(StockStrategy.created_at >= start_time)
            if end_time:
                query = query.filter(StockStrategy.created_at <= end_time)
                
            # 添加股票代码过滤
            if stock_code:
                query = query.filter(StockStrategy.stock_code.like(f'%{stock_code}%'))
                
            # 添加股票名称过滤
            if stock_name:
                query = query.filter(StockStrategy.stock_name.like(f'%{stock_name}%'))
                
            # 添加交易动作过滤
            if action:
                query = query.filter(StockStrategy.action == action)
                
            # 添加状态过滤（只有当 is_active 不为 None 时才添加过滤条件）
            if is_active is not None:
                query = query.filter(StockStrategy.is_active == is_active)
            
            # 组合排序条件：1. 是否有效，2. 更新时间，3. 创建时间
            sort_conditions = [
                StockStrategy.is_active.desc(),  # 有效的排在前面
                StockStrategy.updated_at.desc() if order == 'desc' else StockStrategy.updated_at.asc(),
                StockStrategy.created_at.desc() if order == 'desc' else StockStrategy.created_at.asc()
            ]
            
            # 应用排序条件
            query = query.order_by(*sort_conditions)
            
            # 执行查询
            strategies = query.all()
            
            # 记录详细日志
            logger.info("="*50)
            logger.info("搜索策略列表（排序规则：1.是否有效 2.更新时间 3.创建时间）:")
            logger.info("搜索条件:")
            logger.info(f"  时间范围: {start_time or '不限'} 至 {end_time or '不限'}")
            logger.info(f"  股票代码: {stock_code or '不限'}")
            logger.info(f"  股票名称: {stock_name or '不限'}")
            logger.info(f"  交易动作: {action or '不限'}")
            logger.info(f"  是否有效: {is_active if is_active is not None else '不限'}")
            logger.info(f"  排序字段: {sort_by}")
            logger.info(f"  排序方式: {order}")
            logger.info("-"*50)
            logger.info("搜索结果:")
            for strategy in strategies:
                logger.info(
                    f"ID: {strategy.id:3d} | "
                    f"名称: {strategy.stock_name:10s} | "
                    f"代码: {strategy.stock_code:6s} | "
                    f"是否有效: {'是' if strategy.is_active else '否'} | "
                    f"创建时间: {strategy.created_at.strftime('%Y-%m-%d %H:%M:%S')} | "
                    f"更新时间: {strategy.updated_at.strftime('%Y-%m-%d %H:%M:%S')}"
                )
            logger.info("-"*50)
            logger.info(f"共获取到 {len(strategies)} 条记录")
            logger.info("="*50)
            
            return [strategy.to_dict() for strategy in strategies]
            
        except Exception as e:
            logger.error(f"查询策略列表失败: {str(e)}", exc_info=True)
            raise 