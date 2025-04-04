"""
Web应用主模块
提供Web界面和WebSocket支持
"""
from fastapi import FastAPI, WebSocket, Request, WebSocketDisconnect
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from pathlib import Path
import json
import asyncio
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
        # 活跃的WebSocket连接列表
        self.active_connections: List[WebSocket] = []
        # 连接到对话管理器的映射
        self.managers: Dict[WebSocket, DialogueManager] = {}
        # 心跳检测定时器
        self.heartbeat_task = None
        
    async def connect(self, websocket: WebSocket):
        """建立新的WebSocket连接"""
        await websocket.accept()
        self.active_connections.append(websocket)
        # 为每个连接创建一个对话管理器实例
        self.managers[websocket] = DialogueManager()
        
        # 启动心跳检测
        if not self.heartbeat_task:
            self.heartbeat_task = asyncio.create_task(self._heartbeat())
    
    def disconnect(self, websocket: WebSocket):
        """断开WebSocket连接"""
        if websocket in self.active_connections:
            self.active_connections.remove(websocket)
        if websocket in self.managers:
            # 结束对话会话
            self.managers[websocket].end_session()
            del self.managers[websocket]
            
        # 如果没有活跃连接，停止心跳检测
        if not self.active_connections and self.heartbeat_task:
            self.heartbeat_task.cancel()
            self.heartbeat_task = None

    async def broadcast(self, message: str):
        """广播消息到所有连接"""
        for connection in self.active_connections:
            try:
                await connection.send_text(message)
            except Exception:
                # 如果发送失败，移除该连接
                await self.disconnect(connection)

    async def _heartbeat(self):
        """心跳检测，定期检查连接是否存活"""
        while True:
            await asyncio.sleep(30)  # 每30秒检查一次
            for connection in self.active_connections.copy():
                try:
                    await connection.send_json({"type": "ping"})
                except Exception:
                    # 如果发送失败，说明连接已断开
                    await self.disconnect(connection)

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
    try:
        # 连接WebSocket
        await manager.connect(websocket)
        
        while True:
            # 接收消息
            try:
                message = await websocket.receive_text()
                
                # 如果是心跳响应，直接跳过
                if message == "pong":
                    continue
                
                # 获取当前连接的对话管理器
                dialogue_manager = manager.managers.get(websocket)
                if not dialogue_manager:
                    await websocket.send_json({
                        "type": "error",
                        "content": "会话已失效，请刷新页面重试",
                        "timestamp": datetime.now().isoformat()
                    })
                    continue
                
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
                        if response.get("thinking"):
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
                
            except WebSocketDisconnect:
                # 客户端断开连接
                manager.disconnect(websocket)
                break
                
            except Exception as e:
                # 其他错误
                print(f"WebSocket错误: {str(e)}")
                try:
                    error_message = {
                        "type": "error",
                        "content": "连接异常，请刷新页面重试",
                        "timestamp": datetime.now().isoformat()
                    }
                    await websocket.send_json(error_message)
                except:
                    pass
                break
                
    except Exception as e:
        print(f"WebSocket错误: {str(e)}")
    finally:
        # 断开连接
        manager.disconnect(websocket)

@app.get("/api/logs")
async def get_logs(
    start_time: Optional[str] = None,
    end_time: Optional[str] = None,
    search_text: Optional[str] = None
) -> Dict[str, Any]:
    """获取系统日志
    Args:
        start_time: 开始时间（ISO格式）
        end_time: 结束时间（ISO格式）
        search_text: 搜索文本
    Returns:
        Dict: 日志数据
    """
    try:
        # 从数据库查询日志
        logs = db.get_logs(start_time, end_time, search_text)
        
        # 格式化日志数据
        formatted_logs = []
        for log in logs:
            formatted_logs.append({
                "session_id": log["session_id"],
                "timestamp": log["timestamp"],  
                "agent_name": log["agent_name"],
                "input_text": log["input_text"],
                "output_text": log["output_text"],
                "response_time_ms": log["response_time_ms"],
                "input_tokens": log["input_tokens"],
                "output_tokens": log["output_tokens"],
                "model_name": log["model_name"],
                "status": log["status"],
                "error_message": log["error_message"],
                "session_start_time": log["session_start_time"]
            })
            
        return {
            "status": "success",
            "data": formatted_logs
        }
        
    except Exception as e:
        return {
            "status": "error",
            "message": str(e)
        }
