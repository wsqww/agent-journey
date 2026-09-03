# AGENTS.md — agent-journey 仓库指南

个人学习仓库：前端工程师兼职转型 Agent 工程师（6-9 个月兼职路线）。文档与代码均为**自用**，没有外部协作者。

仓库分两层，动任何文件前先分清：

- **内容层（SSOT）**：`docs/` 下的 markdown（学习路线、工具表、反模式库、易变事实）、`phase-1..6/` 各阶段练习代码、`notes/` 复盘与考官模板。
- **渲染层**：`docs/.vitepress/`（VitePress 学习网站），只负责把 md 渲染成站，**不含任何学习内容**。

## 铁律

1. **内容只进 md，不进站点代码**：改学习计划/内容一律改 `docs/` 下的 md；不要往 `.vitepress/` 写内容，也不要为内容改动渲染层。
2. **易变事实单一来源**：模型名/价格只写在 `docs/versions.md`，其他文档链接过去、不复制；工具版本号只出现在各项目的 `pyproject.toml`，文档不写死版本号；代码示例统一用 `-latest` 别名占位（如 `gpt-5-latest`）。
3. **文档分工不串味**：`phase-N-*.md`（非 daily-plan）讲 Why/认知/标准；`phase-N-daily-plan.md` 讲 How/代码/任务。改一边时检查另一边是否失同步。
4. **网站是"元工作"**：只在阶段缓冲周迭代站点本身；日常会话默认不动 `.vitepress/`，防止工具建设挤占学习。若用户主动要求改站，不受此限。
5. **密钥绝不入库**：API Key 一律环境变量（`.env*` 已 ignore）；发现硬编码密钥立即指出，不要照抄进新代码。
6. **改动后自查本文件**：每次修改项目内容结束后，自查本次改动是否影响本文件所载事实（命令、目录结构、约定、部署流程等），有影响时同步更新本文件，再结束任务。

## 常用命令

```bash
npm install          # 安装依赖（仅渲染层需要，Node 22）
npm run site:dev     # 本地预览 http://localhost:5173
npm run site:build   # 构建静态站到 docs/.vitepress/dist/
npm run site:preview # 预览构建产物
```

`phase-N/` 下的 Python 练习各自管理虚拟环境与依赖，仓库根没有全局 Python 工程；不要在根目录安装 Python 依赖。

## 新增/改名页面（零登记）

侧边栏与进度统计由 `docs/.vitepress/discover.ts` 编译时扫描自动生成，**无需注册**，但必须遵守命名约定：

- `docs/learning-path/README.md` → 「总览」组；经 rewrites 映射为 `/learning-path/` 路由，**文件名保持 README.md 不改**
- `docs/learning-path/phase-N-*.md` → 「第 N 阶段」组；`*-daily-plan.md` 归「每日计划」，其余归「阶段文档」
- `docs/*.md`（除 `index.md`）→ 「附录」组，条目名取文件 H1
- `index.md` 是网站首页；`_` 开头的文件是草稿，不入站

**坑**：页面清单是编译期产物——dev 模式下新增/删除 md 后需重启 `site:dev` 才生效；`site:preview` 看到旧清单同理，先重新 build。

## 部署

push 到 `main` 即自动构建并发布 GitHub Pages（`.github/workflows/deploy-site.yml`，Node 22 + `npm ci`）。没有手动部署步骤，不要另加部署脚本。

## 其他约定

- 全仓库中文书写（文档、注释、commit message）。
- `ignoreDeadLinks: true` 是刻意的：md 内容链接到站外文件（如 `../../notes/*.md`），内容文件是 SSOT、不为建站改动；不要为过死链检查而改链接或搬文件。
- 学习进度勾选存在浏览器 localStorage，与 md 勾选框、Git 互不相干，不要尝试同步。
- 覆盖 VitePress 主题组件样式时，scoped 属性选择器会压过普通同名规则，需 `!important`（先例见 `theme/custom.css` 的 VPHero 覆盖）。
- 未经明确指示不要 `git add/commit/push`；`.zcode/ .codex/ .cursor/ .trae/` 等 agent 工作目录已被 ignore，产物只写进这些目录或 `notes/`，不要散落在仓库根。
