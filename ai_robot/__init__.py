"""
AI机器人包

此包包含了所有AI模型的实现，每个模型都有自己的独立实现文件。
"""

import os
import logging
from .base import BaseAIProcessor
from .zhipu import ZhipuAIProcessor
from .deepseek import DeepseekAIProcessor

# 配置日志
logger = logging.getLogger(__name__)

def create_ai_processor() -> BaseAIProcessor:
    """
    创建AI处理器实例
    
    从环境变量 AI_TYPE 读取配置，可选值：'zhipu', 'deepseek'，默认为'zhipu'
        
    Returns:
        BaseAIProcessor: AI处理器实例
    """
    ai_type = os.getenv('AI_TYPE', 'zhipu').lower()
    logger.info("="*50)
    logger.info(f"正在初始化 AI 处理器...")
    logger.info(f"当前选择的 AI 模型: {ai_type}")
    logger.info("="*50)
    
    if ai_type == 'deepseek':
        return DeepseekAIProcessor()
    return ZhipuAIProcessor()  # 默认使用智谱AI 