"""
智谱AI处理器模块

此模块实现了智谱AI的具体调用逻辑
"""

import os
from typing import Dict, Any
from zhipuai import ZhipuAI
from .base import BaseAIProcessor

class ZhipuAIProcessor(BaseAIProcessor):
    """智谱AI处理器"""
    def __init__(self):
        super().__init__()
        self.api_key = os.getenv('ZHIPU_API_KEY')
        if not self.api_key:
            raise ValueError("未找到ZHIPU_API_KEY环境变量")
        self.client = ZhipuAI(api_key=self.api_key)

    def call_ai_api(self, user_input: str, retry_count: int = 0) -> Dict[str, Any]:
        """调用智谱AI API并处理响应"""
        max_retries = 3
        current_retry = retry_count
        
        while current_retry < max_retries:
            try:
                # 构建请求消息
                messages = [
                    {"role": "system", "content": self.system_prompt},
                    {"role": "user", "content": user_input}
                ]
                
                # 如果是重试，添加额外提示
                if current_retry > 0:
                    messages.append({
                        "role": "user",
                        "content": f"请严格按照示例格式返回 JSON 数据，确保返回股票代码。这是第 {current_retry + 1} 次尝试。"
                    })
                
                # 调用智谱 AI 接口
                self.logger.info(f"调用智谱AI (第 {current_retry + 1} 次尝试)")
                response = self.client.chat.completions.create(
                    model="glm-4-flash",
                    messages=messages,
                    temperature=0.1,
                    max_tokens=2000
                )
                
                # 获取返回的文本内容
                content = response.choices[0].message.content.strip()
                self.logger.info(f"AI响应原始内容:\n{content}")
                
                # 清理和验证JSON
                result = self.clean_json_content(content)
                
                # 如果验证通过，直接返回
                if self.validate_json_schema(result):
                    return result
                    
                # 如果验证失败，记录错误并继续重试
                current_retry += 1
                
            except Exception as e:
                self.logger.error(f"API 调用失败: {str(e)}")
                current_retry += 1
                
        # 如果达到最大重试次数，返回错误信息
        return {
            "error": "AI 服务暂时无法正确解析策略，请稍后重试或提供更详细的信息"
        } 