"""
Agent实现模块
"""
from abc import ABC, abstractmethod
from typing import Dict, List, Optional, Any
from .config import Config

class BaseAgent(ABC):
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.name = config.get('name', '')
        self.model = config.get('model', '')
        self.role = config.get('role', '')
        self.prompt_template = config.get('prompt_template', '')

    @abstractmethod
    def process(self, user_input: str, dialogue_history: List[Dict[str, str]]) -> str:
        """处理用户输入"""
        pass

class DispatcherAgent(BaseAgent):
    """调度Agent：决定使用哪个子系统回复"""
    def process(self, user_input: str, dialogue_history: List[Dict[str, str]]) -> str:
        # 构建prompt
        prompt = self.prompt_template.format(
            dialogue_history=self._format_history(dialogue_history),
            user_input=user_input
        )
        # TODO: 调用模型API
        # 返回"sys1"或"sys2"
        return "sys1"  # 临时返回，待实现模型调用

    def _format_history(self, history: List[Dict[str, str]]) -> str:
        """格式化对话历史"""
        formatted = []
        for msg in history:
            role = msg.get('role', '')
            content = msg.get('content', '')
            formatted.append(f"{role}: {content}")
        return "\n".join(formatted)

class Sys1Agent(BaseAgent):
    """短链思考Agent：处理简单对话"""
    def process(self, user_input: str, dialogue_history: List[Dict[str, str]]) -> str:
        prompt = self.prompt_template.format(
            dialogue_history=self._format_history(dialogue_history),
            user_input=user_input
        )
        # TODO: 调用模型API
        return "这是sys1的回复"  # 临时返回，待实现模型调用

    def _format_history(self, history: List[Dict[str, str]]) -> str:
        return "\n".join([f"{msg['role']}: {msg['content']}" for msg in history])

class Sys2Agent(BaseAgent):
    """长链思考Agent：处理需要深度思考的问题"""
    def process(self, user_input: str, dialogue_history: List[Dict[str, str]]) -> str:
        prompt = self.prompt_template.format(
            dialogue_history=self._format_history(dialogue_history),
            user_input=user_input
        )
        # TODO: 调用模型API
        return "[思考过程]\n分析...\n\n[回复]\n这是sys2的回复"  # 临时返回，待实现模型调用

    def _format_history(self, history: List[Dict[str, str]]) -> str:
        return "\n".join([f"{msg['role']}: {msg['content']}" for msg in history])
