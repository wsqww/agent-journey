import { defineConfig } from "vitepress";
import type { Plugin } from "vite";
import { discoverPages } from "./discover";
import type { SitePage } from "./pages";

/**
 * VitePress 站点配置。
 *
 * 职责：站点元信息、页面发现（discover.ts）、virtual module 注入、本页目录、本地搜索。
 * 关键取舍：
 *   - 页面清单零登记：编译时扫描 docs/ 自动生成侧边栏与进度分母，新增 md 重跑编译即可生效；
 *     dev 模式下 VitePress 只在配置变化时热重启，新增 md 后需重启 dev server。
 *   - ignoreDeadLinks: md 内容里存在指向站外文件的链接（如 ../../notes/*.md），
 *     内容文件是 SSOT 不为建站改动，因此放宽死链检查。
 *   - rewrites: VitePress 只认 index.md 作目录首页，而总览文件按 GitHub 惯例叫 README.md，
 *     映射为目录路由 /learning-path/ —— 源文件保持 README.md 不动（SSOT）。
 *   - outline level [2, 3]：每日计划里 Week 是 H1、Day 是 H2，右侧目录即"天"级导航。
 */

// 编译时扫描一次，作为侧边栏与 virtual module 的唯一数据源
const PAGES: SitePage[] = discoverPages();

/**
 * 把扫描结果注入为虚拟模块 "virtual:aj-pages"。
 * 这样客户端主题组件（进度条等）能与配置共享同一份数据，且无需把 node:fs 打进浏览器包。
 *
 * @param pages 编译时扫描得到的页面清单。
 * @returns Vite 插件。
 */
function virtualPagesPlugin(pages: SitePage[]): Plugin {
  const id = "virtual:aj-pages";
  return {
    name: "aj-virtual-pages",
    resolveId(virtualId) {
      return virtualId === id ? "\0" + id : null;
    },
    load(resolvedId) {
      if (resolvedId === "\0" + id) {
        return `export default ${JSON.stringify(pages)}`;
      }
      return null;
    },
  };
}

export default defineConfig({
  lang: "zh-CN",
  title: "Agent 工程师学习路线",
  description: "前端工程师 → 全职 Agent 工程师的 6-9 个月兼职转型路线",
  ignoreDeadLinks: true,

  // 站点图标（docs/public/favicon.svg）
  head: [["link", { rel: "icon", type: "image/svg+xml", href: "/favicon.svg" }]],

  // VitePress 只认 index.md 作目录首页，而总览文件按 GitHub 惯例叫 README.md。
  // 用 rewrites 把它映射为目录路由 /learning-path/ —— 源文件保持 README.md 不动（SSOT）。
  rewrites: {
    "learning-path/README.md": "learning-path/index.md",
  },

  vite: {
    plugins: [virtualPagesPlugin(PAGES)],
  },

  themeConfig: {
    siteTitle: "Agent 工程师学习路线",

    // 顶部导航：外链 VitePress 会自动加 ↗ 角标并新窗口打开，手机端自动进抽屉菜单
    nav: [{ text: "Github", link: "https://github.com/wsqww/agent-journey" }],

    // 侧边栏：按扫描结果的分组顺序生成，「总览」默认展开
    sidebar: [...new Set(PAGES.map((p) => p.group))].map((group) => ({
      text: group,
      collapsed: group !== "总览",
      items: PAGES.filter((p) => p.group === group).map((p) => ({
        text: p.text,
        link: p.route,
      })),
    })),

    // 右侧大纲显示 H2/H3：在每日计划长文里提供 周(H1 除外)/天 级锚点导航
    outline: { label: "本页目录", level: [2, 3] },

    // 本地搜索（构建时生成索引，无外部服务）
    search: {
      provider: "local",
      options: {
        translations: {
          button: { buttonText: "搜索文档", buttonAriaLabel: "搜索文档" },
          modal: {
            noResultsText: "没有找到结果",
            resetButtonTitle: "清空关键词",
            footer: { selectText: "选择", navigateText: "切换", closeText: "关闭" },
          },
        },
      },
    },

    darkModeSwitchLabel: "主题",
    docFooter: { prev: "上一篇", next: "下一篇" },
    lastUpdated: { text: "最后更新" },
  },
});
