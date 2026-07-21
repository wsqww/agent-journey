# Agent 工程师学习路线（前端转型）

为前端工程师定制的 6-9 个月兼职转型路线，目标：**全职 Agent 工程师**。

👉 **完整路线文档：** [docs/learning-path/README.md](./docs/learning-path/README.md)

## 仓库结构

```
agent-study/
├── docs/learning-path/    # 学习路线文档（README + 6 阶段 + 6 份每日计划）
├── phase-1/ ~ phase-6/    # 各阶段代码练习与作品集项目
├── notes/                 # 学习笔记
└── .gitignore
```

## 快速开始

1. 从 [学习路线总览](./docs/learning-path/README.md) 开始，通读"起点 / 核心原则 / 降级路径"
2. 按阶段顺序推进，每阶段先读阶段文档（Why），再跟每日计划（How）
3. 代码放在对应 `phase-N/` 目录，笔记放在 `notes/`

## 约定

- **文档分工：** 阶段文档讲 Why/认知/标准，每日计划讲 How/代码/任务。详见 [总览](./docs/learning-path/README.md#文档分工约定ssot避免维护时两边不同步)
- **时效：** 文档模型名/价格/工具版本以各厂官方最新为准，每季度自行校准
- **密钥：** API Key 一律用环境变量，绝不入库（`.gitignore` 已屏蔽 `.env`）

## 补充资料

- 🔧 [工具速查表](./docs/toolkit.md)：一页汇总所有用到的工具（LLM / 向量库 / 框架 / 部署…），按用途分类，含选型决策树。学习时 bookmark，做新项目时当选型参考。
- 🚫 [反模式库](./docs/anti-patterns.md)：18 个真实工程坑（"错在哪 → 怎么改"），按阶段分类。每学完一个阶段回来扫一遍对应章节，code review 当 checklist 用。

