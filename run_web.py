"""
Web应用启动脚本
"""
import uvicorn
import socket
import os
import subprocess
import sys
import time
from src.web.app import app

def check_port_in_use(port):
    """检查端口是否被占用
    
    Args:
        port: 要检查的端口号
        
    Returns:
        bool: 如果端口被占用返回True，否则返回False
    """
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        return s.connect_ex(('localhost', port)) == 0

def find_process_using_port(port):
    """查找占用指定端口的进程
    
    Args:
        port: 端口号
        
    Returns:
        int: 进程ID，如果没有找到则返回None
    """
    try:
        # 使用netstat命令查找占用端口的进程
        cmd = f'netstat -ano | findstr :{port}'
        result = subprocess.check_output(cmd, shell=True).decode('utf-8')
        
        if result:
            # 提取进程ID
            for line in result.strip().split('\n'):
                if f':{port}' in line and ('LISTENING' in line or 'ESTABLISHED' in line):
                    parts = line.strip().split()
                    if len(parts) > 4:
                        return int(parts[-1])
        return None
    except Exception as e:
        print(f"查找进程时出错: {e}")
        return None

def kill_process(pid):
    """终止指定的进程
    
    Args:
        pid: 进程ID
        
    Returns:
        bool: 如果成功终止进程返回True，否则返回False
    """
    try:
        # 使用taskkill命令终止进程
        subprocess.run(f'taskkill /F /PID {pid}', shell=True, check=True)
        print(f"已终止进程 (PID: {pid})")
        return True
    except subprocess.CalledProcessError as e:
        print(f"终止进程失败: {e}")
        return False

def free_port(port):
    """释放指定的端口
    
    Args:
        port: 要释放的端口号
        
    Returns:
        bool: 如果成功释放端口返回True，否则返回False
    """
    if not check_port_in_use(port):
        print(f"端口 {port} 未被占用")
        return True
        
    print(f"端口 {port} 已被占用，尝试释放...")
    pid = find_process_using_port(port)
    
    if pid:
        print(f"找到占用端口 {port} 的进程 (PID: {pid})")
        if kill_process(pid):
            # 等待端口释放
            for _ in range(5):  # 最多等待5秒
                if not check_port_in_use(port):
                    print(f"端口 {port} 已成功释放")
                    return True
                time.sleep(1)
            print(f"端口 {port} 仍然被占用")
            return False
    else:
        print(f"未找到占用端口 {port} 的进程")
        return False

if __name__ == "__main__":
    PORT = 8001
    
    # 尝试释放端口
    if check_port_in_use(PORT):
        if not free_port(PORT):
            print(f"无法释放端口 {PORT}，应用将退出")
            sys.exit(1)
    
    print(f"启动Web应用，监听端口: {PORT}")
    uvicorn.run(app, host="0.0.0.0", port=PORT)
