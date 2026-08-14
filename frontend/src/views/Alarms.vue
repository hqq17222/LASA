<template>
  <div class="alarms-modern">
    <div class="alarm-layout">
      <!-- 左侧新建预警 -->
      <div class="alarm-form-panel">
        <div class="panel-header">
          <div class="ph-glow" style="background: rgba(239,68,68,0.3);"></div>
          <el-icon :size="16" color="#dc3535"><WarningFilled /></el-icon>
          <span>新建预警</span>
        </div>
        <div class="af-body">
          <div class="form-group">
            <label class="form-label">项目</label>
            <el-select v-model="form.project_id" class="dark-select">
              <el-option v-for="p in projects" :key="p.id" :label="p.name" :value="p.id" />
            </el-select>
          </div>
          <div class="form-group">
            <label class="form-label">预警标题</label>
            <el-input v-model="form.title" placeholder="输入预警标题" />
          </div>
          <div class="form-group">
            <label class="form-label">预警级别</label>
            <div class="level-selector">
              <div class="level-btn" :class="{ active: form.level === 'yellow' }" @click="form.level = 'yellow'">
                <div class="lv-dot" style="background: #eab308; box-shadow: 0 0 8px #eab308;"></div>
                <span>黄色</span>
              </div>
              <div class="level-btn" :class="{ active: form.level === 'orange' }" @click="form.level = 'orange'">
                <div class="lv-dot" style="background: #f97316; box-shadow: 0 0 8px #f97316;"></div>
                <span>橙色</span>
              </div>
              <div class="level-btn" :class="{ active: form.level === 'red' }" @click="form.level = 'red'">
                <div class="lv-dot" style="background: #ef4444; box-shadow: 0 0 8px #ef4444;"></div>
                <span>红色</span>
              </div>
            </div>
          </div>
          <div class="form-group">
            <label class="form-label">预警类型</label>
            <el-input v-model="form.alarm_type" placeholder="如: deviation" />
          </div>
          <div class="form-group">
            <label class="form-label">关联指标</label>
            <el-input v-model="form.indicator_name" placeholder="如: ndvi" />
          </div>
          <div class="form-group">
            <label class="form-label">说明</label>
            <el-input v-model="form.message" type="textarea" rows="3" placeholder="预警详情说明..." />
          </div>
          <el-button type="primary" size="default" class="create-btn" :icon="WarningFilled" @click="createAlarm">创建预警</el-button>
        </div>
      </div>

      <!-- 右侧预警列表 -->
      <div class="alarm-list-panel">
        <div class="al-header">
          <div class="alh-title">
            <div class="alh-glow" style="background: rgba(245,158,11,0.3);"></div>
            <el-icon :size="16" color="#c77f0a"><Bell /></el-icon>
            <span>预警列表</span>
            <el-tag v-if="openCount > 0" type="danger" size="small" class="alh-count">{{ openCount }} 未处理</el-tag>
          </div>
          <div class="alh-filter">
            <button class="alf-btn" :class="{ active: statusFilter === '' }" @click="statusFilter = ''">全部</button>
            <button class="alf-btn" :class="{ active: statusFilter === 'open' }" @click="statusFilter = 'open'">未处理</button>
            <button class="alf-btn" :class="{ active: statusFilter === 'closed' }" @click="statusFilter = 'closed'">已处理</button>
          </div>
        </div>

        <div class="alarm-cards">
          <div class="alarm-card" v-for="a in filteredAlarms" :key="a.id" :class="a.level">
            <div class="ac-glow" :class="a.level"></div>
            <div class="ac-header">
              <div class="ac-level" :class="a.level">
                <div class="ac-level-dot"></div>
                <span>{{ a.level }}</span>
              </div>
              <div class="ac-time">{{ formatDate(a.created_at) }}</div>
            </div>
            <div class="ac-title">{{ a.title }}</div>
            <div class="ac-meta">
              <span class="ac-type">{{ a.alarm_type }}</span>
              <span class="ac-indicator" v-if="a.indicator_name">{{ a.indicator_name }}</span>
            </div>
            <div class="ac-message" v-if="a.message">{{ a.message }}</div>
            <div class="ac-actions">
              <el-button v-if="a.status === 'open'" type="primary" size="small" text :icon="Check" @click="handle(a)">处理</el-button>
              <el-tag v-else type="success" size="small">已处理</el-tag>
              <el-button type="danger" size="small" text :icon="Delete" @click="remove(a)">删除</el-button>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { ElMessage } from 'element-plus'
import { WarningFilled, Bell, Check, Delete } from '@element-plus/icons-vue'
import { projectApi, alarmApi } from '../api.js'

const projects = ref([])
const alarms = ref([])
const form = ref({ project_id: '', level: 'yellow', alarm_type: 'deviation', title: '', message: '', indicator_name: '' })
const statusFilter = ref('')

const openCount = computed(() => alarms.value.filter(a => a.status === 'open').length)
const filteredAlarms = computed(() => {
  let arr = statusFilter.value ? alarms.value.filter(a => a.status === statusFilter.value) : alarms.value
  return arr.sort((a, b) => new Date(b.created_at) - new Date(a.created_at))
})

function formatDate(t) {
  if (!t) return '-'
  return new Date(t).toLocaleString('zh-CN', { month: 'short', day: 'numeric', hour: '2-digit', minute: '2-digit' })
}

onMounted(async () => {
  projects.value = await projectApi.list()
  if (projects.value.length) form.value.project_id = projects.value[0].id
  loadAlarms()
})

async function loadAlarms() { alarms.value = await alarmApi.list() }
async function createAlarm() { await alarmApi.create(form.value); ElMessage.success('预警已创建'); await loadAlarms() }
async function handle(row) { await alarmApi.handle(row.id); await loadAlarms() }
async function remove(row) { await alarmApi.remove(row.id); await loadAlarms() }
</script>

<style scoped>
.alarms-modern { height: 100%; }
.alarm-layout { display: flex; gap: 16px; height: calc(100vh - 104px); }

/* 左侧表单 */
.alarm-form-panel {
  width: 300px; flex-shrink: 0;
  background: rgba(255,255,255,0.72);
  border: 1px solid rgba(255,255,255,0.85);
  border-radius: 16px;
  backdrop-filter: blur(12px);
  box-shadow: 0 4px 20px rgba(46,125,82,0.07);
  display: flex; flex-direction: column;
  overflow: hidden;
}
.panel-header {
  display: flex; align-items: center; gap: 8px;
  padding: 14px 16px;
  border-bottom: 1px solid rgba(15,60,40,0.06);
  font-weight: 600; color: #1e3a2f; font-size: 13px;
  position: relative;
}
.ph-glow { position: absolute; left: 8px; top: 10px; width: 24px; height: 24px; border-radius: 50%; filter: blur(8px); opacity: 0.6; }

.af-body { padding: 14px 16px; overflow-y: auto; }
.form-group { margin-bottom: 14px; }
.form-label { display: block; font-size: 11px; color: #7a968a; margin-bottom: 5px; font-weight: 500; }

.level-selector { display: flex; gap: 6px; }
.level-btn {
  flex: 1; display: flex; flex-direction: column; align-items: center; gap: 5px;
  padding: 10px 6px; border-radius: 10px;
  background: rgba(255,255,255,0.55);
  border: 1px solid rgba(15,60,40,0.08);
  cursor: pointer; transition: all 0.2s;
}
.level-btn:hover { background: rgba(255,255,255,0.8); }
.level-btn.active { border-color: rgba(14,159,110,0.35); background: rgba(16,185,129,0.08); }
.level-btn span { font-size: 10px; color: #5a7a6a; }
.lv-dot { width: 12px; height: 12px; border-radius: 50%; }
.create-btn { width: 100%; margin-top: 4px; }

/* 右侧列表 */
.alarm-list-panel {
  flex: 1; display: flex; flex-direction: column;
  min-width: 0;
}
.al-header {
  display: flex; align-items: center; justify-content: space-between;
  padding: 12px 18px;
  background: rgba(255,255,255,0.72);
  border: 1px solid rgba(255,255,255,0.85);
  border-radius: 14px;
  backdrop-filter: blur(12px);
  box-shadow: 0 4px 20px rgba(46,125,82,0.07);
  margin-bottom: 12px;
}
.alh-title { display: flex; align-items: center; gap: 8px; font-weight: 600; color: #1e3a2f; font-size: 13px; position: relative; }
.alh-glow { position: absolute; left: -6px; top: -4px; width: 24px; height: 24px; border-radius: 50%; filter: blur(8px); opacity: 0.6; }
.alh-count { margin-left: 6px; }

.alh-filter { display: flex; gap: 6px; }
.alf-btn {
  padding: 4px 12px; border-radius: 8px;
  background: rgba(255,255,255,0.55);
  border: 1px solid rgba(15,60,40,0.08);
  color: #7a968a; font-size: 11px; cursor: pointer;
  transition: all 0.2s;
}
.alf-btn:hover { background: rgba(255,255,255,0.8); }
.alf-btn.active { background: rgba(245,158,11,0.12); border-color: rgba(245,158,11,0.3); color: #c77f0a; }

.alarm-cards {
  flex: 1; overflow-y: auto;
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(300px, 1fr));
  gap: 12px;
  align-content: start;
}
.alarm-card {
  position: relative;
  background: rgba(255,255,255,0.72);
  border: 1px solid rgba(255,255,255,0.85);
  border-radius: 14px;
  padding: 16px;
  transition: all 0.3s ease;
  overflow: hidden;
  box-shadow: 0 4px 20px rgba(46,125,82,0.07);
}
.alarm-card:hover { border-color: rgba(255,255,255,1); transform: translateY(-2px); box-shadow: 0 8px 28px rgba(46,125,82,0.12); }
.ac-glow {
  position: absolute; top: -20px; right: -20px;
  width: 60px; height: 60px; border-radius: 50%;
  filter: blur(30px); opacity: 0.12;
}
.ac-glow.yellow { background: #eab308; }
.ac-glow.orange { background: #f97316; }
.ac-glow.red { background: #ef4444; }

.ac-header { display: flex; align-items: center; justify-content: space-between; margin-bottom: 10px; }
.ac-level { display: flex; align-items: center; gap: 5px; font-size: 10px; padding: 2px 8px; border-radius: 4px; font-weight: 600; }
.ac-level.yellow { background: rgba(234,179,8,0.14); color: #a16207; }
.ac-level.orange { background: rgba(249,115,22,0.14); color: #dd6a1a; }
.ac-level.red { background: rgba(239,68,68,0.12); color: #dc3535; }
.ac-level-dot { width: 5px; height: 5px; border-radius: 50%; background: currentColor; }
.ac-time { font-size: 10px; color: #9ab5a8; }

.ac-title { font-size: 14px; font-weight: 600; color: #1e3a2f; margin-bottom: 6px; }
.ac-meta { display: flex; gap: 8px; margin-bottom: 6px; }
.ac-type, .ac-indicator { font-size: 10px; padding: 1px 7px; border-radius: 4px; background: rgba(15,60,40,0.05); color: #7a968a; }
.ac-message { font-size: 11px; color: #5a7a6a; line-height: 1.5; margin-bottom: 10px; }
.ac-actions { display: flex; justify-content: space-between; align-items: center; }

@media (max-width: 900px) {
  .alarm-layout { flex-direction: column; height: auto; }
  .alarm-form-panel { width: 100%; }
  .alarm-cards { grid-template-columns: 1fr; }
}
</style>
