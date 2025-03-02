"""
持仓服务模块

此模块提供持仓相关的业务逻辑处理
"""

import logging
import requests
import time
from typing import List, Dict, Any, Optional
from ..models import db
from ..models.position import StockPosition
import random
from decimal import Decimal

logger = logging.getLogger(__name__)

class PositionService:
    """持仓服务类"""
    
    # 股票价格缓存
    __price_cache = {}
    # 缓存过期时间（秒）
    CACHE_EXPIRY = 60  # 1分钟缓存
    
    def get_real_time_price(self, stock_code: str) -> Optional[float]:
        """
        获取股票实时价格
        
        Args:
            stock_code: 股票代码
            
        Returns:
            Optional[float]: 股票最新价格，如果获取失败则返回 None
        """
        # 检查缓存
        if stock_code in self.__price_cache:
            cache_item = self.__price_cache[stock_code]
            # 如果缓存未过期，返回缓存的价格
            if time.time() - cache_item['timestamp'] < self.CACHE_EXPIRY:
                logger.debug(f"从缓存获取股票 {stock_code} 的价格: {cache_item['price']}")
                return cache_item['price']
        
        try:
            # 处理港股代码
            if len(stock_code) == 4 and stock_code.isdigit():
                stock_code = f"hk0{stock_code}"
            elif len(stock_code) == 5 and stock_code.startswith('0') and stock_code[1:].isdigit():
                stock_code = f"hk{stock_code}"
            
            # 判断股票市场
            if stock_code.startswith('hk'):
                market = "hk"
                full_code = stock_code
            else:
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
                        latest_price = float(data[6] if market == "hk" else data[3])  # 港股价格在第7个位置
                        if latest_price > 0:  # 确保价格有效
                            logger.info(f"从新浪获取到股票 {stock_code} 的最新价格: {latest_price}")
                            # 更新缓存
                            self.__price_cache[stock_code] = {
                                'price': latest_price,
                                'timestamp': time.time()
                            }
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
                            # 更新缓存
                            self.__price_cache[stock_code] = {
                                'price': latest_price,
                                'timestamp': time.time()
                            }
                            return latest_price
            
            # 如果都失败了，尝试东方财富接口
            eastmoney_headers = headers.copy()
            eastmoney_headers.update({
                'Referer': 'https://quote.eastmoney.com'
            })
            
            market_id = '1' if market == 'sh' else ('0' if market == 'sz' else '116')  # 港股市场ID为116
            response = requests.get(
                f"https://push2.eastmoney.com/api/qt/stock/get?secid={market_id}.{stock_code.replace('hk', '')}",
                headers=eastmoney_headers,
                timeout=5
            )
            
            if response.status_code == 200:
                data = response.json()
                if 'data' in data and 'f43' in data['data']:
                    latest_price = float(data['data']['f43']) / 100  # 东方财富的价格需要除以100
                    if latest_price > 0:
                        logger.info(f"从东方财富获取到股票 {stock_code} 的最新价格: {latest_price}")
                        # 更新缓存
                        self.__price_cache[stock_code] = {
                            'price': latest_price,
                            'timestamp': time.time()
                        }
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
            
            # 优化：一次性收集所有股票代码
            stock_codes = list(set([position.stock_code for position in positions]))
            
            # 先获取所有价格，再更新持仓，减少API请求和数据库操作
            price_map = {}
            for stock_code in stock_codes:
                latest_price = self.get_real_time_price(stock_code)
                if latest_price:
                    price_map[stock_code] = latest_price
            
            # 更新所有持仓
            for position in positions:
                if position.stock_code in price_map:
                    position.update_market_value(price_map[position.stock_code])
            
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

    def update_position(self, stock_code: str, stock_name: str, volume: int, price: float, action: str, position_ratio: float = None, original_position_ratio: float = None) -> Dict[str, Any]:
        """
        更新持仓信息
        
        Args:
            stock_code: 股票代码
            stock_name: 股票名称
            volume: 交易量
            price: 交易价格
            action: 交易动作（buy/sell/add/trim/hold）
            position_ratio: 仓位比例
            original_position_ratio: 原始买入仓位比例（用于trim操作）
            
        Returns:
            Dict[str, Any]: 更新后的持仓信息
        """
        try:
            # 获取或创建持仓记录
            position = StockPosition.query.filter_by(stock_code=stock_code).first()
            
            # 处理hold操作：不进行实际交易，仅记录策略
            if action == 'hold':
                if not position:
                    logger.warning(f"股票 {stock_code} 没有持仓，不能执行hold操作")
                    return None
                logger.info(f"股票 {stock_code} 执行hold操作，不进行实际交易")
                return position.to_dict() if position else None
            
            if not position:
                if action in ['sell', 'trim']:
                    raise ValueError(f"股票 {stock_code} 没有持仓，无法执行 {action} 操作")
                position = StockPosition(
                    stock_code=stock_code,
                    stock_name=stock_name,
                    total_volume=0,
                    original_cost=0,
                    total_amount=0
                )
                db.session.add(position)
            
            # 检查卖出/减仓数量是否超过持仓
            if action in ['sell', 'trim'] and volume > position.total_volume:
                raise ValueError(f"{action}数量 {volume} 超过持仓数量 {position.total_volume}")
            
            # 更新原始仓位比例
            if action == 'buy':
                # 首次买入，直接设置原始仓位比例
                position.original_position_ratio = position_ratio
                logger.info(f"首次买入：设置原始仓位比例为 {position_ratio}")
            elif action == 'add':
                # 加仓操作，累加原始仓位比例
                current_ratio = position.original_position_ratio or 0
                position.original_position_ratio = current_ratio + position_ratio
                logger.info(f"加仓操作：原始仓位比例从 {current_ratio} 更新为 {position.original_position_ratio}")
            elif action == 'trim' and original_position_ratio is not None:
                # 减仓操作，直接使用执行记录服务计算好的原始仓位比例
                position.original_position_ratio = original_position_ratio
                logger.info(f"减仓操作：更新原始仓位比例为 {original_position_ratio}")
            elif action == 'sell':
                # 卖出操作，如果是清仓则清除原始仓位比例
                if volume == position.total_volume:
                    position.original_position_ratio = None
                    logger.info("清仓操作：清除原始仓位比例")
            
            # 更新持仓信息
            if action in ['buy', 'add']:
                # 买入或加仓操作，基本逻辑相同
                self._update_position_buy(position, volume, price)
            elif action == 'sell':
                # 卖出操作
                self._update_position_sell(position, volume, price)
            elif action == 'trim':
                # 减仓操作
                self._update_position_trim(position, volume, price)
            
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
    
    def _update_position_buy(self, position: StockPosition, volume: int, price: float):
        """
        处理买入/加仓操作
        
        Args:
            position: 持仓对象
            volume: 交易量
            price: 交易价格
        """
        # 转换为Decimal以提高精度
        dec_price = Decimal(str(price))
        dec_volume = Decimal(str(volume))
        dec_original_cost = Decimal(str(position.original_cost))
        dec_total_volume = Decimal(str(position.total_volume))
        
        # 计算新的原始平均成本
        new_total_volume = dec_total_volume + dec_volume
        if new_total_volume > 0:
            total_cost = dec_original_cost * dec_total_volume + dec_price * dec_volume
            position.original_cost = float(total_cost / new_total_volume)
        else:
            position.original_cost = float(price)
        
        # 买入时动态成本等于原始成本
        position.dynamic_cost = position.original_cost
        position.total_volume += volume
        
        # 更新持仓金额
        position.total_amount = position.total_volume * position.original_cost
        
        # 如果有最新价格，更新市值和浮动盈亏
        if position.latest_price:
            position.update_market_value(position.latest_price)
    
    def _update_position_sell(self, position: StockPosition, volume: int, price: float):
        """
        处理卖出操作
        
        Args:
            position: 持仓对象
            volume: 交易量
            price: 交易价格
        """
        # 转换为Decimal以提高精度
        dec_price = Decimal(str(price))
        dec_volume = Decimal(str(volume))
        dec_total_volume = Decimal(str(position.total_volume))
        
        # 使用新公式计算卖出后的动态成本
        # 新成本价 = (原持仓数量 × 原成本价 - 卖出数量 × 卖出价) / (原持仓数量 - 卖出数量)
        dec_dynamic_cost = Decimal(str(position.dynamic_cost))
        remaining_volume = dec_total_volume - dec_volume
        
        if remaining_volume > 0:
            # 计算新的动态成本
            new_total_cost = dec_dynamic_cost * dec_total_volume - dec_price * dec_volume
            position.dynamic_cost = float(new_total_cost / remaining_volume)
            # 如果计算结果为负数，设置为0
            if position.dynamic_cost < 0:
                position.dynamic_cost = 0
        else:
            # 清仓时重置所有成本
            position.original_cost = 0
            position.dynamic_cost = 0
            position.original_position_ratio = None
        
        position.total_volume -= volume
        
        # 更新持仓金额
        position.total_amount = position.total_volume * position.dynamic_cost
        
        # 如果有最新价格，更新市值和浮动盈亏
        if position.latest_price:
            position.update_market_value(position.latest_price)
    
    def _update_position_trim(self, position: StockPosition, volume: int, price: float):
        """
        处理减仓操作
        
        Args:
            position: 持仓对象
            volume: 交易量
            price: 交易价格
        """
        # 减仓本质上也是卖出操作，逻辑与卖出相同
        self._update_position_sell(position, volume, price)

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