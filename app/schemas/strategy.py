"""
策略数据验证模式模块

此模块定义了策略相关的数据验证模式
"""

from typing import Optional
from pydantic import BaseModel, Field, validator

class StrategyBase(BaseModel):
    """策略基础模式"""
    stock_name: str = Field(..., description="股票名称")
    stock_code: str = Field(..., description="股票代码", pattern="^[0-9]{6}$")
    action: str = Field(..., description="执行动作", pattern="^(buy|sell)$")
    position_ratio: float = Field(..., description="操作比例", ge=0, le=1)
    price_min: Optional[float] = Field(None, description="最小执行价")
    price_max: Optional[float] = Field(None, description="最大执行价")
    take_profit_price: Optional[float] = Field(None, description="止盈价")
    stop_loss_price: Optional[float] = Field(None, description="止损价")
    other_conditions: Optional[str] = Field(None, description="其他操作条件")
    reason: Optional[str] = Field(None, description="操作理由")

    @validator('price_max')
    def validate_price_range(cls, v, values):
        """验证价格区间"""
        if v is not None and values.get('price_min') is not None:
            if v < values['price_min']:
                raise ValueError('最大执行价不能小于最小执行价')
        return v

    @validator('stop_loss_price')
    def validate_stop_loss(cls, v, values):
        """验证止损价"""
        if v is not None and values.get('price_min') is not None:
            if values['price_min'] <= v:
                raise ValueError('止损价必须小于最小执行价')
        return v

    @validator('take_profit_price')
    def validate_take_profit(cls, v, values):
        """验证止盈价"""
        if v is not None and values.get('price_max') is not None:
            if values['price_max'] >= v:
                raise ValueError('止盈价必须大于最大执行价')
        return v

class StrategyCreate(StrategyBase):
    """创建策略模式"""
    pass

class StrategyUpdate(StrategyBase):
    """更新策略模式"""
    pass

class StrategyInDB(StrategyBase):
    """数据库中的策略模式"""
    id: int
    created_at: str
    updated_at: str
    is_active: bool

    class Config:
        orm_mode = True 