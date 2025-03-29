# Dual System Experiment (双系统实验)

这是一个基于多Agent架构的对话系统实验项目。系统包含三个子系统：调度Agent、短链思考Agent (sys1) 和长链思考Agent (sys2)。

## 项目结构

```
dual_sys_exp/
├── config/
│   └── prompt_config.yaml    # 各子系统的prompt配置
├── src/                      # 源代码目录
└── README.md                 # 项目说明文档
```

## 系统架构

系统包含三个主要组件：

1. 调度Agent (DeepSeek-V3.0)
   - 负责决策使用哪个子系统回复
   - 基于问题类型进行智能路由

2. sys1 - 短链思考Agent (DeepSeek-V3.0)
   - 处理简单对话和日常交互
   - 提供简短、自然的回复

3. sys2 - 长链思考Agent (DeepSeek-R1)
   - 处理需要深度思考的问题
   - 提供详细的思考过程和分析

## 特点

- 多模型协同：结合DeepSeek-V3.0和DeepSeek-R1的优势
- 共享上下文：所有子系统共享对话历史
- 智能调度：根据问题类型自动选择合适的处理系统
