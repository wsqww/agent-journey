<script setup lang="ts">
/**
 * 顶栏学习进度条。
 *
 * 职责：显示"已完成 n/总数"进度条；点击展开全部页面清单，可跳转回顾、可见完成状态。
 * 数据：来自 useProgress()（localStorage 持久化），分母为 learning-path 页面数，
 *       附录不计入进度、也不出现在清单里。
 * 联动：state 为 reactive，页脚"标记完成"后本组件自动刷新，无需事件通信。
 * 交互：点击区域外任意处收起清单（桌面浮层惯例，抽屉实例同样生效）。
 */
import { computed, onBeforeUnmount, onMounted, ref } from "vue";
import { useData } from "vitepress";
import {
  routeFromRelativePath,
  useProgress,
  PROGRESS_PAGES,
} from "../useProgress";

const { completedCount, total, state } = useProgress();
const { page } = useData();

/** 清单展开开关（点击进度条区域切换）。 */
const expanded = ref(false);

/** 组件根节点（进度条+浮层）引用，用于判断点击落点是否在区域内。 */
const root = ref<HTMLElement | null>(null);

/** 点击根节点以外区域时收起清单；触发按钮在根内，自身开合不受影响。 */
function onDocClick(e: MouseEvent): void {
  if (root.value && !root.value.contains(e.target as Node)) {
    expanded.value = false;
  }
}

// 挂载后监听整页点击、卸载时移除，防止监听器泄漏（SSR 构建期不执行）
onMounted(() => document.addEventListener("click", onDocClick));
onBeforeUnmount(() => document.removeEventListener("click", onDocClick));

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
  <div ref="root" class="aj-progress">
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
        v-for="p in PROGRESS_PAGES"
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
