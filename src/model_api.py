"""
模型API调用模块
处理与百炼平台API的交互
"""
import os
import time
from typing import Dict, Any, Tuple
from openai import OpenAI
from openai import APITimeoutError, APIError
from dotenv import load_dotenv
import backoff  # 用于实现重试机制

# 加载环境变量
load_dotenv()

class ModelAPI:
    """百炼平台模型API封装"""
    
    def __init__(self):
        """初始化API配置"""
        # 从环境变量获取API密钥
        self.api_key = os.getenv('DASHSCOPE_API_KEY')
        if not self.api_key:
            raise ValueError("未找到DASHSCOPE_API_KEY环境变量")
            
        # 初始化OpenAI客户端
        self.client = OpenAI(
            api_key=self.api_key,
            base_url="https://dashscope.aliyuncs.com/compatible-mode/v1"
        )
        
        # 模型配置
        self.intent_model = "tongyi-intent-detect-v3"
        self.qwen_model = "qwen2.5-14b-instruct-1m"
        self.deepseek_model = "deepseek-r1"
        
        # 重试配置
        self.max_retries = 3
        self.max_time = 30  # 最大重试时间（秒）
        self.request_timeout = 30  # 请求超时时间（秒）
        
        # 重试计数器
        self._retry_count = 0

    def call_intent(self, prompt: str) -> Tuple[str, int, int, int, str]:
        """调用通义千问模型进行意图识别
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
        return self._make_request(prompt, self.intent_model)

    def call_qwen(self, prompt: str) -> Tuple[str, int, int, int, str]:
        """调用通义千问模型
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
        return self._make_request(prompt, self.qwen_model)

    def call_deepseek(self, prompt: str) -> Tuple[str, int, int, int, str]:
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
        return self._make_request(prompt, self.deepseek_model)

    @backoff.on_exception(
        backoff.expo,
        (APITimeoutError, APIError),
        max_tries=3,
        max_time=30,
        on_backoff=lambda details: setattr(details['args'][0], '_retry_count', details['tries'])
    )
    def _make_request(self, prompt: str, model: str) -> Tuple[str, int, int, int, str]:
        """发送API请求
        Args:
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
        start_time = time.time()  # 开始计时
        try:
            # 创建聊天完成请求
            completion = self.client.chat.completions.create(
                model=model,
                messages=[
                    {"role": "system", "content": "You are a helpful assistant."},
                    {"role": "user", "content": prompt}
                ],
                timeout=self.request_timeout  # 设置请求超时时间
            )
            
            # 计算响应时间（毫秒）
            response_time = int((time.time() - start_time) * 1000)
            
            # 提取响应信息
            response = completion.model_dump()
            
            # 获取输出文本
            output_text = response['choices'][0]['message']['content']
            
            # 获取token使用情况
            usage = response['usage']
            input_tokens = usage['prompt_tokens']
            output_tokens = usage['completion_tokens']
            
            # 重置重试计数器
            self._retry_count = 0
            
            return (
                output_text,
                response_time,
                input_tokens,
                output_tokens,
                None
            )
        except APITimeoutError as e:
            error_msg = "请求超时，正在重试..."
            print(f"API调用超时: {error_msg}")
            if self._retry_count >= self.max_retries - 1:
                return "", int((time.time() - start_time) * 1000), 0, 0, "请求超时，请稍后重试"
            raise
        except Exception as e:
            error_msg = str(e)
            print(f"API调用错误: {error_msg}")
            # 如果是最后一次重试，返回错误信息
            if self._retry_count >= self.max_retries - 1:
                return "", int((time.time() - start_time) * 1000), 0, 0, error_msg
            # 否则继续重试
            raise

# 创建全局实例
api = ModelAPI()
