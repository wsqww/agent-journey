import { h } from "vue";
import DefaultTheme from "vitepress/theme";
import NavBarProgress from "./components/NavBarProgress.vue";
import DocCompleteToggle from "./components/DocCompleteToggle.vue";
import "./custom.css";

/**
 * 自定义主题：在默认主题基础上注入两个学习进度组件。
 *
 * 职责：
 *   - NavBarProgress  → 顶栏右侧：总进度条（已完成 n/16）
 *   - DocCompleteToggle → 正文页脚上方："标记本页已完成"按钮
 * 其余外观与行为全部沿用 VitePress 默认主题。
 */
export default {
  extends: DefaultTheme,
  Layout: () =>
    h(DefaultTheme.Layout, null, {
      "nav-bar-content-after": () => h(NavBarProgress),
      "doc-footer-before": () => h(DocCompleteToggle),
    }),
};
