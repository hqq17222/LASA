<template>
  <div class="phase-plan-modern">
    <div class="pp-layout">
      <!-- 左侧项目选择 + 总进度 -->
      <div class="pp-sidebar">
        <div class="panel-header">
          <div class="ph-glow" style="background: rgba(6,182,212,0.3);"></div>
          <el-icon :size="16" color="#0b8fa8"><Calendar /></el-icon>
          <span>阶段计划</span>
        </div>
        <div class="pp-project-select">
          <label class="form-label">选择项目</label>
          <el-select v-model="projectId" placeholder="选择项目" @change="load" class="dark-select">
            <el-option v-for="p in projects" :key="p.id" :label="p.name" :value="p.id" />
          </el-select>
        </div>
        <div class="pp-summary" v-if="list.length">
          <div class="pps-title">整体进度</div>
          <div class="pps-ring">
            <svg viewBox="0 0 120 120" class="ring-svg">
              <circle cx="60" cy="60" r="50" fill="none" stroke="rgba(15,60,40,0.08)" stroke-width="8"/>
              <circle cx="60" cy="60" r="50" fill="none" stroke="url(#ringGrad)" stroke-width="8"
                stroke-linecap="round" stroke-dasharray="314"
                :stroke-dashoffset="314 - (overallProgress / 100 * 314)"
                transform="rotate(-90 60 60)"
                style="filter: drop-shadow(0 0 6px rgba(16,185,129,0.4)); transition: stroke-dashoffset 1s ease;"
              />
              <defs><linearGradient id="ringGrad" x1="0" y1="0" x2="1" y2="1"><stop offset="0%" stop-color="#10b981"/><stop offset="100%" stop-color="#06b6d4"/></linearGradient></defs>
            </svg>
            <div class="ring-text">
              <div class="ring-num">{{ overallProgress }}%</div>
              <div class="ring-label">已完成</div>
            </div>
          </div>
          <div class="pps-stats">
            <div class="ps-item"><span class="ps-dot" style="background:#10b981"></span>已完成 {{ completedCount }}</div>
            <div class="ps-item"><span class="ps-dot" style="background:#3b82f6"></span>进行中 {{ ongoingCount }}</div>
            <div class="ps-item"><span class="ps-dot" style="background:#9ab5a8"></span>待启动 {{ pendingCount }}</div>
          </div>
        </div>
      </div>

      <!-- 右侧时间线 -->
      <div class="pp-main">
        <div class="timeline-modern">
          <div class="tl-line"></div>
          <div class="tl-items">
            <div class="tl-item" v-for="(item, idx) in list" :key="item.id" :class="item.status">
              <div class="tl-dot" :class="item.status">
                <div class="tl-dot-inner"></div>
                <div v-if="item.status === 'ongoing'" class="tl-pulse"></div>
              </div>
              <div class="tl-card">
                <div class="tl-card-glow" :class="item.status"></div>
                <div class="tl-header">
                  <div class="tl-phase">Phase {{ item.phase_no }}</div>
                  <div class="tl-time">{{ item.time_range }}</div>
                  <div class="tl-status" :class="item.status">{{ statusText(item.status) }}</div>
                </div>
                <div class="tl-name">{{ item.name }}</div>
                <div class="tl-goal"><b>目标</b> {{ item.goal }}</div>
                <div class="tl-tasks"><b>关键任务</b> {{ item.key_tasks }}</div>
                <div class="tl-deliver"><b>交付物</b> {{ item.deliverables }}</div>
                <div class="tl-milestones"><b>里程碑</b> {{ item.milestones }}</div>
                <div class="tl-progress-wrap">
                  <div class="tl-progress-track">
                    <div class="tl-progress-fill" :class="item.status" :style="{ width: item.progress + '%' }"></div>
                  </div>
                  <span class="tl-progress-num">{{ item.progress }}%</span>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { Calendar } from '@element-plus/icons-vue'
import { projectApi, phasePlanApi } from '../api.js'

const projects = ref([])
const projectId = ref('')
const list = ref([])

const overallProgress = computed(() => {
  if (!list.value.length) return 0
  return Math.round(list.value.reduce((s, i) => s + i.progress, 0) / list.value.length)
})
const completedCount = computed(() => list.value.filter(i => i.status === 'completed').length)
const ongoingCount = computed(() => list.value.filter(i => i.status === 'ongoing').length)
const pendingCount = computed(() => list.value.filter(i => i.status === 'pending').length)

function statusText(s) {
  return { completed: '已完成', ongoing: '进行中', pending: '待启动' }[s] || s
}

async function load() { if (!projectId.value) return; list.value = await phasePlanApi.list(projectId.value) }

onMounted(async () => {
  projects.value = await projectApi.list()
  if (projects.value.length) { projectId.value = projects.value[0].id; await load() }
})
</script>

<style scoped>
.phase-plan-modern { height: 100%; }
.pp-layout { display: flex; gap: 16px; height: calc(100vh - 104px); }

/* 左侧 */
.pp-sidebar {
  width: 260px; flex-shrink: 0;
  background: rgba(255,255,255,0.6);
  border: 1px solid rgba(255,255,255,0.85);
  border-radius: 16px;
  backdrop-filter: blur(12px);
  display: flex; flex-direction: column;
  overflow: hidden;
  box-shadow: 0 4px 20px rgba(46,125,82,0.07);
}
.panel-header {
  display: flex; align-items: center; gap: 8px;
  padding: 14px 16px;
  border-bottom: 1px solid rgba(15,60,40,0.06);
  font-weight: 600; color: #1e3a2f; font-size: 13px;
  position: relative;
}
.ph-glow { position: absolute; left: 8px; top: 10px; width: 24px; height: 24px; border-radius: 50%; filter: blur(8px); opacity: 0.6; }

.pp-project-select { padding: 14px 16px; }
.form-label { display: block; font-size: 11px; color: #7a968a; margin-bottom: 5px; font-weight: 500; }

.pp-summary { padding: 0 16px 16px; flex: 1; }
.pps-title { font-size: 12px; font-weight: 600; color: #5a7a6a; margin-bottom: 14px; }
.pps-ring { position: relative; width: 140px; height: 140px; margin: 0 auto 16px; }
.ring-svg { width: 100%; height: 100%; }
.ring-text { position: absolute; inset: 0; display: flex; flex-direction: column; align-items: center; justify-content: center; }
.ring-num { font-size: 24px; font-weight: 800; color: #0f2e1f; line-height: 1; }
.ring-label { font-size: 10px; color: #9ab5a8; margin-top: 2px; }

.pps-stats { display: flex; flex-direction: column; gap: 8px; }
.ps-item { display: flex; align-items: center; gap: 8px; font-size: 11px; color: #5a7a6a; }
.ps-dot { width: 6px; height: 6px; border-radius: 50%; }

/* 右侧时间线 */
.pp-main { flex: 1; overflow-y: auto; min-width: 0; }
.timeline-modern { position: relative; padding: 20px 20px 20px 40px; }
.tl-line {
  position: absolute; left: 54px; top: 30px; bottom: 30px;
  width: 2px;
  background: linear-gradient(180deg, rgba(16,185,129,0.4), rgba(59,130,246,0.25), rgba(15,60,40,0.08));
}
.tl-items { display: flex; flex-direction: column; gap: 20px; }

.tl-item { position: relative; display: flex; align-items: flex-start; gap: 20px; }
.tl-dot {
  position: relative; z-index: 1;
  width: 28px; height: 28px; border-radius: 50%;
  display: flex; align-items: center; justify-content: center;
  flex-shrink: 0; margin-top: 6px;
  border: 2px solid;
  background: #fff;
}
.tl-dot.completed { border-color: #10b981; }
.tl-dot.ongoing { border-color: #3b82f6; }
.tl-dot.pending { border-color: #9ab5a8; }
.tl-dot-inner { width: 10px; height: 10px; border-radius: 50%; }
.tl-dot.completed .tl-dot-inner { background: #10b981; box-shadow: 0 0 8px #10b981; }
.tl-dot.ongoing .tl-dot-inner { background: #3b82f6; box-shadow: 0 0 8px #3b82f6; }
.tl-dot.pending .tl-dot-inner { background: #9ab5a8; }
.tl-pulse {
  position: absolute; inset: -4px; border-radius: 50%;
  border: 2px solid rgba(59,130,246,0.3);
  animation: tlPulse 2s ease-out infinite;
}
@keyframes tlPulse {
  0% { transform: scale(1); opacity: 1; }
  100% { transform: scale(1.5); opacity: 0; }
}

.tl-card {
  position: relative;
  flex: 1;
  background: rgba(255,255,255,0.6);
  border: 1px solid rgba(255,255,255,0.85);
  border-radius: 14px;
  padding: 16px 18px;
  transition: all 0.3s ease;
  overflow: hidden;
  box-shadow: 0 4px 20px rgba(46,125,82,0.06);
}
.tl-card:hover { border-color: rgba(46,158,99,0.3); }
.tl-card-glow {
  position: absolute; top: -20px; right: -20px;
  width: 60px; height: 60px; border-radius: 50%;
  filter: blur(30px); opacity: 0.08;
}
.tl-card-glow.completed { background: #10b981; }
.tl-card-glow.ongoing { background: #3b82f6; }
.tl-card-glow.pending { background: #9ab5a8; }

.tl-header { display: flex; align-items: center; gap: 10px; margin-bottom: 8px; flex-wrap: wrap; }
.tl-phase {
  font-size: 10px; padding: 2px 8px; border-radius: 4px;
  background: rgba(15,60,40,0.06); color: #5a7a6a; font-weight: 600;
}
.tl-time { font-size: 11px; color: #7a968a; }
.tl-status { font-size: 10px; padding: 2px 8px; border-radius: 4px; font-weight: 600; margin-left: auto; }
.tl-status.completed { background: rgba(16,185,129,0.12); color: #0d9862; }
.tl-status.ongoing { background: rgba(59,130,246,0.12); color: #2470d8; }
.tl-status.pending { background: rgba(100,116,139,0.1); color: #7a968a; }

.tl-name { font-size: 15px; font-weight: 700; color: #0f2e1f; margin-bottom: 10px; }
.tl-goal, .tl-tasks, .tl-deliver, .tl-milestones {
  font-size: 11px; color: #5a7a6a; line-height: 1.6; margin-bottom: 4px;
}
.tl-goal b, .tl-tasks b, .tl-deliver b, .tl-milestones b { color: #3d5a4c; margin-right: 4px; }

.tl-progress-wrap { display: flex; align-items: center; gap: 10px; margin-top: 10px; }
.tl-progress-track { flex: 1; height: 5px; background: rgba(15,60,40,0.08); border-radius: 3px; overflow: hidden; }
.tl-progress-fill { height: 100%; border-radius: 3px; transition: width 0.8s ease; }
.tl-progress-fill.completed { background: linear-gradient(90deg, #10b981, #06b6d4); box-shadow: 0 0 8px rgba(16,185,129,0.3); }
.tl-progress-fill.ongoing { background: linear-gradient(90deg, #3b82f6, #8b5cf6); box-shadow: 0 0 8px rgba(59,130,246,0.3); }
.tl-progress-fill.pending { background: #9ab5a8; }
.tl-progress-num { font-size: 11px; color: #7a968a; font-variant-numeric: tabular-nums; width: 36px; text-align: right; }

@media (max-width: 900px) {
  .pp-layout { flex-direction: column; height: auto; }
  .pp-sidebar { width: 100%; }
  .timeline-modern { padding: 12px 8px 12px 24px; }
  .tl-line { left: 38px; }
}
</style>
