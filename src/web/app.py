"""
Web应用主模块
提供Web界面和WebSocket支持
"""
from fastapi import FastAPI, WebSocket, Request
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from pathlib import Path
import json
from datetime import datetime
from typing import List, Dict, Any, Optional

from src.dialogue_manager import DialogueManager
from src.database import db

# 创建FastAPI应用
app = FastAPI(title="双系统实验")

# 获取当前文件所在目录
current_dir = Path(__file__).parent
static_dir = current_dir / "static"
templates_dir = current_dir / "templates"

# 挂载静态文件目录
app.mount("/static", StaticFiles(directory=str(static_dir)), name="static")

# 创建模板引擎
templates = Jinja2Templates(directory=str(templates_dir))

class ConnectionManager:
    """WebSocket连接管理器"""
    def __init__(self):
        self.active_connections: List[WebSocket] = []

    async def connect(self, websocket: WebSocket):
        """建立新的WebSocket连接"""
        await websocket.accept()
        self.active_connections.append(websocket)

    def disconnect(self, websocket: WebSocket):
        """断开WebSocket连接"""
        self.active_connections.remove(websocket)

    async def broadcast(self, message: str):
        """广播消息到所有连接"""
        for connection in self.active_connections:
            await connection.send_text(message)

# 创建连接管理器实例
manager = ConnectionManager()

@app.get("/", response_class=HTMLResponse)
async def chat_page(request: Request):
    """聊天页面"""
    return templates.TemplateResponse(
        "chat.html",
        {"request": request}
    )

@app.get("/logs", response_class=HTMLResponse)
async def logs_page(request: Request):
    """日志页面"""
    return templates.TemplateResponse(
        "logs.html",
        {"request": request}
    )

@app.websocket("/ws/chat")
async def websocket_endpoint(websocket: WebSocket):
    """WebSocket端点，处理实时聊天"""
    # 创建对话管理器
    dialogue_manager = DialogueManager()
    
    try:
        # 连接WebSocket
        await manager.connect(websocket)
        
        while True:
            # 接收消息
            message = await websocket.receive_text()
            
            # 处理用户输入
            try:
                # 调用对话管理器处理输入
                response = dialogue_manager.process_input(message)
                
                # 根据响应类型发送不同格式的消息
                if response["type"] == "message":
                    # 普通消息直接发送
                    reply = {
                        "type": "message",
                        "role": "assistant",
                        "content": response["content"],
                        "timestamp": datetime.now().isoformat()
                    }
                    await websocket.send_json(reply)
                    
                elif response["type"] == "sys2":
                    # sys2的思考过程和回复分开发送
                    
                    # 先发送思考过程
                    if response["thinking"]:
                        thinking = {
                            "type": "sys2-thinking",
                            "content": response["thinking"],
                            "timestamp": datetime.now().isoformat()
                        }
                        await websocket.send_json(thinking)
                    
                    # 再发送回复
                    reply = {
                        "type": "sys2-response",
                        "content": response["response"],
                        "timestamp": datetime.now().isoformat()
                    }
                    await websocket.send_json(reply)
                    
                elif response["type"] == "error":
                    # 错误消息
                    error_message = {
                        "type": "error",
                        "content": response["content"],
                        "timestamp": datetime.now().isoformat()
                    }
                    await websocket.send_json(error_message)
                
            except Exception as e:
                # 发送错误消息
                error_message = {
                    "type": "error",
                    "content": f"处理失败: {str(e)}",
                    "timestamp": datetime.now().isoformat()
                }
                await websocket.send_json(error_message)
                
    except Exception as e:
        print(f"WebSocket错误: {str(e)}")
    finally:
        # 结束会话
        dialogue_manager.end_session()
        # 断开连接
        manager.disconnect(websocket)

@app.get("/api/logs")
async def get_logs(
    start_time: Optional[str] = None,
    end_time: Optional[str] = None,
    search_text: Optional[str] = None
):
    """获取系统日志
    Args:
        start_time: 开始时间（ISO格式）
        end_time: 结束时间（ISO格式）
        search_text: 搜索文本
    Returns:
        Dict: 日志数据
    """
    try:
        # 构建查询条件
        conditions = []
        params = []
        
        if start_time:
            conditions.append("timestamp >= ?")
            params.append(start_time)
            
        if end_time:
            conditions.append("timestamp <= ?")
            params.append(end_time)
            
        if search_text:
            conditions.append("(input_text LIKE ? OR output_text LIKE ?)")
            search_pattern = f"%{search_text}%"
            params.extend([search_pattern, search_pattern])
            
        # 构建SQL查询
        query = """
            SELECT l.*, s.start_time as session_start_time
            FROM system_logs l
            JOIN sessions s ON l.session_id = s.session_id
        """
        
        if conditions:
            query += " WHERE " + " AND ".join(conditions)
            
        query += " ORDER BY l.timestamp DESC LIMIT 1000"
        
        # 执行查询
        db.cursor.execute(query, params)
        logs = []
        for row in db.cursor.fetchall():
            log = {
                "session_id": row[1],  # 添加session_id字段
                "timestamp": row[2],
                "agent_name": row[3],
                "input_text": row[4],
                "output_text": row[5],
                "response_time_ms": row[6],
                "input_tokens": row[7],
                "output_tokens": row[8],
                "model_name": row[9],
                "status": row[10],
                "error_message": row[11],
                "session_start_time": row[12]
            }
            logs.append(log)
            
        return {"status": "success", "data": logs}
        
    except Exception as e:
        return {"status": "error", "message": str(e)}
