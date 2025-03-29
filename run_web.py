"""
Web应用启动脚本
"""
import uvicorn
from src.web.app import app

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8001)
