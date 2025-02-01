from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

db = SQLAlchemy()

class StockStrategy(db.Model):
    """股票策略模型"""
    __tablename__ = 'stock_strategies'

    id = db.Column(db.Integer, primary_key=True)
    stock_name = db.Column(db.String(100), nullable=False, comment='股票名称')
    stock_code = db.Column(db.String(20), nullable=False, comment='股票代码')
    action = db.Column(db.Enum('buy', 'sell'), nullable=False, comment='执行动作')
    position_ratio = db.Column(db.Float, nullable=False, comment='操作比例')
    
    # 执行价位区间
    price_min = db.Column(db.Float, nullable=True, comment='最小执行价')
    price_max = db.Column(db.Float, nullable=True, comment='最大执行价')
    
    take_profit_price = db.Column(db.Float, nullable=True, comment='止盈价')
    stop_loss_price = db.Column(db.Float, nullable=True, comment='止损价')
    other_conditions = db.Column(db.Text, nullable=True, comment='其他操作条件')
    reason = db.Column(db.Text, nullable=True, comment='操作理由')
    
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow, comment='策略制定时间')
    updated_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow, comment='策略修正时间')
    is_active = db.Column(db.Boolean, nullable=False, default=True, comment='策略是否有效')

    def to_dict(self):
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
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat(),
            'is_active': self.is_active
        } 