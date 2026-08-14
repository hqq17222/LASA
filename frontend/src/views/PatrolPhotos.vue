<template>
  <div class="patrol-photos-modern">
    <!-- 顶部工具栏 -->
    <div class="pp-toolbar">
      <div class="toolbar-left">
        <el-select v-model="projectId" placeholder="选择项目" size="default" @change="loadAll" class="dark-select" style="width:200px">
          <el-option v-for="p in projects" :key="p.id" :label="p.name" :value="p.id" />
        </el-select>
        <el-divider direction="vertical" class="dark-divider" />
        <el-upload :disabled="!projectId" action="/api/v1/patrol-photos/upload" :data="{ project_id: projectId }"
          :headers="uploadHeaders"
          :on-success="onUploadSuccess" :on-error="onUploadError" :show-file-list="false" :auto-upload="true"
          accept="image/jpeg,image/jpg,image/png,image/heic,image/heif,video/mp4,video/quicktime,video/3gpp,.mp4,.mov,.3gp,.avi,.mkv" multiple>
          <el-button type="primary" :disabled="!projectId" :icon="Upload">上传照片/录像</el-button>
        </el-upload>
        <el-button :disabled="!projectId" :icon="Picture" @click="batchUploadDialog = true" class="dark-btn">批量上传</el-button>
        <el-button :icon="FolderOpened" @click="vecInputRef?.click()" class="dark-btn">加载矢量图层</el-button>
        <input ref="vecInputRef" type="file" accept=".geojson,.json,.kml,.gpx" multiple style="display:none" @change="onVecFiles" />
        <el-button :icon="Position" @click="$router.push('/field')" class="dark-btn">野外科考</el-button>
      </div>
      <div class="toolbar-right">
        <div class="stat-pill"><el-icon :size="12" color="#5a7a6a"><Picture /></el-icon><span>{{ stats.photos ?? stats.total }} 照片</span></div>
        <div class="stat-pill video" v-if="stats.videos"><el-icon :size="12" color="#7a4fd0"><VideoCamera /></el-icon><span>{{ stats.videos }} 录像</span></div>
        <div class="stat-pill gps" v-if="stats.with_gps"><el-icon :size="12" color="#0d9862"><Location /></el-icon><span>{{ stats.with_gps }} GPS</span></div>
        <div class="stat-pill defect" v-if="stats.with_defect"><el-icon :size="12" color="#dc3535"><WarningFilled /></el-icon><span>{{ stats.with_defect }} 缺陷</span></div>
      </div>
    </div>

    <!-- 筛选栏 -->
    <div class="pp-filterbar">
      <el-radio-group v-model="fltType" size="small">
        <el-radio-button value="all">全部</el-radio-button>
        <el-radio-button value="photo">仅照片</el-radio-button>
        <el-radio-button value="video">仅录像</el-radio-button>
      </el-radio-group>
      <el-radio-group v-model="fltGps" size="small">
        <el-radio-button value="all">全部定位</el-radio-button>
        <el-radio-button value="with">已定位</el-radio-button>
        <el-radio-button value="without">未定位</el-radio-button>
      </el-radio-group>
      <el-input v-model="fltKw" size="small" placeholder="搜索文件名 / 备注 / 航线" clearable style="width:220px" :prefix-icon="Search" />
      <span class="flt-count">{{ filteredCount }} / {{ allPhotoCount }} 项</span>
      <template v-if="selectedIds.size">
        <el-divider direction="vertical" class="dark-divider" />
        <span class="sel-info">已选 {{ selectedIds.size }} 项</span>
        <el-button size="small" type="danger" plain @click="batchRemove">批量删除</el-button>
        <el-button size="small" text @click="selectedIds.clear(); refreshSel()">取消选择</el-button>
      </template>
    </div>

    <!-- 主体 -->
    <div class="pp-main-area">
      <!-- 左侧资源树 -->
      <div class="pp-resource-panel">
        <div class="rp-header">
          <el-icon :size="16" color="#2470d8"><FolderOpened /></el-icon>
          <span>资源列表</span>
          <span class="rp-count">{{ allPhotoCount }}</span>
        </div>
        <div class="resource-tree">
          <div v-if="filteredGrouped.length === 0" class="rp-empty"><el-empty description="暂无符合条件的媒体文件" :image-size="60" /></div>
          <div v-else class="tree-content">
            <div v-for="dateNode in filteredGrouped" :key="dateNode.date" class="date-group">
              <div class="date-header" @click="toggleDate(dateNode.date)">
                <el-icon><Calendar /></el-icon>
                <span class="date-text">{{ dateNode.date }}</span>
                <span class="date-count">{{ dateNode.total_count }}项</span>
                <el-icon class="toggle-icon" :class="{ rotated: collapsedDates[dateNode.date] }"><ArrowDown /></el-icon>
              </div>
              <div v-show="!collapsedDates[dateNode.date]" class="route-list">
                <div v-for="routeNode in dateNode.routes" :key="routeNode.route" class="route-group">
                  <div class="route-header" @click="toggleRoute(dateNode.date, routeNode.route)">
                    <el-icon><MapLocation /></el-icon>
                    <span class="route-text">{{ routeNode.route }}</span>
                    <span class="route-count">{{ routeNode.count }}项</span>
                    <el-icon class="toggle-icon" :class="{ rotated: collapsedRoutes[`${dateNode.date}-${routeNode.route}`] }"><ArrowDown /></el-icon>
                  </div>
                  <div v-show="!collapsedRoutes[`${dateNode.date}-${routeNode.route}`]" class="photo-grid">
                    <div v-for="photo in routeNode.photos" :key="photo.id" class="photo-thumb"
                      :class="{ active: selectedPhoto?.id === photo.id, 'has-defect': photo.defect_type, checked: selectedIds.has(photo.id) }"
                      @click="selectPhoto(photo)">
                      <div class="thumb-img-wrapper">
                        <video v-if="photo.media_type === 'video'" :src="photo.file_path" preload="metadata" muted playsinline></video>
                        <img v-else :src="photo.file_path" loading="lazy" />
                        <div v-if="photo.media_type === 'video'" class="video-badge">🎬{{ photo.duration ? ' ' + fmtDur(photo.duration) : '' }}</div>
                        <div v-if="photo.defect_type" class="defect-badge">{{ defectShort(photo.defect_type) }}</div>
                        <div class="sel-box" @click.stop="toggleSel(photo.id)">
                          <el-icon v-if="selectedIds.has(photo.id)" color="#0d9862"><CircleCheckFilled /></el-icon>
                          <el-icon v-else color="#9ab5a8"><CircleCheck /></el-icon>
                        </div>
                      </div>
                      <div class="thumb-info">
                        <div class="thumb-name">{{ photo.original_name }}</div>
                        <div class="thumb-meta">
                          <el-icon v-if="photo.lon" :size="10"><Location /></el-icon>
                          <span v-if="photo.lon" style="color:#0d9862">GPS</span>
                          <span v-else style="color:#9ab5a8">无GPS</span>
                        </div>
                      </div>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- 右侧地图 -->
      <div class="pp-map-panel">
        <div ref="mapEl" class="map-container"></div>
        <div class="map-actions">
          <el-button size="small" circle title="我的位置" :loading="locating" @click="locateMe">📍</el-button>
        </div>
        <div v-if="manualLoc" class="loc-banner">📍 浏览器定位不可用（HTTP 页面限制），请在地图上点击你当前所在的位置
          <el-button size="small" text type="danger" @click="manualLoc = false">取消</el-button>
        </div>
        <div v-if="vecLayers.length || sharedList.length" class="vec-panel">
          <div class="vec-title">自定义图层</div>
          <div v-for="v in vecLayers" :key="v.id" class="vec-item">
            <span class="vec-color" :style="{ background: v.color }"></span>
            <span class="vec-name" :title="v.name" @click="fitVec(v)">{{ v.name }}</span>
            <span class="vec-op" @click="toggleVec(v)">{{ map && map.hasLayer(v.layer) ? '隐藏' : '显示' }}</span>
            <span class="vec-op danger" @click="removeVec(v)">移除</span>
          </div>
          <div v-if="sharedList.length" class="vec-title" style="margin-top:6px">项目共享图层</div>
          <div v-for="v in sharedList" :key="v.id" class="vec-item">
            <span class="vec-color" :style="{ background: v.color }"></span>
            <span class="vec-name" :title="v.name" @click="fitVec(v)">{{ v.name }}</span>
            <span class="vec-op" @click="toggleVec(v)">{{ map && map.hasLayer(v.layer) ? '隐藏' : '显示' }}</span>
          </div>
        </div>
        <div class="map-legend">
          <div class="legend-item"><span class="lg-dot normal"></span>照片</div>
          <div class="legend-item"><span class="lg-dot video"></span>录像</div>
          <div class="legend-item"><span class="lg-dot defect"></span>有缺陷</div>
          <div class="legend-item"><span class="lg-dot selected"></span>选中</div>
        </div>
      </div>
    </div>

    <!-- 照片详情弹窗 -->
    <el-dialog v-model="detailVisible" :title="selectedPhoto?.original_name || '照片详情'" width="820px" top="5vh" class="photo-dialog">
      <div v-if="selectedPhoto" class="photo-detail">
        <div class="detail-main">
          <div class="detail-image-wrapper">
            <video v-if="selectedPhoto.media_type === 'video'" :src="selectedPhoto.file_path" controls class="detail-video" />
            <img v-else :src="selectedPhoto.file_path" class="detail-image" />
            <div v-if="selectedPhoto.defect_type" class="detail-defect-banner">
              <el-icon><WarningFilled /></el-icon>
              <span>缺陷类型：{{ selectedPhoto.defect_type }}</span>
              <span v-if="selectedPhoto.defect_confidence">（置信度 {{ (selectedPhoto.defect_confidence * 100).toFixed(0) }}%）</span>
            </div>
          </div>
        </div>
        <div class="detail-sidebar">
          <el-tabs v-model="activeTab">
            <el-tab-pane label="基本信息" name="info">
              <el-descriptions :column="1" size="small" border>
                <el-descriptions-item label="文件名">{{ selectedPhoto.original_name }}</el-descriptions-item>
                <el-descriptions-item label="类型">{{ selectedPhoto.media_type === 'video' ? '🎬 录像' : '📷 照片' }}</el-descriptions-item>
                <el-descriptions-item v-if="selectedPhoto.media_type === 'video'" label="时长">{{ selectedPhoto.duration ? fmtDur(selectedPhoto.duration) : '-' }}</el-descriptions-item>
                <el-descriptions-item label="大小">{{ fmtSize(selectedPhoto.file_size) }}</el-descriptions-item>
                <el-descriptions-item label="拍摄时间">{{ selectedPhoto.photo_time || '-' }}</el-descriptions-item>
                <el-descriptions-item label="航线">{{ selectedPhoto.flight_route || '-' }}</el-descriptions-item>
                <el-descriptions-item label="日期">{{ selectedPhoto.flight_date || '-' }}</el-descriptions-item>
                <el-descriptions-item label="经度">{{ selectedPhoto.lon?.toFixed(6) || '-' }}</el-descriptions-item>
                <el-descriptions-item label="纬度">{{ selectedPhoto.lat?.toFixed(6) || '-' }}</el-descriptions-item>
                <el-descriptions-item label="海拔">{{ selectedPhoto.altitude ? selectedPhoto.altitude + 'm' : '-' }}</el-descriptions-item>
                <el-descriptions-item label="相机">{{ selectedPhoto.camera_make }} {{ selectedPhoto.camera_model }}</el-descriptions-item>
                <el-descriptions-item v-if="selectedPhoto.media_type !== 'video'" label="尺寸">{{ selectedPhoto.image_width }} × {{ selectedPhoto.image_height }}</el-descriptions-item>
              </el-descriptions>
            </el-tab-pane>
            <el-tab-pane label="位置补标" name="location">
              <div class="loc-panel">
                <div class="loc-cur">
                  当前位置：<b v-if="selectedPhoto.lon">{{ selectedPhoto.lat.toFixed(6) }}, {{ selectedPhoto.lon.toFixed(6) }}</b>
                  <b v-else style="color:#c77f0a">未定位</b>
                </div>
                <div class="loc-tip">点击下方小地图选点（可缩放拖动），选好后保存</div>
                <div ref="locMapEl" class="loc-map"></div>
                <div class="loc-picked" v-if="pickedLoc">已选：<b>{{ pickedLoc.lat.toFixed(6) }}, {{ pickedLoc.lng.toFixed(6) }}</b></div>
                <div class="form-actions">
                  <el-button v-if="selectedPhoto.lon" size="small" type="danger" plain @click="clearLoc">清除定位</el-button>
                  <el-button size="small" type="primary" :disabled="!pickedLoc" :loading="savingLoc" @click="saveLoc">保存位置</el-button>
                </div>
              </div>
            </el-tab-pane>
            <el-tab-pane label="缺陷标注" name="defect">
              <div v-if="!editingDefect && selectedPhoto.defect_type" class="defect-view">
                <el-alert :title="selectedPhoto.defect_type" type="warning" :description="selectedPhoto.defect_desc || '暂无详细描述'" :closable="false" show-icon />
                <div class="defect-meta">
                  <p>置信度：<el-tag size="small">{{ (selectedPhoto.defect_confidence * 100).toFixed(0) }}%</el-tag></p>
                  <p>备注：{{ selectedPhoto.inspector_note || '无' }}</p>
                </div>
                <el-button type="primary" size="small" @click="startEditDefect">编辑标注</el-button>
              </div>
              <div v-else class="defect-edit">
                <el-form label-width="80px" size="default">
                  <el-form-item label="缺陷类型">
                    <el-select v-model="defectForm.defect_type" placeholder="选择缺陷类型">
                      <el-option label="无缺陷" value="" />
                      <el-option label="植被退化" value="植被退化" />
                      <el-option label="病虫害" value="病虫害" />
                      <el-option label="裸露" value="裸露" />
                      <el-option label="其他" value="其他" />
                    </el-select>
                  </el-form-item>
                  <el-form-item label="缺陷描述"><el-input v-model="defectForm.defect_desc" type="textarea" rows="3" /></el-form-item>
                  <el-form-item label="置信度"><el-slider v-model="defectForm.defect_confidence" :min="0" :max="1" :step="0.01" /></el-form-item>
                  <el-form-item label="备注"><el-input v-model="defectForm.inspector_note" type="textarea" rows="2" /></el-form-item>
                </el-form>
                <div class="form-actions">
                  <el-button @click="editingDefect = false">取消</el-button>
                  <el-button type="primary" @click="saveDefect" :loading="savingDefect">保存</el-button>
                </div>
              </div>
            </el-tab-pane>
          </el-tabs>
        </div>
      </div>
    </el-dialog>

    <!-- 批量上传 -->
    <el-dialog v-model="batchUploadDialog" title="批量上传巡检照片" width="600px">
      <el-form label-width="100px">
        <el-form-item label="选择文件">
          <el-upload ref="batchUploadRef" action="/api/v1/patrol-photos/batch-upload" :data="{ project_id: projectId }"
            :headers="uploadHeaders"
            :on-success="onBatchSuccess" :on-error="onUploadError" :auto-upload="false" multiple drag accept="image/jpeg,image/jpg,image/png,image/heic,image/heif,video/mp4,video/quicktime,video/3gpp,.mp4,.mov,.3gp,.avi,.mkv">
            <el-icon :size="40"><Upload /></el-icon>
            <div class="el-upload__text">拖拽文件到此处，或 <em>点击上传</em></div>
          </el-upload>
        </el-form-item>
        <el-form-item label="航线编号"><el-input v-model="batchFlightRoute" placeholder="如：航线-A01" /></el-form-item>
        <el-form-item label="飞行日期"><el-date-picker v-model="batchFlightDate" type="date" placeholder="选择日期" value-format="YYYY-MM-DD" /></el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="batchUploadDialog = false">取消</el-button>
        <el-button type="primary" @click="submitBatchUpload">开始上传</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, nextTick, watch } from 'vue'
import L from 'leaflet'
import 'leaflet/dist/leaflet.css'
import { ElMessage, ElMessageBox } from 'element-plus'
import { Upload, Picture, FolderOpened, Calendar, MapLocation, Location, ArrowDown, WarningFilled, Position, VideoCamera, Search, CircleCheck, CircleCheckFilled } from '@element-plus/icons-vue'
import { projectApi, patrolPhotoApi, fieldOpsApi } from '../api.js'

const mapEl = ref(null)
let map = null
let photoLayer = null
let layersControl = null

const projects = ref([])
const projectId = ref('')
const groupedData = ref([])
const stats = ref({ total: 0, with_gps: 0, without_gps: 0, with_defect: 0 })
const collapsedDates = ref({})
const collapsedRoutes = ref({})
const selectedPhoto = ref(null)
const detailVisible = ref(false)
const activeTab = ref('info')
const editingDefect = ref(false)
const savingDefect = ref(false)
const defectForm = ref({ defect_type: '', defect_desc: '', defect_confidence: 0.8, inspector_note: '' })
const allPhotoCount = ref(0)
const batchUploadDialog = ref(false)
const batchUploadRef = ref(null)
const batchFlightRoute = ref('')
const batchFlightDate = ref('')
const uploadHeaders = { Authorization: `Bearer ${localStorage.getItem('lasa_token') || ''}` }

/* ─── 筛选 ─── */
const fltType = ref('all')
const fltGps = ref('all')
const fltKw = ref('')
function matchFlt(p) {
  if (fltType.value !== 'all' && (p.media_type || 'photo') !== fltType.value) return false
  if (fltGps.value === 'with' && p.lon == null) return false
  if (fltGps.value === 'without' && p.lon != null) return false
  const kw = fltKw.value.trim().toLowerCase()
  if (kw) {
    const hay = `${p.original_name || ''} ${p.inspector_note || ''} ${p.flight_route || ''} ${p.flight_date || ''}`.toLowerCase()
    if (!hay.includes(kw)) return false
  }
  return true
}
const filteredGrouped = computed(() => {
  const out = []
  for (const d of groupedData.value) {
    const routes = []
    for (const r of d.routes) {
      const photos = r.photos.filter(matchFlt)
      if (photos.length) routes.push({ ...r, photos, count: photos.length })
    }
    if (routes.length) out.push({ ...d, routes, total_count: routes.reduce((s, r) => s + r.count, 0) })
  }
  return out
})
const filteredCount = computed(() => filteredGrouped.value.reduce((s, d) => s + d.total_count, 0))

/* ─── 批量选择 ─── */
const selectedIds = ref(new Set())
const selTick = ref(0)
function refreshSel() { selTick.value++ }
function toggleSel(id) {
  const s = new Set(selectedIds.value)
  if (s.has(id)) s.delete(id); else s.add(id)
  selectedIds.value = s
}
async function batchRemove() {
  try {
    await ElMessageBox.confirm(`确定删除选中的 ${selectedIds.value.size} 个文件？文件将从服务器移除且不可恢复。`, '批量删除', { type: 'warning', confirmButtonText: '删除', cancelButtonText: '取消' })
  } catch { return }
  try {
    const r = await patrolPhotoApi.batchDelete([...selectedIds.value])
    ElMessage.success(`已删除 ${r.deleted} 个文件`)
    selectedIds.value = new Set()
    if (detailVisible.value && selectedIds.value.has(selectedPhoto.value?.id)) detailVisible.value = false
    await loadAll()
  } catch (e) { ElMessage.error('批量删除失败：' + (e.message || e)) }
}

/* ─── 位置补标小地图 ─── */
const locMapEl = ref(null)
let locMap = null
let locMarker = null
const pickedLoc = ref(null)
const savingLoc = ref(false)
function initLocMap() {
  if (!locMapEl.value) return
  if (locMap) { locMap.remove(); locMap = null; locMarker = null }
  pickedLoc.value = null
  const c = selectedPhoto.value
  const center = c?.lat != null ? [c.lat, c.lon] : [29.65, 91.1]
  const zoom = c?.lat != null ? 14 : 10
  locMap = L.map(locMapEl.value, { zoomControl: true }).setView(center, zoom)
  L.tileLayer('https://{s}.basemaps.cartocdn.com/light_all/{z}/{x}/{y}{r}.png', { attribution: '&copy;OSM, &copy;CartoDB', maxZoom: 19, subdomains: 'abcd' }).addTo(locMap)
  if (c?.lat != null) locMarker = L.marker([c.lat, c.lon], { draggable: true }).addTo(locMap)
    .on('dragend', e => { const ll = e.target.getLatLng(); pickedLoc.value = ll })
  locMap.on('click', e => {
    pickedLoc.value = e.latlng
    if (locMarker) locMarker.setLatLng(e.latlng)
    else locMarker = L.marker(e.latlng, { draggable: true }).addTo(locMap)
      .on('dragend', ev => { const ll = ev.target.getLatLng(); pickedLoc.value = ll })
  })
  setTimeout(() => locMap && locMap.invalidateSize(), 120)
}
async function saveLoc() {
  if (!selectedPhoto.value || !pickedLoc.value) return
  savingLoc.value = true
  try {
    const updated = await patrolPhotoApi.updateLocation(selectedPhoto.value.id, { lon: +pickedLoc.value.lng.toFixed(7), lat: +pickedLoc.value.lat.toFixed(7), altitude: selectedPhoto.value.altitude })
    selectedPhoto.value = updated
    pickedLoc.value = null
    ElMessage.success('位置已保存')
    await loadGrouped(); await loadMapLayers()
  } catch (e) { ElMessage.error('保存失败：' + (e.message || e)) }
  finally { savingLoc.value = false }
}
async function clearLoc() {
  try {
    await ElMessageBox.confirm('清除该文件的定位信息？', '清除定位', { type: 'warning' })
  } catch { return }
  try {
    const updated = await patrolPhotoApi.updateLocation(selectedPhoto.value.id, { lon: null, lat: null, altitude: null })
    selectedPhoto.value = updated
    pickedLoc.value = null
    ElMessage.success('已清除定位')
    await loadGrouped(); await loadMapLayers()
  } catch (e) { ElMessage.error(e.message || String(e)) }
}

/* ─── 自定义矢量图层（GeoJSON / KML / GPX，本地持久化） ─── */
const vecInputRef = ref(null)
const vecLayers = ref([])
const VEC_KEY = 'lasa_pp_vec_layers'
const VEC_COLORS = ['#e67e22', '#2470d8', '#c0392b', '#0b8fa8', '#7a4fd0', '#2E9E63']
const vecUid = () => 'v' + Date.now().toString(36) + Math.random().toString(36).slice(2, 5)

function vecStyle(color) { return { color, weight: 2.5, opacity: 0.9, fillColor: color, fillOpacity: 0.15 } }
function propPopup(props, fallback) {
  const rows = Object.entries(props || {}).filter(([, v]) => v != null && String(v).length < 60).slice(0, 6)
    .map(([k, v]) => `<div style="font-size:12px"><b>${k}</b>: ${v}</div>`).join('')
  return `<div style="min-width:140px;color:#333"><div style="font-weight:600;margin-bottom:4px">${fallback}</div>${rows}</div>`
}
function parseVecFile(name, text, color) {
  const ext = name.split('.').pop().toLowerCase()
  if (ext === 'geojson' || ext === 'json') {
    const gj = JSON.parse(text)
    return L.geoJSON(gj, {
      style: () => vecStyle(color),
      pointToLayer: (f, ll) => L.circleMarker(ll, { radius: 6, ...vecStyle(color), fillOpacity: 0.7 }),
      onEachFeature: (f, l) => l.bindPopup(propPopup(f.properties, f.properties?.name || name)),
    })
  }
  const doc = new DOMParser().parseFromString(text, 'text/xml')
  const group = L.layerGroup()
  if (ext === 'kml') {
    doc.querySelectorAll('Placemark').forEach(pm => {
      const nm = pm.querySelector('name')?.textContent || name
      const parseCoords = s => s.trim().split(/\s+/).map(c => { const [x, y] = c.split(',').map(Number); return [y, x] })
      pm.querySelectorAll('Point coordinates').forEach(c =>
        L.circleMarker(parseCoords(c.textContent)[0], { radius: 6, ...vecStyle(color), fillOpacity: 0.7 }).addTo(group).bindPopup(nm))
      pm.querySelectorAll('LineString coordinates').forEach(c =>
        L.polyline(parseCoords(c.textContent), vecStyle(color)).addTo(group).bindPopup(nm))
      pm.querySelectorAll('Polygon coordinates').forEach(c =>
        L.polygon(parseCoords(c.textContent), vecStyle(color)).addTo(group).bindPopup(nm))
    })
  } else if (ext === 'gpx') {
    doc.querySelectorAll('trk').forEach(trk => {
      const pts = [...trk.querySelectorAll('trkpt')].map(p => [+p.getAttribute('lat'), +p.getAttribute('lon')])
      if (pts.length > 1) L.polyline(pts, vecStyle(color)).addTo(group).bindPopup(trk.querySelector('name')?.textContent || name)
    })
    doc.querySelectorAll('wpt').forEach(w =>
      L.circleMarker([+w.getAttribute('lat'), +w.getAttribute('lon')], { radius: 6, ...vecStyle(color), fillOpacity: 0.7 }).addTo(group)
        .bindPopup(w.querySelector('name')?.textContent || name))
  }
  return group
}
function addVecLayer(name, text, fmtColor, persist = true) {
  try {
    const layer = parseVecFile(name, text, fmtColor)
    if (!layer.getLayers().length) { ElMessage.warning(`${name} 中未解析到几何要素`); return }
    layer.addTo(map)
    const v = { id: vecUid(), name, color: fmtColor, layer }
    vecLayers.value.push(v)
    if (layer.getBounds && layer.getBounds().isValid()) map.fitBounds(layer.getBounds(), { padding: [30, 30], maxZoom: 15 })
    if (persist) {
      try {
        const arr = JSON.parse(localStorage.getItem(VEC_KEY) || '[]')
        arr.push({ name, text: text.length > 1.5e6 ? null : text, color: fmtColor })
        localStorage.setItem(VEC_KEY, JSON.stringify(arr.filter(a => a.text)))
      } catch (e) { ElMessage.warning('图层过大，仅本次会话保留') }
    }
    ElMessage.success(`图层「${name}」已加载（${layer.getLayers().length} 个要素）`)
  } catch (e) { ElMessage.error(`${name} 解析失败：` + e.message) }
}
async function onVecFiles(e) {
  const files = [...e.target.files]; e.target.value = ''
  for (const f of files) addVecLayer(f.name, await f.text(), VEC_COLORS[vecLayers.value.length % VEC_COLORS.length])
}
function restoreVecLayers() {
  try {
    const arr = JSON.parse(localStorage.getItem(VEC_KEY) || '[]')
    for (const a of arr) addVecLayer(a.name, a.text, a.color, false)
  } catch (e) { /* ignore */ }
}
function removeVec(v) {
  if (map && map.hasLayer(v.layer)) map.removeLayer(v.layer)
  vecLayers.value = vecLayers.value.filter(x => x.id !== v.id)
  try {
    const arr = JSON.parse(localStorage.getItem(VEC_KEY) || '[]').filter(a => a.name !== v.name)
    localStorage.setItem(VEC_KEY, JSON.stringify(arr))
  } catch (e) { /* ignore */ }
}
function toggleVec(v) {
  if (!map) return
  if (map.hasLayer(v.layer)) map.removeLayer(v.layer); else v.layer.addTo(map)
  vecLayers.value = [...vecLayers.value]
}
function fitVec(v) { if (map && v.layer.getBounds && v.layer.getBounds().isValid()) map.fitBounds(v.layer.getBounds(), { padding: [30, 30], maxZoom: 15 }) }

/* ─── 项目共享图层（服务端持久化，全员可见） ─── */
const sharedList = ref([])
async function loadSharedLayers() {
  if (!projectId.value || !map) return
  const ly = await fieldOpsApi.layers(projectId.value).catch(() => [])
  for (const v of sharedList.value) { if (map.hasLayer(v.layer)) map.removeLayer(v.layer) }
  const list = []
  for (const l of ly) {
    try {
      const layer = parseVecFile(l.name, l.content, l.color || '#e67e22')
      if (!layer.getLayers().length) continue
      layer.addTo(map)
      list.push({ id: 'srv' + l.id, name: l.name, color: l.color || '#e67e22', layer, shared: true })
    } catch (e) { /* ignore */ }
  }
  sharedList.value = list
}

/* ─── 我的位置 ─── */
const locating = ref(false)
const manualLoc = ref(false)
let myLocMarker = null, myAccCircle = null
function showMyLoc(lat, lng, acc) {
  if (myLocMarker) map.removeLayer(myLocMarker)
  if (myAccCircle) map.removeLayer(myAccCircle)
  myLocMarker = L.circleMarker([lat, lng], { radius: 8, fillColor: '#2470d8', color: '#fff', weight: 3, fillOpacity: 1 }).addTo(map)
    .bindPopup('📍 我的位置').openPopup()
  if (acc) myAccCircle = L.circle([lat, lng], { radius: acc, color: '#2470d8', weight: 1, fillColor: '#2470d8', fillOpacity: 0.12 }).addTo(map)
  map.flyTo([lat, lng], Math.max(map.getZoom(), 14), { duration: 0.8 })
}
function locateMe() {
  if (!navigator.geolocation) { manualLoc.value = true; return }
  locating.value = true
  navigator.geolocation.getCurrentPosition(
    pos => { locating.value = false; showMyLoc(pos.coords.latitude, pos.coords.longitude, pos.coords.accuracy) },
    () => { locating.value = false; manualLoc.value = true },
    { enableHighAccuracy: true, timeout: 10000, maximumAge: 30000 })
}

/* ─── 工具 ─── */
const fmtDur = s => { s = Math.round(s); return `${Math.floor(s / 60)}:${String(s % 60).padStart(2, '0')}` }
function fmtSize(b) {
  if (!b) return '-'
  if (b > 1 << 20) return (b / (1 << 20)).toFixed(1) + ' MB'
  return Math.round(b / 1024) + ' KB'
}

function defectShort(type) {
  const map = { '植被退化': '退化', '病虫害': '虫害', '裸露': '裸露', '其他': '其他' }
  return map[type] || type
}
function toggleDate(date) { collapsedDates.value[date] = !collapsedDates.value[date] }
function toggleRoute(date, route) { const key = `${date}-${route}`; collapsedRoutes.value[key] = !collapsedRoutes.value[key] }

async function loadProjects() {
  projects.value = await projectApi.list()
  if (projects.value.length && !projectId.value) projectId.value = projects.value[0].id
}
async function loadGrouped() {
  if (!projectId.value) return
  groupedData.value = await patrolPhotoApi.grouped(projectId.value)
  allPhotoCount.value = groupedData.value.reduce((s, d) => s + d.total_count, 0)
  if (groupedData.value.length > 0) collapsedDates.value[groupedData.value[0].date] = false
}
async function loadStats() { if (!projectId.value) return; stats.value = await patrolPhotoApi.stats(projectId.value) }

async function loadMapLayers() {
  if (!projectId.value || !map || !photoLayer) return
  const data = await patrolPhotoApi.mapLayers(projectId.value)
  photoLayer.clearLayers()
  const gj = L.geoJSON(data, {
    pointToLayer: (feature, latlng) => {
      const defectType = feature.properties.defect_type
      const isSelected = selectedPhoto.value && selectedPhoto.value.id === feature.properties.id
      const color = defectType ? '#ef4444' : (feature.properties.media_type === 'video' ? '#7a4fd0' : '#10b981')
      const radius = isSelected ? 10 : 7
      return L.circleMarker(latlng, { radius, fillColor: color, color: isSelected ? '#3b82f6' : '#fff', weight: isSelected ? 3 : 2, opacity: 1, fillOpacity: 0.85 })
    },
    onEachFeature: (feature, layer) => {
      const p = feature.properties
      layer.bindPopup(`<div style="min-width:180px;color:#333"><div style="font-weight:600;margin-bottom:6px">${p.media_type === 'video' ? '🎬 ' : '📷 '}${p.original_name}</div><div style="font-size:12px">航线: ${p.flight_route || '-'} 日期: ${p.flight_date || '-'}</div>${p.defect_type ? `<div style="margin-top:6px;color:#ef4444;font-size:12px">⚠ ${p.defect_type}</div>` : ''}</div>`)
      layer.on('click', () => { for (const d of groupedData.value) for (const r of d.routes) { const photo = r.photos.find(ph => ph.id === p.id); if (photo) { selectPhoto(photo); break } } })
    },
  })
  gj.eachLayer(l => photoLayer.addLayer(l))
  if (photoLayer.getLayers().length > 0) map.fitBounds(photoLayer.getBounds(), { padding: [40, 40], maxZoom: 15 })
}

function selectPhoto(photo) {
  selectedPhoto.value = photo; detailVisible.value = true; activeTab.value = 'info'; editingDefect.value = false
  if (photo.lon && photo.lat && map) { map.flyTo([photo.lat, photo.lon], 16, { duration: 0.8 }); loadMapLayers() }
}
function startEditDefect() {
  editingDefect.value = true
  defectForm.value = { defect_type: selectedPhoto.value.defect_type || '', defect_desc: selectedPhoto.value.defect_desc || '', defect_confidence: selectedPhoto.value.defect_confidence || 0.8, inspector_note: selectedPhoto.value.inspector_note || '' }
}
async function saveDefect() {
  if (!selectedPhoto.value) return
  savingDefect.value = true
  try {
    const updated = await patrolPhotoApi.updateDefect(selectedPhoto.value.id, defectForm.value)
    selectedPhoto.value = updated; editingDefect.value = false; ElMessage.success('缺陷标注已保存')
    await loadGrouped(); await loadMapLayers()
  } catch (e) { ElMessage.error(e) }
  finally { savingDefect.value = false }
}

function onUploadSuccess() { ElMessage.success('上传成功'); loadAll() }
function onUploadError(err) { ElMessage.error('上传失败: ' + (err.message || '未知错误')) }
function submitBatchUpload() {
  if (!batchUploadRef.value || !batchUploadRef.value.uploadFiles.length) { ElMessage.warning('请先选择文件'); return }
  batchUploadRef.value.data = { project_id: projectId.value, flight_route: batchFlightRoute.value, flight_date: batchFlightDate.value }
  batchUploadRef.value.submit()
}
function onBatchSuccess(res) { const successCount = res.results.filter(r => r.success).length; ElMessage.success(`批量上传完成：${successCount}/${res.total} 成功`); batchUploadDialog.value = false; batchUploadRef.value?.clearFiles?.(); loadAll() }

async function loadAll() { await Promise.all([loadGrouped(), loadStats()]); nextTick(() => { loadMapLayers(); loadSharedLayers() }) }

watch(activeTab, t => { if (t === 'location' && detailVisible.value) nextTick(() => initLocMap()) })

onMounted(async () => {
  await loadProjects()
  map = L.map(mapEl.value, { zoomControl: false }).setView([29.65, 91.1], 10)
  L.control.zoom({ position: 'bottomright' }).addTo(map)

  /* 底图切换：浅色 / 遥感影像 / 影像+注记 / 地形 */
  const osmAttr = '&copy;OpenStreetMap 贡献者'
  const esriImg = L.tileLayer('https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}', { attribution: 'Esri, Maxar, Earthstar Geographics', maxZoom: 19 })
  const esriLbl = L.tileLayer('https://server.arcgisonline.com/ArcGIS/rest/services/Reference/World_Boundaries_and_Places/MapServer/tile/{z}/{y}/{x}', { maxZoom: 19 })
  const baseMaps = {
    '浅色底图': L.tileLayer('https://{s}.basemaps.cartocdn.com/light_all/{z}/{x}/{y}{r}.png', { attribution: osmAttr + ', &copy;CartoDB', maxZoom: 19, subdomains: 'abcd' }),
    '遥感影像': esriImg,
    '影像+注记': L.layerGroup([esriImg, esriLbl]),
    '地形图': L.tileLayer('https://{s}.tile.opentopomap.org/{z}/{x}/{y}.png', { attribution: osmAttr + ', &copy;OpenTopoMap', maxZoom: 18 }),
  }
  baseMaps['浅色底图'].addTo(map)
  photoLayer = L.layerGroup().addTo(map)
  layersControl = L.control.layers(baseMaps, { '照片/录像点位': photoLayer }, { position: 'topright', collapsed: true }).addTo(map)
  restoreVecLayers()
  map.on('click', e => {
    if (!manualLoc.value) return
    manualLoc.value = false
    showMyLoc(e.latlng.lat, e.latlng.lng, 0)
    ElMessage.success('已手动标定当前位置')
  })
  if (projectId.value) await loadAll()
})
watch(() => projectId.value, async () => { if (projectId.value) await loadAll() })
</script>

<style scoped>
.patrol-photos-modern { height: 100%; display: flex; flex-direction: column; }

/* 工具栏 */
.pp-toolbar { display: flex; align-items: center; justify-content: space-between; padding: 12px 16px; background: rgba(255,255,255,0.72); border: 1px solid rgba(255,255,255,0.85); border-radius: 14px; margin-bottom: 12px; box-shadow: 0 4px 20px rgba(46,125,82,0.07); flex-wrap: wrap; gap: 8px; }
.toolbar-left, .toolbar-right { display: flex; align-items: center; gap: 10px; flex-wrap: wrap; }
.dark-divider { border-color: rgba(15,60,40,0.12) !important; }
.dark-btn { background: rgba(255,255,255,0.65) !important; border: 1px solid rgba(15,60,40,0.12) !important; color: #3d5a4c !important; }
.stat-pill { display: flex; align-items: center; gap: 5px; padding: 4px 10px; border-radius: 10px; background: rgba(255,255,255,0.65); border: 1px solid rgba(15,60,40,0.08); font-size: 11px; color: #5a7a6a; }
.stat-pill.gps { border-color: rgba(16,185,129,0.3); color: #0d9862; }
.stat-pill.defect { border-color: rgba(239,68,68,0.3); color: #dc3535; }
.stat-pill.video { border-color: rgba(122,79,208,0.3); color: #7a4fd0; }

/* 筛选栏 */
.pp-filterbar { display: flex; align-items: center; gap: 10px; padding: 8px 14px; background: rgba(255,255,255,0.6); border: 1px solid rgba(255,255,255,0.8); border-radius: 12px; margin-bottom: 12px; flex-wrap: wrap; }
.flt-count { font-size: 11px; color: #7a968a; }
.sel-info { font-size: 12px; color: #0d9862; font-weight: 600; }

/* 主体 */
.pp-main-area { flex: 1; display: flex; gap: 12px; min-height: 0; overflow: hidden; }
.pp-resource-panel { width: 280px; flex-shrink: 0; background: rgba(255,255,255,0.72); border: 1px solid rgba(255,255,255,0.85); border-radius: 14px; backdrop-filter: blur(12px); box-shadow: 0 4px 20px rgba(46,125,82,0.07); display: flex; flex-direction: column; overflow: hidden; }
.rp-header { padding: 12px 14px; border-bottom: 1px solid rgba(15,60,40,0.06); font-weight: 600; color: #1e3a2f; display: flex; align-items: center; gap: 8px; font-size: 13px; }
.rp-count { margin-left: auto; font-size: 11px; padding: 1px 7px; border-radius: 4px; background: rgba(15,60,40,0.05); color: #7a968a; }
.resource-tree { flex: 1; overflow-y: auto; padding: 8px; }
.rp-empty { padding: 20px 0; }

/* 树形 */
.date-group { margin-bottom: 4px; }
.date-header { display: flex; align-items: center; gap: 6px; padding: 8px 10px; border-radius: 8px; cursor: pointer; font-weight: 600; color: #1e3a2f; font-size: 12px; transition: background 0.15s; }
.date-header:hover { background: rgba(15,60,40,0.04); }
.date-text { flex: 1; }
.date-count { font-size: 10px; color: #9ab5a8; font-weight: 400; }
.route-group { margin-left: 10px; margin-bottom: 2px; }
.route-header { display: flex; align-items: center; gap: 6px; padding: 6px 10px; border-radius: 6px; cursor: pointer; color: #5a7a6a; font-size: 11px; transition: background 0.15s; }
.route-header:hover { background: rgba(15,60,40,0.03); }
.route-text { flex: 1; }
.route-count { font-size: 10px; color: #9ab5a8; }
.toggle-icon { font-size: 11px; color: #9ab5a8; transition: transform 0.2s; }
.toggle-icon.rotated { transform: rotate(-90deg); }

/* 照片缩略图 */
.photo-grid { display: grid; grid-template-columns: repeat(2, 1fr); gap: 5px; padding: 5px 5px 5px 16px; }
.photo-thumb { border-radius: 6px; overflow: hidden; cursor: pointer; border: 2px solid transparent; transition: all 0.15s; background: rgba(255,255,255,0.55); }
.photo-thumb:hover { border-color: rgba(15,60,40,0.15); }
.photo-thumb.active { border-color: #2470d8; box-shadow: 0 0 0 2px rgba(36,112,216,0.15); }
.photo-thumb.has-defect { border-color: rgba(220,53,53,0.4); }
.thumb-img-wrapper { position: relative; height: 60px; background: #e6efe9; display: flex; align-items: center; justify-content: center; }
.thumb-img-wrapper img { width: 100%; height: 100%; object-fit: cover; }
.thumb-img-wrapper video { width: 100%; height: 100%; object-fit: cover; pointer-events: none; }
.video-badge { position: absolute; bottom: 2px; left: 2px; background: rgba(0,0,0,0.62); color: #fff; font-size: 9px; padding: 1px 5px; border-radius: 3px; }
.sel-box { position: absolute; top: 2px; left: 2px; background: rgba(255,255,255,0.85); border-radius: 50%; width: 16px; height: 16px; display: flex; align-items: center; justify-content: center; cursor: pointer; z-index: 2; }
.photo-thumb.checked { border-color: #0d9862; box-shadow: 0 0 0 2px rgba(13,152,98,0.18); }
.defect-badge { position: absolute; top: 2px; right: 2px; background: #dc3535; color: #fff; font-size: 9px; padding: 1px 4px; border-radius: 3px; font-weight: 600; }
.thumb-info { padding: 3px 5px; }
.thumb-name { font-size: 9px; color: #3d5a4c; white-space: nowrap; overflow: hidden; text-overflow: ellipsis; }
.thumb-meta { font-size: 9px; display: flex; align-items: center; gap: 2px; margin-top: 1px; }

/* 地图 */
.pp-map-panel { flex: 1; position: relative; border-radius: 14px; overflow: hidden; border: 1px solid rgba(255,255,255,0.85); box-shadow: 0 4px 20px rgba(46,125,82,0.07); }
.map-container { width: 100%; height: 100%; }
.map-actions { position: absolute; top: 12px; left: 12px; z-index: 500; display: flex; gap: 6px; }
.map-actions .el-button { background: rgba(255,255,255,0.92); border: 1px solid rgba(15,60,40,0.15); box-shadow: 0 2px 8px rgba(46,125,82,0.15); font-size: 15px; }
.loc-banner { position: absolute; top: 54px; left: 12px; right: 12px; z-index: 500; background: rgba(255,251,235,0.96); border: 1px solid rgba(202,138,4,0.35); color: #854d0e; border-radius: 10px; padding: 7px 12px; font-size: 12px; display: flex; align-items: center; gap: 8px; flex-wrap: wrap; }
.vec-panel { position: absolute; top: 54px; right: 12px; z-index: 500; background: rgba(255,255,255,0.92); border: 1px solid rgba(15,60,40,0.1); border-radius: 10px; padding: 8px 10px; max-width: 220px; box-shadow: 0 4px 14px rgba(46,125,82,0.12); }
.vec-title { font-size: 11px; font-weight: 600; color: #3d5a4c; margin-bottom: 5px; }
.vec-item { display: flex; align-items: center; gap: 6px; font-size: 11px; color: #3d5a4c; padding: 2px 0; }
.vec-color { width: 10px; height: 10px; border-radius: 3px; flex-shrink: 0; }
.vec-name { flex: 1; white-space: nowrap; overflow: hidden; text-overflow: ellipsis; cursor: pointer; }
.vec-name:hover { color: #0d9862; }
.vec-op { cursor: pointer; color: #2470d8; flex-shrink: 0; }
.vec-op.danger { color: #dc3535; }
.map-legend { position: absolute; bottom: 12px; left: 12px; background: rgba(255,255,255,0.88); border-radius: 8px; padding: 6px 10px; display: flex; gap: 12px; font-size: 11px; color: #3d5a4c; border: 1px solid rgba(255,255,255,0.9); box-shadow: 0 2px 10px rgba(46,125,82,0.1); z-index: 400; }
.legend-item { display: flex; align-items: center; gap: 4px; }
.lg-dot { width: 8px; height: 8px; border-radius: 50%; }
.lg-dot.normal { background: #10b981; }
.lg-dot.video { background: #7a4fd0; }
.lg-dot.defect { background: #ef4444; }
.lg-dot.selected { background: #2470d8; border: 2px solid #fff; }

/* 弹窗 */
:deep(.photo-dialog .el-dialog__body) { padding: 0; }
.photo-detail { display: flex; gap: 0; height: 480px; }
.detail-main { flex: 1; background: #eef4f0; display: flex; align-items: center; justify-content: center; position: relative; overflow: hidden; }
.detail-image-wrapper { position: relative; width: 100%; height: 100%; display: flex; align-items: center; justify-content: center; }
.detail-image { max-width: 100%; max-height: 100%; object-fit: contain; }
.detail-video { width: 100%; height: 100%; object-fit: contain; background: #000; }
.loc-panel { padding: 8px 0; font-size: 12px; color: #3d5a4c; }
.loc-cur { margin-bottom: 6px; }
.loc-tip { font-size: 11px; color: #7a968a; margin-bottom: 8px; }
.loc-map { width: 100%; height: 240px; border-radius: 10px; border: 1px solid rgba(15,60,40,0.1); z-index: 1; }
.loc-picked { margin-top: 8px; color: #0d9862; }
.detail-defect-banner { position: absolute; bottom: 0; left: 0; right: 0; background: rgba(220,53,53,0.92); color: #fff; padding: 8px 12px; font-size: 13px; display: flex; align-items: center; gap: 6px; }
.detail-sidebar { width: 260px; flex-shrink: 0; padding: 12px; border-left: 1px solid rgba(15,60,40,0.06); overflow-y: auto; }
.defect-view { padding: 8px 0; }
.defect-meta { margin: 12px 0; font-size: 13px; color: #5a7a6a; }
.defect-meta p { margin: 6px 0; }
.form-actions { display: flex; justify-content: flex-end; gap: 8px; margin-top: 12px; }

:deep(.leaflet-container) { background: #f2f7f4 !important; }
:deep(.leaflet-popup-content-wrapper) { background: rgba(255,255,255,0.96) !important; border: 1px solid rgba(15,60,40,0.08) !important; border-radius: 10px !important; box-shadow: 0 8px 24px rgba(46,125,82,0.15); color: #1e3a2f !important; }
:deep(.leaflet-popup-tip) { background: rgba(255,255,255,0.96) !important; }

@media (max-width: 900px) {
  .pp-main-area { flex-direction: column; overflow-y: auto; }
  .pp-resource-panel { width: 100%; max-height: 320px; }
  .pp-map-panel { min-height: 380px; }
  .photo-detail { flex-direction: column; height: auto; }
  .detail-main { height: 260px; }
  .detail-sidebar { width: 100%; border-left: none; border-top: 1px solid rgba(15,60,40,0.06); }
}
</style>
