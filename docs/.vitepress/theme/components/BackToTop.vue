<script setup lang="ts">
/**
 * 回顶部按钮。
 *
 * 职责：长文档（每日计划数千行）快速返回页顶。滚动超过阈值出现在右下角，
 *       点击平滑回顶；全站所有页面生效（挂在 layout-bottom 插槽）。
 * SSR 安全：scrollY 读取与监听器注册都在 onMounted（仅浏览器执行）。
 */
import { onMounted, onUnmounted, ref } from "vue";

/** 按钮是否可见（reactive，驱动过渡动画）。 */
const visible = ref(false);

/** 出现阈值：向下滚动超过该像素数才显示。 */
const THRESHOLD = 300;

/** 滚动回调：更新可见状态。副作用：修改 visible。 */
function onScroll(): void {
  visible.value = window.scrollY > THRESHOLD;
}

/** 点击处理：平滑滚动回页顶。 */
function backToTop(): void {
  window.scrollTo({ top: 0, behavior: "smooth" });
}

onMounted(() => {
  onScroll(); // 处理刷新时已处于页面中部的情况
  window.addEventListener("scroll", onScroll, { passive: true });
});

onUnmounted(() => {
  window.removeEventListener("scroll", onScroll);
});
</script>

<template>
  <transition name="aj-backtop">
    <button
      v-if="visible"
      class="aj-backtop"
      aria-label="回到顶部"
      title="回到顶部"
      @click="backToTop"
    >
      ↑
    </button>
  </transition>
</template>
