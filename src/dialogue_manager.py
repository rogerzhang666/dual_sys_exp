"""
对话管理模块
负责协调各个Agent的工作，管理对话流程和历史记录
"""
from typing import Dict, List, Optional  # 导入类型提示
from .config import Config  # 导入配置管理模块
from .agents import DispatcherAgent, Sys1Agent, Sys2Agent  # 导入Agent实现

class DialogueManager:
    """对话管理器：协调各个Agent的工作，维护对话状态"""
    
    def __init__(self, config_path: Optional[str] = None):
        """初始化对话管理器
        Args:
            config_path: 可选的配置文件路径
        """
        # 加载配置文件
        self.config = Config(config_path)
        
        # 初始化各个Agent实例
        self.dispatcher = DispatcherAgent(self.config.get_agent_config('dispatcher'))
        self.sys1 = Sys1Agent(self.config.get_agent_config('sys1'))
        self.sys2 = Sys2Agent(self.config.get_agent_config('sys2'))
        
        # 初始化对话历史列表
        self.dialogue_history: List[Dict[str, str]] = []

    def process_input(self, user_input: str) -> str:
        """处理用户输入，返回系统回复
        Args:
            user_input: 用户输入的文本
        Returns:
            str: 系统的回复文本
        """
        # 将用户输入添加到对话历史
        self.dialogue_history.append({
            'role': '用户',
            'content': user_input
        })

        # 使用调度Agent决定由哪个子系统处理
        selected_sys = self.dispatcher.process(user_input, self.dialogue_history)
        
        # 根据调度结果选择相应的子系统处理
        if selected_sys == "sys1":
            response = self.sys1.process(user_input, self.dialogue_history)
        else:
            response = self.sys2.process(user_input, self.dialogue_history)

        # 将系统回复添加到对话历史
        self.dialogue_history.append({
            'role': '赵敏敏',
            'content': response
        })

        return response

    def clear_history(self):
        """清空对话历史记录"""
        self.dialogue_history = []
