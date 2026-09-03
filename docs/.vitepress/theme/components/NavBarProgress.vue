<script setup lang="ts">
/**
 * 顶栏学习进度条。
 *
 * 职责：显示"已完成 n/总数"进度条；点击展开全部页面清单，可跳转回顾、可见完成状态。
 * 数据：来自 useProgress()（localStorage 持久化），分母为 pages.ts 登记的受追踪页面数。
 * 联动：state 为 reactive，页脚"标记完成"后本组件自动刷新，无需事件通信。
 */
import { computed, ref } from "vue";
import { useData } from "vitepress";
import { routeFromRelativePath, useProgress } from "../useProgress";
import { CONTENT_PAGES } from "../../pages";

const { completedCount, total, state } = useProgress();
const { page } = useData();

/** 清单展开开关（点击进度条区域切换）。 */
const expanded = ref(false);

/** 当前页路由，用于清单中高亮。 */
const currentRoute = computed(() =>
  routeFromRelativePath(String(page.value.relativePath)),
);

/** 进度百分比（进度条宽度）。 */
const percent = computed(() =>
  total === 0 ? 0 : Math.round((completedCount.value / total) * 100),
);
</script>

<template>
  <div class="aj-progress">
    <button
      class="aj-progress-trigger"
      :aria-expanded="expanded"
      title="学习进度（存本机浏览器，点击展开清单）"
      @click="expanded = !expanded"
    >
      <span class="aj-progress-bar">
        <span class="aj-progress-fill" :style="{ width: percent + '%' }" />
      </span>
      <span class="aj-progress-text">{{ completedCount }}/{{ total }}</span>
    </button>

    <div v-if="expanded" class="aj-progress-pop">
      <p class="aj-progress-pop-title">学习进度（仅存本机浏览器）</p>
      <a
        v-for="p in CONTENT_PAGES"
        :key="p.route"
        :href="p.route"
        class="aj-progress-item"
        :class="{
          'is-done': state[p.route],
          'is-current': p.route === currentRoute,
        }"
        @click="expanded = false"
      >
        <span class="aj-progress-check">{{ state[p.route] ? "✓" : "" }}</span>
        <span>{{ p.group }} · {{ p.text }}</span>
      </a>
    </div>
  </div>
</template>
