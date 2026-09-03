import rawPages from "virtual:aj-pages";

/**
 * 站点页面清单（消费端）—— 内容在构建时由 discover.ts 从 docs/ 自动扫描生成，
 * 经 config.mts 注入的 virtual module 传入，**不再手工维护**。
 *
 * 职责：为侧边栏（config.mts）与进度组件（theme/）提供同一份页面数据；
 *       新增/删除 md 后重新编译即可，本文件无需改动。
 * 类型：virtual module 的声明见 virtual-pages.d.ts。
 */

/** 单个受追踪页面的元信息。 */
export interface SitePage {
  /** 站内路由（不带 .md 后缀；目录首页以 `/` 结尾）。 */
  route: string;
  /** 侧边栏显示名。 */
  text: string;
  /** 侧边栏分组名，同一分组渲染为一个可折叠区块。 */
  group: string;
}

/** 全部受追踪页面（顺序 = 侧边栏顺序，含附录）。进度分母在 useProgress 内过滤附录后计算。 */
export const CONTENT_PAGES: SitePage[] = rawPages;
