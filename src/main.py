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
    print("欢迎与赵敏敏聊天！输入 'quit' 结束对话。")
    
    # 主对话循环
    while True:
        # 获取用户输入
        user_input = input("\n用户: ").strip()
        
        # 检查是否退出命令
        if user_input.lower() == 'quit':
            print("再见！")
            break
            
        # 处理用户输入并获取系统回复
        response = manager.process_input(user_input)
        # 显示系统回复
        print(f"\n赵敏敏: {response}")

if __name__ == "__main__":
    main()
