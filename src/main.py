"""
主程序入口
提供命令行交互界面，处理用户输入和系统回复
"""
from dialogue_manager import DialogueManager  # 导入对话管理器

def main():
    """主函数：初始化系统并启动交互循环"""
    # 初始化对话管理器
    manager = DialogueManager()
    
    # 显示欢迎信息
    print("Welcome to chat! Type 'quit' to exit.")
    
    # 主对话循环
    while True:
        try:
            # 获取用户输入
            user_input = input("\nUser: ").strip()
            
            # 检查是否退出命令
            if user_input.lower() == 'quit':
                print("Goodbye!")
                break
                
            # 处理用户输入并获取系统回复
            response = manager.process_input(user_input)
            # 显示系统回复
            print(f"\nAssistant: {response}")
        except EOFError:
            break
        except KeyboardInterrupt:
            break
        except Exception as e:
            print(f"\nError: {str(e)}")

if __name__ == "__main__":
    main()
