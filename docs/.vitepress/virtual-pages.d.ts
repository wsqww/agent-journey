// virtual:aj-pages 模块的类型声明。
// 实际内容由 config.mts 里注册的 Vite 虚拟模块插件在编译时提供（数据来自 discover.ts 扫描）。
declare module "virtual:aj-pages" {
  import type { SitePage } from "./pages";
  const pages: SitePage[];
  export default pages;
}
