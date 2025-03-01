"""
策略执行记录模型模块

此模块定义了策略执行记录相关的数据库模型
"""

from datetime import datetime
import pytz
from typing import Dict, Any
from . import db

# 设置中国时区
CN_TIMEZONE = pytz.timezone('Asia/Shanghai')

class StrategyExecution(db.Model):
    """策略执行记录模型"""
    __tablename__ = 'strategy_executions'
    
    # 设置表的字符集和排序规则
    __table_args__ = {
        'mysql_engine': 'InnoDB',
        'mysql_charset': 'utf8mb4',
        'mysql_collate': 'utf8mb4_unicode_ci'
    }

    id = db.Column(db.Integer, primary_key=True)
    strategy_id = db.Column(db.Integer, db.ForeignKey('stock_strategies.id'), nullable=False, comment='策略ID')
    stock_code = db.Column(db.String(20, collation='utf8mb4_unicode_ci'), nullable=False, comment='股票代码')
    stock_name = db.Column(db.String(100, collation='utf8mb4_unicode_ci'), nullable=False, comment='股票名称')
    action = db.Column(db.Enum('buy', 'sell', 'add', 'trim', 'hold', name='execution_action_types'), nullable=False, comment='执行操作')
    execution_price = db.Column(db.Float, nullable=False, comment='执行价格')
    volume = db.Column(db.Integer, nullable=False, comment='交易量')
    position_ratio = db.Column(db.Float, nullable=True, comment='仓位比例')
    original_position_ratio = db.Column(db.Float, nullable=True, comment='原始买入仓位比例')
    execution_time = db.Column(db.DateTime, nullable=False, default=lambda: datetime.now(CN_TIMEZONE), comment='执行时间')
    execution_result = db.Column(db.Enum('success', 'failed', 'partial', name='execution_result_types'), nullable=False, comment='执行结果')
    remarks = db.Column(db.Text(collation='utf8mb4_unicode_ci'), nullable=True, comment='备注说明')
    created_at = db.Column(db.DateTime, nullable=False, default=lambda: datetime.now(CN_TIMEZONE), comment='创建时间')
    updated_at = db.Column(db.DateTime, nullable=False, default=lambda: datetime.now(CN_TIMEZONE), onupdate=lambda: datetime.now(CN_TIMEZONE), comment='更新时间')

    def to_dict(self) -> Dict[str, Any]:
        """将模型转换为字典"""
        return {
            'id': self.id,
            'strategy_id': self.strategy_id,
            'stock_name': self.stock_name,
            'stock_code': self.stock_code,
            'action': self.action,
            'execution_price': self.execution_price,
            'volume': self.volume,
            'position_ratio': self.position_ratio,
            'original_position_ratio': self.original_position_ratio,
            'execution_time': self.execution_time.astimezone(CN_TIMEZONE).strftime('%Y-%m-%d %H:%M:%S'),
            'execution_result': self.execution_result,
            'remarks': self.remarks,
            'created_at': self.created_at.astimezone(CN_TIMEZONE).strftime('%Y-%m-%d %H:%M:%S'),
            'updated_at': self.updated_at.astimezone(CN_TIMEZONE).strftime('%Y-%m-%d %H:%M:%S')
        } 