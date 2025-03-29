"""
模型API调用模块
处理与DeepSeek API的交互
"""
import os
from typing import Optional, Dict, Any
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
        self.v3_endpoint = f"{self.base_url}/chat/completions"
        self.r1_endpoint = f"{self.base_url}/r1/chat/completions"

    def call_v3(self, prompt: str) -> str:
        """调用DeepSeek V3.0模型
        Args:
            prompt: 输入的prompt文本
        Returns:
            str: 模型的回复文本
        """
        return self._make_request(self.v3_endpoint, prompt)

    def call_r1(self, prompt: str) -> str:
        """调用DeepSeek R1模型
        Args:
            prompt: 输入的prompt文本
        Returns:
            str: 模型的回复文本
        """
        return self._make_request(self.r1_endpoint, prompt)

    def _make_request(self, endpoint: str, prompt: str) -> str:
        """发送API请求
        Args:
            endpoint: API端点URL
            prompt: 输入的prompt文本
        Returns:
            str: 模型的回复文本
        Raises:
            Exception: API调用失败时抛出异常
        """
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        
        data = {
            "messages": [{"role": "user", "content": prompt}],
            "temperature": 0.7,
            "max_tokens": 1000
        }
        
        try:
            response = requests.post(endpoint, headers=headers, json=data)
            response.raise_for_status()
            return response.json()['choices'][0]['message']['content']
        except Exception as e:
            raise Exception(f"API调用失败: {str(e)}")

# 创建全局实例
api = ModelAPI()
