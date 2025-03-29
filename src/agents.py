"""
Agent实现模块
定义了系统中所有Agent的基类和具体实现
"""
from abc import ABC, abstractmethod  # 导入抽象基类支持
from typing import Dict, List, Optional, Any, Tuple  # 导入类型提示
from src.config import Config  # 导入配置类
from src.model_api import api  # 导入模型API
from src.database import db  # 导入数据库

class BaseAgent(ABC):
    """Agent基类，定义了所有Agent的通用接口和属性"""
    def __init__(self, config: Dict[str, Any]):
        """初始化Agent
        Args:
            config: Agent的配置信息字典
        """
        self.config = config  # 存储完整配置
        self.name = config.get('name', '')  # Agent名称
        self.model = config.get('model', '')  # 使用的模型名称
        self.role = config.get('role', '')  # Agent的角色描述
        self.prompt_template = config.get('prompt_template', '')  # prompt模板

    @abstractmethod
    def process(self, user_input: str, dialogue_history: List[Dict[str, str]], session_id: int) -> str:
        """处理用户输入的抽象方法，需要被子类实现
        Args:
            user_input: 用户的输入文本
            dialogue_history: 对话历史记录列表
            session_id: 当前会话ID
        Returns:
            str: Agent的回复
        """
        pass

    def _log_api_call(self, session_id: int, input_text: str, output: Tuple[str, int, int, int, Optional[str]]):
        """记录API调用日志
        Args:
            session_id: 会话ID
            input_text: 输入文本
            output: API调用返回的元组(输出文本, 响应时间, 输入tokens, 输出tokens, 错误信息)
        """
        output_text, response_time, input_tokens, output_tokens, error = output
        db.add_system_log(
            session_id=session_id,
            agent_name=self.name,
            input_text=input_text,
            output_text=output_text,
            response_time_ms=response_time,
            input_tokens=input_tokens,
            output_tokens=output_tokens,
            model_name=self.model,
            status='error' if error else 'success',
            error_message=error
        )
        if error:
            raise Exception(error)
        return output_text

class DispatcherAgent(BaseAgent):
    """调度Agent：决定使用哪个子系统回复"""
    def process(self, user_input: str, dialogue_history: List[Dict[str, str]], session_id: int) -> str:
        """处理用户输入，决定使用哪个子系统
        Args:
            user_input: 用户的输入文本
            dialogue_history: 对话历史记录列表
            session_id: 当前会话ID
        Returns:
            str: 'sys1'或'sys2'，表示选择的子系统
        """
        # 构建prompt，填充对话历史和用户输入
        prompt = self.prompt_template.format(
            dialogue_history=self._format_history(dialogue_history),
            user_input=user_input
        )
        # 调用DeepSeek V3模型并记录日志
        output = api.call_v3(prompt)
        return self._log_api_call(session_id, prompt, output)

    def _format_history(self, history: List[Dict[str, str]]) -> str:
        """格式化对话历史
        Args:
            history: 对话历史记录列表
        Returns:
            str: 格式化后的对话历史文本
        """
        formatted = []
        for msg in history:
            role = msg.get('role', '')  # 获取发言角色
            content = msg.get('content', '')  # 获取发言内容
            formatted.append(f"{role}: {content}")  # 格式化为"角色: 内容"的形式
        return "\n".join(formatted)  # 用换行符连接所有对话记录

class Sys1Agent(BaseAgent):
    """短链思考Agent：处理简单对话"""
    def process(self, user_input: str, dialogue_history: List[Dict[str, str]], session_id: int) -> str:
        """处理用户输入，生成简短回复
        Args:
            user_input: 用户的输入文本
            dialogue_history: 对话历史记录列表
            session_id: 当前会话ID
        Returns:
            str: Agent的回复
        """
        # 构建prompt，填充对话历史和用户输入
        prompt = self.prompt_template.format(
            dialogue_history=self._format_history(dialogue_history),
            user_input=user_input
        )
        # 调用DeepSeek V3模型并记录日志
        output = api.call_v3(prompt)
        return self._log_api_call(session_id, prompt, output)

    def _format_history(self, history: List[Dict[str, str]]) -> str:
        """格式化对话历史
        Args:
            history: 对话历史记录列表
        Returns:
            str: 格式化后的对话历史文本
        """
        return "\n".join([f"{msg['role']}: {msg['content']}" for msg in history])

class Sys2Agent(BaseAgent):
    """长链思考Agent：处理需要深度思考的问题"""
    def process(self, user_input: str, dialogue_history: List[Dict[str, str]], session_id: int) -> str:
        """处理用户输入，生成包含思考过程的回复
        Args:
            user_input: 用户的输入文本
            dialogue_history: 对话历史记录列表
            session_id: 当前会话ID
        Returns:
            str: 包含思考过程和回复的文本
        """
        # 构建prompt，填充对话历史和用户输入
        prompt = self.prompt_template.format(
            dialogue_history=self._format_history(dialogue_history),
            user_input=user_input
        )
        # 调用DeepSeek R1模型并记录日志
        output = api.call_r1(prompt)
        return self._log_api_call(session_id, prompt, output)

    def _format_history(self, history: List[Dict[str, str]]) -> str:
        """格式化对话历史
        Args:
            history: 对话历史记录列表
        Returns:
            str: 格式化后的对话历史文本
        """
        return "\n".join([f"{msg['role']}: {msg['content']}" for msg in history])
