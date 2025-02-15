"""
持仓模型模块

此模块定义了股票持仓相关的数据库模型
"""

from datetime import datetime
from typing import Dict, Any
import pytz
from decimal import Decimal, getcontext
from . import db

# 设置中国时区
CN_TIMEZONE = pytz.timezone('Asia/Shanghai')
# 设置高精度计算
getcontext().prec = 8

class StockPosition(db.Model):
    """股票持仓模型"""
    __tablename__ = 'stock_positions'
    
    # 设置表的字符集和排序规则
    __table_args__ = {
        'mysql_engine': 'InnoDB',
        'mysql_charset': 'utf8mb4',
        'mysql_collate': 'utf8mb4_unicode_ci'
    }

    id = db.Column(db.Integer, primary_key=True, comment='持仓ID')
    stock_code = db.Column(db.String(20, collation='utf8mb4_unicode_ci'), nullable=False, comment='股票代码')
    stock_name = db.Column(db.String(100, collation='utf8mb4_unicode_ci'), nullable=False, comment='股票名称')
    total_volume = db.Column(db.Integer, nullable=False, default=0, comment='持仓数量')
    original_cost = db.Column(db.Float, nullable=False, default=0, comment='原始平均成本')
    dynamic_cost = db.Column(db.Float, nullable=False, default=0, comment='动态成本价（股票软件风格）')
    total_amount = db.Column(db.Float, nullable=False, default=0, comment='持仓金额')
    latest_price = db.Column(db.Float, nullable=True, comment='最新价格')
    market_value = db.Column(db.Float, nullable=True, comment='市值')
    floating_profit = db.Column(db.Float, nullable=True, comment='浮动盈亏')
    floating_profit_ratio = db.Column(db.Float, nullable=True, comment='浮动盈亏比例')
    
    created_at = db.Column(db.DateTime, nullable=False, default=lambda: datetime.now(CN_TIMEZONE), comment='创建时间')
    updated_at = db.Column(db.DateTime, nullable=False, default=lambda: datetime.now(CN_TIMEZONE), onupdate=lambda: datetime.now(CN_TIMEZONE), comment='更新时间')

    def __repr__(self):
        """返回持仓的字符串表示"""
        return f'<Position {self.id}: {self.stock_name}({self.stock_code}) - {self.total_volume}股>'

    def to_dict(self) -> Dict[str, Any]:
        """将模型转换为字典"""
        return {
            'id': self.id,
            'stock_code': self.stock_code,
            'stock_name': self.stock_name,
            'total_volume': self.total_volume,
            'original_cost': self.original_cost,
            'dynamic_cost': self.dynamic_cost,
            'total_amount': self.total_amount,
            'latest_price': self.latest_price,
            'market_value': self.market_value,
            'floating_profit': self.floating_profit,
            'floating_profit_ratio': self.floating_profit_ratio,
            'created_at': self.created_at.astimezone(CN_TIMEZONE).strftime('%Y-%m-%d %H:%M:%S'),
            'updated_at': self.updated_at.astimezone(CN_TIMEZONE).strftime('%Y-%m-%d %H:%M:%S')
        }

    def update_position(self, volume: int, price: float, action: str):
        """
        更新持仓信息，使用股票软件风格的动态成本计算方式
        
        Args:
            volume: 交易量
            price: 交易价格
            action: 交易动作（buy/sell）
        """
        # 转换为Decimal以提高精度
        dec_price = Decimal(str(price))
        dec_volume = Decimal(str(volume))
        dec_original_cost = Decimal(str(self.original_cost))
        dec_total_volume = Decimal(str(self.total_volume))
        
        if action == 'buy':
            # 计算新的原始平均成本
            new_total_volume = dec_total_volume + dec_volume
            if new_total_volume > 0:
                total_cost = dec_original_cost * dec_total_volume + dec_price * dec_volume
                self.original_cost = float(total_cost / new_total_volume)
            else:
                self.original_cost = float(price)
            
            # 买入时动态成本等于原始成本
            self.dynamic_cost = self.original_cost
            self.total_volume += volume
            
        elif action == 'sell':
            if volume > self.total_volume:
                raise ValueError("卖出数量超过当前持仓量")
            
            # 计算实现的盈亏
            dec_dynamic_cost = Decimal(str(self.dynamic_cost))
            realized_profit = (dec_price - dec_dynamic_cost) * dec_volume
            
            # 调整剩余持仓的动态成本
            total_cost = dec_dynamic_cost * dec_total_volume - realized_profit
            self.total_volume -= volume
            
            if self.total_volume > 0:
                # 更新动态成本
                self.dynamic_cost = float(total_cost / Decimal(str(self.total_volume)))
            else:
                # 清仓时重置所有成本
                self.original_cost = 0
                self.dynamic_cost = 0
        
        # 更新持仓金额
        self.total_amount = self.total_volume * (self.dynamic_cost if action == 'sell' else self.original_cost)
        
        # 如果有最新价格，更新市值和浮动盈亏
        if self.latest_price:
            self.update_market_value(self.latest_price)

    def update_market_value(self, latest_price: float):
        """
        更新市值和浮动盈亏
        
        Args:
            latest_price: 最新价格
        """
        self.latest_price = latest_price
        self.market_value = self.total_volume * latest_price
        # 使用动态成本计算浮动盈亏
        self.floating_profit = self.market_value - (self.total_volume * self.dynamic_cost)
        
        # 当动态成本小于等于0时，浮动盈亏比例设为一个足够大的数字
        if self.total_volume > 0 and self.dynamic_cost <= 0:
            self.floating_profit_ratio = 999999
        else:
            # 正常情况下计算浮动盈亏比例
            self.floating_profit_ratio = (self.floating_profit / (self.total_volume * self.dynamic_cost)) if self.total_volume > 0 and self.dynamic_cost > 0 else 0 