"""
股票策略模型模块

此模块定义了股票策略相关的数据库模型
"""

from datetime import datetime
from typing import Dict, Any
import pytz
from . import db

# 设置中国时区
CN_TIMEZONE = pytz.timezone('Asia/Shanghai')

class StockStrategy(db.Model):
    """股票策略模型"""
    __tablename__ = 'stock_strategies'
    
    # 设置表的字符集和排序规则
    __table_args__ = {
        'mysql_engine': 'InnoDB',
        'mysql_charset': 'utf8mb4',
        'mysql_collate': 'utf8mb4_unicode_ci'
    }

    id = db.Column(db.Integer, primary_key=True)
    stock_name = db.Column(db.String(100, collation='utf8mb4_unicode_ci'), nullable=False, comment='股票名称')
    stock_code = db.Column(db.String(20, collation='utf8mb4_unicode_ci'), nullable=False, comment='股票代码')
    action = db.Column(db.Enum('buy', 'sell', name='action_types'), nullable=False, comment='执行动作')
    position_ratio = db.Column(db.Float, nullable=False, comment='操作比例')
    
    # 执行价位区间
    price_min = db.Column(db.Float, nullable=True, comment='最小执行价')
    price_max = db.Column(db.Float, nullable=True, comment='最大执行价')
    
    take_profit_price = db.Column(db.Float, nullable=True, comment='止盈价')
    stop_loss_price = db.Column(db.Float, nullable=True, comment='止损价')
    other_conditions = db.Column(db.Text(collation='utf8mb4_unicode_ci'), nullable=True, comment='其他操作条件')
    reason = db.Column(db.Text(collation='utf8mb4_unicode_ci'), nullable=True, comment='操作理由')
    
    created_at = db.Column(db.DateTime, nullable=False, default=lambda: datetime.now(CN_TIMEZONE), comment='策略制定时间')
    updated_at = db.Column(db.DateTime, nullable=False, default=lambda: datetime.now(CN_TIMEZONE), onupdate=lambda: datetime.now(CN_TIMEZONE), comment='策略修正时间')
    is_active = db.Column(db.Boolean, nullable=False, default=True, comment='策略是否有效')

    def to_dict(self) -> Dict[str, Any]:
        """将模型转换为字典"""
        return {
            'id': self.id,
            'stock_name': self.stock_name,
            'stock_code': self.stock_code,
            'action': self.action,
            'position_ratio': self.position_ratio,
            'price_min': self.price_min,
            'price_max': self.price_max,
            'take_profit_price': self.take_profit_price,
            'stop_loss_price': self.stop_loss_price,
            'other_conditions': self.other_conditions,
            'reason': self.reason,
            'created_at': self.created_at.astimezone(CN_TIMEZONE).strftime('%Y-%m-%d %H:%M:%S'),
            'updated_at': self.updated_at.astimezone(CN_TIMEZONE).strftime('%Y-%m-%d %H:%M:%S'),
            'is_active': self.is_active
        } 