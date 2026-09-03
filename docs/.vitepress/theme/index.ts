import { h } from "vue";
import DefaultTheme from "vitepress/theme";
import NavBarProgress from "./components/NavBarProgress.vue";
import DocCompleteToggle from "./components/DocCompleteToggle.vue";
import BackToTop from "./components/BackToTop.vue";
import "./custom.css";

/**
 * 自定义主题：在默认主题基础上注入三个学习向组件。
 *
 * 职责：
 *   - NavBarProgress   → 总进度条（已完成 n/N）：桌面在顶栏搜索框与 Github 之间；
 *                        窄屏（<960px）顶栏实例隐藏，同一组件收进汉堡抽屉顶部
 *   - DocCompleteToggle → 正文页脚上方："标记本页已完成"按钮
 *   - BackToTop        → 右下角浮动：回顶部按钮（长文档快速返回）
 * Github 仓库链接走 config.mts 的 themeConfig.nav（标准导航项，零定制）。
 * 其余外观与行为全部沿用 VitePress 默认主题。
 */
export default {
  extends: DefaultTheme,
  Layout: () =>
    h(DefaultTheme.Layout, null, {
      "nav-bar-content-after": () => h(NavBarProgress),
      "nav-screen-content-before": () => h(NavBarProgress),
      "doc-footer-before": () => h(DocCompleteToggle),
      "layout-bottom": () => h(BackToTop),
    }),
};
