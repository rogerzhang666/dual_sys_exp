"""
对话管理模块
"""
from typing import Dict, List, Optional
from .config import Config
from .agents import DispatcherAgent, Sys1Agent, Sys2Agent

class DialogueManager:
    def __init__(self, config_path: Optional[str] = None):
        # 加载配置
        self.config = Config(config_path)
        
        # 初始化agents
        self.dispatcher = DispatcherAgent(self.config.get_agent_config('dispatcher'))
        self.sys1 = Sys1Agent(self.config.get_agent_config('sys1'))
        self.sys2 = Sys2Agent(self.config.get_agent_config('sys2'))
        
        # 对话历史
        self.dialogue_history: List[Dict[str, str]] = []

    def process_input(self, user_input: str) -> str:
        """处理用户输入，返回系统回复"""
        # 记录用户输入
        self.dialogue_history.append({
            'role': '用户',
            'content': user_input
        })

        # 通过调度Agent决定使用哪个子系统
        selected_sys = self.dispatcher.process(user_input, self.dialogue_history)
        
        # 根据选择调用相应的子系统
        if selected_sys == "sys1":
            response = self.sys1.process(user_input, self.dialogue_history)
        else:
            response = self.sys2.process(user_input, self.dialogue_history)

        # 记录系统回复
        self.dialogue_history.append({
            'role': '赵敏敏',
            'content': response
        })

        return response

    def clear_history(self):
        """清空对话历史"""
        self.dialogue_history = []
