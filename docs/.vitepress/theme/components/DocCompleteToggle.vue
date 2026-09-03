<script setup lang="ts">
/**
 * 页脚"标记本页已完成"按钮。
 *
 * 职责：对受进度追踪的页面提供完成标记入口；非受追踪页（首页、附录）不渲染。
 * 数据：写入 useProgress() 的 localStorage 状态，顶栏进度条随之自动更新。
 */
import { computed } from "vue";
import { useData } from "vitepress";
import {
  routeFromRelativePath,
  useProgress,
  PROGRESS_PAGES,
} from "../useProgress";

const { page } = useData();
const { isDone, toggle } = useProgress();

/** 当前页路由。 */
const route = computed(() => routeFromRelativePath(String(page.value.relativePath)));

/** 当前页是否受进度追踪（附录页与首页不在 PROGRESS_PAGES 里，隐藏按钮）。 */
const tracked = computed(() => PROGRESS_PAGES.some((p) => p.route === route.value));

/** 当前页完成状态。 */
const done = computed(() => isDone(route.value));
</script>

<template>
  <div v-if="tracked" class="aj-complete">
    <button
      class="aj-complete-btn"
      :class="{ 'is-done': done }"
      @click="toggle(route)"
    >
      {{ done ? "✓ 已完成本页（点击取消）" : "标记本页已完成" }}
    </button>
    <span class="aj-complete-hint">进度仅存本机浏览器；md 里的勾选框仍以 Git 为准</span>
  </div>
</template>
