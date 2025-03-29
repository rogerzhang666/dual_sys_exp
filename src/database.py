"""
数据库管理模块
负责对话历史和系统日志的存储与检索
"""
import os
import sqlite3
from typing import Dict, List, Any, Optional
from datetime import datetime

class Database:
    """数据库管理类"""
    
    def __init__(self, db_path: Optional[str] = None):
        """初始化数据库连接
        Args:
            db_path: 数据库文件路径，如果为None则使用默认路径
        """
        if db_path is None:
            # 获取当前文件所在目录
            current_dir = os.path.dirname(os.path.abspath(__file__))
            # 构建默认数据库文件路径
            db_path = os.path.join(os.path.dirname(current_dir), 'data', 'dialogue.db')
            
        # 确保数据目录存在
        os.makedirs(os.path.dirname(db_path), exist_ok=True)
            
        self.db_path = db_path
        self.conn = sqlite3.connect(db_path)
        self.cursor = self.conn.cursor()
        
        # 初始化数据库表
        self._init_tables()
        
    def _init_tables(self):
        """初始化数据库表"""
        # 对话会话表
        self.cursor.execute('''
        CREATE TABLE IF NOT EXISTS sessions (
            session_id INTEGER PRIMARY KEY AUTOINCREMENT,
            start_time DATETIME NOT NULL,
            end_time DATETIME,
            status TEXT DEFAULT 'active'
        )
        ''')
        
        # 对话消息表
        self.cursor.execute('''
        CREATE TABLE IF NOT EXISTS messages (
            message_id INTEGER PRIMARY KEY AUTOINCREMENT,
            session_id INTEGER NOT NULL,
            timestamp DATETIME NOT NULL,
            role TEXT NOT NULL,
            content TEXT NOT NULL,
            FOREIGN KEY (session_id) REFERENCES sessions(session_id)
        )
        ''')
        
        # 系统日志表
        self.cursor.execute('''
        CREATE TABLE IF NOT EXISTS system_logs (
            log_id INTEGER PRIMARY KEY AUTOINCREMENT,
            session_id INTEGER NOT NULL,
            timestamp DATETIME NOT NULL,
            agent_name TEXT NOT NULL,
            input_text TEXT NOT NULL,
            output_text TEXT NOT NULL,
            response_time_ms INTEGER NOT NULL,
            input_tokens INTEGER NOT NULL,
            output_tokens INTEGER NOT NULL,
            model_name TEXT NOT NULL,
            status TEXT NOT NULL,
            error_message TEXT,
            FOREIGN KEY (session_id) REFERENCES sessions(session_id)
        )
        ''')
        
        self.conn.commit()
        
    def create_session(self) -> int:
        """创建新的对话会话
        Returns:
            int: 会话ID
        """
        self.cursor.execute(
            'INSERT INTO sessions (start_time) VALUES (?)',
            (datetime.now(),)
        )
        self.conn.commit()
        return self.cursor.lastrowid
        
    def end_session(self, session_id: int):
        """结束对话会话
        Args:
            session_id: 会话ID
        """
        self.cursor.execute(
            'UPDATE sessions SET end_time = ?, status = ? WHERE session_id = ?',
            (datetime.now(), 'completed', session_id)
        )
        self.conn.commit()
        
    def add_message(self, session_id: int, role: str, content: str):
        """添加对话消息
        Args:
            session_id: 会话ID
            role: 发言角色
            content: 消息内容
        """
        self.cursor.execute(
            'INSERT INTO messages (session_id, timestamp, role, content) VALUES (?, ?, ?, ?)',
            (session_id, datetime.now(), role, content)
        )
        self.conn.commit()
        
    def get_session_messages(self, session_id: int) -> List[Dict[str, Any]]:
        """获取会话的所有消息
        Args:
            session_id: 会话ID
        Returns:
            List[Dict[str, Any]]: 消息列表
        """
        self.cursor.execute(
            'SELECT timestamp, role, content FROM messages WHERE session_id = ? ORDER BY timestamp',
            (session_id,)
        )
        messages = []
        for row in self.cursor.fetchall():
            messages.append({
                'timestamp': row[0],
                'role': row[1],
                'content': row[2]
            })
        return messages
        
    def add_system_log(self, session_id: int, agent_name: str, input_text: str,
                      output_text: str, response_time_ms: int, input_tokens: int,
                      output_tokens: int, model_name: str, status: str,
                      error_message: Optional[str] = None):
        """添加系统日志
        Args:
            session_id: 会话ID
            agent_name: Agent名称
            input_text: 输入文本
            output_text: 输出文本
            response_time_ms: 响应时间（毫秒）
            input_tokens: 输入token数量
            output_tokens: 输出token数量
            model_name: 使用的模型名称
            status: 状态（success/error）
            error_message: 错误信息（如果有）
        """
        self.cursor.execute(
            '''INSERT INTO system_logs 
               (session_id, timestamp, agent_name, input_text, output_text,
                response_time_ms, input_tokens, output_tokens, model_name,
                status, error_message)
               VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)''',
            (session_id, datetime.now(), agent_name, input_text, output_text,
             response_time_ms, input_tokens, output_tokens, model_name,
             status, error_message)
        )
        self.conn.commit()
        
    def get_session_logs(self, session_id: int) -> List[Dict[str, Any]]:
        """获取会话的所有系统日志
        Args:
            session_id: 会话ID
        Returns:
            List[Dict[str, Any]]: 日志列表
        """
        self.cursor.execute(
            '''SELECT timestamp, agent_name, input_text, output_text,
                      response_time_ms, input_tokens, output_tokens,
                      model_name, status, error_message
               FROM system_logs 
               WHERE session_id = ? 
               ORDER BY timestamp''',
            (session_id,)
        )
        logs = []
        for row in self.cursor.fetchall():
            logs.append({
                'timestamp': row[0],
                'agent_name': row[1],
                'input_text': row[2],
                'output_text': row[3],
                'response_time_ms': row[4],
                'input_tokens': row[5],
                'output_tokens': row[6],
                'model_name': row[7],
                'status': row[8],
                'error_message': row[9]
            })
        return logs
        
    def close(self):
        """关闭数据库连接"""
        self.conn.close()
        
# 创建全局实例
db = Database()
