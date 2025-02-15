"""
持仓服务模块

此模块提供持仓相关的业务逻辑处理
"""

import logging
import requests
from typing import List, Dict, Any, Optional
from ..models import db
from ..models.position import StockPosition

logger = logging.getLogger(__name__)

class PositionService:
    """持仓服务类"""
    
    def get_real_time_price(self, stock_code: str) -> Optional[float]:
        """
        获取股票实时价格
        
        Args:
            stock_code: 股票代码
            
        Returns:
            Optional[float]: 股票最新价格，如果获取失败则返回 None
        """
        try:
            # 判断股票市场（上海/深圳）
            market = "sh" if stock_code.startswith(('6', '9')) else "sz"
            full_code = f"{market}{stock_code}"
            
            # 设置通用请求头
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36',
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
                'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8',
                'Connection': 'keep-alive'
            }
            
            # 尝试从新浪接口获取数据
            sina_headers = headers.copy()
            sina_headers.update({
                'Referer': 'https://finance.sina.com.cn'
            })
            
            response = requests.get(
                f"https://hq.sinajs.cn/list={full_code}",
                headers=sina_headers,
                timeout=5  # 设置5秒超时
            )
            
            if response.status_code == 200:
                # 解析返回数据
                content = response.content.decode('gbk')  # 新浪接口使用GBK编码
                if 'FAILED' not in content:
                    data = content.split('=')[1].strip('"').split(',')
                    if len(data) > 3:
                        latest_price = float(data[3])  # 当前价格在第4个位置
                        if latest_price > 0:  # 确保价格有效
                            logger.info(f"从新浪获取到股票 {stock_code} 的最新价格: {latest_price}")
                            return latest_price
            
            # 如果新浪接口失败，尝试腾讯接口
            tencent_headers = headers.copy()
            tencent_headers.update({
                'Referer': 'https://finance.qq.com'
            })
            
            response = requests.get(
                f"https://qt.gtimg.cn/q={full_code}",
                headers=tencent_headers,
                timeout=5
            )
            
            if response.status_code == 200:
                content = response.content.decode('gbk')  # 腾讯接口也使用GBK编码
                if 'v_' in content:  # 确认返回了有效数据
                    data = content.split('~')
                    if len(data) > 3:
                        latest_price = float(data[3])
                        if latest_price > 0:  # 确保价格有效
                            logger.info(f"从腾讯获取到股票 {stock_code} 的最新价格: {latest_price}")
                            return latest_price
            
            # 如果都失败了，尝试东方财富接口
            eastmoney_headers = headers.copy()
            eastmoney_headers.update({
                'Referer': 'https://quote.eastmoney.com'
            })
            
            market_id = '1' if market == 'sh' else '0'
            response = requests.get(
                f"https://push2.eastmoney.com/api/qt/stock/get?secid={market_id}.{stock_code}&fields=f43",
                headers=eastmoney_headers,
                timeout=5
            )
            
            if response.status_code == 200:
                data = response.json()
                if 'data' in data and 'f43' in data['data']:
                    latest_price = float(data['data']['f43']) / 100  # 东方财富的价格需要除以100
                    if latest_price > 0:
                        logger.info(f"从东方财富获取到股票 {stock_code} 的最新价格: {latest_price}")
                        return latest_price
            
            logger.warning(f"无法从任何数据源获取股票 {stock_code} 的实时价格")
            return None
            
        except requests.Timeout:
            logger.error(f"获取股票 {stock_code} 实时价格超时")
            return None
        except requests.RequestException as e:
            logger.error(f"获取股票 {stock_code} 实时价格请求异常: {str(e)}")
            return None
        except ValueError as e:
            logger.error(f"解析股票 {stock_code} 价格数据失败: {str(e)}")
            return None
        except Exception as e:
            logger.error(f"获取股票 {stock_code} 实时价格发生未知错误: {str(e)}")
            return None
    
    def update_all_positions(self) -> List[Dict[str, Any]]:
        """
        更新所有持仓的市值信息
        
        Returns:
            List[Dict[str, Any]]: 更新后的持仓列表
        """
        try:
            positions = StockPosition.query.all()
            for position in positions:
                latest_price = self.get_real_time_price(position.stock_code)
                if latest_price:
                    position.update_market_value(latest_price)
            
            db.session.commit()
            return [position.to_dict() for position in positions]
            
        except Exception as e:
            db.session.rollback()
            logger.error(f"更新所有持仓市值失败: {str(e)}")
            raise

    def get_all_positions(self) -> List[Dict[str, Any]]:
        """获取所有持仓"""
        try:
            positions = StockPosition.query.all()
            return [position.to_dict() for position in positions]
        except Exception as e:
            logger.error(f"获取持仓列表失败: {str(e)}", exc_info=True)
            raise

    def get_position(self, stock_code: str) -> Optional[Dict[str, Any]]:
        """获取单个股票的持仓"""
        try:
            position = StockPosition.query.filter_by(stock_code=stock_code).first()
            return position.to_dict() if position else None
        except Exception as e:
            logger.error(f"获取持仓信息失败: {str(e)}", exc_info=True)
            raise

    def update_position(self, stock_code: str, stock_name: str, volume: int, price: float, action: str) -> Dict[str, Any]:
        """
        更新持仓信息
        
        Args:
            stock_code: 股票代码
            stock_name: 股票名称
            volume: 交易量
            price: 交易价格
            action: 交易动作（buy/sell）
            
        Returns:
            Dict[str, Any]: 更新后的持仓信息
        """
        try:
            # 获取或创建持仓记录
            position = StockPosition.query.filter_by(stock_code=stock_code).first()
            if not position:
                if action == 'sell':
                    raise ValueError(f"股票 {stock_code} 没有持仓，无法卖出")
                position = StockPosition(
                    stock_code=stock_code,
                    stock_name=stock_name,
                    total_volume=0,
                    original_cost=0,
                    total_amount=0
                )
                db.session.add(position)
            
            # 检查卖出数量是否超过持仓
            if action == 'sell' and volume > position.total_volume:
                raise ValueError(f"卖出数量 {volume} 超过持仓数量 {position.total_volume}")
            
            # 更新持仓信息
            position.update_position(volume, price, action)
            
            # 如果持仓数量为0，删除持仓记录
            if position.total_volume == 0:
                db.session.delete(position)
                logger.info(f"股票 {stock_code} 持仓数量为0，删除持仓记录")
                db.session.commit()
                return None
            
            db.session.commit()
            return position.to_dict()
            
        except Exception as e:
            db.session.rollback()
            logger.error(f"更新持仓失败: {str(e)}", exc_info=True)
            raise

    def update_market_value(self, stock_code: str, latest_price: float) -> Dict[str, Any]:
        """
        更新股票市值
        
        Args:
            stock_code: 股票代码
            latest_price: 最新价格
            
        Returns:
            Dict[str, Any]: 更新后的持仓信息
        """
        try:
            position = StockPosition.query.filter_by(stock_code=stock_code).first()
            if not position:
                raise ValueError(f"股票 {stock_code} 没有持仓记录")
            
            position.update_market_value(latest_price)
            db.session.commit()
            return position.to_dict()
            
        except Exception as e:
            db.session.rollback()
            logger.error(f"更新市值失败: {str(e)}", exc_info=True)
            raise 