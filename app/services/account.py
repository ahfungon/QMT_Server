"""
账户资金服务模块

此模块提供账户资金相关的业务逻辑处理
"""

import logging
from typing import Dict, Any, Optional
from ..models import db
from ..models.account import AccountFunds
from ..models.position import StockPosition

logger = logging.getLogger(__name__)

class AccountService:
    """账户资金服务类"""
    
    def get_account_funds(self) -> Dict[str, Any]:
        """
        获取账户资金信息，同时更新资产总值
        
        Returns:
            Dict[str, Any]: 账户资金信息
        """
        try:
            # 获取账户信息（总是获取ID为1的记录）
            account = AccountFunds.query.get(1)
            if not account:
                # 如果不存在则创建初始账户
                account = AccountFunds(
                    initial_assets=300000.00,  # 初始资金30万
                    total_assets=300000.00,  # 初始总资产30万
                    available_funds=300000.00,  # 初始可用资金30万
                    frozen_funds=0.00,  # 初始冻结资金0
                    total_profit=0.00,  # 初始总盈亏0
                    total_profit_ratio=0.00  # 初始收益率0
                )
                db.session.add(account)
                db.session.commit()
            
            # 计算所有持仓的市值总和
            positions = StockPosition.query.all()
            total_market_value = sum(position.market_value or 0 for position in positions)
            
            # 更新资产总值（可用资金 + 冻结资金 + 持仓市值）
            account.total_assets = account.available_funds + account.frozen_funds + total_market_value
            # 更新总盈亏和收益率
            account.update_profit()
            db.session.commit()
            
            logger.info(f"账户资金信息：总资产={account.total_assets}, 可用资金={account.available_funds}, "
                       f"冻结资金={account.frozen_funds}, 总收益率={account.total_profit_ratio}%")
            return account.to_dict()
            
        except Exception as e:
            logger.error(f"获取账户资金信息失败: {str(e)}")
            raise
    
    def update_funds(self, available_funds: float, frozen_funds: float) -> Dict[str, Any]:
        """
        更新账户资金
        
        Args:
            available_funds: 可用资金
            frozen_funds: 冻结资金
            
        Returns:
            Dict[str, Any]: 更新后的账户资金信息
        """
        try:
            account = AccountFunds.query.get(1)
            if not account:
                raise ValueError("账户信息不存在")
            
            account.available_funds = available_funds
            account.frozen_funds = frozen_funds
            
            # 更新总资产
            positions = StockPosition.query.all()
            total_market_value = sum(position.market_value or 0 for position in positions)
            account.total_assets = available_funds + frozen_funds + total_market_value
            # 更新总盈亏和收益率
            account.update_profit()
            
            db.session.commit()
            logger.info(f"更新账户资金：总资产={account.total_assets}, 可用资金={available_funds}, "
                       f"冻结资金={frozen_funds}, 总收益率={account.total_profit_ratio}%")
            return account.to_dict()
            
        except Exception as e:
            db.session.rollback()
            logger.error(f"更新账户资金失败: {str(e)}")
            raise
    
    def freeze_funds(self, amount: float) -> Dict[str, Any]:
        """
        冻结资金
        
        Args:
            amount: 要冻结的金额
            
        Returns:
            Dict[str, Any]: 更新后的账户资金信息
        """
        try:
            account = AccountFunds.query.get(1)
            if not account:
                raise ValueError("账户信息不存在")
            
            if amount > account.available_funds:
                raise ValueError(f"可用资金不足：需要 {amount}，实际可用 {account.available_funds}")
            
            account.available_funds -= amount
            account.frozen_funds += amount
            # 更新总盈亏和收益率（总资产不变，但为了保持一致性，仍然调用更新方法）
            account.update_profit()
            db.session.commit()
            
            logger.info(f"冻结资金 {amount}：可用资金={account.available_funds}, 冻结资金={account.frozen_funds}, "
                       f"总收益率={account.total_profit_ratio}%")
            return account.to_dict()
            
        except Exception as e:
            db.session.rollback()
            logger.error(f"冻结资金失败: {str(e)}")
            raise
    
    def unfreeze_funds(self, amount: float) -> Dict[str, Any]:
        """
        解冻资金
        
        Args:
            amount: 要解冻的金额
            
        Returns:
            Dict[str, Any]: 更新后的账户资金信息
        """
        try:
            account = AccountFunds.query.get(1)
            if not account:
                raise ValueError("账户信息不存在")
            
            if amount > account.frozen_funds:
                raise ValueError(f"冻结资金不足：需要解冻 {amount}，实际冻结 {account.frozen_funds}")
            
            account.frozen_funds -= amount
            account.available_funds += amount
            # 更新总盈亏和收益率（总资产不变，但为了保持一致性，仍然调用更新方法）
            account.update_profit()
            db.session.commit()
            
            logger.info(f"解冻资金 {amount}：可用资金={account.available_funds}, 冻结资金={account.frozen_funds}, "
                       f"总收益率={account.total_profit_ratio}%")
            return account.to_dict()
            
        except Exception as e:
            db.session.rollback()
            logger.error(f"解冻资金失败: {str(e)}")
            raise 