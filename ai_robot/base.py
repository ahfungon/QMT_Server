"""
AI处理器基类模块

此模块定义了所有AI处理器的基础接口和共同功能
"""

import os
import json
import logging
from abc import ABC, abstractmethod
from typing import Dict, Any, List
import re

class BaseAIProcessor(ABC):
    """AI处理器基类"""
    def __init__(self):
        # 配置日志记录
        logging.basicConfig(level=logging.INFO)
        self.logger = logging.getLogger(self.__class__.__name__)
        
        # 系统提示词
        self.system_prompt = """你是一个专业的股票交易策略分析助手。你的任务是分析用户输入的策略文本，并提取关键信息。

第一步：判断用户输入是否包含以下要素中的至少两个：
1. 股票名称或股票代码
2. 交易相关信息（如价格区间、仓位、止盈止损等）
3. 交易理由或分析（如技术面、基本面分析等）

如果用户输入与股票交易完全无关（比如谈论天气、生活等），请直接返回：
{
    "error": "与股票交易无关，暂不处理"
}

第二步：如果用户输入包含足够的交易相关信息，进行策略解析，将用户输入转换为以下格式的JSON数据：

{
    "stock_name": "股票名称（字符串）",
    "stock_code": "股票代码（6位数字字符串）",
    "action": "buy或sell（字符串），如果不确定则填null",
    "position_ratio": 0.5,
    "price_min": 10.5,
    "price_max": 11.0,
    "take_profit_price": 12.0,
    "stop_loss_price": 9.5,
    "other_conditions": "其他交易条件（字符串）",
    "reason": "操作理由（字符串）"
}"""

        # 定义 JSON Schema
        self.schema = {
            "type": "object",
            "properties": {
                "error": {"type": "string"},
                "stock_name": {"type": "string"},
                "stock_code": {
                    "type": "string",
                    "pattern": "^\\d{6}$"
                },
                "action": {
                    "type": ["string", "null"],
                    "enum": ["buy", "sell", None]
                },
                "position_ratio": {
                    "type": "number",
                    "minimum": 0,
                    "maximum": 1
                },
                "price_min": {"type": ["number", "null"]},
                "price_max": {"type": ["number", "null"]},
                "take_profit_price": {"type": ["number", "null"]},
                "stop_loss_price": {"type": ["number", "null"]},
                "other_conditions": {"type": ["string", "null"]},
                "reason": {"type": ["string", "null"]}
            },
            "oneOf": [
                {
                    "required": ["error"]
                },
                {
                    "required": ["stock_name", "stock_code", "position_ratio"]
                }
            ],
            "additionalProperties": False
        }

    @abstractmethod
    def call_ai_api(self, user_input: str, retry_count: int = 0) -> Dict[str, Any]:
        """调用 AI API 并处理响应"""
        pass

    def validate_json_schema(self, data: Dict[str, Any]) -> bool:
        """验证 JSON 数据是否符合预定义的 Schema"""
        try:
            from jsonschema import validate, ValidationError
            validate(instance=data, schema=self.schema)
            self.logger.info("JSON Schema 验证通过")
            return True
        except ImportError:
            self.logger.error("jsonschema 模块未安装")
            return False
        except ValidationError as e:
            self.logger.error(f"Schema验证失败: {str(e)}")
            return False
        except Exception as e:
            self.logger.error(f"Schema验证异常: {str(e)}")
            return False

    def process_strategy(self, user_input: str) -> Dict[str, Any]:
        """处理用户输入的策略文本"""
        try:
            self.logger.info("="*50)
            self.logger.info(f"用户输入: {user_input}")
            
            # 调用 AI API 并获取结果
            result = self.call_ai_api(user_input)
            
            self.logger.info("处理结果: 策略解析成功")
            self.logger.info(f"{json.dumps(result, ensure_ascii=False, indent=2)}")
            self.logger.info("="*50)
            return result
            
        except Exception as e:
            error_msg = f"策略处理失败: {str(e)}"
            self.logger.error(error_msg)
            self.logger.info("="*50)
            raise Exception(error_msg)

    def extract_stock_code(self, text: str) -> str:
        """从文本中提取股票代码"""
        pattern = r'[（(](\d{6})[)）]'
        match = re.search(pattern, text)
        return match.group(1) if match else None

    def clean_json_content(self, content: str) -> Dict[str, Any]:
        """清理并解析JSON内容"""
        json_match = re.search(r'\{[^{]*\}', content, re.DOTALL)
        if not json_match:
            self.logger.error("未找到有效的 JSON 数据")
            raise ValueError("未找到有效的 JSON 数据")
        
        content = json_match.group()
        content = re.sub(r'//.*?\n', '\n', content)
        content = re.sub(r'/\*.*?\*/', '', content, flags=re.DOTALL)
        content = '\n'.join(line.strip() for line in content.splitlines() if line.strip())
        
        self.logger.info(f"清理后的JSON:\n{content}")
        
        try:
            result = json.loads(content)
            self.logger.info(f"JSON解析成功:\n{json.dumps(result, ensure_ascii=False, indent=2)}")
            return result
        except json.JSONDecodeError as e:
            self.logger.error(f"JSON 解析失败: {str(e)}")
            raise 