"""
股价自动更新器模块

此模块提供自动更新股票价格的功能
"""

import time
import threading
from datetime import datetime, time as dt_time
import pytz
from flask import current_app
from ..services.position import PositionService
from ..utils.logger import setup_logger

logger = setup_logger('price_updater')
CN_TIMEZONE = pytz.timezone('Asia/Shanghai')

class PriceUpdater(threading.Thread):
    """股价更新器"""
    
    # 定义交易时间
    MORNING_START = dt_time(9, 30)  # 上午开盘时间 9:30
    MORNING_END = dt_time(11, 30)   # 上午收盘时间 11:30
    AFTERNOON_START = dt_time(13, 0) # 下午开盘时间 13:00
    AFTERNOON_END = dt_time(15, 0)   # 下午收盘时间 15:00
    
    # 定义更新间隔（秒）
    TRADING_INTERVAL = 30      # 交易时段更新间隔：30秒
    NON_TRADING_INTERVAL = 300 # 非交易时段更新间隔：5分钟
    
    def __init__(self, app, interval: int = None):
        """
        初始化更新器
        Args:
            app: Flask应用实例
            interval: 自定义更新间隔（秒），如果不指定则根据交易时间自动调整
        """
        super().__init__()
        self.app = app
        self.custom_interval = interval
        self.running = True
        self.daemon = True  # 设置为守护线程，随主进程退出而退出
        
    def is_trading_time(self) -> bool:
        """
        判断当前是否为交易时间
        
        Returns:
            bool: 是否为交易时间
        """
        now = datetime.now(CN_TIMEZONE)
        current_time = now.time()
        
        # 判断是否为工作日（周一到周五）
        if now.weekday() >= 5:  # 5和6代表周六和周日
            return False
            
        # 判断是否在交易时段
        morning_session = self.MORNING_START <= current_time <= self.MORNING_END
        afternoon_session = self.AFTERNOON_START <= current_time <= self.AFTERNOON_END
        
        return morning_session or afternoon_session
        
    def get_current_interval(self) -> int:
        """
        获取当前应该使用的更新间隔
        
        Returns:
            int: 更新间隔（秒）
        """
        if self.custom_interval:
            return self.custom_interval
            
        return self.TRADING_INTERVAL if self.is_trading_time() else self.NON_TRADING_INTERVAL
        
    def run(self):
        """运行更新任务"""
        logger.info(f"【后端自动】股价更新器启动")
        
        while self.running:
            try:
                # 获取当前应该使用的更新间隔
                current_interval = self.get_current_interval()
                is_trading = self.is_trading_time()
                
                # 在应用上下文中执行更新操作
                with self.app.app_context():
                    position_service = PositionService()
                    if is_trading:
                        logger.info(f"【后端自动】开始更新所有持仓的市值信息... (当前为交易时段，更新间隔: {current_interval}秒)")
                    else:
                        logger.info(f"【后端自动】开始更新所有持仓的市值信息... (当前为非交易时段，更新间隔: {current_interval}秒)")
                    
                    # 更新所有持仓的市值信息
                    positions = position_service.update_all_positions()
                    if positions:
                        logger.info(f"【后端自动】成功更新 {len(positions)} 个持仓的市值信息")
                    else:
                        logger.info("【后端自动】当前没有需要更新的持仓")
                        
            except Exception as e:
                logger.error(f"【后端自动】更新市值失败: {str(e)}")
                
            time.sleep(current_interval)
                
    def stop(self):
        """停止更新任务"""
        self.running = False
        logger.info("【后端自动】股价更新器已停止") 