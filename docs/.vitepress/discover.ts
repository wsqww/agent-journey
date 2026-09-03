import fs from "node:fs";
import path from "node:path";
import type { SitePage } from "./pages";

/**
 * 构建时页面发现 —— 从文件系统自动生成站点页面清单（SSOT 是 docs/ 下的 md 本身）。
 *
 * 职责：扫描 docs/ 下的 markdown，按仓库命名约定推导路由、分组与标题，
 *       供侧边栏（config.mts）与进度统计（主题组件）使用，新增页面零登记。
 *
 * 命名约定（与仓库现有结构一致）：
 *   - docs/learning-path/README.md            → 「总览」组
 *   - docs/learning-path/phase-N-*.md         → 「第 N 阶段」组；其中
 *     *-daily-plan.md → 条目「每日计划 · How 与任务」，其余 → 「阶段文档 · Why 与标准」
 *     （同组出现多个非 daily 文件时，条目名退回用文件 H1 以示区分）
 *   - docs/*.md（排除 index.md）               → 「附录」组，条目名用 H1
 *   - 组标题：取阶段文档 H1（如「第 1 阶段：Python 基础 + LLM API 入门」），
 *     并尝试从顶部 blockquote 解析「周期：**6 周**」追加时长
 *
 * 排除规则：index.md（网站首页）与下划线开头的文件（`_draft.md`）不入站。
 */

/** docs/ 目录（discover.ts 位于 docs/.vitepress/ 下，上一级即 docs/）。 */
const DOCS_ROOT = path.resolve(import.meta.dirname, "..");

/** 阶段文件名中的 N，用于分组与排序。 */
const PHASE_RE = /^phase-(\d+)-(.+)\.md$/;

/** 从阶段文档顶部 blockquote 解析学习周期，如 "6 周"、"4-5 周"。 */
const PERIOD_RE = /周期：\s*(\d+(?:\s*[-–~]\s*\d+)?\s*周)/;

/**
 * 从 markdown 文本中提取首个 H1 标题。
 * 关键防御：跳过 frontmatter 与代码围栏内的 `#` 行（每日计划里有大量 python 注释）。
 *
 * @param text 完整 markdown 文本。
 * @returns H1 文本（不含 `#`）；找不到返回 null。
 */
export function extractH1(text: string): string | null {
  let inFrontmatter = false;
  let frontmatterDone = false;
  let inFence = false;
  for (const line of text.split("\n")) {
    if (!frontmatterDone && line.trim() === "---") {
      // 首个 --- 进入 frontmatter，第二个 --- 结束
      if (!inFrontmatter) {
        inFrontmatter = true;
        continue;
      }
      frontmatterDone = true;
      continue;
    }
    if (inFrontmatter && !frontmatterDone) continue;
    if (line.startsWith("```")) {
      inFence = !inFence;
      continue;
    }
    if (!inFence && line.startsWith("# ")) return line.slice(2).trim();
  }
  return null;
}

/**
 * 读取单个 md 文件的 H1 与（阶段文档才有的）周期信息。
 *
 * @param file md 文件绝对路径。
 * @returns { h1, period }；period 未解析到时为 null。
 */
function readMeta(file: string): { h1: string | null; period: string | null } {
  const text = fs.readFileSync(file, "utf-8");
  const head = text.split("\n").slice(0, 40).join("\n");
  return {
    h1: extractH1(text),
    // 先剥掉 markdown 加粗符号：文档里的写法是 "**周期：** **6 周**"，加粗拆两段
    period:
      head.replace(/\*\*/g, "").match(PERIOD_RE)?.[1]?.replace(/\s+/g, "") ??
      null,
  };
}

/**
 * 扫描 docs/ 生成有序页面清单。
 *
 * 返回顺序即侧边栏顺序：总览 → 各阶段（阶段文档在前、每日计划在后，按 N 升序）→ 附录。
 * 任何文件读取/解析失败都会直接抛错——构建工具应当响亮失败，而不是静默缺页。
 *
 * @returns 有序 SitePage 数组。
 */
export function discoverPages(): SitePage[] {
  const learningDir = path.join(DOCS_ROOT, "learning-path");
  const pages: SitePage[] = [];

  // —— 总览：learning-path/README.md（GitHub 惯例文件名，经 rewrites 映射为目录路由）
  const overviewFile = path.join(learningDir, "README.md");
  if (fs.existsSync(overviewFile)) {
    pages.push({ route: "/learning-path/", text: "学习路线总览", group: "总览" });
  }

  // —— 各阶段：扫描 learning-path/phase-N-*.md，按 N 分组
  const phaseFiles = fs
    .readdirSync(learningDir)
    .filter((f) => PHASE_RE.test(f))
    .sort();

  interface PhaseDoc {
    file: string;
    isDaily: boolean;
    isStage: boolean; // H1 匹配「第 N 阶段：」的阶段主文档
    h1: string | null;
    period: string | null;
  }
  const byPhase = new Map<number, PhaseDoc[]>();
  for (const f of phaseFiles) {
    const m = f.match(PHASE_RE)!;
    const n = Number(m[1]);
    const meta = readMeta(path.join(learningDir, f));
    const isDaily = f.includes("daily-plan");
    const doc: PhaseDoc = {
      file: f,
      isDaily,
      isStage: !isDaily && !!meta.h1?.match(new RegExp(`^第\\s*${n}\\s*阶段\\s*[：:]`)),
      ...meta,
    };
    if (!byPhase.has(n)) byPhase.set(n, []);
    byPhase.get(n)!.push(doc);
  }

  for (const [n, docs] of [...byPhase.entries()].sort((a, b) => a[0] - b[0])) {
    // 组标题：取阶段主文档的 H1 + 周期；没有主文档时用默认名
    const stage = docs.find((d) => d.isStage);
    let group = `第 ${n} 阶段`;
    if (stage) {
      const theme = stage.h1!.replace(/^第\s*\d+\s*阶段\s*[：:]\s*/, "");
      group += ` · ${theme}`;
      if (stage.period) group += `（${stage.period}）`;
    }
    // 组内排序：阶段主文档 → 其他非 daily（字母序）→ 每日计划
    const ordered = [
      ...(stage ? [stage] : []),
      ...docs.filter((d) => !d.isDaily && d !== stage),
      ...docs.filter((d) => d.isDaily),
    ];
    // 条目名：daily 固定标签；唯一的非 daily 用固定标签；其余用 H1 区分
    const nonDaily = docs.filter((d) => !d.isDaily);
    for (const d of ordered) {
      const route = `/learning-path/${d.file.replace(/\.md$/, "")}`;
      const text =
        d.isDaily || nonDaily.length === 1
          ? d.isDaily
            ? "每日计划 · How 与任务"
            : "阶段文档 · Why 与标准"
          : (d.h1 ?? d.file);
      pages.push({ route, text, group });
    }
  }

  // —— 附录：docs/ 顶层的 md（排除首页 index.md 与下划线草稿）
  const appendix = fs
    .readdirSync(DOCS_ROOT)
    .filter(
      (f) =>
        f.endsWith(".md") && f !== "index.md" && !f.startsWith("_"),
    )
    .sort();
  for (const f of appendix) {
    const h1 = readMeta(path.join(DOCS_ROOT, f)).h1;
    pages.push({
      route: `/${f.replace(/\.md$/, "")}`,
      text: h1 ?? f,
      group: "附录",
    });
  }

  return pages;
}
