import { ref, onMounted, onUnmounted } from 'vue'

/** 视口 < 820px 视为移动端（与移动端设计稿断点一致） */
export function useIsMobile(breakpoint = 820) {
  const isMobile = ref(window.innerWidth < breakpoint)
  const onResize = () => { isMobile.value = window.innerWidth < breakpoint }
  onMounted(() => window.addEventListener('resize', onResize))
  onUnmounted(() => window.removeEventListener('resize', onResize))
  return isMobile
}
