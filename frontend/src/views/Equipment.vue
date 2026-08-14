<template>
  <div class="equipment-modern">
    <div class="eq-layout">
      <!-- 左侧设备类别统计 -->
      <div class="eq-sidebar">
        <div class="panel-header">
          <div class="ph-glow" style="background: rgba(139,92,246,0.3);"></div>
          <el-icon :size="16" color="#7a4fd0"><Cpu /></el-icon>
          <span>设备概览</span>
        </div>
        <div class="cat-stats">
          <div class="cat-item" v-for="c in categoryStats" :key="c.key"
            :class="{ active: filter === c.key }" @click="filter = c.key"
            :style="{ '--cat-color': c.color }">
            <div class="cat-glow"></div>
            <div class="cat-icon" :style="{ background: c.color + '18', color: c.color }">
              <el-icon :size="18"><component :is="c.icon" /></el-icon>
            </div>
            <div class="cat-info">
              <div class="cat-name">{{ c.name }}</div>
              <div class="cat-count">{{ c.count }} 台/套</div>
            </div>
          </div>
        </div>
        <div class="eq-total">
          <div class="et-num">{{ list.length }}</div>
          <div class="et-label">设备总数</div>
        </div>
      </div>

      <!-- 右侧设备列表 -->
      <div class="eq-main">
        <div class="eq-toolbar">
          <div class="toolbar-title">
            <span class="t-label">设备清单</span>
            <span class="t-filter" v-if="filter">/ {{ categoryName(filter) }}</span>
          </div>
          <el-select v-model="projectId" placeholder="选择项目" size="small" @change="load" class="dark-select" style="width:180px">
            <el-option v-for="p in projects" :key="p.id" :label="p.name" :value="p.id" />
          </el-select>
        </div>

        <div class="eq-cards">
          <div class="eq-card" v-for="item in filteredList" :key="item.id" :style="{ '--eq-color': catColor(item.category) }">
            <div class="eq-glow"></div>
            <div class="eq-header">
              <div class="eq-cat-tag" :class="item.category">{{ categoryName(item.category) }}</div>
              <div class="eq-status" :class="item.status">
                <span class="st-dot"></span>{{ statusLabel(item.status) }}
              </div>
            </div>
            <div class="eq-name">{{ item.name }}</div>
            <div class="eq-model">{{ item.model_no || '—' }}</div>
            <div class="eq-specs">{{ item.specs }}</div>
            <div class="eq-footer">
              <div class="eq-qty">数量: <b>{{ item.quantity }}</b></div>
              <div class="eq-freq">{{ item.frequency }}</div>
            </div>
            <div class="eq-purpose">{{ item.purpose }}</div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { Cpu, MapLocation, Camera, Monitor, Link, Platform } from '@element-plus/icons-vue'
import { projectApi, equipmentApi } from '../api.js'

const projects = ref([])
const projectId = ref('')
const list = ref([])
const filter = ref('')

const catConfig = {
  satellite: { name: '卫星/航空', icon: MapLocation, color: '#2470d8' },
  uav: { name: '无人机', icon: Camera, color: '#7a4fd0' },
  sensor: { name: '地面传感', icon: Monitor, color: '#0e9f6e' },
  communication: { name: '通信', icon: Link, color: '#d97706' },
  compute: { name: '计算', icon: Platform, color: '#0b8fa8' },
}
function catColor(c) { return catConfig[c]?.color || '#5a7a6a' }
function categoryName(c) { return catConfig[c]?.name || c }
function statusLabel(s) { return { planned: '计划中', running: '运行中', maintenance: '维护中', retired: '已退役' }[s] || s }

const filteredList = computed(() => filter.value ? list.value.filter(i => i.category === filter.value) : list.value)

const categoryStats = computed(() => {
  return Object.entries(catConfig).map(([key, cfg]) => ({
    key, ...cfg,
    count: list.value.filter(i => i.category === key).reduce((s, i) => s + (i.quantity || 1), 0)
  }))
})

async function load() { if (!projectId.value) return; list.value = await equipmentApi.list(projectId.value) }

onMounted(async () => {
  projects.value = await projectApi.list()
  if (projects.value.length) { projectId.value = projects.value[0].id; await load() }
})
</script>

<style scoped>
.equipment-modern { height: 100%; }
.eq-layout { display: flex; gap: 16px; height: calc(100vh - 104px); }

/* 左侧 */
.eq-sidebar {
  width: 240px; flex-shrink: 0;
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

.cat-stats { padding: 8px; flex: 1; overflow-y: auto; }
.cat-item {
  position: relative;
  display: flex; align-items: center; gap: 10px;
  padding: 10px 12px; border-radius: 12px;
  cursor: pointer; transition: all 0.2s;
  margin-bottom: 4px;
  border: 1px solid transparent;
  overflow: hidden;
}
.cat-item:hover { background: rgba(255,255,255,0.6); }
.cat-item.active { background: rgba(255,255,255,0.85); border-color: var(--cat-color); }
.cat-glow {
  position: absolute; right: -10px; top: -10px;
  width: 40px; height: 40px; border-radius: 50%;
  background: var(--cat-color);
  filter: blur(20px); opacity: 0;
  transition: opacity 0.3s;
}
.cat-item:hover .cat-glow, .cat-item.active .cat-glow { opacity: 0.12; }
.cat-icon {
  width: 36px; height: 36px; border-radius: 10px;
  display: flex; align-items: center; justify-content: center;
  flex-shrink: 0;
}
.cat-name { font-size: 12px; font-weight: 600; color: #1e3a2f; }
.cat-count { font-size: 10px; color: #9ab5a8; margin-top: 1px; }

.eq-total {
  padding: 14px 16px;
  border-top: 1px solid rgba(15,60,40,0.06);
  text-align: center;
}
.et-num { font-size: 28px; font-weight: 800; color: #0f2e1f; line-height: 1; }
.et-label { font-size: 11px; color: #9ab5a8; margin-top: 4px; }

/* 右侧 */
.eq-main { flex: 1; display: flex; flex-direction: column; min-width: 0; }
.eq-toolbar {
  display: flex; align-items: center; justify-content: space-between;
  padding: 12px 18px;
  background: rgba(255,255,255,0.6);
  border: 1px solid rgba(255,255,255,0.85);
  border-radius: 14px;
  backdrop-filter: blur(12px);
  margin-bottom: 12px;
  box-shadow: 0 4px 20px rgba(46,125,82,0.07);
}
.toolbar-title { display: flex; align-items: center; gap: 8px; }
.t-label { font-size: 14px; font-weight: 600; color: #1e3a2f; }
.t-filter { font-size: 12px; color: #7a968a; }

.eq-cards {
  flex: 1; overflow-y: auto;
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(280px, 1fr));
  gap: 12px;
  align-content: start;
}
.eq-card {
  position: relative;
  background: rgba(255,255,255,0.6);
  border: 1px solid rgba(255,255,255,0.85);
  border-radius: 14px;
  padding: 16px;
  transition: all 0.3s ease;
  overflow: hidden;
  box-shadow: 0 4px 20px rgba(46,125,82,0.06);
}
.eq-card:hover {
  border-color: rgba(46,158,99,0.3);
  transform: translateY(-2px);
  box-shadow: 0 8px 24px rgba(46,125,82,0.12), 0 0 20px var(--eq-color);
}
.eq-glow {
  position: absolute; top: -20px; right: -20px;
  width: 60px; height: 60px; border-radius: 50%;
  background: var(--eq-color);
  filter: blur(30px); opacity: 0.08;
}
.eq-header { display: flex; align-items: center; justify-content: space-between; margin-bottom: 10px; }
.eq-cat-tag { font-size: 10px; padding: 2px 8px; border-radius: 4px; font-weight: 600; }
.eq-cat-tag.satellite { background: rgba(59,130,246,0.12); color: #2470d8; }
.eq-cat-tag.uav { background: rgba(139,92,246,0.12); color: #7a4fd0; }
.eq-cat-tag.sensor { background: rgba(16,185,129,0.12); color: #0d9862; }
.eq-cat-tag.communication { background: rgba(245,158,11,0.12); color: #c77f0a; }
.eq-cat-tag.compute { background: rgba(6,182,212,0.12); color: #0b8fa8; }
.eq-status { display: flex; align-items: center; gap: 5px; font-size: 10px; color: #7a968a; }
.eq-status .st-dot { width: 5px; height: 5px; border-radius: 50%; }
.eq-status.running .st-dot { background: #10b981; box-shadow: 0 0 6px #10b981; }
.eq-status.planned .st-dot { background: #7a968a; }
.eq-status.maintenance .st-dot { background: #f59e0b; box-shadow: 0 0 6px #f59e0b; }
.eq-status.retired .st-dot { background: #ef4444; }

.eq-name { font-size: 14px; font-weight: 600; color: #1e3a2f; margin-bottom: 2px; }
.eq-model { font-size: 11px; color: #7a968a; margin-bottom: 8px; }
.eq-specs { font-size: 11px; color: #5a7a6a; line-height: 1.5; margin-bottom: 10px; display: -webkit-box; -webkit-line-clamp: 2; -webkit-box-orient: vertical; overflow: hidden; }
.eq-footer { display: flex; justify-content: space-between; font-size: 10px; color: #9ab5a8; margin-bottom: 6px; }
.eq-footer b { color: #3d5a4c; }
.eq-purpose { font-size: 10px; color: #9ab5a8; line-height: 1.4; display: -webkit-box; -webkit-line-clamp: 2; -webkit-box-orient: vertical; overflow: hidden; }

@media (max-width: 900px) {
  .eq-layout { flex-direction: column; height: auto; }
  .eq-sidebar { width: 100%; }
  .eq-cards { grid-template-columns: 1fr; }
}
</style>
