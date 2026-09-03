import { computed, reactive } from "vue";
import { CONTENT_PAGES } from "../pages";

/**
 * 学习进度状态（v1 存本机 localStorage，不经网络、不入库）。
 *
 * 职责：为导航栏进度条与页脚"标记完成"按钮提供共享的读写状态。
 * 存储：key = agent-journey-progress-v1，value = { [route]: true }。
 * 扩展点：未来要跨设备同步时，把 persist() 改为写仓库里的 progress.json 即可，
 *         调用方无需改动。
 */

const STORAGE_KEY = "agent-journey-progress-v1";

/** 路由 -> 是否已完成。reactive 保证两个组件视图自动联动。 */
const state = reactive<Record<string, boolean>>({});

/** 是否已从 localStorage 恢复过（只恢复一次）。 */
let hydrated = false;

/**
 * 从 localStorage 恢复进度。
 * 关键副作用：SSR 构建期没有 localStorage，必须判空跳过，仅在浏览器执行。
 */
function hydrate(): void {
  if (hydrated || typeof localStorage === "undefined") {
    hydrated = true;
    return;
  }
  try {
    Object.assign(state, JSON.parse(localStorage.getItem(STORAGE_KEY) ?? "{}"));
  } catch {
    // 数据损坏时按空进度处理，不让站点白屏
  }
  hydrated = true;
}

/** 把当前进度写回 localStorage。 */
function persist(): void {
  if (typeof localStorage === "undefined") return;
  localStorage.setItem(STORAGE_KEY, JSON.stringify(state));
}

/**
 * 提供给组件的进度 API。
 * 返回：state（原始映射）、isDone / toggle（查与改）、completedCount / total（进度条数据）。
 */
export function useProgress() {
  hydrate();

  /** 查询某页是否已标记完成。 */
  const isDone = (route: string): boolean => !!state[route];

  /** 切换某页完成状态并持久化。 */
  const toggle = (route: string): void => {
    state[route] = !state[route];
    persist();
  };

  /** 已完成页数（computed：依赖 reactive state，标记后进度条自动刷新）。 */
  const completedCount = computed(
    () => CONTENT_PAGES.filter((p) => state[p.route]).length,
  );

  /** 进度分母 = 受追踪页面总数。 */
  const total = CONTENT_PAGES.length;

  return { state, isDone, toggle, completedCount, total };
}

/**
 * 把 VitePress 的页面相对路径规整为站内路由。
 * 参数：relativePath，如 "learning-path/phase-1-daily-plan.md"，
 *       或目录首页的 "learning-path/README.md" / "learning-path/index.md"（rewrites 后两者都会出现）。
 * 返回：路由，如 "/learning-path/phase-1-daily-plan" 或 "/learning-path/"。
 */
export function routeFromRelativePath(relativePath: string): string {
  return (
    "/" +
    relativePath
      .replace(/(^|\/)(README|index)\.md$/, "$1")
      .replace(/\.md$/, "")
  );
}
