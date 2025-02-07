"""
DeepSeek AI处理器模块

此模块实现了DeepSeek AI的具体调用逻辑
"""

import os
import requests
from typing import Dict, Any
from .base import BaseAIProcessor

class DeepseekAIProcessor(BaseAIProcessor):
    """DeepSeek AI处理器"""
    def __init__(self):
        super().__init__()
        self.api_key = os.getenv('DEEPSEEK_API_KEY')
        if not self.api_key:
            raise ValueError("未找到DEEPSEEK_API_KEY环境变量")
        self.api_url = "https://api.deepseek.com/v1/chat/completions"

    def call_ai_api(self, user_input: str, retry_count: int = 0) -> Dict[str, Any]:
        """调用DeepSeek API并处理响应"""
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
            
            # 调用DeepSeek API
            self.logger.info(f"调用DeepSeek AI (第 {retry_count + 1} 次尝试)")
            headers = {
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json"
            }
            data = {
                "model": "deepseek-chat",
                "messages": messages,
                "temperature": 0.1,
                "max_tokens": 2000
            }
            
            response = requests.post(self.api_url, headers=headers, json=data)
            response.raise_for_status()
            
            # 获取返回的文本内容
            content = response.json()['choices'][0]['message']['content'].strip()
            self.logger.info(f"AI响应原始内容:\n{content}")
            
            # 清理和验证JSON
            try:
                result = self.clean_json_content(content)
                if not self.validate_json_schema(result):
                    return self.call_ai_api(user_input, retry_count + 1)
                return result
            except Exception as e:
                self.logger.error(f"JSON处理失败: {str(e)}")
                return self.call_ai_api(user_input, retry_count + 1)
            
        except Exception as e:
            self.logger.error(f"API 调用失败: {str(e)}")
            return self.call_ai_api(user_input, retry_count + 1) 