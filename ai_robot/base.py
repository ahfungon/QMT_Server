"""
AI处理器基类模块

此模块定义了所有AI处理器的基础接口和共同功能
"""

import os
import json
import logging
from abc import ABC, abstractmethod
from typing import Dict, Any, List, Tuple, Optional
import re
import requests
from urllib.parse import quote
from jsonschema import validate, ValidationError

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

第二步：分析交易动作
1. 如果文本中明确提到"买入"、"建仓"、"做多"等，设置 action 为 "buy"
2. 如果文本中明确提到"卖出"、"清仓"、"做空"等，设置 action 为 "sell"
3. 如果文本中明确提到"加仓"，设置 action 为 "add"
4. 如果文本中明确提到"减仓"，设置 action 为 "trim"
5. 如果文本中明确提到"持有"、"持仓待涨"、"观望"等，设置 action 为 "hold"
6. 如果没有明确提到交易动作，根据以下规则判断：
   - 如果提到"看好"、"上涨"、"突破"等积极词汇，设置为 "buy"
   - 如果提到"看空"、"下跌"、"跌破"等消极词汇，设置为 "sell"
   - 如果实在无法判断，默认设置为 "buy"

第三步：分析仓位比例
1. 如果文本中明确提到仓位比例（如"30%仓位"、"0.3仓"等），直接使用该数值
2. 如果文本中提到"轻仓"、"小仓"，设置为 20（表示20%）
3. 如果文本中提到"半仓"，设置为 50（表示50%）
4. 如果文本中提到"重仓"、"满仓"，设置为 80（表示80%）
5. 如果没有提到仓位信息：
   - 对于买入操作，默认设置为 10（10%仓位）
   - 对于卖出操作，默认设置为 50（50%仓位）
   - 对于加仓操作，默认设置为 10（10%仓位）
   - 对于减仓操作，默认设置为 30（30%仓位）
   - 对于持有操作，仓位比例不适用，设置为 0

第四步：将用户输入转换为以下格式的JSON数据：

{
    "stock_name": "股票名称（字符串）",
    "stock_code": "股票代码（A股6位数字，港股4-5位数字）",
    "action": "buy/sell/add/trim/hold（字符串）",
    "position_ratio": 10,  # 整数，表示百分比，范围0-100
    "price_min": 10.5,
    "price_max": 11.0,
    "take_profit_price": 12.0,
    "stop_loss_price": 9.5,
    "other_conditions": "其他交易条件（字符串）",
    "reason": "操作理由（字符串）"
}

注意：
1. position_ratio 字段必须返回，且必须是 0-100 之间的整数，表示百分比。
2. 对于 trim 操作，需要提醒用户系统会使用特殊的计算方式：减仓交易量 = 当前持股量 × (减仓比例 ÷ 原始买入仓位比例)。
3. 对于 hold 操作，position_ratio 设置为 0。"""

        # 定义 JSON Schema
        self.schema = {
            "type": "object",
            "properties": {
                "error": {"type": "string"},
                "stock_name": {"type": "string"},
                "stock_code": {
                    "type": "string",
                    "pattern": "^\\d{4,6}$"  # 支持4-6位数字
                },
                "action": {
                    "type": ["string", "null"],
                    "enum": ["buy", "sell", "add", "trim", "hold", None]
                },
                "position_ratio": {
                    "type": ["number", "null"],
                    "minimum": 0,
                    "maximum": 100
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
                    "required": ["stock_name", "stock_code"]
                }
            ],
            "additionalProperties": False
        }

    @abstractmethod
    def call_ai_api(self, user_input: str, retry_count: int = 0) -> Dict[str, Any]:
        """调用 AI API 并处理响应"""
        pass

    def get_stock_info(self, keyword: str) -> Optional[Tuple[str, str]]:
        """
        查询股票信息
        
        Args:
            keyword: 股票名称或代码关键词
            
        Returns:
            Optional[Tuple[str, str]]: (股票代码, 股票名称) 或 None
        """
        if not keyword.strip():
            return None

        try:
            api_url = f"https://suggest3.sinajs.cn/suggest/type=&key={quote(keyword)}"
            response = requests.get(api_url, timeout=5)
            response.raise_for_status()
            return self._parse_stock_info(response.text)
        except requests.RequestException as e:
            self.logger.error(f"股票信息查询失败: {str(e)}")
            return None

    def _parse_stock_info(self, response: str) -> Optional[Tuple[str, str]]:
        """
        解析股票信息响应
        
        Args:
            response: API响应文本
            
        Returns:
            Optional[Tuple[str, str]]: (股票代码, 股票名称) 或 None
        """
        result_start = response.find('"') + 1
        result_end = response.rfind('"')
        if result_start >= 0 and result_end > result_start:
            results_str = response[result_start:result_end]
            items = results_str.split(';')
            
            # 存储找到的 A 股和其他股票
            a_share = None
            other_share = None
            
            for item in items:
                fields = item.split(',')
                if len(fields) >= 5:
                    stock_code = fields[2]
                    stock_name = fields[4]
                    category = fields[3]
                    
                    # 排除指数
                    if self._is_index(category, stock_name):
                        continue
                        
                    # 判断是否为 A 股（以 00/60/30/68 开头的6位数字）
                    if re.match(r'^(00|60|30|68)\d{4}$', stock_code):
                        if not a_share:  # 记录第一个找到的 A 股
                            a_share = (stock_code, stock_name)
                    elif not other_share:  # 记录第一个找到的其他股票
                        other_share = (stock_code, stock_name)
            
            # 优先返回 A 股，如果没有则返回其他股票
            return a_share or other_share
            
        return None

    def _is_index(self, category: str, stock_name: str) -> bool:
        """
        判断是否为指数
        
        Args:
            category: 分类信息
            stock_name: 股票名称
            
        Returns:
            bool: 是否为指数
        """
        return '指数' in category or '指数' in stock_name

    def validate_json_schema(self, data: Dict[str, Any]) -> bool:
        """验证JSON数据是否符合预定义的模式"""
        try:
            # 如果缺少股票代码但有股票名称，尝试查询补充
            if data.get('stock_code') is None and data.get('stock_name'):
                stock_info = self.get_stock_info(data['stock_name'])
                if stock_info:
                    data['stock_code'] = stock_info[0]
                    self.logger.info(f"自动补充股票代码: {data['stock_code']}")
            
            # 如果缺少股票名称但有股票代码，尝试查询补充
            elif data.get('stock_name') is None and data.get('stock_code'):
                stock_info = self.get_stock_info(data['stock_code'])
                if stock_info:
                    data['stock_name'] = stock_info[1]
                    self.logger.info(f"自动补充股票名称: {data['stock_name']}")

            # 验证JSON Schema
            validate(instance=data, schema=self.schema)
            return True
            
        except ValidationError as e:
            self.logger.error(f"Schema验证失败: {str(e)}\n\n{e.absolute_path}\n\nOn instance:\n{e.instance}")
            return False
        except Exception as e:
            self.logger.error(f"验证过程发生错误: {str(e)}")
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
            
            # 如果是有效的策略数据（不是错误信息）
            if 'error' not in result:
                # 只有在缺少股票代码或名称其中之一时，才调用新浪接口查询
                if bool(result.get('stock_code')) != bool(result.get('stock_name')):
                    # 使用已有的信息查询
                    search_key = result.get('stock_code') or result.get('stock_name')
                    stock_info = self.get_stock_info(search_key)
                    if stock_info:
                        result['stock_code'] = stock_info[0]  # 标准化的股票代码
                        result['stock_name'] = stock_info[1]  # 股票名称
                        self.logger.info(f"自动补充股票信息: {stock_info}")
                    else:
                        self.logger.warning(f"未找到股票信息: {search_key}")
            
            self.logger.info(f"JSON解析成功:\n{json.dumps(result, ensure_ascii=False, indent=2)}")
            return result
        except json.JSONDecodeError as e:
            self.logger.error(f"JSON 解析失败: {str(e)}")
            raise 