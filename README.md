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
│   ├── model_api.py         # DeepSeek API封装
│   ├── agents.py            # Agent实现
│   ├── dialogue_manager.py  # 对话管理
│   └── main.py             # 主程序入口
├── .env.example            # 环境变量模板
├── requirements.txt        # 项目依赖
└── README.md              # 项目说明文档
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

### 2. 模型API (model_api.py)
- 封装DeepSeek API的调用
- 支持V3.0和R1两个模型接口
- 通过环境变量管理API密钥
- 统一的错误处理机制

### 3. Agent实现 (agents.py)
- 定义了Agent的基类 `BaseAgent`
- 实现了三个具体的Agent类
- 每个Agent都支持对话历史上下文
- 集成了模型API调用

### 4. 对话管理 (dialogue_manager.py)
- 统一管理所有Agent的调度和交互
- 维护对话历史记录
- 提供清理对话历史的功能

### 5. 主程序 (main.py)
- 提供命令行交互界面
- 支持连续对话
- 使用'quit'命令退出系统

## 快速开始

1. 配置环境变量：
```bash
cp .env.example .env
# 编辑.env文件，填入您的DeepSeek API密钥
```

2. 安装依赖：
```bash
pip install -r requirements.txt
```

3. 运行程序：
```bash
python src/main.py
```

## 环境要求

- Python版本：3.8+
- 依赖包：
  - pyyaml>=6.0.1：配置文件解析
  - python-dotenv>=1.0.0：环境变量管理
  - requests>=2.31.0：API调用

## 配置说明

### 环境变量
- `DEEPSEEK_API_KEY`：DeepSeek API密钥

### 配置文件 (prompt_config.yaml)
- agents:
  - dispatcher：调度Agent的配置
  - sys1：短链思考Agent的配置
  - sys2：长链思考Agent的配置

## 待实现功能

- [ ] 对话历史持久化
- [ ] 更多单元测试
- [ ] 错误处理和重试机制
- [ ] 并发请求优化

## 开发说明

- 代码风格：遵循PEP 8规范
- 分支管理：
  - main：主分支
  - feature/*：功能开发分支
- 提交规范：使用Angular提交规范
