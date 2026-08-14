<template>
  <router-view v-if="isLoginPage" />
  <Layout v-else />
</template>

<script setup>
import { computed } from 'vue'
import { useRoute } from 'vue-router'
import Layout from './components/Layout.vue'

const route = useRoute()
const isLoginPage = computed(() => route.path === '/login')
</script>

<style>
/* ===== 高原绿水青山 · 浅色玻璃拟态全局样式 ===== */
:root {
  --bg-primary: #eef5f0;
  --bg-secondary: #f6faf7;
  --bg-card: rgba(255, 255, 255, 0.72);
  --bg-card-hover: rgba(255, 255, 255, 0.88);
  --bg-glass: rgba(255, 255, 255, 0.85);
  --border-glass: rgba(255, 255, 255, 0.85);
  --border-glass-hover: rgba(14, 159, 110, 0.35);
  --text-primary: #0f2e1f;
  --text-secondary: #3d5a4c;
  --text-muted: #7a968a;
  --accent-green: #0e9f6e;
  --accent-green-glow: rgba(14, 159, 110, 0.3);
  --accent-cyan: #0b8fa8;
  --accent-cyan-glow: rgba(11, 143, 168, 0.3);
  --accent-blue: #2470d8;
  --accent-purple: #7a4fd0;
  --accent-orange: #c77f0a;
  --accent-red: #dc3535;
  --shadow-glow: 0 0 20px rgba(14, 159, 110, 0.12);
  --shadow-card: 0 4px 24px rgba(46, 125, 82, 0.08);
  --radius-sm: 8px;
  --radius-md: 12px;
  --radius-lg: 16px;
  --radius-xl: 20px;
  --el-color-primary: #0e9f6e;
}

* { box-sizing: border-box; margin: 0; padding: 0; }

html {
  scroll-behavior: smooth;
  font-size: 14px;
}

body {
  margin: 0;
  font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", "PingFang SC", "Hiragino Sans GB", "Microsoft YaHei", "Noto Sans SC", Roboto, sans-serif;
  -webkit-font-smoothing: antialiased;
  -moz-osx-font-smoothing: grayscale;
  background: linear-gradient(120deg, #e8f5ec, #e3f2f7, #eef7e9, #e8f0fa);
  background-size: 400% 400%;
  animation: gradientFlow 28s ease infinite;
  color: var(--text-primary);
  overflow: hidden;
}

/* 高原极光 —— 绿/青双层径向渐变缓慢漂移 */
body::before {
  content: '';
  position: fixed;
  inset: -20%;
  background:
    radial-gradient(ellipse 45% 35% at 18% 22%, rgba(16, 185, 129, 0.14), transparent 65%),
    radial-gradient(ellipse 40% 32% at 82% 12%, rgba(56, 189, 248, 0.12), transparent 65%),
    radial-gradient(ellipse 42% 36% at 72% 85%, rgba(52, 211, 153, 0.10), transparent 65%);
  animation: auroraDrift 36s ease-in-out infinite alternate;
  pointer-events: none;
  z-index: 0;
}
body::after {
  content: '';
  position: fixed;
  inset: -20%;
  background:
    radial-gradient(ellipse 38% 30% at 25% 78%, rgba(14, 165, 183, 0.10), transparent 60%),
    radial-gradient(ellipse 34% 28% at 88% 55%, rgba(110, 231, 183, 0.12), transparent 60%);
  animation: auroraDrift 44s ease-in-out infinite alternate-reverse;
  pointer-events: none;
  z-index: 0;
}

@keyframes gradientFlow {
  0% { background-position: 0% 50%; }
  50% { background-position: 100% 50%; }
  100% { background-position: 0% 50%; }
}
@keyframes auroraDrift {
  0% { transform: translate(0, 0) scale(1); }
  50% { transform: translate(3%, -2%) scale(1.06); }
  100% { transform: translate(-3%, 2%) scale(1.02); }
}

#app { height: 100vh; position: relative; z-index: 1; }

/* 滚动条 */
::-webkit-scrollbar { width: 5px; height: 5px; }
::-webkit-scrollbar-track { background: transparent; }
::-webkit-scrollbar-thumb { background: rgba(15, 60, 40, 0.15); border-radius: 10px; }
::-webkit-scrollbar-thumb:hover { background: rgba(15, 60, 40, 0.28); }

/* ===== Element Plus 浅色主题覆盖 ===== */
:deep(.el-card) {
  background: var(--bg-card) !important;
  border: 1px solid var(--border-glass) !important;
  border-radius: var(--radius-lg) !important;
  backdrop-filter: blur(12px);
  color: var(--text-primary);
  box-shadow: var(--shadow-card);
  transition: all 0.3s ease;
}
:deep(.el-card:hover) {
  border-color: var(--border-glass-hover) !important;
  box-shadow: 0 8px 32px rgba(46, 125, 82, 0.14), var(--shadow-glow);
}
:deep(.el-card__header) {
  border-bottom: 1px solid rgba(15, 60, 40, 0.07) !important;
  color: var(--text-primary);
  font-weight: 600;
  padding: 14px 18px;
}
:deep(.el-card__body) {
  color: var(--text-secondary);
  padding: 18px;
}

:deep(.el-button--primary) {
  background: linear-gradient(135deg, #10b981, #0e9f6e) !important;
  border: none !important;
  box-shadow: 0 4px 14px rgba(14, 159, 110, 0.3) !important;
  transition: all 0.3s ease !important;
}
:deep(.el-button--primary:hover) {
  transform: translateY(-1px);
  box-shadow: 0 6px 20px rgba(14, 159, 110, 0.42) !important;
}

:deep(.el-tag) {
  border: 1px solid rgba(15, 60, 40, 0.1) !important;
  backdrop-filter: blur(4px);
}
:deep(.el-tag--success) { background: rgba(16, 185, 129, 0.12) !important; color: #0d9862 !important; }
:deep(.el-tag--warning) { background: rgba(245, 158, 11, 0.12) !important; color: #c77f0a !important; }
:deep(.el-tag--danger) { background: rgba(239, 68, 68, 0.12) !important; color: #dc3535 !important; }
:deep(.el-tag--info) { background: rgba(90, 122, 106, 0.12) !important; color: #3d5a4c !important; }

:deep(.el-table) {
  background: transparent !important;
  --el-table-border-color: rgba(15, 60, 40, 0.08);
  --el-table-header-bg-color: rgba(255, 255, 255, 0.55);
  --el-table-row-hover-bg-color: rgba(16, 185, 129, 0.06);
  --el-table-text-color: var(--text-secondary);
  --el-table-header-text-color: var(--text-primary);
}
:deep(.el-table th) { font-weight: 600; }
:deep(.el-table tr) { background: transparent !important; }

:deep(.el-input__wrapper) {
  background: rgba(255, 255, 255, 0.7) !important;
  border: 1px solid rgba(15, 60, 40, 0.1) !important;
  box-shadow: none !important;
  border-radius: var(--radius-sm) !important;
}
:deep(.el-input__inner) { color: var(--text-primary) !important; }

:deep(.el-dialog) {
  background: var(--bg-glass) !important;
  border: 1px solid var(--border-glass) !important;
  border-radius: var(--radius-xl) !important;
  backdrop-filter: blur(20px) !important;
  box-shadow: 0 25px 50px rgba(46, 125, 82, 0.2) !important;
}
:deep(.el-dialog__header) { color: var(--text-primary) !important; border-bottom: 1px solid rgba(15, 60, 40, 0.07); }
:deep(.el-dialog__title) { color: var(--text-primary) !important; font-weight: 600; }

:deep(.el-divider) { border-color: rgba(15, 60, 40, 0.1) !important; }

:deep(.el-empty__description) { color: var(--text-muted) !important; }

:deep(.el-progress-bar__outer) { background: rgba(15, 60, 40, 0.08) !important; }

:deep(.el-form-item__label) { color: var(--text-secondary) !important; }

:deep(.el-select-dropdown) {
  background: var(--bg-glass) !important;
  border: 1px solid var(--border-glass) !important;
  backdrop-filter: blur(16px) !important;
}
:deep(.el-select-dropdown__item) { color: var(--text-secondary) !important; }
:deep(.el-select-dropdown__item.hover) { background: rgba(16, 185, 129, 0.08) !important; }
:deep(.el-select-dropdown__item.selected) { color: var(--accent-green) !important; }

:deep(.el-breadcrumb__inner) { color: var(--text-muted) !important; }
:deep(.el-breadcrumb__item:last-child .el-breadcrumb__inner) { color: var(--text-primary) !important; }

:deep(.el-alert) {
  background: rgba(255, 255, 255, 0.7) !important;
  border: 1px solid rgba(15, 60, 40, 0.08) !important;
  border-radius: var(--radius-md) !important;
}

:deep(.el-overlay) { backdrop-filter: blur(4px); }

:deep(.el-descriptions__label) { color: var(--text-muted) !important; }
:deep(.el-descriptions__content) { color: var(--text-primary) !important; }
:deep(.el-descriptions__body) { background: transparent !important; }
</style>
