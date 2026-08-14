<template>
  <div class="indicators-modern">
    <div class="ind-layout">
      <!-- 左侧计算面板 -->
      <div class="calc-panel">
        <div class="panel-header">
          <div class="ph-glow" style="background: rgba(16,185,129,0.3);"></div>
          <el-icon :size="16" color="#0d9862"><DataAnalysis /></el-icon>
          <span>指标计算</span>
        </div>
        <div class="calc-form">
          <div class="form-group">
            <label class="form-label">选择项目</label>
            <el-select v-model="form.project_id" placeholder="选择项目" class="dark-select">
              <el-option v-for="p in projects" :key="p.id" :label="p.name" :value="p.id" />
            </el-select>
          </div>
          <div class="form-group">
            <label class="form-label">选择指标</label>
            <el-select v-model="form.indicator_name" placeholder="选择指标" filterable class="dark-select">
              <el-option-group v-for="group in metaGroups" :key="group.label" :label="group.label">
                <el-option v-for="i in group.items" :key="i.name" :label="`${i.display_name} (${i.symbol})`" :value="i.name" />
              </el-option-group>
            </el-select>
          </div>
          <div class="form-group">
            <label class="form-label">计算周期</label>
            <el-input v-model="form.period" placeholder="如 2026" />
          </div>
          <div class="form-group">
            <label class="form-label">参数 (JSON)</label>
            <el-input v-model="paramsText" type="textarea" rows="5" class="code-input" />
          </div>
          <el-button type="primary" size="default" @click="compute" :loading="loading" class="calc-btn" :icon="DataAnalysis">
            开始计算
          </el-button>
        </div>

        <!-- 指标元信息卡 -->
        <div v-if="currentMeta" class="meta-card">
          <div class="meta-header">
            <div class="meta-symbol">{{ currentMeta.symbol }}</div>
            <div class="meta-name">{{ currentMeta.display_name }}</div>
          </div>
          <div class="meta-dims">
            <span class="dim-tag" :class="currentMeta.dimension">{{ dimensionName(currentMeta.dimension) }}</span>
            <span class="meta-unit">{{ currentMeta.unit }}</span>
          </div>
          <div class="meta-detail">
            <div class="md-row"><span class="md-label">公式</span><span class="md-val">{{ currentMeta.formula || '-' }}</span></div>
            <div class="md-row"><span class="md-label">数据源</span><span class="md-val">{{ currentMeta.data_source || '-' }}</span></div>
            <div class="md-row"><span class="md-label">目标阈值</span><span class="md-val" style="color:#c77f0a">{{ currentMeta.target_threshold || '-' }}</span></div>
          </div>
        </div>
      </div>

      <!-- 右侧结果面板 -->
      <div class="result-panel">
        <div class="result-header">
          <div class="rh-title">
            <div class="rh-glow" style="background: rgba(59,130,246,0.3);"></div>
            <el-icon :size="16" color="#2470d8"><Histogram /></el-icon>
            <span>指标结果</span>
          </div>
          <div class="dim-filters">
            <button v-for="d in dimFilters" :key="d.key" class="dim-btn" :class="{ active: dimensionFilter === d.key }" @click="dimensionFilter = d.key">
              {{ d.label }}
            </button>
          </div>
        </div>

        <!-- 结果卡片网格 -->
        <div class="result-grid">
          <div class="result-card" v-for="r in filteredResults" :key="r.id" :style="{ '--r-color': dimColor(r.dimension) }">
            <div class="rc-glow"></div>
            <div class="rc-header">
              <div class="rc-symbol">{{ r.symbol }}</div>
              <div class="rc-dim" :class="r.dimension">{{ dimensionName(r.dimension) }}</div>
            </div>
            <div class="rc-value">
              <span class="rc-num">{{ r.value != null ? r.value.toFixed(2) : '-' }}</span>
              <span class="rc-unit">{{ r.unit }}</span>
            </div>
            <div class="rc-bar-track">
              <div class="rc-bar" :style="{ width: Math.min((r.value || 0) / 100 * 100, 100) + '%', background: dimColor(r.dimension) }"></div>
            </div>
            <div class="rc-meta">
              <span class="rc-period">{{ r.period }}</span>
              <span class="rc-threshold">目标: {{ r.target_threshold || '-' }}</span>
            </div>
            <div class="rc-footer">
              <span class="rc-time">{{ formatDate(r.computed_at) }}</span>
              <el-button type="danger" size="small" text :icon="Delete" @click="removeResult(r)">删除</el-button>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, computed, watch } from 'vue'
import { ElMessage } from 'element-plus'
import { DataAnalysis, Histogram, Delete } from '@element-plus/icons-vue'
import { projectApi, indicatorApi } from '../api.js'

const projects = ref([])
const metaList = ref([])
const form = ref({ project_id: '', indicator_name: 'ndvi', period: '2026', params: {} })
const paramsText = ref('{}')
const loading = ref(false)
const results = ref([])
const dimensionFilter = ref('')

const dimFilters = [
  { key: '', label: '全部' },
  { key: 'structure', label: '结构' },
  { key: 'function', label: '功能' },
  { key: 'pressure', label: '压力' },
  { key: 'response', label: '工程响应' },
  { key: 'stability', label: '稳定性' },
]

const dimColors = {
  structure: '#2470d8', function: '#0e9f6e', pressure: '#d97706',
  response: '#7a4fd0', stability: '#dc3535'
}
function dimColor(d) { return dimColors[d] || '#5a7a6a' }

const currentMeta = computed(() => metaList.value.find(i => i.name === form.value.indicator_name))
const metaGroups = computed(() => {
  const groups = { structure: '结构指标', function: '功能指标', pressure: '压力指标', response: '工程响应指标', stability: '稳定性指标' }
  return Object.entries(groups).map(([k, label]) => ({ label, items: metaList.value.filter(i => i.dimension === k) }))
})
const filteredResults = computed(() => dimensionFilter.value ? results.value.filter(i => i.dimension === dimensionFilter.value) : results.value)

function dimensionName(d) {
  const map = { structure: '结构', function: '功能', pressure: '压力', response: '工程响应', stability: '稳定性' }
  return map[d] || d
}
function formatDate(t) {
  if (!t) return '-'
  return new Date(t).toLocaleString('zh-CN', { month: 'short', day: 'numeric', hour: '2-digit', minute: '2-digit' })
}

onMounted(async () => {
  projects.value = await projectApi.list()
  metaList.value = await indicatorApi.meta()
  if (projects.value.length) form.value.project_id = projects.value[0].id
  loadResults()
})

watch(() => form.value.indicator_name, (name) => {
  const meta = metaList.value.find(i => i.name === name)
  if (meta && meta.name === 'sc') paramsText.value = JSON.stringify({ R: 500, K: 0.3, LS: 5, C: 0.5, P: 1.0, area_ha: 1000 }, null, 2)
  else if (meta && meta.name === 'wh') paramsText.value = JSON.stringify({ precip: 500, runoff: 50, et: 400 }, null, 2)
  else paramsText.value = '{}'
})

async function loadResults() { results.value = await indicatorApi.list(form.value.project_id || 0) }

async function compute() {
  try { form.value.params = JSON.parse(paramsText.value || '{}') }
  catch (e) { ElMessage.error('参数 JSON 格式错误'); return }
  loading.value = true
  try { await indicatorApi.compute(form.value); ElMessage.success('计算完成'); await loadResults() }
  catch (e) { ElMessage.error(e) }
  finally { loading.value = false }
}

async function removeResult(row) { await indicatorApi.remove(row.id); await loadResults() }
</script>

<style scoped>
.indicators-modern { height: 100%; }
.ind-layout { display: flex; gap: 16px; height: calc(100vh - 104px); }

/* 左侧计算面板 */
.calc-panel {
  width: 300px; flex-shrink: 0;
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

.calc-form { padding: 14px 16px; overflow-y: auto; }
.form-group { margin-bottom: 14px; }
.form-label { display: block; font-size: 11px; color: #7a968a; margin-bottom: 5px; font-weight: 500; }
.code-input :deep(textarea) { font-family: 'Fira Code', 'Consolas', monospace; font-size: 12px; }
.calc-btn { width: 100%; margin-top: 4px; }

/* 指标元信息卡 */
.meta-card {
  margin: 0 16px 16px;
  padding: 14px;
  background: rgba(255,255,255,0.55);
  border: 1px solid rgba(255,255,255,0.85);
  border-radius: 12px;
}
.meta-header { display: flex; align-items: center; gap: 10px; margin-bottom: 8px; }
.meta-symbol {
  width: 36px; height: 36px; border-radius: 10px;
  background: linear-gradient(135deg, rgba(16,185,129,0.2), rgba(6,182,212,0.15));
  display: flex; align-items: center; justify-content: center;
  font-size: 14px; font-weight: 700; color: #0d9862;
}
.meta-name { font-size: 13px; font-weight: 600; color: #1e3a2f; }
.meta-dims { display: flex; gap: 8px; margin-bottom: 10px; }
.dim-tag {
  font-size: 10px; padding: 2px 8px; border-radius: 4px; font-weight: 600;
}
.dim-tag.structure { background: rgba(59,130,246,0.15); color: #2470d8; }
.dim-tag.function { background: rgba(16,185,129,0.15); color: #0d9862; }
.dim-tag.pressure { background: rgba(245,158,11,0.15); color: #c77f0a; }
.dim-tag.response { background: rgba(139,92,246,0.15); color: #7a4fd0; }
.dim-tag.stability { background: rgba(239,68,68,0.15); color: #dc3535; }
.meta-unit { font-size: 10px; color: #9ab5a8; }
.meta-detail { display: flex; flex-direction: column; gap: 6px; }
.md-row { display: flex; justify-content: space-between; font-size: 11px; }
.md-label { color: #9ab5a8; }
.md-val { color: #5a7a6a; max-width: 140px; text-align: right; }

/* 右侧结果面板 */
.result-panel {
  flex: 1; display: flex; flex-direction: column;
  min-width: 0;
}
.result-header {
  display: flex; align-items: center; justify-content: space-between;
  padding: 12px 18px;
  background: rgba(255,255,255,0.6);
  border: 1px solid rgba(255,255,255,0.85);
  border-radius: 14px;
  backdrop-filter: blur(12px);
  margin-bottom: 12px;
  box-shadow: 0 4px 20px rgba(46,125,82,0.07);
}
.rh-title { display: flex; align-items: center; gap: 8px; font-weight: 600; color: #1e3a2f; font-size: 13px; position: relative; }
.rh-glow { position: absolute; left: -6px; top: -4px; width: 24px; height: 24px; border-radius: 50%; filter: blur(8px); opacity: 0.6; }

.dim-filters { display: flex; gap: 6px; flex-wrap: wrap; }
.dim-btn {
  padding: 4px 12px; border-radius: 8px;
  background: rgba(255,255,255,0.55);
  border: 1px solid rgba(255,255,255,0.85);
  color: #7a968a; font-size: 11px; cursor: pointer;
  transition: all 0.2s;
}
.dim-btn:hover { background: rgba(255,255,255,0.85); color: #5a7a6a; }
.dim-btn.active { background: rgba(59,130,246,0.12); border-color: rgba(59,130,246,0.3); color: #2470d8; }

/* 结果卡片网格 */
.result-grid {
  flex: 1; overflow-y: auto;
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(220px, 1fr));
  gap: 12px;
  align-content: start;
}
.result-card {
  position: relative;
  background: rgba(255,255,255,0.6);
  border: 1px solid rgba(255,255,255,0.85);
  border-radius: 14px;
  padding: 16px;
  transition: all 0.3s ease;
  overflow: hidden;
  box-shadow: 0 4px 20px rgba(46,125,82,0.06);
}
.result-card:hover {
  border-color: rgba(46,158,99,0.3);
  transform: translateY(-2px);
  box-shadow: 0 8px 24px rgba(46,125,82,0.12), 0 0 20px var(--r-color);
}
.rc-glow {
  position: absolute; top: -20px; right: -20px;
  width: 60px; height: 60px; border-radius: 50%;
  background: var(--r-color);
  filter: blur(30px); opacity: 0.1;
}
.rc-header { display: flex; align-items: center; justify-content: space-between; margin-bottom: 10px; }
.rc-symbol {
  font-size: 18px; font-weight: 800;
  background: linear-gradient(135deg, #0f2e1f, #5a7a6a);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
}
.rc-dim { font-size: 10px; padding: 2px 8px; border-radius: 4px; }
.rc-dim.structure { background: rgba(59,130,246,0.12); color: #2470d8; }
.rc-dim.function { background: rgba(16,185,129,0.12); color: #0d9862; }
.rc-dim.pressure { background: rgba(245,158,11,0.12); color: #c77f0a; }
.rc-dim.response { background: rgba(139,92,246,0.12); color: #7a4fd0; }
.rc-dim.stability { background: rgba(239,68,68,0.12); color: #dc3535; }

.rc-value { margin-bottom: 10px; }
.rc-num { font-size: 28px; font-weight: 800; color: #0f2e1f; line-height: 1; }
.rc-unit { font-size: 12px; color: #7a968a; margin-left: 4px; }

.rc-bar-track { height: 4px; background: rgba(15,60,40,0.08); border-radius: 2px; margin-bottom: 10px; overflow: hidden; }
.rc-bar { height: 100%; border-radius: 2px; transition: width 0.8s ease; box-shadow: 0 0 8px var(--r-color); }

.rc-meta { display: flex; justify-content: space-between; font-size: 10px; color: #9ab5a8; margin-bottom: 8px; }
.rc-footer { display: flex; justify-content: space-between; align-items: center; }
.rc-time { font-size: 10px; color: #9ab5a8; }

@media (max-width: 900px) {
  .ind-layout { flex-direction: column; height: auto; }
  .calc-panel { width: 100%; }
}
</style>
