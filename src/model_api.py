"""
模型API调用模块
处理与DeepSeek API的交互
"""
import os
import time
from typing import Optional, Dict, Any, Tuple
import requests
from dotenv import load_dotenv

# 加载环境变量
load_dotenv()

class ModelAPI:
    """DeepSeek模型API封装"""
    
    def __init__(self):
        """初始化API配置"""
        # 从环境变量获取API密钥
        self.api_key = os.getenv('DEEPSEEK_API_KEY')
        if not self.api_key:
            raise ValueError("未找到DEEPSEEK_API_KEY环境变量")
            
        # API端点配置
        self.base_url = "https://api.deepseek.com/v1"
        self.model_v3 = "deepseek-chat"
        self.model_r1 = "deepseek-reasoner"
        self.v3_endpoint = f"{self.base_url}/chat/completions"
        self.r1_endpoint = f"{self.base_url}/chat/completions"

    def call_v3(self, prompt: str) -> Tuple[str, int, int, int, str]:
        """调用DeepSeek V3.0模型
        Args:
            prompt: 输入的prompt文本
        Returns:
            Tuple[str, int, int, int, str]: 
            - 模型的回复文本
            - 响应时间（毫秒）
            - 输入token数量
            - 输出token数量
            - 错误信息（如果有）
        """
        return self._make_request(self.v3_endpoint, prompt, self.model_v3)

    def call_r1(self, prompt: str) -> Tuple[str, int, int, int, str]:
        """调用DeepSeek R1模型
        Args:
            prompt: 输入的prompt文本
        Returns:
            Tuple[str, int, int, int, str]: 
            - 模型的回复文本
            - 响应时间（毫秒）
            - 输入token数量
            - 输出token数量
            - 错误信息（如果有）
        """
        return self._make_request(self.r1_endpoint, prompt, self.model_r1)

    def _make_request(self, endpoint: str, prompt: str, model: str) -> Tuple[str, int, int, int, str]:
        """发送API请求
        Args:
            endpoint: API端点URL
            prompt: 输入的prompt文本
            model: 模型名称
        Returns:
            Tuple[str, int, int, int, str]: 
            - 模型的回复文本
            - 响应时间（毫秒）
            - 输入token数量
            - 输出token数量
            - 错误信息（如果有）
        """
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        
        data = {
            "model": model,
            "messages": [{"role": "user", "content": prompt}],
            "temperature": 0.7,
            "max_tokens": 1000
        }
        
        start_time = time.time()
        error_msg = None
        try:
            response = requests.post(endpoint, headers=headers, json=data)
            response.raise_for_status()
            response_data = response.json()
            
            # 提取token数量
            input_tokens = response_data.get('usage', {}).get('prompt_tokens', 0)
            output_tokens = response_data.get('usage', {}).get('completion_tokens', 0)
            
            # 计算响应时间（毫秒）
            response_time = int((time.time() - start_time) * 1000)
            
            return (
                response_data['choices'][0]['message']['content'],
                response_time,
                input_tokens,
                output_tokens,
                None
            )
        except Exception as e:
            error_msg = str(e)
            print(f"请求数据: {data}")
            print(f"响应内容: {response.text if 'response' in locals() else 'No response'}")
            return "", int((time.time() - start_time) * 1000), 0, 0, error_msg

# 创建全局实例
api = ModelAPI()
