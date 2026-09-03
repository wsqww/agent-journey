# Agent 工程师学习路线（前端转型）

为前端工程师定制的 6-9 个月兼职转型路线，目标：**全职 Agent 工程师**。

👉 **完整路线文档：** [docs/learning-path/README.md](./docs/learning-path/README.md)

## 仓库结构

```
agent-journey/
├── docs/
│   ├── learning-path/     # 学习路线文档（README + 6 阶段 + 6 份每日计划）
│   ├── toolkit.md         # 工具选型速查表
│   ├── anti-patterns.md   # 反模式库
│   ├── versions.md        # 易变事实 SSOT（模型/价格/校准清单）
│   └── .vitepress/        # 学习网站（VitePress 配置与主题，仅渲染层）
├── phase-1/ ~ phase-6/    # 各阶段代码练习与作品集项目
├── notes/                 # 学习笔记、每周复盘与 LLM 考官模板
└── .gitignore
```

## 快速开始

1. 从 [学习路线总览](./docs/learning-path/README.md) 开始，通读"起点 / 核心原则 / 降级路径"
2. 按阶段顺序推进，每阶段先读阶段文档（Why），再跟每日计划（How）
3. 代码放在对应 `phase-N/` 目录，笔记放在 `notes/`

## 学习网站（可选）

仓库内置一个 VitePress 文档站，把路线渲染成可导航、可标记进度的网页（内容仍以 md 为唯一来源，网站只是渲染层）：

```bash
npm install         # 首次安装依赖
npm run site:dev    # 本地预览 → http://localhost:5173
npm run site:build  # 构建静态站（docs/.vitepress/dist/，可部署到 Vercel）
```

- **进度标记**存在本机浏览器（localStorage），与 md 里的勾选框、Git 互不干扰
- **约定：** 学内容、改计划一律改 md；不要往站点代码里写内容。**新增页面零登记**——编译时自动扫描 `docs/` 生成侧边栏与进度统计（命名约定见 `docs/.vitepress/discover.ts` 头注释）；dev 模式下新增 md 需重启 `site:dev`

## 约定

- **文档分工：** 阶段文档讲 Why/认知/标准，每日计划讲 How/代码/任务。详见 [总览](./docs/learning-path/README.md#文档分工约定ssot避免维护时两边不同步)
- **时效：** 文档模型名/价格/工具版本以各厂官方最新为准，每季度自行校准
- **密钥：** API Key 一律用环境变量，绝不入库（`.gitignore` 已屏蔽 `.env`）
- **复盘与回填：** 每周复制 [notes/retro-template.md](./notes/retro-template.md) 复盘，阶段末把实测周数回填该阶段耗时参考表；自检配合 [LLM 考官模板](./notes/llm-examiner-prompt.md)。断联超过 2 周按总览的[断联重启协议](./docs/learning-path/README.md#断联重启协议预先承诺)执行，禁止从头再来

## 补充资料

- 🔧 [工具速查表](./docs/toolkit.md)：一页汇总所有用到的工具（LLM / 向量库 / 框架 / 部署…），按用途分类，含选型决策树。学习时 bookmark，做新项目时当选型参考。
- 🚫 [反模式库](./docs/anti-patterns.md)：18 个真实工程坑（"错在哪 → 怎么改"），按阶段分类。每学完一个阶段回来扫一遍对应章节，code review 当 checklist 用。
- 🗓 [易变事实 SSOT](./docs/versions.md)：模型名 / 价格等时点数据的唯一来源，含季度校准清单（技术 + 市场两项）。校准时只改这一个文件。

