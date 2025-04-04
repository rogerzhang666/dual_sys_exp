# Dual System Experiment (双系统实验)

这是一个基于多Agent架构的对话系统实验项目。系统包含三个子系统：调度Agent、短链思考Agent (sys1) 和长链思考Agent (sys2)。

## 项目结构

```
dual_sys_exp/
├── config/
│   └── prompt_config.yaml    # 各子系统的prompt配置
├── data/
│   └── dialogue.db          # SQLite数据库，存储对话历史和系统日志
├── src/
│   ├── __init__.py
│   ├── config.py            # 配置加载模块
│   ├── model_api.py         # 百炼平台 API封装
│   ├── agents.py            # Agent实现
│   ├── database.py          # 数据库管理
│   ├── dialogue_manager.py  # 对话管理
│   ├── main.py              # 命令行界面主程序入口
│   └── web/                 # Web应用相关文件
│       ├── __init__.py
│       ├── app.py           # FastAPI Web应用
│       ├── static/          # 静态资源文件
│       └── templates/       # HTML模板文件
│           ├── base.html    # 基础模板
│           ├── chat.html    # 聊天界面模板
│           └── logs.html    # 日志查看界面模板
├── run_web.py               # Web应用启动脚本
├── .env.example             # 环境变量模板
├── requirements.txt         # 项目依赖
└── README.md                # 项目说明文档
```

## 系统架构

系统包含三个主要组件：

1. 调度Agent (通义千问)
   - 使用 `tongyi-intent-detect-v3` 模型进行意图识别
   - 负责决策使用哪个子系统回复
   - 基于问题类型进行智能路由
   - 实现类：`DispatcherAgent`

2. sys1 - 短链思考Agent (通义千问)
   - 使用 `qwen2.5-14b-instruct-1m` 模型
   - 处理简单对话和日常交互
   - 提供简短、自然的回复
   - 实现类：`Sys1Agent`

3. sys2 - 长链思考Agent (DeepSeek)
   - 使用 `deepseek-r1` 模型
   - 处理需要深度思考的问题
   - 提供详细的思考过程和分析
   - 实现类：`Sys2Agent`

## 核心模块说明

### 1. 配置管理 (config.py)
- 负责加载和解析YAML配置文件
- 提供各个Agent的prompt模板和配置参数
- 支持自定义配置文件路径

### 2. 模型API (model_api.py)
- 封装百炼平台 API的调用
- 使用 OpenAI 兼容模式访问 API
- 支持多种模型接口：
  - 通义千问意图识别模型
  - 通义千问2.5-14B模型
  - DeepSeek-R1模型
- 通过环境变量管理API密钥
- 统一的错误处理机制
- 自动统计token使用量和响应时间

### 3. Agent实现 (agents.py)
- 定义了Agent的基类 `BaseAgent`
- 实现了三个具体的Agent类
- 每个Agent都支持对话历史上下文
- 集成了模型API调用
- 自动记录系统日志
- sys2支持思考过程和回复的分离

### 4. 数据库管理 (database.py)
- 使用SQLite数据库存储数据
- 管理对话会话和历史记录
- 记录系统运行日志
- 支持以下数据表：
  - sessions：对话会话管理
  - messages：对话消息存储
  - system_logs：系统运行日志

### 5. 对话管理 (dialogue_manager.py)
- 统一管理所有Agent的调度和交互
- 维护对话历史记录
- 管理对话会话生命周期
- 支持对话历史持久化
- 提供清理对话历史的功能

### 6. Web应用 (web/app.py)
- 基于FastAPI开发的Web界面
- 提供直观的聊天交互界面
- 支持WebSocket实时通信
- 包含系统日志查看页面
- 提供API接口查询日志数据
- 支持查看详细的系统日志，包括：
  - 调用时间和响应时间
  - 输入输出文本
  - Token使用情况
  - 系统状态和错误信息

## 环境要求

- Python 3.8+
- 依赖包：见 requirements.txt
- 环境变量：
  - DASHSCOPE_API_KEY：百炼平台 API密钥

## 快速开始

1. 安装依赖：
```bash
pip install -r requirements.txt
```

2. 配置环境变量：
- 复制 `.env.example` 为 `.env`
- 填写你的百炼平台 API密钥

3. 启动Web服务：
```bash
python run_web.py
```

4. 访问系统：
- 打开浏览器访问 http://localhost:8001
- 开始与赵敏敏对话！

## 待办事项

- [x] 接入百炼平台 API
- [x] 优化意图识别
- [x] 完善日志系统
- [x] 实现思考过程分离
- [ ] 更多单元测试
- [ ] 错误处理和重试机制
- [ ] 并发请求优化
- [ ] 对话历史导出功能
- [ ] 移动端UI优化

## 许可证

MIT License
