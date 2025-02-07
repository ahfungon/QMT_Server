"""
DeepSeek AI处理器模块

此模块实现了DeepSeek AI的具体调用逻辑
"""

import os
from typing import Dict, Any
import httpx
from openai import OpenAI, APITimeoutError, APIError
import json
from .base import BaseAIProcessor

class DeepseekAIProcessor(BaseAIProcessor):
    """DeepSeek AI处理器"""
    def __init__(self):
        super().__init__()
        self.api_key = os.getenv('DEEPSEEK_API_KEY')
        if not self.api_key:
            raise ValueError("未找到DEEPSEEK_API_KEY环境变量")
        
        # 创建httpx客户端，设置较长的超时时间
        timeout = httpx.Timeout(
            timeout=120.0,  # 总超时时间
            connect=30.0,   # 连接超时
            read=90.0,      # 读取超时
            write=30.0      # 写入超时
        )
        
        transport = httpx.HTTPTransport(
            retries=3,  # 传输层重试次数
            verify=True # SSL验证
        )
        
        http_client = httpx.Client(
            timeout=timeout,
            transport=transport,
            follow_redirects=True
        )
        
        # 初始化OpenAI客户端
        self.client = OpenAI(
            api_key=self.api_key,
            base_url="https://api.deepseek.com/v1",
            http_client=http_client
        )

    def call_ai_api(self, user_input: str, retry_count: int = 0) -> Dict[str, Any]:
        """调用DeepSeek API并处理响应"""
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
                
                # 调用DeepSeek API
                self.logger.info(f"调用DeepSeek AI (第 {current_retry + 1} 次尝试)")
                response = self.client.chat.completions.create(
                    model="deepseek-chat",
                    messages=messages,
                    stream=False,
                    temperature=0.1  # 降低随机性
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
                
            except APITimeoutError as e:
                self.logger.error(f"API 请求超时: {str(e)}")
                current_retry += 1
            except APIError as e:
                self.logger.error(f"API 服务错误: {str(e)}")
                current_retry += 1
            except ValueError as e:
                self.logger.error(f"数据验证错误: {str(e)}")
                current_retry += 1
            except Exception as e:
                self.logger.error(f"API 调用失败: {str(e)}")
                current_retry += 1
                
        # 如果达到最大重试次数，返回错误信息
        return {
            "error": "AI 服务暂时无法正确解析策略，请稍后重试或提供更详细的信息"
        } 