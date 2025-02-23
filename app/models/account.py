"""
账户资金模型模块

此模块定义了账户资金相关的数据库模型
"""

from datetime import datetime
from typing import Dict, Any
import pytz
from . import db

# 设置中国时区
CN_TIMEZONE = pytz.timezone('Asia/Shanghai')

class AccountFunds(db.Model):
    """账户资金模型"""
    __tablename__ = 'account_funds'
    
    # 设置表的字符集和排序规则
    __table_args__ = {
        'mysql_engine': 'InnoDB',
        'mysql_charset': 'utf8mb4',
        'mysql_collate': 'utf8mb4_unicode_ci'
    }

    id = db.Column(db.Integer, primary_key=True, comment='账户ID')
    initial_assets = db.Column(db.Float, nullable=False, comment='初始资金')
    total_assets = db.Column(db.Float, nullable=False, default=0, comment='资产总值')
    available_funds = db.Column(db.Float, nullable=False, default=0, comment='可用资金')
    frozen_funds = db.Column(db.Float, nullable=False, default=0, comment='冻结资金')
    total_profit = db.Column(db.Float, nullable=False, default=0, comment='总盈亏')
    total_profit_ratio = db.Column(db.Float, nullable=False, default=0, comment='总收益率')
    created_at = db.Column(db.DateTime, nullable=False, default=lambda: datetime.now(CN_TIMEZONE), comment='创建时间')
    updated_at = db.Column(db.DateTime, nullable=False, default=lambda: datetime.now(CN_TIMEZONE), onupdate=lambda: datetime.now(CN_TIMEZONE), comment='更新时间')

    def __repr__(self):
        """返回账户资金的字符串表示"""
        return f'<AccountFunds {self.id}: 总资产={self.total_assets}, 可用资金={self.available_funds}, 总收益率={self.total_profit_ratio}%>'

    def to_dict(self) -> Dict[str, Any]:
        """将模型转换为字典"""
        return {
            'id': self.id,
            'initial_assets': self.initial_assets,
            'total_assets': self.total_assets,
            'available_funds': self.available_funds,
            'frozen_funds': self.frozen_funds,
            'total_profit': self.total_profit,
            'total_profit_ratio': self.total_profit_ratio,
            'created_at': self.created_at.astimezone(CN_TIMEZONE).strftime('%Y-%m-%d %H:%M:%S'),
            'updated_at': self.updated_at.astimezone(CN_TIMEZONE).strftime('%Y-%m-%d %H:%M:%S')
        }

    def update_profit(self):
        """更新总盈亏和收益率"""
        self.total_profit = self.total_assets - self.initial_assets
        self.total_profit_ratio = (self.total_assets - self.initial_assets) / self.initial_assets * 100 if self.initial_assets > 0 else 0 