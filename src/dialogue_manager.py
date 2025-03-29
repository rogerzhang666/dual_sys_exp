"""
对话管理模块
负责协调多个Agent的对话流程
"""
from typing import Dict, List, Optional  # 导入类型提示
from src.config import Config  # 导入配置模块
from src.agents import DispatcherAgent, Sys1Agent, Sys2Agent  # 导入Agent类
from src.database import db  # 导入数据库

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
        
        # 创建新会话
        self.session_id = db.create_session()
        
        # 从数据库加载对话历史
        self.dialogue_history = self._load_history()
        
    def process_input(self, user_input: str) -> str:
        """处理用户输入，返回系统回复
        Args:
            user_input: 用户输入的文本
        Returns:
            str: 系统的回复文本
        """
        # 添加用户输入到对话历史
        self._add_message('用户', user_input)
        
        try:
            # 使用调度器决定使用哪个子系统
            system = self.dispatcher.process(user_input, self.dialogue_history, self.session_id)
            
            # 根据调度结果选择相应的Agent处理
            if system.strip().lower() == 'sys1':
                response = self.sys1.process(user_input, self.dialogue_history, self.session_id)
            else:
                response = self.sys2.process(user_input, self.dialogue_history, self.session_id)
                
            # 添加系统回复到对话历史
            self._add_message('赵敏敏', response)
            
            return response
            
        except Exception as e:
            error_msg = f"处理失败: {str(e)}"
            # 记录错误消息
            self._add_message('系统', error_msg)
            return error_msg
        
    def _add_message(self, role: str, content: str):
        """添加消息到对话历史
        Args:
            role: 发言角色
            content: 消息内容
        """
        # 添加到内存中的对话历史
        self.dialogue_history.append({
            'role': role,
            'content': content
        })
        
        # 保存到数据库
        db.add_message(self.session_id, role, content)
        
    def _load_history(self) -> List[Dict[str, str]]:
        """从数据库加载对话历史
        Returns:
            List[Dict[str, str]]: 对话历史列表
        """
        messages = db.get_session_messages(self.session_id)
        return [{'role': msg['role'], 'content': msg['content']} for msg in messages]
        
    def end_session(self):
        """结束当前会话"""
        db.end_session(self.session_id)
        
    def clear_history(self):
        """清空对话历史"""
        self.dialogue_history.clear()
