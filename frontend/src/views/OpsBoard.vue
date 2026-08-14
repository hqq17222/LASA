<template>
  <div class="ops-page">
    <div class="page-title">外业调查指挥看板</div>
    <div class="page-subtitle">人员位置 · 样地完成度 · 采集进度总览（数据来自队员 App / 网页端同步的轨迹与照片）</div>

    <div class="ops-layout">
      <!-- 左侧信息面板 -->
      <div class="ops-panel">
        <el-select v-model="projectId" placeholder="选择项目" size="small" style="width:100%" @change="loadAll">
          <el-option v-for="p in projects" :key="p.id" :label="p.name" :value="p.id" />
        </el-select>

        <el-tabs v-model="tab" class="ops-tabs">
          <!-- ══ 人员 ══ -->
          <el-tab-pane name="team">
            <template #label>人员 <el-badge v-if="team.length" :value="team.length" type="success" /></template>
            <div v-if="!team.length" class="empty-tip">暂无队员轨迹数据<br /><span class="dim">队员在外业 App 或野外科考页同步轨迹后显示</span></div>
            <div v-for="m in team" :key="m.username" class="member-card" @click="m.last_lat && flyTo(m.last_lat, m.last_lon, 15)">
              <div class="mc-head">
                <span class="mc-dot" :class="{ live: isLive(m.last_time) }"></span>
                <b>{{ m.display_name }}</b>
                <span class="mc-user">@{{ m.username }}</span>
              </div>
              <div class="mc-row">🕐 {{ isLive(m.last_time) ? '在线 · ' : '' }}{{ fmtTime(m.last_time) }}</div>
              <div class="mc-row">📈 今日 {{ m.today_km }} km / {{ m.today_tracks }} 条轨迹 · 累计 {{ m.track_count }} 条</div>
              <div class="mc-row">📷 已采集 {{ m.photo_count }} 张照片</div>
            </div>
          </el-tab-pane>

          <!-- ══ 样地 ══ -->
          <el-tab-pane name="plots">
            <template #label>样地 <el-badge v-if="plots.length" :value="`${donePlots}/${plots.length}`" type="primary" /></template>
            <div class="plot-actions">
              <el-button size="small" type="primary" plain @click="addPlotMode = !addPlotMode" :type="addPlotMode ? 'warning' : 'primary'">
                {{ addPlotMode ? '取消标点' : '📍 地图标点' }}
              </el-button>
              <el-button size="small" plain @click="plotFileRef?.click()">导入 GeoJSON</el-button>
              <input ref="plotFileRef" type="file" accept=".geojson,.json" style="display:none" @change="onPlotFile" />
            </div>
            <el-progress v-if="plots.length" :percentage="Math.round(donePlots / plots.length * 100)" :stroke-width="10" style="margin:8px 0" />
            <div v-if="addPlotMode" class="add-plot-tip">在右侧地图上点击样地位置，然后填写编号</div>
            <div v-if="!plots.length" class="empty-tip">暂无样地<br /><span class="dim">地图标点或从 GeoJSON 批量导入</span></div>
            <div v-for="pl in plots" :key="pl.id" class="plot-item" @click="flyTo(pl.lat, pl.lon, 16)">
              <span class="pl-badge" :class="pl.status">{{ pl.status === 'done' ? '✓' : '○' }}</span>
              <div class="pl-body">
                <b>{{ pl.code }}</b><span v-if="pl.name"> · {{ pl.name }}</span>
                <div class="pl-sub">{{ pl.lat.toFixed(5) }}, {{ pl.lon.toFixed(5) }} · 半径 {{ pl.radius }}m · 照片 {{ pl.photo_count }}</div>
              </div>
              <span class="pl-del" @click.stop="removePlot(pl)">✕</span>
            </div>
          </el-tab-pane>

          <!-- ══ 图层 ══ -->
          <el-tab-pane name="layers">
            <template #label>图层 <el-badge v-if="layers.length" :value="layers.length" type="info" /></template>
            <el-button size="small" plain style="width:100%" @click="layerFileRef?.click()">📂 上传共享矢量图层（全队员可见）</el-button>
            <input ref="layerFileRef" type="file" accept=".geojson,.json,.kml,.gpx" multiple style="display:none" @change="onLayerFiles" />
            <div v-if="!layers.length" class="empty-tip">暂无共享图层<br /><span class="dim">上传研究区边界、作业单元等矢量数据</span></div>
            <div v-for="ly in layers" :key="ly.id" class="layer-item">
              <span class="ly-color" :style="{ background: ly.color }"></span>
              <div class="ly-body" @click="fitLayer(ly)">
                <b>{{ ly.name }}</b>
                <div class="ly-sub">{{ ly.fmt.toUpperCase() }} · {{ ly.created_by || '系统' }}</div>
              </div>
              <span class="ly-op" @click="toggleLayer(ly)">{{ ly._on ? '隐藏' : '显示' }}</span>
              <span class="ly-op danger" @click="removeLayer(ly)">✕</span>
            </div>
          </el-tab-pane>
        </el-tabs>

        <div class="ops-legend">
          <span><i class="dot done"></i>已调查样地</span>
          <span><i class="dot pending"></i>待调查样地</span>
          <span><i class="dot person"></i>队员位置</span>
        </div>
      </div>

      <!-- 右侧地图 -->
      <div class="ops-map-wrap">
        <div ref="mapEl" class="ops-map"></div>
        <el-button class="refresh-btn" size="small" :loading="loading" @click="loadAll">🔄 刷新</el-button>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, onUnmounted, nextTick } from 'vue'
import L from 'leaflet'
import 'leaflet/dist/leaflet.css'
import { ElMessage, ElMessageBox } from 'element-plus'
import { projectApi, fieldOpsApi } from '../api.js'

const mapEl = ref(null)
let map = null
let plotLayer = null, teamLayer = null, trackLayer = null
const layerObjs = {}  // layerId -> L.layer

const projects = ref([]); const projectId = ref(null)
const team = ref([]); const plots = ref([]); const layers = ref([])
const tab = ref('team')
const loading = ref(false)
const addPlotMode = ref(false)
const plotFileRef = ref(null); const layerFileRef = ref(null)

const donePlots = computed(() => plots.value.filter(p => p.status === 'done').length)

const fmtTime = t => {
  if (!t) return '无位置上报'
  const d = new Date(t + (t.endsWith('Z') ? '' : 'Z'))
  return d.toLocaleString('zh-CN', { month: '2-digit', day: '2-digit', hour: '2-digit', minute: '2-digit' })
}
const isLive = t => t && (Date.now() - new Date(t + (t.endsWith('Z') ? '' : 'Z')).getTime()) < 30 * 60 * 1000

async function loadAll() {
  loading.value = true
  try {
    const [t, pl, ly] = await Promise.all([
      fieldOpsApi.teamStatus().catch(() => []),
      projectId.value ? fieldOpsApi.plots(projectId.value).catch(() => []) : [],
      projectId.value ? fieldOpsApi.layers(projectId.value).catch(() => []) : [],
    ])
    team.value = t; plots.value = pl
    // 图层：保留已加载对象，仅同步元数据
    const oldIds = new Set(Object.keys(layerObjs).map(Number))
    for (const l of ly) {
      l._on = oldIds.has(l.id) ? map.hasLayer(layerObjs[l.id]) : true
      if (!layerObjs[l.id]) { layerObjs[l.id] = buildLayer(l); if (l._on) layerObjs[l.id].addTo(map) }
    }
    for (const id of oldIds) if (!ly.find(x => x.id === id)) { map.removeLayer(layerObjs[id]); delete layerObjs[id] }
    layers.value = ly
    renderMap()
  } finally { loading.value = false }
}

/* ── 共享图层解析（与巡检照片页同规则） ── */
function vecStyle(c) { return { color: c, weight: 2.5, opacity: 0.9, fillColor: c, fillOpacity: 0.15 } }
function buildLayer(ly) {
  const color = ly.color || '#e67e22'
  if (ly.fmt === 'geojson' || ly.fmt === 'json') {
    return L.geoJSON(JSON.parse(ly.content), {
      style: () => vecStyle(color),
      pointToLayer: (f, ll) => L.circleMarker(ll, { radius: 6, ...vecStyle(color), fillOpacity: 0.7 }),
      onEachFeature: (f, l) => f.properties && l.bindPopup(`<b>${f.properties.name || ly.name}</b>`),
    })
  }
  const doc = new DOMParser().parseFromString(ly.content, 'text/xml')
  const g = L.layerGroup()
  if (ly.fmt === 'kml') {
    doc.querySelectorAll('Placemark').forEach(pm => {
      const nm = pm.querySelector('name')?.textContent || ly.name
      const pc = s => s.trim().split(/\s+/).map(c => { const [x, y] = c.split(',').map(Number); return [y, x] })
      pm.querySelectorAll('Point coordinates').forEach(c => L.circleMarker(pc(c.textContent)[0], { radius: 6, ...vecStyle(color), fillOpacity: 0.7 }).addTo(g).bindPopup(nm))
      pm.querySelectorAll('LineString coordinates').forEach(c => L.polyline(pc(c.textContent), vecStyle(color)).addTo(g).bindPopup(nm))
      pm.querySelectorAll('Polygon coordinates').forEach(c => L.polygon(pc(c.textContent), vecStyle(color)).addTo(g).bindPopup(nm))
    })
  } else if (ly.fmt === 'gpx') {
    doc.querySelectorAll('trk').forEach(trk => {
      const pts = [...trk.querySelectorAll('trkpt')].map(p => [+p.getAttribute('lat'), +p.getAttribute('lon')])
      if (pts.length > 1) L.polyline(pts, vecStyle(color)).addTo(g).bindPopup(trk.querySelector('name')?.textContent || ly.name)
    })
    doc.querySelectorAll('wpt').forEach(w => L.circleMarker([+w.getAttribute('lat'), +w.getAttribute('lon')], { radius: 6, ...vecStyle(color), fillOpacity: 0.7 }).addTo(g).bindPopup(w.querySelector('name')?.textContent || ly.name))
  }
  return g
}

/* ── 地图渲染 ── */
const UC = ['#2470d8', '#e67e22', '#0b8fa8', '#7a4fd0', '#c0392b', '#2E9E63']
function renderMap() {
  plotLayer.clearLayers(); teamLayer.clearLayers(); trackLayer.clearLayers()
  const bounds = []
  plots.value.forEach(p => {
    const done = p.status === 'done'
    L.circle([p.lat, p.lon], { radius: p.radius, color: done ? '#10b981' : '#e6a23c', weight: 1.5, fillOpacity: 0.12, fillColor: done ? '#10b981' : '#e6a23c' }).addTo(plotLayer)
    L.circleMarker([p.lat, p.lon], { radius: 7, fillColor: done ? '#10b981' : '#e6a23c', color: '#fff', weight: 2, fillOpacity: 0.95 })
      .addTo(plotLayer)
      .bindTooltip(`${p.code}${p.name ? ' · ' + p.name : ''}`, { permanent: true, direction: 'top', offset: [0, -8], className: 'plot-label' })
      .bindPopup(`<b>${p.code}</b> ${p.name || ''}<br>状态：${done ? '✅ 已调查' : '⏳ 待调查'}<br>半径内照片：${p.photo_count}<br>${p.note || ''}`)
    bounds.push([p.lat, p.lon])
  })
  team.value.forEach((m, i) => {
    if (m.last_lat == null) return
    const col = UC[i % UC.length]
    L.circleMarker([m.last_lat, m.last_lon], { radius: 9, fillColor: col, color: '#fff', weight: 3, fillOpacity: 1 })
      .addTo(teamLayer)
      .bindTooltip(`👤 ${m.display_name}`, { permanent: true, direction: 'bottom', offset: [0, 10], className: 'person-label' })
      .bindPopup(`<b>${m.display_name}</b> @${m.username}<br>最后上报：${fmtTime(m.last_time)}<br>今日：${m.today_km} km / ${m.today_tracks} 条<br>照片：${m.photo_count} 张`)
    bounds.push([m.last_lat, m.last_lon])
  })
  if (bounds.length && !map._opsInitFit) { map.fitBounds(L.latLngBounds(bounds), { padding: [50, 50], maxZoom: 14 }); map._opsInitFit = true }
}
function flyTo(lat, lon, z = 15) { map.flyTo([lat, lon], z, { duration: 0.7 }) }

/* ── 样地管理 ── */
async function onMapClick(e) {
  if (!addPlotMode.value) return
  addPlotMode.value = false
  let code = ''
  try {
    const { value } = await ElMessageBox.prompt('请输入样地编号（如 NT-01）', '新增样地', { confirmButtonText: '创建', cancelButtonText: '取消', inputPattern: /\S+/, inputErrorMessage: '编号不能为空' })
    code = value.trim()
  } catch { return }
  let name = ''
  try {
    const { value } = await ElMessageBox.prompt('样地名称（可留空）', '新增样地', { confirmButtonText: '确定', cancelButtonText: '跳过' })
    name = (value || '').trim()
  } catch { /* 跳过 */ }
  try {
    await fieldOpsApi.createPlot({ project_id: projectId.value, code, name, lon: +e.latlng.lng.toFixed(7), lat: +e.latlng.lat.toFixed(7), radius: 25 })
    ElMessage.success(`样地 ${code} 已创建`)
    loadAll()
  } catch (err) { ElMessage.error('创建失败：' + err) }
}
async function onPlotFile(e) {
  const f = e.target.files[0]; e.target.value = ''
  if (!f) return
  try {
    const r = await fieldOpsApi.importPlots(projectId.value, JSON.parse(await f.text()))
    ElMessage.success(`导入 ${r.created} 个样地${r.skipped ? `，跳过 ${r.skipped} 个（重复或非点要素）` : ''}`)
    loadAll()
  } catch (err) { ElMessage.error('导入失败：' + err) }
}
async function removePlot(pl) {
  try { await ElMessageBox.confirm(`删除样地 ${pl.code}？`, '删除样地', { type: 'warning' }) } catch { return }
  await fieldOpsApi.removePlot(pl.id)
  ElMessage.success('已删除'); loadAll()
}

/* ── 图层管理 ── */
async function onLayerFiles(e) {
  const files = [...e.target.files]; e.target.value = ''
  const palette = ['#e67e22', '#2470d8', '#c0392b', '#0b8fa8', '#7a4fd0', '#2E9E63']
  for (const f of files) {
    const fmt = f.name.split('.').pop().toLowerCase()
    try {
      await fieldOpsApi.createLayer({ project_id: projectId.value, name: f.name, fmt, content: await f.text(), color: palette[layers.value.length % palette.length] })
      ElMessage.success(`图层「${f.name}」已共享`)
    } catch (err) { ElMessage.error(`${f.name} 上传失败：` + err) }
  }
  loadAll()
}
function toggleLayer(ly) {
  const obj = layerObjs[ly.id]
  if (!obj) return
  if (map.hasLayer(obj)) map.removeLayer(obj); else obj.addTo(map)
  ly._on = !ly._on
}
function fitLayer(ly) {
  const obj = layerObjs[ly.id]
  if (obj && obj.getBounds && obj.getBounds().isValid()) map.fitBounds(obj.getBounds(), { padding: [40, 40], maxZoom: 15 })
}
async function removeLayer(ly) {
  try { await ElMessageBox.confirm(`删除共享图层「${ly.name}」？所有用户将不再看到。`, '删除图层', { type: 'warning' }) } catch { return }
  await fieldOpsApi.removeLayer(ly.id)
  ElMessage.success('已删除'); loadAll()
}

let timer = null
onMounted(async () => {
  projects.value = await projectApi.list().catch(() => [])
  if (projects.value.length) projectId.value = projects.value[0].id
  map = L.map(mapEl.value, { zoomControl: false }).setView([29.65, 91.1], 11)
  L.control.zoom({ position: 'bottomright' }).addTo(map)
  const esriImg = L.tileLayer('https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}', { attribution: 'Esri, Maxar', maxZoom: 19 })
  const esriLbl = L.tileLayer('https://server.arcgisonline.com/ArcGIS/rest/services/Reference/World_Boundaries_and_Places/MapServer/tile/{z}/{y}/{x}', { maxZoom: 19 })
  const base = {
    '浅色底图': L.tileLayer('https://{s}.basemaps.cartocdn.com/light_all/{z}/{x}/{y}{r}.png', { attribution: '&copy;OSM, &copy;CartoDB', maxZoom: 19, subdomains: 'abcd' }),
    '遥感影像': esriImg,
    '影像+注记': L.layerGroup([esriImg, esriLbl]),
  }
  base['浅色底图'].addTo(map)
  plotLayer = L.layerGroup().addTo(map); teamLayer = L.layerGroup().addTo(map); trackLayer = L.layerGroup().addTo(map)
  L.control.layers(base, { '样地': plotLayer, '队员位置': teamLayer, '轨迹': trackLayer }, { position: 'topright' }).addTo(map)
  map.on('click', onMapClick)
  await loadAll()
  timer = setInterval(loadAll, 60000)  // 每分钟自动刷新人员位置
})
onUnmounted(() => { if (timer) clearInterval(timer); if (map) { map.remove(); map = null } })
</script>

<style scoped>
.ops-page { height: 100%; display: flex; flex-direction: column; }
.page-title { font-size: 20px; font-weight: 800; color: #0f2e1f; }
.page-subtitle { font-size: 12px; color: #7a968a; margin: 4px 0 12px; }
.ops-layout { flex: 1; display: flex; gap: 12px; min-height: 0; }
.ops-panel {
  width: 320px; flex-shrink: 0; overflow-y: auto; padding: 12px;
  background: rgba(255,255,255,0.72); border: 1px solid rgba(255,255,255,0.85);
  border-radius: 14px; backdrop-filter: blur(12px); box-shadow: 0 4px 20px rgba(46,125,82,0.07);
}
.ops-tabs { margin-top: 10px; }
.ops-tabs :deep(.el-tabs__item) { color: #3d5a4c; }
.ops-tabs :deep(.el-tabs__item.is-active) { color: #0d9862; font-weight: 600; }
.empty-tip { text-align: center; color: #9ab5a8; font-size: 12px; padding: 24px 0; line-height: 1.8; }
.empty-tip .dim { font-size: 11px; }

.member-card { border: 1px solid rgba(15,60,40,0.08); border-radius: 12px; padding: 10px 12px; margin-bottom: 8px; cursor: pointer; background: rgba(255,255,255,0.6); transition: all .15s; }
.member-card:hover { border-color: rgba(13,152,98,0.3); box-shadow: 0 2px 10px rgba(46,125,82,0.1); }
.mc-head { display: flex; align-items: center; gap: 6px; font-size: 13px; color: #0f2e1f; }
.mc-user { font-size: 11px; color: #9ab5a8; }
.mc-dot { width: 8px; height: 8px; border-radius: 50%; background: #c4d4cb; flex-shrink: 0; }
.mc-dot.live { background: #10b981; box-shadow: 0 0 0 3px rgba(16,185,129,0.2); }
.mc-row { font-size: 11px; color: #5a7a6a; margin-top: 3px; }

.plot-actions { display: flex; gap: 6px; }
.add-plot-tip { font-size: 11px; color: #c77f0a; background: rgba(230,162,60,0.1); border-radius: 8px; padding: 6px 8px; margin: 6px 0; }
.plot-item { display: flex; align-items: center; gap: 8px; padding: 8px 10px; border-radius: 10px; cursor: pointer; }
.plot-item:hover { background: rgba(15,60,40,0.04); }
.pl-badge { width: 20px; height: 20px; border-radius: 50%; display: flex; align-items: center; justify-content: center; font-size: 12px; flex-shrink: 0; }
.pl-badge.done { background: rgba(16,185,129,0.15); color: #0d9862; }
.pl-badge.pending { background: rgba(230,162,60,0.15); color: #c77f0a; }
.pl-body { flex: 1; min-width: 0; font-size: 12px; color: #0f2e1f; }
.pl-sub { font-size: 10px; color: #9ab5a8; margin-top: 2px; }
.pl-del { color: #dc3535; font-size: 12px; padding: 2px 4px; }

.layer-item { display: flex; align-items: center; gap: 8px; padding: 8px 10px; border-radius: 10px; }
.layer-item:hover { background: rgba(15,60,40,0.04); }
.ly-color { width: 12px; height: 12px; border-radius: 3px; flex-shrink: 0; }
.ly-body { flex: 1; min-width: 0; font-size: 12px; color: #0f2e1f; cursor: pointer; }
.ly-sub { font-size: 10px; color: #9ab5a8; margin-top: 1px; }
.ly-op { font-size: 11px; color: #2470d8; cursor: pointer; flex-shrink: 0; }
.ly-op.danger { color: #dc3535; }

.ops-legend { display: flex; gap: 12px; padding: 10px 4px 2px; border-top: 1px solid rgba(15,60,40,0.07); margin-top: 8px; font-size: 11px; color: #5a7a6a; flex-wrap: wrap; }
.ops-legend .dot { display: inline-block; width: 9px; height: 9px; border-radius: 50%; margin-right: 4px; }
.ops-legend .dot.done { background: #10b981; }
.ops-legend .dot.pending { background: #e6a23c; }
.ops-legend .dot.person { background: #2470d8; }

.ops-map-wrap { flex: 1; position: relative; border-radius: 14px; overflow: hidden; border: 1px solid rgba(255,255,255,0.85); box-shadow: 0 4px 20px rgba(46,125,82,0.07); }
.ops-map { width: 100%; height: 100%; }
.refresh-btn { position: absolute; top: 12px; left: 12px; z-index: 500; background: rgba(255,255,255,0.92); }

:deep(.plot-label) { background: rgba(255,255,255,0.9); border: 1px solid rgba(15,60,40,0.15); border-radius: 4px; font-size: 10px; padding: 0 4px; color: #0f2e1f; box-shadow: none; }
:deep(.plot-label::before) { display: none; }
:deep(.person-label) { background: rgba(36,112,216,0.9); color: #fff; border: none; border-radius: 4px; font-size: 10px; padding: 1px 5px; box-shadow: none; }
:deep(.person-label::before) { display: none; }
:deep(.leaflet-container) { background: #f2f7f4 !important; }

@media (max-width: 900px) {
  .ops-layout { flex-direction: column; overflow-y: auto; }
  .ops-panel { width: 100%; max-height: 46vh; }
  .ops-map-wrap { min-height: 52vh; }
}
</style>
