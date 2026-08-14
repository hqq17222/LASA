<template>
  <el-container class="layout">
    <!-- 左侧磨砂侧边栏 -->
    <el-aside width="240px" class="sidebar">
      <!-- Logo 区域 -->
      <div class="brand">
        <div class="brand-glow"></div>
        <div class="brand-icon">
          <svg width="32" height="32" viewBox="0 0 32 32" fill="none">
            <defs>
              <linearGradient id="logoGrad" x1="0" y1="0" x2="32" y2="32">
                <stop offset="0%" stop-color="#10b981"/>
                <stop offset="100%" stop-color="#0b8fa8"/>
              </linearGradient>
            </defs>
            <circle cx="16" cy="16" r="14" stroke="url(#logoGrad)" stroke-width="2" fill="none"/>
            <path d="M16 6 L16 16 L24 20" stroke="url(#logoGrad)" stroke-width="2" stroke-linecap="round"/>
            <circle cx="16" cy="16" r="3" fill="url(#logoGrad)"/>
          </svg>
        </div>
        <div class="brand-text">
          <div class="brand-title">拉萨南北山</div>
          <div class="brand-sub">生态监测评估系统</div>
        </div>
      </div>

      <!-- 导航菜单 -->
      <el-menu :default-active="$route.path" router class="menu" :collapse-transition="false">
        <el-menu-item index="/">
          <div class="menu-icon"><el-icon :size="18"><HomeFilled /></el-icon></div>
          <span>工作台</span>
        </el-menu-item>
        <el-menu-item index="/map">
          <div class="menu-icon"><el-icon :size="18"><MapLocation /></el-icon></div>
          <span>生态一张图</span>
        </el-menu-item>
        <el-menu-item index="/data">
          <div class="menu-icon"><el-icon :size="18"><Document /></el-icon></div>
          <span>数据目录</span>
        </el-menu-item>
        <el-menu-item index="/patrol-photos">
          <div class="menu-icon"><el-icon :size="18"><Camera /></el-icon></div>
          <span>巡检照片</span>
        </el-menu-item>
        <el-menu-item index="/field">
          <div class="menu-icon"><el-icon :size="18"><Position /></el-icon></div>
          <span>野外科考</span>
        </el-menu-item>
        <el-menu-item index="/ops">
          <div class="menu-icon"><el-icon :size="18"><Monitor /></el-icon></div>
          <span>外业看板</span>
        </el-menu-item>
        <el-menu-item index="/indicators">
          <div class="menu-icon"><el-icon :size="18"><DataAnalysis /></el-icon></div>
          <span>评估指标</span>
        </el-menu-item>
        <el-menu-item index="/equipment">
          <div class="menu-icon"><el-icon :size="18"><Cpu /></el-icon></div>
          <span>设备清单</span>
        </el-menu-item>
        <el-menu-item index="/phase-plan">
          <div class="menu-icon"><el-icon :size="18"><Calendar /></el-icon></div>
          <span>阶段计划</span>
        </el-menu-item>
        <el-menu-item index="/alarms">
          <div class="menu-icon"><el-icon :size="18"><WarningFilled /></el-icon></div>
          <span>偏离度预警</span>
        </el-menu-item>
        <el-menu-item index="/reports">
          <div class="menu-icon"><el-icon :size="18"><Reading /></el-icon></div>
          <span>评估报告</span>
        </el-menu-item>
        <el-divider class="menu-divider" />
        <el-menu-item v-if="isAdmin" index="/users">
          <div class="menu-icon"><el-icon :size="18"><UserFilled /></el-icon></div>
          <span>用户管理</span>
        </el-menu-item>
        <el-menu-item index="/ins">
          <div class="menu-icon"><el-icon :size="18"><HelpFilled /></el-icon></div>
          <span>使用说明</span>
        </el-menu-item>
      </el-menu>

      <!-- 底部时间 -->
      <div class="sidebar-footer">
        <div class="footer-line"></div>
        <div class="footer-content">
          <div class="time-box">
            <div class="time-main">{{ timeParts.hh }}:{{ timeParts.mm }}</div>
            <div class="time-sub">{{ timeParts.YYYY }}-{{ timeParts.MM }}-{{ timeParts.DD }} 星期{{ timeParts.week }}</div>
          </div>
          <div class="status-dot" :class="{ online: healthOk }">
            <div class="pulse"></div>
          </div>
        </div>
      </div>
    </el-aside>

    <!-- 主内容区 -->
    <el-container class="main-wrap">
      <!-- 玻璃拟态顶部栏 -->
      <el-header height="64px" class="header">
        <div class="header-glass"></div>
        <div class="header-content">
          <div class="header-left">
            <div class="page-badge">
              <el-icon :size="16" color="#0e9f6e"><component :is="routeIcon" /></el-icon>
            </div>
            <span class="page-title">{{ $route.meta.title || '系统' }}</span>
            <div class="breadcrumb-wrap">
              <el-breadcrumb separator="/">
                <el-breadcrumb-item :to="{ path: '/' }">首页</el-breadcrumb-item>
                <el-breadcrumb-item>{{ $route.meta.title || '系统' }}</el-breadcrumb-item>
              </el-breadcrumb>
            </div>
          </div>
          <div class="header-right">
            <div class="stat-pills">
              <div class="pill pill-success">
                <div class="pill-dot"></div>
                <span>运行正常</span>
              </div>
              <div class="pill pill-version">
                <span>v0.5.0</span>
              </div>
            </div>
            <div class="user-chip">
              <div class="user-avatar">
                <el-icon :size="14"><UserFilled /></el-icon>
              </div>
              <span class="user-name">{{ userName }}</span>
              <span class="user-role" :class="userRole">{{ roleName }}</span>
              <el-icon class="logout-btn" :size="15" title="退出登录" @click="doLogout"><SwitchButton /></el-icon>
            </div>
          </div>
        </div>
      </el-header>

      <el-main class="main">
        <router-view />
      </el-main>
    </el-container>
  </el-container>
</template>

<script setup>
import { ref, onMounted, onUnmounted, computed } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import {
  HomeFilled, MapLocation, Document, DataAnalysis, Cpu, Calendar,
  WarningFilled, Reading, HelpFilled, Monitor, UserFilled, Camera, Position, SwitchButton
} from '@element-plus/icons-vue'
import { healthApi, authApi } from '../api.js'

const route = useRoute()
const router = useRouter()
const healthOk = ref(false)

const currentUser = computed(() => {
  try { return JSON.parse(localStorage.getItem('lasa_user') || '{}') } catch { return {} }
})
const userName = computed(() => currentUser.value.display_name || currentUser.value.username || '未登录')
const userRole = computed(() => currentUser.value.role || 'viewer')
const roleName = computed(() => ({ admin: '管理员', manager: '项目主管', analyst: '数据分析', viewer: '只读访客' }[userRole.value] || userRole.value))
const isAdmin = computed(() => userRole.value === 'admin')

async function doLogout() {
  try { await authApi.logout() } catch { /* ignore */ }
  localStorage.removeItem('lasa_token')
  localStorage.removeItem('lasa_user')
  ElMessage.success('已退出登录')
  router.push('/login')
}

const routeIconMap = {
  '/': HomeFilled,
  '/map': MapLocation,
  '/data': Document,
  '/indicators': DataAnalysis,
  '/equipment': Cpu,
  '/phase-plan': Calendar,
  '/patrol-photos': Camera,
  '/field': Position,
  '/ops': Monitor,
  '/alarms': WarningFilled,
  '/reports': Reading,
  '/users': UserFilled,
  '/ins': HelpFilled,
}
const routeIcon = computed(() => routeIconMap[route.path] || Monitor)

const timeParts = ref({ YYYY: '', MM: '', DD: '', hh: '', mm: '', week: '' })
let timer = null

function updateTime() {
  const now = new Date()
  const pad = (n) => String(n).padStart(2, '0')
  const weekDays = ['日', '一', '二', '三', '四', '五', '六']
  timeParts.value = {
    YYYY: now.getFullYear(),
    MM: pad(now.getMonth() + 1),
    DD: pad(now.getDate()),
    hh: pad(now.getHours()),
    mm: pad(now.getMinutes()),
    week: weekDays[now.getDay()],
  }
}

onMounted(async () => {
  updateTime()
  timer = setInterval(updateTime, 1000)
  try {
    await healthApi()
    healthOk.value = true
  } catch { healthOk.value = false }
})

onUnmounted(() => {
  if (timer) clearInterval(timer)
})
</script>

<style scoped>
.layout { height: 100vh; }

/* ===== 左侧浅色磨砂侧边栏 ===== */
.sidebar {
  background: linear-gradient(180deg, rgba(255,255,255,0.88) 0%, rgba(240,248,243,0.82) 50%, rgba(235,245,240,0.88) 100%);
  backdrop-filter: blur(18px) saturate(1.2);
  -webkit-backdrop-filter: blur(18px) saturate(1.2);
  position: relative;
  display: flex;
  flex-direction: column;
  border-right: 1px solid rgba(255,255,255,0.9);
  box-shadow: 2px 0 20px rgba(46,125,82,0.06);
}
.sidebar::before {
  content: '';
  position: absolute; inset: 0;
  background:
    radial-gradient(ellipse 80% 50% at 20% 40%, rgba(16,185,129,0.08), transparent),
    radial-gradient(ellipse 60% 40% at 80% 60%, rgba(11,143,168,0.06), transparent);
  pointer-events: none;
}

/* Logo */
.brand {
  position: relative;
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 22px 20px 18px;
  z-index: 1;
}
.brand-glow {
  position: absolute; top: 12px; left: 20px;
  width: 32px; height: 32px;
  border-radius: 50%;
  background: radial-gradient(circle, rgba(16,185,129,0.35), transparent 70%);
  filter: blur(8px);
}
.brand-icon { position: relative; z-index: 1; }
.brand-text { line-height: 1.25; }
.brand-title {
  font-size: 16px; font-weight: 700;
  background: linear-gradient(135deg, #0f2e1f, #2E9E63);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  letter-spacing: 0.5px;
}
.brand-sub { font-size: 11px; color: #7a968a; margin-top: 2px; }

/* 菜单 */
.menu {
  border-right: none;
  background: transparent;
  flex: 1;
  --el-menu-text-color: #3d5a4c;
  --el-menu-hover-text-color: #0f2e1f;
  --el-menu-hover-bg-color: rgba(16,185,129,0.07);
  --el-menu-bg-color: transparent;
  --el-menu-item-height: 44px;
  padding: 4px 10px;
  z-index: 1;
}
:deep(.el-menu-item) {
  border-radius: 10px;
  margin-bottom: 3px;
  font-size: 13px;
  transition: all 0.25s ease;
  position: relative;
  overflow: hidden;
}
:deep(.el-menu-item::before) {
  content: '';
  position: absolute; left: 0; top: 50%; transform: translateY(-50%);
  width: 3px; height: 0; border-radius: 0 3px 3px 0;
  background: linear-gradient(180deg, #10b981, #0b8fa8);
  transition: height 0.3s ease;
}
:deep(.el-menu-item:hover::before) { height: 20px; }
:deep(.el-menu-item.is-active::before) { height: 28px; }

:deep(.el-menu-item .menu-icon) {
  width: 32px; height: 32px; border-radius: 8px;
  display: flex; align-items: center; justify-content: center;
  background: rgba(16,185,129,0.06);
  margin-right: 10px;
  transition: all 0.3s ease;
}
:deep(.el-menu-item:hover .menu-icon) {
  background: rgba(16,185,129,0.14);
  box-shadow: 0 0 12px rgba(16,185,129,0.18);
}
:deep(.el-menu-item.is-active .menu-icon) {
  background: linear-gradient(135deg, rgba(16,185,129,0.22), rgba(11,143,168,0.16));
  box-shadow: 0 0 16px rgba(16,185,129,0.22);
}
:deep(.el-menu-item.is-active) {
  background: linear-gradient(90deg, rgba(16,185,129,0.12), transparent) !important;
  color: #0f2e1f !important;
  font-weight: 600;
}
:deep(.el-menu-item.is-active .menu-icon .el-icon) { color: #0d9862; }

.menu-divider {
  margin: 8px 16px !important;
  border-color: rgba(15,60,40,0.08) !important;
}

/* 底部时间 */
.sidebar-footer {
  padding: 0 16px 16px;
  z-index: 1;
}
.footer-line {
  height: 1px;
  background: linear-gradient(90deg, transparent, rgba(15,60,40,0.12), transparent);
  margin-bottom: 12px;
}
.footer-content {
  display: flex; align-items: center; justify-content: space-between;
}
.time-box { text-align: left; }
.time-main {
  font-size: 22px; font-weight: 700;
  background: linear-gradient(135deg, #0f2e1f, #2E9E63);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  line-height: 1;
  font-variant-numeric: tabular-nums;
}
.time-sub { font-size: 10px; color: #9ab5a8; margin-top: 4px; }
.status-dot {
  width: 10px; height: 10px; border-radius: 50%;
  background: #9ab5a8; position: relative;
  transition: background 0.3s;
}
.status-dot.online { background: #10b981; }
.pulse {
  position: absolute; inset: -4px;
  border-radius: 50%;
  border: 2px solid transparent;
  animation: none;
}
.status-dot.online .pulse {
  border-color: rgba(16,185,129,0.3);
  animation: pulse-ring 2s ease-out infinite;
}
@keyframes pulse-ring {
  0% { transform: scale(0.8); opacity: 1; }
  100% { transform: scale(1.8); opacity: 0; }
}

/* ===== 玻璃拟态顶部栏 ===== */
.header {
  position: relative;
  padding: 0;
  overflow: visible;
  z-index: 10;
}
.header-glass {
  position: absolute; inset: 0;
  background: rgba(255, 255, 255, 0.68);
  backdrop-filter: blur(16px) saturate(1.2);
  -webkit-backdrop-filter: blur(16px) saturate(1.2);
  border-bottom: 1px solid rgba(255,255,255,0.9);
  box-shadow: 0 2px 16px rgba(46,125,82,0.06);
}
.header-content {
  position: relative;
  height: 100%;
  display: flex; align-items: center; justify-content: space-between;
  padding: 0 24px;
}

.header-left {
  display: flex; align-items: center; gap: 12px;
}
.page-badge {
  width: 32px; height: 32px; border-radius: 10px;
  background: linear-gradient(135deg, rgba(16,185,129,0.16), rgba(11,143,168,0.12));
  border: 1px solid rgba(16,185,129,0.2);
  display: flex; align-items: center; justify-content: center;
}
.page-title {
  font-size: 17px; font-weight: 700;
  background: linear-gradient(135deg, #0f2e1f, #2E9E63);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
}
.breadcrumb-wrap {
  padding-left: 12px;
  border-left: 1px solid rgba(15,60,40,0.1);
}

.header-right {
  display: flex; align-items: center; gap: 14px;
}
.stat-pills {
  display: flex; align-items: center; gap: 8px;
}
.pill {
  display: flex; align-items: center; gap: 6px;
  padding: 5px 12px; border-radius: 20px;
  font-size: 12px;
  border: 1px solid rgba(15,60,40,0.1);
  backdrop-filter: blur(4px);
}
.pill-success {
  background: rgba(16,185,129,0.12);
  color: #0d9862;
}
.pill-dot {
  width: 6px; height: 6px; border-radius: 50%;
  background: #10b981;
  box-shadow: 0 0 6px rgba(16,185,129,0.5);
}
.pill-version {
  background: rgba(255,255,255,0.6);
  color: #7a968a;
}
.user-chip {
  display: flex; align-items: center; gap: 8px;
  padding: 4px 12px 4px 4px;
  border-radius: 20px;
  background: rgba(255,255,255,0.6);
  border: 1px solid rgba(255,255,255,0.9);
}
.user-avatar {
  width: 26px; height: 26px; border-radius: 50%;
  background: linear-gradient(135deg, #10b981, #0b8fa8);
  display: flex; align-items: center; justify-content: center;
  color: #fff;
}
.user-name { font-size: 12px; color: #3d5a4c; }
.user-role { font-size: 10px; padding: 1px 7px; border-radius: 8px; font-weight: 600; }
.user-role.admin { background: rgba(220,53,53,0.1); color: #dc3535; }
.user-role.manager { background: rgba(221,106,26,0.12); color: #dd6a1a; }
.user-role.analyst { background: rgba(36,112,216,0.1); color: #2470d8; }
.user-role.viewer { background: rgba(90,122,106,0.12); color: #5a7a6a; }
.logout-btn { color: #9ab5a8; cursor: pointer; transition: color 0.2s; }
.logout-btn:hover { color: #dc3535; }

/* 主内容区 */
.main {
  background: transparent;
  padding: 20px 24px;
  overflow: auto;
}

/* ===== 移动端适配：侧边栏转顶部横向导航 ===== */
@media (max-width: 768px) {
  .layout { flex-direction: column; }
  .sidebar {
    width: 100% !important;
    height: auto;
    flex-direction: row;
    align-items: center;
    border-right: none;
    border-bottom: 1px solid rgba(255,255,255,0.9);
    box-shadow: 0 2px 14px rgba(46,125,82,0.08);
  }
  .brand { padding: 10px 12px; flex-shrink: 0; }
  .brand-glow, .brand-sub { display: none; }
  .brand-title { font-size: 14px; white-space: nowrap; }
  .menu {
    display: flex;
    overflow-x: auto;
    overflow-y: hidden;
    padding: 6px 8px;
    -webkit-overflow-scrolling: touch;
  }
  .menu::-webkit-scrollbar { display: none; }
  :deep(.el-menu-item) {
    flex-shrink: 0;
    margin-bottom: 0;
    margin-right: 4px;
    padding: 6px 10px !important;
    height: 38px;
    line-height: 38px;
  }
  :deep(.el-menu-item::before) { display: none; }
  :deep(.el-menu-item .menu-icon) { display: none; }
  :deep(.el-menu-item span) { font-size: 12px; white-space: nowrap; }
  .menu-divider, .sidebar-footer { display: none; }
  .header { height: 48px !important; }
  .header-content { padding: 0 12px; }
  .breadcrumb-wrap, .user-chip, .pill-success { display: none; }
  .page-title { font-size: 15px; }
  .main { padding: 12px; }
}
</style>
