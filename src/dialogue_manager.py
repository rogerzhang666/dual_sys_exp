"""
对话管理模块
负责协调多个Agent的对话流程
"""
from typing import Dict, List, Optional  # 导入类型提示模块，用于类型标注
from src.config import Config  # 导入配置模块，用于加载系统配置
from src.agents import DispatcherAgent, Sys1Agent, Sys2Agent  # 导入三种不同的Agent类
from src.database import db  # 导入数据库模块，用于存储对话历史

class DialogueManager:
    """对话管理器：协调多个Agent的对话流程"""
    
    def __init__(self):
        """初始化对话管理器，加载配置并创建各个Agent实例"""
        # 加载配置文件
        config = Config()
        # 获取所有Agent的配置信息
        agents_config = config.get_agents_config()
        
        # 初始化各个Agent实例
        # 调度器Agent：负责决定使用哪个系统回复用户
        self.dispatcher = DispatcherAgent(agents_config['dispatcher'])
        # 系统1 Agent：处理简单的对话请求
        self.sys1 = Sys1Agent(agents_config['sys1'])
        # 系统2 Agent：处理复杂的对话请求，会生成思考过程
        self.sys2 = Sys2Agent(agents_config['sys2'])
        
        # 创建新的对话会话，并获取会话ID
        self.session_id = db.create_session()
        
        # 从数据库加载当前会话的对话历史
        self.dialogue_history = self._load_history()
        
    def process_input(self, user_input: str) -> dict:
        """处理用户输入，返回系统回复
        Args:
            user_input: 用户输入的文本内容
        Returns:
            dict: 系统的回复信息，包含type和content字段
                 type可能是'message'(普通回复)或'sys2'(sys2回复，包含思考过程和回复)
        """
        # 将用户输入添加到对话历史中
        self._add_message('用户', user_input)
        
        try:
            # 使用调度器Agent决定应该使用哪个子系统来处理用户输入
            system = self.dispatcher.process(user_input, self.dialogue_history, self.session_id)
            
            # 根据调度结果选择相应的Agent处理用户输入
            if system.strip().lower() == 'sys1':
                # 如果调度结果是sys1，使用系统1处理
                response = self.sys1.process(user_input, self.dialogue_history, self.session_id)
                # 将系统1的回复添加到对话历史
                self._add_message('赵敏敏', response)
                # 返回普通消息类型的回复
                return {"type": "message", "content": response}
            else:
                # 如果调度结果不是sys1，则使用系统2处理
                sys2_response = self.sys2.process(user_input, self.dialogue_history, self.session_id)
                
                # 将系统2的完整回复（思考过程+回复内容）添加到对话历史
                complete_response = f"{sys2_response['thinking']}\n\n{sys2_response['response']}"
                self._add_message('赵敏敏', complete_response)
                
                # 返回结构化的系统2响应，包含思考过程和回复内容
                return {
                    "type": "sys2", 
                    "thinking": sys2_response["thinking"],  # 思考过程部分
                    "response": sys2_response["response"]   # 最终回复部分
                }
                
        except Exception as e:
            # 捕获处理过程中的任何异常
            error_msg = f"处理失败: {str(e)}"
            # 将错误消息记录到对话历史
            self._add_message('系统', error_msg)
            # 返回错误类型的消息
            return {"type": "error", "content": error_msg}
        
    def _add_message(self, role: str, content: str):
        """添加消息到对话历史
        Args:
            role: 发言角色（如'用户'、'赵敏敏'、'系统'等）
            content: 消息内容文本
        """
        # 将新消息添加到内存中的对话历史列表
        self.dialogue_history.append({
            'role': role,    # 消息发送者角色
            'content': content  # 消息内容
        })
        
        # 同时将消息保存到数据库中，确保持久化存储
        db.add_message(self.session_id, role, content)
        
    def _load_history(self) -> List[Dict[str, str]]:
        """从数据库加载当前会话的对话历史
        Returns:
            List[Dict[str, str]]: 包含角色和内容的对话历史列表
        """
        # 从数据库获取当前会话的所有消息
        messages = db.get_session_messages(self.session_id)
        # 将数据库返回的消息格式转换为内部使用的格式
        return [{'role': msg['role'], 'content': msg['content']} for msg in messages]
        
    def end_session(self):
        """结束当前会话，在数据库中标记会话已结束"""
        db.end_session(self.session_id)
        
    def clear_history(self):
        """清空内存中的对话历史，但不影响数据库中的记录"""
        self.dialogue_history.clear()
