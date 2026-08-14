<template>
  <div class="map-view-modern">
    <!-- 地图主体 -->
    <div class="map-main">
      <div ref="mapEl" class="map-container"></div>
      <!-- 地图浮动信息卡 -->
      <div class="map-floating-card" v-if="selectedProject">
        <div class="floating-header">
          <div class="floating-title">{{ selectedProject.name }}</div>
          <el-icon class="floating-close" @click="selectedProject = null"><Close /></el-icon>
        </div>
        <div class="floating-body">
          <div class="f-stat-row">
            <div class="f-stat">
              <div class="f-stat-val">{{ projectSummary.obs_count || 0 }}</div>
              <div class="f-stat-label">观测</div>
            </div>
            <div class="f-stat">
              <div class="f-stat-val">{{ projectSummary.indicator_count || 0 }}</div>
              <div class="f-stat-label">指标</div>
            </div>
            <div class="f-stat">
              <div class="f-stat-val" :class="{ warn: (projectSummary.alarm_open || 0) > 0 }">{{ projectSummary.alarm_open || 0 }}</div>
              <div class="f-stat-label">预警</div>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- 右侧控制面板 -->
    <div class="map-sidebar">
      <div class="glass-panel layer-panel">
        <div class="panel-title">
          <div class="title-glow" style="background: rgba(59,130,246,0.3);"></div>
          <el-icon :size="16" color="#2470d8"><Grid /></el-icon>
          <span>图层控制</span>
        </div>
        <div class="layer-tree-modern">
          <div class="layer-item" v-for="node in layerTree" :key="node.id">
            <label class="layer-checkbox" :class="{ checked: checkedKeys.includes(node.id) }">
              <input type="checkbox" :checked="checkedKeys.includes(node.id)" @change="toggleLayer(node.id, $event.target.checked)">
              <span class="check-box">
                <el-icon v-if="checkedKeys.includes(node.id)" :size="10" color="#fff"><Check /></el-icon>
              </span>
              <span class="layer-label">{{ node.label }}</span>
              <span class="layer-type" :class="node.data?.layer_type">{{ typeLabel(node.data?.layer_type) }}</span>
            </label>
          </div>
        </div>
      </div>

      <div class="glass-panel legend-panel">
        <div class="panel-title">
          <div class="title-glow" style="background: rgba(16,185,129,0.3);"></div>
          <el-icon :size="16" color="#0d9862"><Compass /></el-icon>
          <span>图例</span>
        </div>
        <div class="legend-list">
          <div class="legend-row"><span class="lg-dot" style="background: #10b981; box-shadow: 0 0 8px #10b981;"></span>项目边界</div>
          <div class="legend-row"><span class="lg-dot" style="background: #3b82f6; box-shadow: 0 0 8px #3b82f6;"></span>观测点位</div>
          <div class="legend-row"><span class="lg-dot" style="background: #f59e0b; box-shadow: 0 0 8px #f59e0b;"></span>遥感图层</div>
          <div class="legend-row"><span class="lg-dot" style="background: #ef4444; box-shadow: 0 0 8px #ef4444;"></span>预警点位</div>
        </div>
      </div>

      <div class="glass-panel coord-panel">
        <div class="panel-title">
          <div class="title-glow" style="background: rgba(139,92,246,0.3);"></div>
          <el-icon :size="16" color="#7a4fd0"><Location /></el-icon>
          <span>坐标信息</span>
        </div>
        <div class="coord-info">
          <div class="coord-row"><span class="coord-label">坐标系</span><span class="coord-val">CGCS2000 / 高斯-克吕格 3° 带</span></div>
          <div class="coord-row"><span class="coord-label">中央经线</span><span class="coord-val">91°30′E</span></div>
          <div class="coord-row"><span class="coord-label">高程基准</span><span class="coord-val">1985 国家高程基准</span></div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, onUnmounted } from 'vue'
import L from 'leaflet'
import 'leaflet/dist/leaflet.css'
import { Grid, Compass, Location, Close, Check } from '@element-plus/icons-vue'
import { mapApi, projectApi } from '../api.js'

const mapEl = ref(null)
let map = null
const layerTree = ref([])
const checkedKeys = ref(['observations'])
const layerOverlays = {}
const selectedProject = ref(null)
const projectSummary = ref({})

function typeLabel(t) {
  return { project: '面', points: '点', raster: '栅格' }[t] || t
}

function toggleLayer(id, checked) {
  if (checked) {
    if (!checkedKeys.value.includes(id)) checkedKeys.value.push(id)
  } else {
    checkedKeys.value = checkedKeys.value.filter(k => k !== id)
  }
  const layer = layerOverlays[id]
  if (!layer) return
  if (checked) map.addLayer(layer)
  else map.removeLayer(layer)
}

async function loadLayers() {
  const layers = await mapApi.layers()
  layerTree.value = layers.map(l => ({ id: l.layer_id, label: l.name, data: l }))
  for (const l of layers) {
    if (l.layer_type === 'project' && l.geojson) {
      const g = L.geoJSON(l.geojson, {
        style: { color: '#0e9f6e', weight: 2, fillColor: '#10b981', fillOpacity: 0.15 },
        onEachFeature: (feature, layer) => {
          layer.on('click', () => showProjectSummary(l.data))
        },
      }).bindPopup(l.name)
      layerOverlays[l.layer_id] = g
      if (checkedKeys.value.includes(l.layer_id)) map.addLayer(g)
    } else if (l.layer_type === 'points' && l.geojson) {
      const pts = L.geoJSON(l.geojson, {
        pointToLayer: (feature, latlng) => L.circleMarker(latlng, {
          radius: 6, color: '#2470d8', fillColor: '#3b82f6', fillOpacity: 0.8, weight: 2
        }),
      }).bindPopup((f) => `<div style="color:#333;font-size:13px"><b>${f.feature.properties.indicator}</b><br/>数值: ${f.feature.properties.value}</div>`)
      layerOverlays[l.layer_id] = pts
      if (checkedKeys.value.includes(l.layer_id)) map.addLayer(pts)
    }
  }
}

async function showProjectSummary(data) {
  const p = await projectApi.list()
  const project = p.find(x => x.id === parseInt(data.layer_id.split('-')[1]))
  if (project) {
    selectedProject.value = project
    projectSummary.value = await mapApi.summary(project.id)
  }
}

onMounted(async () => {
  map = L.map(mapEl.value, { zoomControl: false }).setView([29.65, 91.1], 10)
  L.control.zoom({ position: 'bottomright' }).addTo(map)
  // 浅色地图样式（雪山白云底图，突出高原特色）
  L.tileLayer('https://{s}.basemaps.cartocdn.com/light_all/{z}/{x}/{y}{r}.png', {
    attribution: '&copy;OpenStreetMap, &copy;CartoDB',
    maxZoom: 19,
    subdomains: 'abcd',
  }).addTo(map)
  await loadLayers()
})

onUnmounted(() => { if (map) map.remove() })
</script>

<style scoped>
.map-view-modern {
  display: flex; gap: 16px;
  height: calc(100vh - 104px);
}

.map-main {
  flex: 1; position: relative; border-radius: 16px; overflow: hidden;
  border: 1px solid rgba(255,255,255,0.85);
  box-shadow: 0 4px 20px rgba(46,125,82,0.08);
}
.map-container {
  width: 100%; height: 100%;
}

/* 浮动信息卡 */
.map-floating-card {
  position: absolute; top: 16px; left: 16px;
  background: rgba(255, 255, 255, 0.9);
  backdrop-filter: blur(16px);
  border: 1px solid rgba(255,255,255,0.9);
  border-radius: 14px;
  padding: 14px 18px;
  min-width: 200px;
  box-shadow: 0 8px 32px rgba(46,125,82,0.16);
  animation: slideIn 0.3s ease;
  z-index: 500;
}
@keyframes slideIn {
  from { opacity: 0; transform: translateY(-10px); }
  to { opacity: 1; transform: translateY(0); }
}
.floating-header {
  display: flex; align-items: center; justify-content: space-between;
  margin-bottom: 12px;
}
.floating-title {
  font-size: 14px; font-weight: 600; color: #0f2e1f;
}
.floating-close {
  color: #7a968a; cursor: pointer; font-size: 14px;
  transition: color 0.2s;
}
.floating-close:hover { color: #dc3535; }
.f-stat-row { display: flex; gap: 16px; }
.f-stat { text-align: center; }
.f-stat-val {
  font-size: 20px; font-weight: 700; color: #0d9862;
  line-height: 1;
}
.f-stat-val.warn { color: #dc3535; }
.f-stat-label { font-size: 10px; color: #7a968a; margin-top: 4px; }

/* 右侧侧边栏 */
.map-sidebar {
  width: 260px; flex-shrink: 0;
  display: flex; flex-direction: column; gap: 12px;
  overflow-y: auto;
}

.glass-panel {
  background: rgba(255,255,255,0.6);
  border: 1px solid rgba(255,255,255,0.85);
  border-radius: 14px;
  backdrop-filter: blur(12px);
  padding: 16px;
  transition: all 0.3s ease;
  box-shadow: 0 4px 20px rgba(46,125,82,0.07);
}
.glass-panel:hover {
  border-color: rgba(46,158,99,0.3);
}

.panel-title {
  display: flex; align-items: center; gap: 8px;
  font-weight: 600; color: #1e3a2f; font-size: 13px;
  margin-bottom: 12px;
  position: relative;
}
.title-glow {
  position: absolute; left: -8px; top: -4px;
  width: 28px; height: 28px; border-radius: 50%;
  filter: blur(10px); opacity: 0.6;
}

/* 图层树 */
.layer-tree-modern { display: flex; flex-direction: column; gap: 6px; }
.layer-checkbox {
  display: flex; align-items: center; gap: 10px;
  padding: 8px 10px; border-radius: 10px;
  cursor: pointer; transition: all 0.2s;
  border: 1px solid transparent;
}
.layer-checkbox:hover { background: rgba(255,255,255,0.6); }
.layer-checkbox.checked { background: rgba(16,185,129,0.08); border-color: rgba(16,185,129,0.25); }
.layer-checkbox input { display: none; }
.check-box {
  width: 18px; height: 18px; border-radius: 5px;
  border: 2px solid rgba(15,60,40,0.18);
  display: flex; align-items: center; justify-content: center;
  transition: all 0.2s;
  flex-shrink: 0;
}
.layer-checkbox.checked .check-box {
  background: linear-gradient(135deg, #10b981, #059669);
  border-color: #10b981;
  box-shadow: 0 0 8px rgba(16,185,129,0.3);
}
.layer-label { font-size: 12px; color: #3d5a4c; flex: 1; }
.layer-type {
  font-size: 10px; padding: 1px 6px; border-radius: 4px;
  background: rgba(255,255,255,0.7);
  color: #7a968a;
}

/* 图例 */
.legend-list { display: flex; flex-direction: column; gap: 8px; }
.legend-row { display: flex; align-items: center; gap: 8px; font-size: 11px; color: #5a7a6a; }
.lg-dot { width: 8px; height: 8px; border-radius: 50%; }

/* 坐标 */
.coord-info { display: flex; flex-direction: column; gap: 8px; }
.coord-row { display: flex; justify-content: space-between; align-items: center; }
.coord-label { font-size: 11px; color: #7a968a; }
.coord-val { font-size: 11px; color: #3d5a4c; font-weight: 500; }

/* Leaflet 浅色覆盖 */
:deep(.leaflet-container) { background: #eef6f0 !important; }
:deep(.leaflet-popup-content-wrapper) {
  background: rgba(255,255,255,0.96) !important;
  border: 1px solid rgba(255,255,255,0.9) !important;
  border-radius: 10px !important;
  backdrop-filter: blur(12px);
  color: #1e3a2f !important;
}
:deep(.leaflet-popup-tip) { background: rgba(255,255,255,0.96) !important; }

@media (max-width: 900px) {
  .map-view-modern { flex-direction: column; height: auto; }
  .map-main { height: 56vh; min-height: 320px; }
  .map-sidebar { width: 100%; flex-direction: column; }
}
</style>
