<template>
  <div class="dashboard">
    <!-- 顶部统计卡片区 -->
    <div class="stats-row">
      <div class="stat-card" v-for="(card, idx) in statCards" :key="idx" :style="{ '--card-accent': card.color }">
        <div class="stat-glow" :style="{ background: card.glow }"></div>
        <div class="stat-content">
          <div class="stat-header">
            <div class="stat-icon" :style="{ background: card.iconBg }">
              <el-icon :size="20" :color="card.color"><component :is="card.icon" /></el-icon>
            </div>
            <div class="stat-trend" :class="card.trendClass">{{ card.trend }}</div>
          </div>
          <div class="stat-value-wrap">
            <div class="stat-value" :style="{ color: card.color }">{{ card.value }}</div>
            <div class="stat-label">{{ card.label }}</div>
          </div>
        </div>
        <svg class="stat-ring" viewBox="0 0 100 100">
          <circle cx="50" cy="50" r="42" fill="none" stroke="rgba(15,60,40,0.06)" stroke-width="3"/>
          <circle cx="50" cy="50" r="42" fill="none" :stroke="card.color" stroke-width="3"
            stroke-linecap="round" stroke-dasharray="264"
            :stroke-dashoffset="264 - (card.ringPct / 100 * 264)"
            transform="rotate(-90 50 50)"
            style="filter: drop-shadow(0 0 4px var(--card-accent)); transition: stroke-dashoffset 1.5s ease;"
          />
        </svg>
      </div>
    </div>

    <!-- 第二行：图表 + 预警 -->
    <div class="row-2">
      <div class="glass-card chart-card">
        <div class="card-header-bar">
          <div class="card-title">
            <div class="title-dot" style="background: linear-gradient(135deg, #10b981, #06b6d4);"></div>
            <span>评估指标趋势</span>
          </div>
          <div class="chart-legend">
            <span class="legend-item"><span class="dot" style="background: #10b981;"></span>NDVI</span>
            <span class="legend-item"><span class="dot" style="background: #3b82f6;"></span>FVC</span>
            <span class="legend-item"><span class="dot" style="background: #f59e0b;"></span>碳储量</span>
          </div>
        </div>
        <div class="chart-area">
          <svg class="area-chart" viewBox="0 0 600 180" preserveAspectRatio="none">
            <defs>
              <linearGradient id="grad1" x1="0" y1="0" x2="0" y2="1">
                <stop offset="0%" stop-color="#10b981" stop-opacity="0.3"/>
                <stop offset="100%" stop-color="#10b981" stop-opacity="0"/>
              </linearGradient>
              <linearGradient id="grad2" x1="0" y1="0" x2="0" y2="1">
                <stop offset="0%" stop-color="#3b82f6" stop-opacity="0.25"/>
                <stop offset="100%" stop-color="#3b82f6" stop-opacity="0"/>
              </linearGradient>
              <linearGradient id="grad3" x1="0" y1="0" x2="0" y2="1">
                <stop offset="0%" stop-color="#f59e0b" stop-opacity="0.2"/>
                <stop offset="100%" stop-color="#f59e0b" stop-opacity="0"/>
              </linearGradient>
            </defs>
            <!-- Grid lines -->
            <line v-for="y in [0,45,90,135,180]" :key="y" x1="0" :y1="y" x2="600" :y2="y" stroke="rgba(15,60,40,0.06)" stroke-width="1"/>
            <!-- Area fills -->
            <path d="M0,120 C80,100 160,80 240,70 S400,40 480,30 S560,20 600,15 L600,180 L0,180 Z" fill="url(#grad1)"/>
            <path d="M0,140 C80,130 160,115 240,100 S400,80 480,65 S560,55 600,50 L600,180 L0,180 Z" fill="url(#grad2)"/>
            <path d="M0,155 C80,148 160,140 240,130 S400,115 480,100 S560,90 600,85 L600,180 L0,180 Z" fill="url(#grad3)"/>
            <!-- Lines -->
            <path d="M0,120 C80,100 160,80 240,70 S400,40 480,30 S560,20 600,15" fill="none" stroke="#10b981" stroke-width="2" stroke-linecap="round" filter="drop-shadow(0 0 4px rgba(16,185,129,0.4))"/>
            <path d="M0,140 C80,130 160,115 240,100 S400,80 480,65 S560,55 600,50" fill="none" stroke="#3b82f6" stroke-width="2" stroke-linecap="round" filter="drop-shadow(0 0 4px rgba(59,130,246,0.4))"/>
            <path d="M0,155 C80,148 160,140 240,130 S400,115 480,100 S560,90 600,85" fill="none" stroke="#f59e0b" stroke-width="2" stroke-linecap="round" filter="drop-shadow(0 0 4px rgba(245,158,11,0.4))"/>
            <!-- End dots -->
            <circle cx="600" cy="15" r="4" fill="#10b981"/>
            <circle cx="600" cy="50" r="4" fill="#3b82f6"/>
            <circle cx="600" cy="85" r="4" fill="#f59e0b"/>
          </svg>
        </div>
      </div>

      <div class="glass-card alarm-card">
        <div class="card-header-bar">
          <div class="card-title">
            <div class="title-dot" style="background: linear-gradient(135deg, #ef4444, #f59e0b);"></div>
            <span>偏离度预警</span>
            <el-tag v-if="stats.alarms > 0" type="danger" size="small" effect="dark" class="alarm-count">{{ stats.alarms }}</el-tag>
          </div>
        </div>
        <div class="alarm-list-modern">
          <div v-if="recentAlarms.length === 0" class="alarm-empty">
            <div class="empty-ring">
              <el-icon :size="28" color="#10b981"><CircleCheck /></el-icon>
            </div>
            <div class="empty-title">系统运行正常</div>
            <div class="empty-sub">当前无未处理预警</div>
          </div>
          <div v-else class="alarm-items">
            <div class="alarm-item-modern" v-for="a in recentAlarms" :key="a.id"
              :class="{ 'level-red': a.level === 'red', 'level-orange': a.level === 'orange', 'level-yellow': a.level === 'yellow' }">
              <div class="alarm-pulse-dot"></div>
              <div class="alarm-body">
                <div class="alarm-title-text">{{ a.title }}</div>
                <div class="alarm-meta">{{ a.alarm_type }} · {{ formatTime(a.created_at) }}</div>
              </div>
              <el-tag :type="levelType(a.level)" size="small" effect="dark">{{ a.level }}</el-tag>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- 第三行：雷达图 + 项目卡片 -->
    <div class="row-3">
      <div class="glass-card radar-card">
        <div class="card-header-bar">
          <div class="card-title">
            <div class="title-dot" style="background: linear-gradient(135deg, #8b5cf6, #ec4899);"></div>
            <span>五维评估雷达</span>
          </div>
        </div>
        <div class="radar-wrap">
          <svg class="radar-chart" viewBox="0 0 240 220">
            <!-- 背景网格 -->
            <g v-for="r in [0.2,0.4,0.6,0.8,1.0]" :key="r">
              <polygon :points="radarPoints(r, 5)" fill="none" stroke="rgba(15,60,40,0.08)" stroke-width="1"/>
            </g>
            <!-- 轴线 -->
            <line v-for="i in 5" :key="'a'+i" :x1="120" :y1="110" :x2="radarAxis(i-1,5).x" :y2="radarAxis(i-1,5).y" stroke="rgba(15,60,40,0.1)" stroke-width="1"/>
            <!-- 数据区域 -->
            <polygon :points="radarDataPoints(dimensionScores)" fill="rgba(139,92,246,0.15)" stroke="#8b5cf6" stroke-width="2" stroke-linejoin="round"/>
            <polygon :points="radarDataPoints(targetScores)" fill="rgba(6,182,212,0.08)" stroke="#06b6d4" stroke-width="1.5" stroke-dasharray="4,4" stroke-linejoin="round"/>
            <!-- 数据点 -->
            <circle v-for="(pt, i) in radarDataCircles(dimensionScores)" :key="'c'+i" :cx="pt.x" :cy="pt.y" r="4" fill="#8b5cf6" stroke="#ffffff" stroke-width="2"/>
            <!-- 标签 -->
            <text v-for="(label, i) in radarLabels" :key="'l'+i" :x="radarLabelPos(i,5).x" :y="radarLabelPos(i,5).y" text-anchor="middle" fill="#5a7a6a" font-size="11">{{ label }}</text>
          </svg>
          <div class="radar-legend">
            <div class="rl-item"><span class="rl-dot" style="background: #8b5cf6;"></span>当前值</div>
            <div class="rl-item"><span class="rl-dot" style="background: #06b6d4; border-style: dashed;"></span>目标值</div>
          </div>
        </div>
      </div>

      <div class="glass-card project-card">
        <div class="card-header-bar">
          <div class="card-title">
            <div class="title-dot" style="background: linear-gradient(135deg, #3b82f6, #06b6d4);"></div>
            <span>项目进展</span>
          </div>
        </div>
        <div class="project-list-modern">
          <div class="project-item-modern" v-for="p in projectList" :key="p.id">
            <div class="project-info">
              <div class="project-name">{{ p.name }}</div>
              <div class="project-code">{{ p.code }}</div>
            </div>
            <div class="project-progress-wrap">
              <div class="progress-track">
                <div class="progress-fill" :style="{ width: (p.progress || 0) + '%', background: p.progress === 100 ? '#10b981' : '#3b82f6' }"></div>
              </div>
              <span class="progress-text">{{ p.progress || 0 }}%</span>
            </div>
            <div class="project-status" :class="p.status">{{ statusLabel(p.status) }}</div>
          </div>
        </div>
      </div>

      <div class="glass-card quick-card">
        <div class="card-header-bar">
          <div class="card-title">
            <div class="title-dot" style="background: linear-gradient(135deg, #f59e0b, #ef4444);"></div>
            <span>快速入口</span>
          </div>
        </div>
        <div class="quick-grid-modern">
          <div class="quick-item-modern" v-for="(item, idx) in quickItems" :key="idx" @click="$router.push(item.path)" :style="{ '--qi-color': item.color }">
            <div class="quick-glow"></div>
            <div class="quick-icon-wrap" :style="{ background: item.bg }">
              <el-icon :size="20" color="#fff"><component :is="item.icon" /></el-icon>
            </div>
            <div class="quick-label">{{ item.label }}</div>
            <div class="quick-desc">{{ item.desc }}</div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import {
  FolderOpened, Document, View, WarningFilled, CircleCheck,
  MapLocation, DataAnalysis, Reading, Cpu, Calendar, Camera, Position
} from '@element-plus/icons-vue'
import { healthApi, projectApi, dataSourceApi, observationApi, alarmApi, indicatorApi } from '../api.js'

const health = ref({})
const stats = ref({ projects: 0, dataSources: 0, observations: 0, alarms: 0 })
const projectList = ref([])
const recentAlarms = ref([])
const dimensionScores = ref([0.72, 0.65, 0.58, 0.80, 0.45])
const targetScores = ref([0.85, 0.80, 0.75, 0.90, 0.70])
const radarLabels = ['结构', '功能', '压力', '工程响应', '稳定性']

const statCards = ref([
  { icon: FolderOpened, label: '项目数', value: 0, color: '#0e9f6e', glow: 'rgba(16,185,129,0.15)', iconBg: 'rgba(16,185,129,0.12)', trend: '活跃', trendClass: 'up', ringPct: 0 },
  { icon: Document, label: '数据源', value: 0, color: '#2470d8', glow: 'rgba(59,130,246,0.15)', iconBg: 'rgba(59,130,246,0.1)', trend: '已归档', trendClass: 'flat', ringPct: 0 },
  { icon: View, label: '观测记录', value: 0, color: '#0b8fa8', glow: 'rgba(6,182,212,0.15)', iconBg: 'rgba(6,182,212,0.1)', trend: '累计', trendClass: 'flat', ringPct: 0 },
  { icon: WarningFilled, label: '未处理预警', value: 0, color: '#dc3535', glow: 'rgba(239,68,68,0.15)', iconBg: 'rgba(239,68,68,0.1)', trend: '待处理', trendClass: 'down', ringPct: 0 },
])

const quickItems = [
  { icon: MapLocation, label: '生态一张图', desc: 'GIS可视化', path: '/map', color: '#3b82f6', bg: 'linear-gradient(135deg, #3b82f6, #1d4ed8)' },
  { icon: Position, label: '野外科考', desc: '照片与轨迹', path: '/field', color: '#0e9f6e', bg: 'linear-gradient(135deg, #10b981, #047857)' },
  { icon: Camera, label: '巡检照片', desc: '无人机巡检', path: '/patrol-photos', color: '#8b5cf6', bg: 'linear-gradient(135deg, #8b5cf6, #7c3aed)' },
  { icon: DataAnalysis, label: '指标计算', desc: '评估分析', path: '/indicators', color: '#f59e0b', bg: 'linear-gradient(135deg, #f59e0b, #d97706)' },
  { icon: WarningFilled, label: '偏离预警', desc: '异常监测', path: '/alarms', color: '#ef4444', bg: 'linear-gradient(135deg, #ef4444, #dc2626)' },
  { icon: Reading, label: '评估报告', desc: '生成报告', path: '/reports', color: '#10b981', bg: 'linear-gradient(135deg, #10b981, #059669)' },
  { icon: Cpu, label: '设备清单', desc: '资产管理', path: '/equipment', color: '#06b6d4', bg: 'linear-gradient(135deg, #06b6d4, #0891b2)' },
]

function formatTime(t) {
  if (!t) return '-'
  return new Date(t).toLocaleString('zh-CN', { month: 'short', day: 'numeric', hour: '2-digit', minute: '2-digit' })
}
function levelType(l) {
  return { yellow: 'warning', orange: 'warning', red: 'danger' }[l] || 'info'
}
function statusLabel(s) {
  return { completed: '已完成', ongoing: '进行中', pending: '待启动', paused: '暂停' }[s] || s
}

/* Radar chart helpers */
function radarPoints(ratio, n) {
  const cx=120, cy=110, R=90
  const pts = []
  for (let i=0; i<n; i++) {
    const angle = (Math.PI*2*i/n) - Math.PI/2
    pts.push(`${cx + R*ratio*Math.cos(angle)},${cy + R*ratio*Math.sin(angle)}`)
  }
  return pts.join(' ')
}
function radarAxis(i, n) {
  const cx=120, cy=110, R=90
  const angle = (Math.PI*2*i/n) - Math.PI/2
  return { x: cx + R*Math.cos(angle), y: cy + R*Math.sin(angle) }
}
function radarDataPoints(scores) {
  const cx=120, cy=110, R=90, n=5
  return scores.map((s,i) => {
    const angle = (Math.PI*2*i/n) - Math.PI/2
    return `${cx + R*s*Math.cos(angle)},${cy + R*s*Math.sin(angle)}`
  }).join(' ')
}
function radarDataCircles(scores) {
  const cx=120, cy=110, R=90, n=5
  return scores.map((s,i) => {
    const angle = (Math.PI*2*i/n) - Math.PI/2
    return { x: cx + R*s*Math.cos(angle), y: cy + R*s*Math.sin(angle) }
  })
}
function radarLabelPos(i, n) {
  const cx=120, cy=110, R=105
  const angle = (Math.PI*2*i/n) - Math.PI/2
  return { x: cx + R*Math.cos(angle), y: cy + R*Math.sin(angle) + 4 }
}

onMounted(async () => {
  health.value = await healthApi().catch(() => ({}))
  const [p, d, o, a, ind] = await Promise.all([
    projectApi.list().catch(() => []),
    dataSourceApi.list().catch(() => []),
    observationApi.list().catch(() => []),
    alarmApi.list({ status: 'open' }).catch(() => []),
    indicatorApi.list(0).catch(() => []),
  ])

  stats.value = { projects: p.length, dataSources: d.length, observations: o.length, alarms: a.length }
  statCards.value[0].value = p.length
  statCards.value[1].value = d.length
  statCards.value[2].value = o.length
  statCards.value[3].value = a.length
  statCards.value[0].ringPct = Math.min(p.length * 20, 100)
  statCards.value[1].ringPct = Math.min(d.length * 15, 100)
  statCards.value[2].ringPct = Math.min(o.length * 2, 100)
  statCards.value[3].ringPct = a.length > 0 ? Math.min(a.length * 25, 100) : 0

  projectList.value = p.slice(0, 5)
  recentAlarms.value = a.slice(0, 5)

  // Compute dimension averages from indicator results
  const dims = { structure: [], function: [], pressure: [], response: [], stability: [] }
  const dimMap = { structure: 0, function: 1, pressure: 2, response: 3, stability: 4 }
  for (const item of ind) {
    if (item.dimension in dims && item.value != null) {
      dims[item.dimension].push(item.value)
    }
  }
  for (const [dim, vals] of Object.entries(dims)) {
    if (vals.length > 0) {
      const avg = vals.reduce((s, v) => s + v, 0) / vals.length
      dimensionScores.value[dimMap[dim]] = Math.min(avg / 100, 1)
    }
  }
})
</script>

<style scoped>
.dashboard { padding-bottom: 20px; }

/* ===== 统计卡片行 ===== */
.stats-row {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 16px;
  margin-bottom: 16px;
}
.stat-card {
  position: relative;
  background: rgba(255,255,255,0.6);
  border: 1px solid rgba(255,255,255,0.85);
  border-radius: 16px;
  padding: 20px;
  backdrop-filter: blur(12px);
  overflow: hidden;
  transition: all 0.3s ease;
  box-shadow: 0 4px 20px rgba(46,125,82,0.07);
}
.stat-card:hover {
  border-color: rgba(46,158,99,0.35);
  transform: translateY(-2px);
  box-shadow: 0 10px 32px rgba(46,125,82,0.14), 0 0 20px var(--card-accent);
}
.stat-glow {
  position: absolute; top: -40px; right: -40px;
  width: 120px; height: 120px; border-radius: 50%;
  filter: blur(40px); opacity: 0.6;
  pointer-events: none;
}
.stat-content { position: relative; z-index: 1; }
.stat-header {
  display: flex; align-items: center; justify-content: space-between;
  margin-bottom: 14px;
}
.stat-icon {
  width: 40px; height: 40px; border-radius: 12px;
  display: flex; align-items: center; justify-content: center;
  border: 1px solid rgba(255,255,255,0.75);
}
.stat-trend {
  font-size: 11px; padding: 3px 10px; border-radius: 12px;
  font-weight: 500;
}
.stat-trend.up { background: rgba(16,185,129,0.12); color: #0d9862; }
.stat-trend.flat { background: rgba(100,116,139,0.1); color: #5a7a6a; }
.stat-trend.down { background: rgba(239,68,68,0.1); color: #dc3535; }
.stat-value {
  font-size: 32px; font-weight: 800;
  line-height: 1; letter-spacing: -1px;
}
.stat-label {
  font-size: 12px; color: #7a968a; margin-top: 6px; font-weight: 500;
}
.stat-ring {
  position: absolute; bottom: -10px; right: -10px;
  width: 100px; height: 100px; opacity: 0.4;
}

/* ===== 玻璃卡片通用 ===== */
.glass-card {
  background: rgba(255,255,255,0.6);
  border: 1px solid rgba(255,255,255,0.85);
  border-radius: 16px;
  backdrop-filter: blur(12px);
  overflow: hidden;
  transition: all 0.3s ease;
  box-shadow: 0 4px 20px rgba(46,125,82,0.07);
}
.glass-card:hover {
  border-color: rgba(46,158,99,0.3);
}
.card-header-bar {
  display: flex; align-items: center; justify-content: space-between;
  padding: 14px 18px;
  border-bottom: 1px solid rgba(15,60,40,0.06);
}
.card-title {
  display: flex; align-items: center; gap: 8px;
  font-weight: 600; color: #0f2e1f; font-size: 14px;
}
.title-dot {
  width: 8px; height: 8px; border-radius: 50%;
}
.alarm-count { margin-left: 6px; }

/* ===== 第二行 ===== */
.row-2 {
  display: grid;
  grid-template-columns: 1.4fr 0.6fr;
  gap: 16px;
  margin-bottom: 16px;
}
.chart-area { padding: 10px 18px 18px; height: 200px; }
.area-chart { width: 100%; height: 100%; }
.chart-legend {
  display: flex; align-items: center; gap: 14px;
}
.legend-item {
  display: flex; align-items: center; gap: 5px;
  font-size: 11px; color: #7a968a;
}
.legend-item .dot { width: 7px; height: 7px; border-radius: 50%; }

/* 预警卡片 */
.alarm-list-modern { padding: 12px 16px; }
.alarm-empty {
  display: flex; flex-direction: column; align-items: center;
  padding: 30px 0; gap: 10px;
}
.empty-ring {
  width: 56px; height: 56px; border-radius: 50%;
  background: rgba(16,185,129,0.1);
  border: 1px solid rgba(16,185,129,0.25);
  display: flex; align-items: center; justify-content: center;
  animation: breathe 3s ease-in-out infinite;
}
@keyframes breathe {
  0%, 100% { box-shadow: 0 0 0 0 rgba(16,185,129,0.25); }
  50% { box-shadow: 0 0 20px 4px rgba(16,185,129,0.12); }
}
.empty-title { font-size: 14px; font-weight: 600; color: #0d9862; }
.empty-sub { font-size: 12px; color: #9ab5a8; }

.alarm-item-modern {
  display: flex; align-items: center; gap: 10px;
  padding: 10px 12px; border-radius: 10px;
  margin-bottom: 6px;
  background: rgba(255,255,255,0.55);
  border: 1px solid transparent;
  transition: all 0.2s ease;
  cursor: pointer;
}
.alarm-item-modern:hover { background: rgba(255,255,255,0.85); }
.alarm-item-modern.level-red { border-color: rgba(239,68,68,0.25); }
.alarm-item-modern.level-orange { border-color: rgba(245,158,11,0.25); }
.alarm-item-modern.level-yellow { border-color: rgba(234,179,8,0.25); }
.alarm-pulse-dot {
  width: 7px; height: 7px; border-radius: 50%; flex-shrink: 0;
  background: #9ab5a8;
}
.level-red .alarm-pulse-dot { background: #ef4444; box-shadow: 0 0 8px rgba(239,68,68,0.5); animation: dotPulse 1.5s ease-in-out infinite; }
.level-orange .alarm-pulse-dot { background: #f59e0b; box-shadow: 0 0 8px rgba(245,158,11,0.5); }
.level-yellow .alarm-pulse-dot { background: #eab308; box-shadow: 0 0 8px rgba(234,179,8,0.5); }
@keyframes dotPulse {
  0%, 100% { opacity: 1; }
  50% { opacity: 0.4; }
}
.alarm-body { flex: 1; min-width: 0; }
.alarm-title-text { font-size: 12px; color: #1e3a2f; font-weight: 500; white-space: nowrap; overflow: hidden; text-overflow: ellipsis; }
.alarm-meta { font-size: 10px; color: #9ab5a8; margin-top: 2px; }

/* ===== 第三行 ===== */
.row-3 {
  display: grid;
  grid-template-columns: 1fr 1fr 1fr;
  gap: 16px;
}

/* 雷达图 */
.radar-wrap {
  padding: 10px 18px 18px;
  display: flex; flex-direction: column; align-items: center;
}
.radar-chart { width: 100%; max-width: 260px; }
.radar-legend {
  display: flex; gap: 16px; margin-top: 8px;
}
.rl-item {
  display: flex; align-items: center; gap: 5px;
  font-size: 11px; color: #7a968a;
}
.rl-dot { width: 8px; height: 3px; border-radius: 2px; }

/* 项目卡片 */
.project-list-modern { padding: 8px 16px 16px; }
.project-item-modern {
  display: flex; align-items: center; gap: 12px;
  padding: 10px 0; border-bottom: 1px solid rgba(15,60,40,0.06);
}
.project-item-modern:last-child { border-bottom: none; }
.project-info { min-width: 0; width: 120px; }
.project-name { font-size: 13px; font-weight: 500; color: #1e3a2f; white-space: nowrap; overflow: hidden; text-overflow: ellipsis; }
.project-code { font-size: 10px; color: #9ab5a8; margin-top: 1px; }
.project-progress-wrap { flex: 1; display: flex; align-items: center; gap: 8px; }
.progress-track { flex: 1; height: 5px; background: rgba(15,60,40,0.08); border-radius: 3px; overflow: hidden; }
.progress-fill { height: 100%; border-radius: 3px; transition: width 0.8s ease; box-shadow: 0 0 6px rgba(59,130,246,0.3); }
.progress-text { font-size: 11px; color: #7a968a; font-variant-numeric: tabular-nums; width: 32px; text-align: right; }
.project-status { font-size: 10px; padding: 2px 8px; border-radius: 10px; }
.project-status.ongoing { background: rgba(59,130,246,0.12); color: #2470d8; }
.project-status.completed { background: rgba(16,185,129,0.12); color: #0d9862; }
.project-status.pending { background: rgba(100,116,139,0.1); color: #5a7a6a; }

/* 快速入口 */
.quick-grid-modern {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 10px;
  padding: 8px 16px 16px;
}
.quick-item-modern {
  position: relative;
  padding: 14px 12px;
  border-radius: 12px;
  background: rgba(255,255,255,0.55);
  border: 1px solid rgba(255,255,255,0.8);
  cursor: pointer;
  transition: all 0.3s ease;
  overflow: hidden;
}
.quick-item-modern:hover {
  border-color: rgba(46,158,99,0.35);
  transform: translateY(-2px);
  box-shadow: 0 8px 24px rgba(46,125,82,0.14);
}
.quick-glow {
  position: absolute; top: -20px; right: -20px;
  width: 60px; height: 60px; border-radius: 50%;
  background: var(--qi-color);
  filter: blur(30px); opacity: 0;
  transition: opacity 0.3s;
}
.quick-item-modern:hover .quick-glow { opacity: 0.18; }
.quick-icon-wrap {
  width: 36px; height: 36px; border-radius: 10px;
  display: flex; align-items: center; justify-content: center;
  margin-bottom: 8px;
  box-shadow: 0 4px 12px rgba(46,125,82,0.18);
}
.quick-label { font-size: 12px; font-weight: 600; color: #1e3a2f; }
.quick-desc { font-size: 10px; color: #9ab5a8; margin-top: 2px; }

@media (max-width: 1200px) {
  .stats-row { grid-template-columns: repeat(2, 1fr); }
  .row-2 { grid-template-columns: 1fr; }
  .row-3 { grid-template-columns: 1fr; }
}
@media (max-width: 768px) {
  .stats-row { grid-template-columns: 1fr; }
}
</style>
