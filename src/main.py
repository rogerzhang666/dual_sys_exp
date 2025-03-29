"""
主程序入口
"""
from dialogue_manager import DialogueManager

def main():
    # 初始化对话管理器
    manager = DialogueManager()
    
    print("欢迎与赵敏敏聊天！输入 'quit' 结束对话。")
    
    while True:
        # 获取用户输入
        user_input = input("\n用户: ").strip()
        
        # 检查是否退出
        if user_input.lower() == 'quit':
            print("再见！")
            break
            
        # 处理用户输入并获取回复
        response = manager.process_input(user_input)
        print(f"\n赵敏敏: {response}")

if __name__ == "__main__":
    main()
