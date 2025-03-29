"""
主程序模块
提供命令行交互界面
"""
import sys
from src.dialogue_manager import DialogueManager

def main():
    """主程序入口"""
    print("Welcome to chat! Type 'quit' to exit.")
    
    # 创建对话管理器实例
    manager = DialogueManager()
    
    try:
        while True:
            # 获取用户输入
            user_input = input("\nUser: ").strip()
            
            # 检查是否退出
            if user_input.lower() == 'quit':
                break
                
            # 处理用户输入并打印回复
            response = manager.process_input(user_input)
            print(f"\n赵敏敏: {response}")
            
    except (KeyboardInterrupt, EOFError):
        print("\nGoodbye!")
    except Exception as e:
        print(f"\nError: {str(e)}")
    finally:
        # 结束会话
        manager.end_session()

if __name__ == "__main__":
    main()
