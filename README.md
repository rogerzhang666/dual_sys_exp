# Dual System Experiment (双系统实验)

这是一个基于多Agent架构的对话系统实验项目。系统包含三个子系统：调度Agent、短链思考Agent (sys1) 和长链思考Agent (sys2)。

## 项目结构

```
dual_sys_exp/
├── config/
│   └── prompt_config.yaml    # 各子系统的prompt配置
├── src/
│   ├── __init__.py
│   ├── config.py            # 配置加载模块
│   ├── agents.py            # Agent实现
│   ├── dialogue_manager.py  # 对话管理
│   └── main.py             # 主程序入口
├── requirements.txt         # 项目依赖
└── README.md               # 项目说明文档
```

## 系统架构

系统包含三个主要组件：

1. 调度Agent (DeepSeek-V3.0)
   - 负责决策使用哪个子系统回复
   - 基于问题类型进行智能路由
   - 实现类：`DispatcherAgent`

2. sys1 - 短链思考Agent (DeepSeek-V3.0)
   - 处理简单对话和日常交互
   - 提供简短、自然的回复
   - 实现类：`Sys1Agent`

3. sys2 - 长链思考Agent (DeepSeek-R1)
   - 处理需要深度思考的问题
   - 提供详细的思考过程和分析
   - 实现类：`Sys2Agent`

## 核心模块说明

### 1. 配置管理 (config.py)
- 负责加载和解析YAML配置文件
- 提供各个Agent的prompt模板和配置参数
- 支持自定义配置文件路径

### 2. Agent实现 (agents.py)
- 定义了Agent的基类 `BaseAgent`
- 实现了三个具体的Agent类
- 每个Agent都支持对话历史上下文

### 3. 对话管理 (dialogue_manager.py)
- 统一管理所有Agent的调度和交互
- 维护对话历史记录
- 提供清理对话历史的功能

### 4. 主程序 (main.py)
- 提供命令行交互界面
- 支持连续对话
- 使用'quit'命令退出系统

## 快速开始

1. 安装依赖：
```bash
pip install -r requirements.txt
```

2. 运行程序：
```bash
python src/main.py
```

## 待实现功能

- [ ] 模型API调用接口
- [ ] 对话历史持久化
- [ ] 更多单元测试
- [ ] 错误处理和重试机制

## 开发说明

- Python版本要求：3.8+
- 配置文件格式：YAML
- 代码风格：遵循PEP 8规范
