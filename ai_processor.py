import os
import json
import logging
from typing import Dict, Any
from zhipuai import ZhipuAI

class AIStrategyProcessor:
    def __init__(self):
        self.api_key = os.getenv('ZHIPU_API_KEY')
        self.client = ZhipuAI(api_key=self.api_key)
        
        # 配置日志记录
        logging.basicConfig(level=logging.INFO)
        self.logger = logging.getLogger(__name__)
        
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
}

字段说明：
- stock_name：必填，字符串类型
- stock_code：必填，6位数字字符串
- action：选填，只能是"buy"、"sell"或null
- position_ratio：必填，0到1之间的小数，表示仓位比例
- price_min：选填，数字类型，最小执行价格
- price_max：选填，数字类型，最大执行价格
- take_profit_price：选填，数字类型，止盈价格
- stop_loss_price：选填，数字类型，止损价格
- other_conditions：选填，字符串类型，其他交易条件
- reason：选填，字符串类型，操作理由

注意事项：
1. 你必须严格按照上述 JSON 格式返回数据
2. 不要返回 Python 代码、函数调用或其他格式
3. 所有数字字段必须是数值类型，不能带引号
4. 所有字符串字段必须带引号
5. 选填字段如果没有值，使用 null
6. 不要添加任何注释、说明文字或代码块标记

示例输入和输出：

1. 输入："今天天气真好"
输出：{"error": "与股票交易无关，暂不处理"}

2. 输入："茅台现在多少钱"
输出：{"error": "与股票交易无关，暂不处理"}

3. 输入："以30元买入平安银行(000001)，仓位30%，止盈34元，止损28元"
输出：
{
    "stock_name": "平安银行",
    "stock_code": "000001",
    "action": "buy",
    "position_ratio": 0.3,
    "price_min": 30,
    "price_max": 30,
    "take_profit_price": 34,
    "stop_loss_price": 28,
    "other_conditions": null,
    "reason": null
}

4. 输入："国科微(300672)的分析：价格区间64.8-65元，建议仓位10%，止盈69元，止损59元。公司在SoC芯片领域有优势。"
输出：
{
    "stock_name": "国科微",
    "stock_code": "300672",
    "action": null,
    "position_ratio": 0.1,
    "price_min": 64.8,
    "price_max": 65,
    "take_profit_price": 69,
    "stop_loss_price": 59,
    "other_conditions": null,
    "reason": "公司在SoC芯片领域有优势"
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

    def call_ai_api(self, user_input: str, retry_count: int = 0) -> Dict[str, Any]:
        """调用 AI API 并处理响应"""
        if retry_count >= 3:
            raise Exception("已达到最大重试次数(3次)，仍未获得有效响应")

        try:
            # 构建请求消息
            messages = [
                {"role": "system", "content": self.system_prompt},
                {"role": "user", "content": user_input}
            ]
            
            # 如果是重试，添加额外提示
            if retry_count > 0:
                messages.append({
                    "role": "user",
                    "content": f"请严格按照示例格式返回 JSON 数据，不要包含任何其他内容。这是第 {retry_count + 1} 次尝试。"
                })
            
            # 调用智谱 AI 接口
            self.logger.info(f"调用AI (第 {retry_count + 1} 次尝试)")
            response = self.client.chat.completions.create(
                model="glm-4",
                messages=messages,
                temperature=0.1,
                max_tokens=2000
            )
            
            # 获取返回的文本内容
            content = response.choices[0].message.content.strip()
            self.logger.info(f"AI响应原始内容:\n{content}")
            
            # 提取和清理 JSON
            import re
            json_match = re.search(r'\{[^{]*\}', content, re.DOTALL)
            if not json_match:
                self.logger.error("未找到有效的 JSON 数据")
                return self.call_ai_api(user_input, retry_count + 1)
            
            content = json_match.group()
            content = re.sub(r'//.*?\n', '\n', content)
            content = re.sub(r'/\*.*?\*/', '', content, flags=re.DOTALL)
            content = '\n'.join(line.strip() for line in content.splitlines() if line.strip())
            
            self.logger.info(f"清理后的JSON:\n{content}")
            
            try:
                result = json.loads(content)
                self.logger.info(f"JSON解析成功:\n{json.dumps(result, ensure_ascii=False, indent=2)}")
            except json.JSONDecodeError as e:
                self.logger.error(f"JSON 解析失败: {str(e)}")
                return self.call_ai_api(user_input, retry_count + 1)
            
            # 验证 JSON Schema
            if not self.validate_json_schema(result):
                self.logger.error("JSON Schema 验证失败，将重试")
                return self.call_ai_api(user_input, retry_count + 1)
            
            return result
            
        except Exception as e:
            self.logger.error(f"API 调用失败: {str(e)}")
            return self.call_ai_api(user_input, retry_count + 1)

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
        import re
        # 匹配形如 (000001) 或 （000001） 的模式
        pattern = r'[（(](\d{6})[)）]'
        match = re.search(pattern, text)
        return match.group(1) if match else None 