<template>
  <div class="reports-modern">
    <div class="rep-layout">
      <!-- 左侧生成报告 -->
      <div class="rep-form-panel">
        <div class="panel-header">
          <div class="ph-glow" style="background: rgba(122,79,208,0.3);"></div>
          <el-icon :size="16" color="#7a4fd0"><Reading /></el-icon>
          <span>生成报告</span>
        </div>
        <div class="rf-body">
          <div class="form-group">
            <label class="form-label">选择项目</label>
            <el-select v-model="form.project_id" class="dark-select">
              <el-option v-for="p in projects" :key="p.id" :label="p.name" :value="p.id" />
            </el-select>
          </div>
          <div class="form-group">
            <label class="form-label">报告标题</label>
            <el-input v-model="form.title" placeholder="输入报告标题" />
          </div>
          <div class="form-group">
            <label class="form-label">报告类型</label>
            <div class="type-cards">
              <div class="type-card" :class="{ active: form.report_type === 'annual' }" @click="form.report_type = 'annual'">
                <div class="tc-icon" style="background: linear-gradient(135deg, #10b981, #059669);"><el-icon :size="16" color="#fff"><Calendar /></el-icon></div>
                <div class="tc-name">年度报告</div>
              </div>
              <div class="type-card" :class="{ active: form.report_type === 'alarm' }" @click="form.report_type = 'alarm'">
                <div class="tc-icon" style="background: linear-gradient(135deg, #ef4444, #dc2626);"><el-icon :size="16" color="#fff"><WarningFilled /></el-icon></div>
                <div class="tc-name">预警报告</div>
              </div>
              <div class="type-card" :class="{ active: form.report_type === 'compare' }" @click="form.report_type = 'compare'">
                <div class="tc-icon" style="background: linear-gradient(135deg, #3b82f6, #1d4ed8);"><el-icon :size="16" color="#fff"><DataAnalysis /></el-icon></div>
                <div class="tc-name">对比报告</div>
              </div>
            </div>
          </div>
          <div class="form-group">
            <label class="form-label">统计周期</label>
            <el-input v-model="form.period" placeholder="如 2026" />
          </div>
          <el-button type="primary" size="default" class="gen-btn" :loading="loading" :icon="Reading" @click="createReport">生成报告</el-button>
        </div>
      </div>

      <!-- 右侧报告列表 -->
      <div class="rep-list-panel">
        <div class="rl-header">
          <div class="rlh-title">
            <div class="rlh-glow" style="background: rgba(16,185,129,0.3);"></div>
            <el-icon :size="16" color="#0d9862"><Document /></el-icon>
            <span>报告列表</span>
            <el-tag type="info" size="small">{{ reports.length }} 份</el-tag>
          </div>
        </div>

        <div class="rep-cards">
          <div class="rep-card" v-for="r in reports" :key="r.id" :class="r.report_type">
            <div class="rc-glow" :class="r.report_type"></div>
            <div class="rc-icon" :class="r.report_type">
              <el-icon :size="22" color="#fff"><component :is="typeIcon(r.report_type)" /></el-icon>
            </div>
            <div class="rc-body">
              <div class="rc-title">{{ r.title }}</div>
              <div class="rc-meta">
                <span class="rc-type">{{ typeLabel(r.report_type) }}</span>
                <span class="rc-period">{{ r.period }}</span>
              </div>
              <div class="rc-time">{{ formatDate(r.created_at) }}</div>
            </div>
            <div class="rc-actions">
              <el-button type="primary" size="small" text :icon="View" @click="openReport(r)">查看</el-button>
              <el-button type="danger" size="small" text :icon="Delete" @click="remove(r)">删除</el-button>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- 报告预览 -->
    <el-dialog v-model="dialogVisible" title="报告预览" width="85%" top="4vh" class="report-dialog">
      <iframe v-if="currentUrl" :src="currentUrl" class="report-frame" />
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { ElMessage } from 'element-plus'
import { Reading, Calendar, WarningFilled, DataAnalysis, Document, View, Delete } from '@element-plus/icons-vue'
import { projectApi, reportApi } from '../api.js'

const projects = ref([])
const reports = ref([])
const form = ref({ project_id: '', title: '', report_type: 'annual', period: '2026' })
const loading = ref(false)
const dialogVisible = ref(false)
const currentUrl = ref('')

function typeLabel(t) { return { annual: '年度报告', alarm: '预警报告', compare: '对比报告' }[t] || t }
function typeIcon(t) { return { annual: Calendar, alarm: WarningFilled, compare: DataAnalysis }[t] || Document }
function formatDate(t) {
  if (!t) return '-'
  return new Date(t).toLocaleString('zh-CN', { month: 'short', day: 'numeric', hour: '2-digit', minute: '2-digit' })
}

onMounted(async () => {
  projects.value = await projectApi.list()
  if (projects.value.length) form.value.project_id = projects.value[0].id
  loadReports()
})

async function loadReports() { reports.value = await reportApi.list(form.value.project_id || 0) }

async function createReport() {
  loading.value = true
  try { await reportApi.create(form.value); ElMessage.success('报告生成成功'); await loadReports() }
  catch (e) { ElMessage.error(e) }
  finally { loading.value = false }
}

function openReport(row) { currentUrl.value = reportApi.html(row.id); dialogVisible.value = true }
async function remove(row) { await reportApi.remove(row.id); await loadReports() }
</script>

<style scoped>
.reports-modern { height: 100%; }
.rep-layout { display: flex; gap: 16px; height: calc(100vh - 104px); }

/* 左侧 */
.rep-form-panel {
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

.rf-body { padding: 14px 16px; overflow-y: auto; }
.form-group { margin-bottom: 14px; }
.form-label { display: block; font-size: 11px; color: #7a968a; margin-bottom: 5px; font-weight: 500; }

.type-cards { display: flex; flex-direction: column; gap: 6px; }
.type-card {
  display: flex; align-items: center; gap: 10px;
  padding: 10px 12px; border-radius: 10px;
  background: rgba(255,255,255,0.55);
  border: 1px solid rgba(15,60,40,0.06);
  cursor: pointer; transition: all 0.2s;
}
.type-card:hover { background: rgba(255,255,255,0.85); }
.type-card.active { border-color: rgba(122,79,208,0.3); background: rgba(122,79,208,0.08); }
.tc-icon { width: 32px; height: 32px; border-radius: 8px; display: flex; align-items: center; justify-content: center; flex-shrink: 0; box-shadow: 0 4px 12px rgba(46,125,82,0.18); }
.tc-name { font-size: 12px; font-weight: 500; color: #1e3a2f; }
.gen-btn { width: 100%; margin-top: 4px; }

/* 右侧 */
.rep-list-panel { flex: 1; display: flex; flex-direction: column; min-width: 0; }
.rl-header {
  display: flex; align-items: center;
  padding: 12px 18px;
  background: rgba(255,255,255,0.72);
  border: 1px solid rgba(255,255,255,0.85);
  border-radius: 14px;
  backdrop-filter: blur(12px);
  box-shadow: 0 4px 20px rgba(46,125,82,0.07);
  margin-bottom: 12px;
}
.rlh-title { display: flex; align-items: center; gap: 8px; font-weight: 600; color: #1e3a2f; font-size: 13px; position: relative; }
.rlh-glow { position: absolute; left: -6px; top: -4px; width: 24px; height: 24px; border-radius: 50%; filter: blur(8px); opacity: 0.6; }

.rep-cards {
  flex: 1; overflow-y: auto;
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(260px, 1fr));
  gap: 12px;
  align-content: start;
}
.rep-card {
  position: relative;
  display: flex; flex-direction: column;
  background: rgba(255,255,255,0.72);
  border: 1px solid rgba(255,255,255,0.85);
  border-radius: 14px;
  padding: 16px;
  transition: all 0.3s ease;
  overflow: hidden;
  box-shadow: 0 4px 20px rgba(46,125,82,0.07);
}
.rep-card:hover { border-color: rgba(255,255,255,1); transform: translateY(-2px); box-shadow: 0 8px 28px rgba(46,125,82,0.12); }
.rc-glow { position: absolute; top: -20px; right: -20px; width: 60px; height: 60px; border-radius: 50%; filter: blur(30px); opacity: 0.12; }
.rc-glow.annual { background: #10b981; }
.rc-glow.alarm { background: #ef4444; }
.rc-glow.compare { background: #3b82f6; }

.rc-icon { width: 40px; height: 40px; border-radius: 10px; display: flex; align-items: center; justify-content: center; margin-bottom: 10px; box-shadow: 0 4px 12px rgba(46,125,82,0.18); }
.rc-icon.annual { background: linear-gradient(135deg, #10b981, #059669); }
.rc-icon.alarm { background: linear-gradient(135deg, #ef4444, #dc2626); }
.rc-icon.compare { background: linear-gradient(135deg, #3b82f6, #1d4ed8); }

.rc-body { flex: 1; }
.rc-title { font-size: 14px; font-weight: 600; color: #1e3a2f; margin-bottom: 6px; line-height: 1.3; }
.rc-meta { display: flex; gap: 8px; margin-bottom: 6px; }
.rc-type, .rc-period { font-size: 10px; padding: 1px 7px; border-radius: 4px; background: rgba(15,60,40,0.05); color: #7a968a; }
.rc-time { font-size: 10px; color: #9ab5a8; }
.rc-actions { display: flex; justify-content: space-between; margin-top: 10px; }

.report-frame { width: 100%; height: 72vh; border: none; border-radius: 10px; background: #fff; }

@media (max-width: 900px) {
  .rep-layout { flex-direction: column; height: auto; }
  .rep-form-panel { width: 100%; }
  .rep-cards { grid-template-columns: 1fr; }
}
</style>
