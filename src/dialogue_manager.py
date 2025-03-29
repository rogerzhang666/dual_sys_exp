"""
对话管理模块
负责协调多个Agent的对话流程
"""
from typing import Dict, List, Optional  # 导入类型提示
from src.config import Config  # 导入配置模块
from src.agents import DispatcherAgent, Sys1Agent, Sys2Agent  # 导入Agent类

class DialogueManager:
    """对话管理器：协调多个Agent的对话流程"""
    
    def __init__(self):
        """初始化对话管理器"""
        # 加载配置
        config = Config()
        agents_config = config.get_agents_config()
        
        # 初始化各个Agent
        self.dispatcher = DispatcherAgent(agents_config['dispatcher'])
        self.sys1 = Sys1Agent(agents_config['sys1'])
        self.sys2 = Sys2Agent(agents_config['sys2'])
        
        # 初始化对话历史
        self.dialogue_history: List[Dict[str, str]] = []
        
    def process_input(self, user_input: str) -> str:
        """处理用户输入，返回系统回复
        Args:
            user_input: 用户输入的文本
        Returns:
            str: 系统的回复文本
        """
        # 添加用户输入到对话历史
        self.dialogue_history.append({
            'role': '用户',
            'content': user_input
        })
        
        # 使用调度器决定使用哪个子系统
        system = self.dispatcher.process(user_input, self.dialogue_history)
        
        # 根据调度结果选择相应的Agent处理
        if system == 'sys1':
            response = self.sys1.process(user_input, self.dialogue_history)
        else:
            response = self.sys2.process(user_input, self.dialogue_history)
            
        # 添加系统回复到对话历史
        self.dialogue_history.append({
            'role': '赵敏敏',
            'content': response
        })
        
        return response
        
    def clear_history(self):
        """清空对话历史"""
        self.dialogue_history.clear()
