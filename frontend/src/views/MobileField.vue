<template>
  <div class="mf-root">
    <!-- ═══ 全屏地图 ═══ -->
    <div ref="mapEl" class="mf-map"></div>

    <!-- 顶栏 -->
    <div class="mf-topbar">
      <div class="mf-title">🏔️ 南北山外业</div>
      <div class="mf-gps" :class="{ ok: myPos }">
        <template v-if="myPos">📍 {{ myPos.lat.toFixed(5) }}, {{ myPos.lon.toFixed(5) }} <span v-if="myPos.acc">±{{ Math.round(myPos.acc) }}m</span></template>
        <template v-else>📍 定位中…</template>
      </div>
      <div class="mf-user" @click="showUserMenu = !showUserMenu">{{ userName }} ▾</div>
      <div v-if="showUserMenu" class="mf-usermenu" @click="logout">退出登录</div>
    </div>

    <!-- 地图浮动按钮 -->
    <div class="mf-fabs">
      <button class="mf-fab" @click="showLayers = !showLayers">🗺️</button>
      <button class="mf-fab" :class="{ active: follow }" @click="toggleFollow">🎯</button>
    </div>

    <!-- 图层切换面板 -->
    <div v-if="showLayers" class="mf-layers">
      <div class="mf-layers-title">底图</div>
      <label class="mf-lrow"><input type="radio" value="road" v-model="baseName" /> 路网地图</label>
      <label class="mf-lrow"><input type="radio" value="sat" v-model="baseName" /> 遥感影像</label>
      <div class="mf-layers-title">业务图层</div>
      <label class="mf-lrow"><input type="checkbox" v-model="showPlots" /> 样地点（{{ plots.length }}）</label>
      <label class="mf-lrow"><input type="checkbox" v-model="showPhotos" /> 我的照片点</label>
      <label class="mf-lrow"><input type="checkbox" v-model="showSurveys" /> 调查记录点</label>
      <template v-if="layers.length">
        <div class="mf-layers-title">共享矢量图层</div>
        <label v-for="ly in layers" :key="ly.id" class="mf-lrow">
          <input type="checkbox" :value="ly.id" v-model="activeLayerIds" /> {{ ly.name }}
        </label>
      </template>
    </div>

    <!-- 找样地：选中样地信息卡 -->
    <div v-if="tab === 'map' && selPlot" class="mf-plotcard">
      <div class="mf-pc-head">
        <b>{{ selPlot.code }}</b><span v-if="selPlot.name"> · {{ selPlot.name }}</span>
        <span class="mf-pc-status" :class="selPlot.status">{{ selPlot.status === 'done' ? '✅ 已采' : '⏳ 待采' }}</span>
        <button class="mf-pc-x" @click="selPlot = null">✕</button>
      </div>
      <div class="mf-pc-body">
        <span v-if="myPos">距离 <b>{{ fmtDist(distTo(selPlot)) }}</b> · 方位 {{ bearingText(selPlot) }}</span>
        <span v-else>等待定位…</span>
        <span v-if="selPlot.note" class="mf-pc-note">📋 {{ selPlot.note }}</span>
      </div>
      <div class="mf-pc-acts">
        <button class="mf-btn small" @click="flyTo(selPlot.lat, selPlot.lon)">🗺️ 飞向</button>
        <button class="mf-btn small primary" @click="startSurveyFor(selPlot)">🌲 发起调查</button>
        <button class="mf-btn small" @click="tab = 'camera'">📷 拍照</button>
      </div>
    </div>

    <!-- 找样地：最近样地速览 -->
    <div v-else-if="tab === 'map' && nearestPlots.length" class="mf-near">
      <div v-for="np in nearestPlots" :key="np.id" class="mf-near-item" @click="selectPlot(np)">
        <span class="mf-near-code" :class="np.status">{{ np.code }}</span>
        <span class="mf-near-dist">{{ myPos ? fmtDist(distTo(np)) : '—' }}</span>
      </div>
    </div>

    <!-- ═══ 底部抽屉（拍照/调查/轨迹） ═══ -->
    <div v-if="tab !== 'map'" class="mf-sheet">
      <!-- 📷 拍照识别 -->
      <div v-if="tab === 'camera'" class="mf-pane">
        <div class="mf-cam-btns">
          <button class="mf-btn primary big" @click="camInput.click()">📷 拍照</button>
          <button class="mf-btn big" @click="albumInput.click()">🖼️ 相册</button>
        </div>
        <input ref="camInputRef" type="file" accept="image/*" capture="environment" style="display:none" @change="onPhoto" />
        <input ref="albumInputRef" type="file" accept="image/jpeg,image/jpg,image/png,image/heic,image/heif" multiple style="display:none" @change="onPhoto" />
        <div class="mf-tip">拍照自动定位并 AI 识别植物；微信/QQ 存图请用「原图」否则定位被剥离</div>

        <div class="mf-list">
          <div v-for="p in photos" :key="p.id" class="mf-item">
            <div class="mf-thumb" @click="preview = p.thumb || p.serverUrl">
              <img v-if="p.thumb || p.serverUrl" :src="p.thumb || p.serverUrl" /><span v-else>🌄</span>
            </div>
            <div class="mf-item-body">
              <div class="mf-item-name">
                <template v-if="p.species">🌿 {{ p.species }}<span v-if="p.conf" class="mf-conf"> {{ Math.round(p.conf * 100) }}%</span></template>
                <template v-else-if="p.identifying">🔍 识别中…</template>
                <template v-else-if="p.identifyError">⚠️ 识别失败</template>
                <template v-else>未识别</template>
              </div>
              <div class="mf-item-sub">
                <template v-if="p.lat != null">📍 {{ p.lat.toFixed(5) }}, {{ p.lon.toFixed(5) }}</template>
                <template v-else>📍 未定位</template>
                · 🕐 {{ p.time }}
              </div>
              <div v-if="p.sci" class="mf-item-sub">{{ p.sci }}<span v-if="p.family"> · {{ p.family }}</span></div>
              <div v-if="p.features" class="mf-item-feat">{{ p.features }}</div>
              <div class="mf-item-acts">
                <button v-if="p.serverId && !p.identifying" class="mf-mini" @click="identify(p)">🔍 {{ p.species ? '重新识别' : '识别' }}</button>
                <button v-if="p.serverId" class="mf-mini" @click="p._edit = !p._edit">✏️ 修正</button>
                <button v-if="!p.serverId" class="mf-mini" @click="uploadOne(p)">⬆️ 重传</button>
                <button v-if="p.lat != null" class="mf-mini" @click="flyTo(p.lat, p.lon); tab = 'map'">🗺️</button>
                <button class="mf-mini danger" @click="delPhoto(p.id)">🗑</button>
              </div>
              <div v-if="p._edit" class="mf-edit">
                <input v-model="p.species" placeholder="物种中文名" class="mf-input" />
                <input v-model="p.sci" placeholder="拉丁学名（可空）" class="mf-input" />
                <button class="mf-btn small primary" @click="saveSpecies(p)">💾 保存修正</button>
              </div>
            </div>
          </div>
          <div v-if="!photos.length" class="mf-empty">还没有照片，拍一张试试</div>
        </div>
      </div>

      <!-- 🌲 样地调查 -->
      <div v-else-if="tab === 'survey'" class="mf-pane">
        <div class="mf-form">
          <select v-model="survey.plot_id" class="mf-input">
            <option :value="null">— 自由调查点（不关联样地）—</option>
            <option v-for="pl in plots" :key="pl.id" :value="pl.id">{{ pl.code }}{{ pl.name ? ' · ' + pl.name : '' }}{{ pl.status === 'done' ? ' ✅' : '' }}</option>
          </select>
          <div class="mf-form-row">
            <input v-model="survey.species" placeholder="优势种（如 油松）" class="mf-input" style="flex:1.4" />
            <input v-model="survey.height_m" type="number" inputmode="decimal" placeholder="树高 m" class="mf-input" />
          </div>
          <div class="mf-form-row">
            <input v-model="survey.dbh_cm" type="number" inputmode="decimal" placeholder="胸径/丛幅 cm" class="mf-input" />
            <input v-model="survey.canopy" type="number" inputmode="decimal" step="0.05" min="0" max="1" placeholder="郁闭度 0-1" class="mf-input" />
            <input v-model="survey.cover_pct" type="number" inputmode="decimal" placeholder="盖度 %" class="mf-input" />
          </div>
          <textarea v-model="survey.note" placeholder="备注：长势、病虫害、坡向坡位、土壤等" class="mf-input" rows="2"></textarea>
          <div class="mf-form-loc">
            <template v-if="myPos">📍 {{ myPos.lat.toFixed(6) }}, {{ myPos.lon.toFixed(6) }}<span v-if="myPos.alt"> · {{ Math.round(myPos.alt) }} m</span></template>
            <template v-else>📍 未定位（仍可提交，坐标留空）</template>
            <span v-if="photos.length && photos[0].serverId" class="mf-form-photo">📷 关联最近照片 #{{ photos[0].serverId }}<input type="checkbox" v-model="survey.linkPhoto" /></span>
          </div>
          <button class="mf-btn primary big" :disabled="submitting" @click="submitSurvey">
            {{ submitting ? '提交中…' : '💾 提交调查记录' }}
          </button>
        </div>
        <div class="mf-list">
          <div v-for="s in surveys" :key="s.id" class="mf-item">
            <div class="mf-thumb sv">🌲</div>
            <div class="mf-item-body">
              <div class="mf-item-name">{{ s.plot_code || '自由点' }}<template v-if="s.species"> · 🌿 {{ s.species }}</template></div>
              <div class="mf-item-sub">
                {{ [s.height_m && `高${s.height_m}m`, s.dbh_cm && `径${s.dbh_cm}cm`, s.canopy_density != null && `郁闭${s.canopy_density}`, s.cover_pct != null && `盖度${s.cover_pct}%`].filter(Boolean).join(' · ') || '无测量值' }}
              </div>
              <div class="mf-item-sub">🕐 {{ (s.created_at || '').slice(5, 16).replace('T', ' ') }} · {{ s.surveyor }}<span v-if="s._local"> · ⏳待同步</span></div>
              <div v-if="s.note" class="mf-item-feat">{{ s.note }}</div>
              <div class="mf-item-acts">
                <button v-if="s.lat != null" class="mf-mini" @click="flyTo(s.lat, s.lon); tab = 'map'">🗺️</button>
                <button class="mf-mini danger" @click="delSurvey(s)">🗑</button>
              </div>
            </div>
          </div>
          <div v-if="!surveys.length" class="mf-empty">暂无调查记录</div>
        </div>
      </div>

      <!-- 🥾 轨迹 -->
      <div v-else-if="tab === 'track'" class="mf-pane">
        <button v-if="inApp" class="mf-btn big" :class="appRec ? 'danger' : 'primary'" @click="appToggleRecord">
          {{ appRec ? '⏸ 结束并保存轨迹' : '● 开始记录（App 后台防熄屏）' }}
        </button>
        <div v-if="inApp" class="mf-rec" :class="{ live: appRec }">{{ appStatus }}</div>
        <button v-if="!inApp" class="mf-btn big" :class="recording ? 'danger' : 'primary'" @click="toggleRecord">
          {{ recording ? '⏸ 结束并保存轨迹' : '● 开始记录轨迹' }}
        </button>
        <div v-if="!inApp" class="mf-rec" :class="{ live: recording }">{{ recStatus }}</div>
        <div class="mf-cam-btns">
          <button class="mf-btn" @click="trackInput.click()">📂 导入 GPX/KML/坐标表</button>
          <input ref="trackInputRef" type="file" accept=".gpx,.kml,.csv,.txt" multiple style="display:none" @change="onTrackFiles" />
        </div>
        <div class="mf-list">
          <div v-for="(t, i) in tracks" :key="t.id" class="mf-item">
            <div class="mf-thumb trk" :style="{ background: TCOLORS[i % 6] + '22', color: TCOLORS[i % 6] }">🥾</div>
            <div class="mf-item-body">
              <div class="mf-item-name">{{ t.name }}</div>
              <div class="mf-item-sub">📏 {{ trackDist(t.pts).toFixed(2) }} km · {{ t.pts.length }} 点<template v-if="trackDur(t.pts)"> · ⏱ {{ trackDur(t.pts) }}</template> · {{ srcName(t.src) }}<span v-if="t.serverId"> · ☁️云端</span></div>
              <div class="mf-item-acts">
                <button class="mf-mini" @click="focusTrack(i); tab = 'map'">🗺️ 查看</button>
                <button class="mf-mini" @click="exportGPX(i)">⬇ GPX</button>
                <button class="mf-mini danger" @click="delTrack(t.id)">🗑</button>
              </div>
            </div>
          </div>
          <div v-if="!tracks.length" class="mf-empty">暂无轨迹</div>
        </div>
      </div>
    </div>

    <!-- ═══ 底部标签栏 ═══ -->
    <div class="mf-tabbar">
      <button v-for="t in TABS" :key="t.key" class="mf-tab" :class="{ on: tab === t.key }" @click="switchTab(t.key)">
        <span class="mf-tab-ico">{{ t.ico }}</span><span>{{ t.name }}</span>
      </button>
    </div>

    <!-- 全屏照片预览 -->
    <div v-if="preview" class="mf-preview" @click="preview = ''">
      <img :src="preview" />
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, onUnmounted, nextTick, watch } from 'vue'
import { useRouter } from 'vue-router'
import L from 'leaflet'
import 'leaflet/dist/leaflet.css'
import { ElMessage } from 'element-plus'
import { patrolPhotoApi, fieldTrackApi, fieldOpsApi } from '../api.js'

const router = useRouter()
const inApp = typeof window.AndroidBridge !== 'undefined'
const userName = ref('')
try { userName.value = JSON.parse(localStorage.getItem('lasa_user') || '{}').display_name || '用户' } catch (e) { userName.value = '用户' }
const showUserMenu = ref(false)
function logout() {
  localStorage.removeItem('lasa_token'); localStorage.removeItem('lasa_user')
  router.replace('/login')
}

/* ───────── 标签页 ───────── */
const TABS = [
  { key: 'map', name: '找样地', ico: '🗺️' },
  { key: 'camera', name: '拍照识别', ico: '📷' },
  { key: 'survey', name: '样地调查', ico: '🌲' },
  { key: 'track', name: '轨迹', ico: '🥾' },
]
const tab = ref('map')
function switchTab(k) { tab.value = k; nextTick(() => map && map.invalidateSize()) }

/* ───────── 本地缓存 ───────── */
const uid = () => 'm' + Date.now().toString(36) + Math.random().toString(36).slice(2, 6)
const photos = ref([]), surveys = ref([]), tracks = ref([])
try {
  const s = localStorage.getItem('lhasa_mobile_v1')
  if (s) { const d = JSON.parse(s); photos.value = d.photos || []; surveys.value = d.surveys || []; tracks.value = d.tracks || [] }
} catch (e) { /* ignore */ }
let saveTimer = null
function saveLocal() {
  clearTimeout(saveTimer)
  saveTimer = setTimeout(() => {
    try {
      localStorage.setItem('lhasa_mobile_v1', JSON.stringify({
        photos: photos.value.slice(0, 60), surveys: surveys.value.filter(s => s._local), tracks: tracks.value,
      }))
    } catch (e) { /* 存储满时静默 */ }
  }, 300)
}

/* ───────── 地图 ───────── */
const mapEl = ref(null)
let map = null, plotLayer = null, photoLayer = null, surveyLayer = null, vecLayer = null, trackLayer = null
let meMarker = null, meCircle = null
const baseName = ref('road')
const showPlots = ref(true), showPhotos = ref(true), showSurveys = ref(true)
const showLayers = ref(false)
const follow = ref(true)
let baseRoad = null, baseSat = null

const TCOLORS = ['#2E9E63', '#2470d8', '#c77f0a', '#0b8fa8', '#7a4fd0', '#dc3535']

function initMap() {
  map = L.map(mapEl.value, { zoomControl: false, preferCanvas: true, tap: true, touchZoom: true, bounceAtZoomLimits: false, attributionControl: false }).setView([29.65, 91.1], 11)
  L.control.zoom({ position: 'bottomright' }).addTo(map)
  baseRoad = L.tileLayer('https://{s}.basemaps.cartocdn.com/light_all/{z}/{x}/{y}{r}.png', { maxZoom: 19, subdomains: 'abcd' })
  baseSat = L.tileLayer('https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}', { maxZoom: 18 })
  baseRoad.addTo(map)
  plotLayer = L.layerGroup().addTo(map)
  vecLayer = L.layerGroup().addTo(map)
  surveyLayer = L.layerGroup().addTo(map)
  photoLayer = L.layerGroup().addTo(map)
  trackLayer = L.layerGroup().addTo(map)
  map.on('dragstart', () => { follow.value = false })
  nextTick(() => map && map.invalidateSize())
  setTimeout(() => map && map.invalidateSize(), 350)
  setTimeout(() => map && map.invalidateSize(), 1200)
}
watch(baseName, v => {
  if (!map) return
  if (v === 'sat') { map.removeLayer(baseRoad); baseSat.addTo(map) } else { map.removeLayer(baseSat); baseRoad.addTo(map) }
})
function flyTo(lat, lon) { if (map) { follow.value = false; map.flyTo([lat, lon], 16, { duration: 0.8 }) } }

/* ───────── 我的位置 ───────── */
const myPos = ref(null)
let posWatch = null
function startLocate() {
  if (!navigator.geolocation) return
  posWatch = navigator.geolocation.watchPosition(pos => {
    myPos.value = { lat: pos.coords.latitude, lon: pos.coords.longitude, acc: pos.coords.accuracy, alt: pos.coords.altitude }
    renderMe()
    if (follow.value && map) map.setView([myPos.value.lat, myPos.value.lon], Math.max(map.getZoom(), 15), { animate: true })
  }, () => {}, { enableHighAccuracy: true, maximumAge: 5000, timeout: 20000 })
}
function renderMe() {
  if (!map || !myPos.value) return
  const ll = [myPos.value.lat, myPos.value.lon]
  if (!meMarker) {
    meMarker = L.circleMarker(ll, { radius: 8, fillColor: '#2470d8', color: '#fff', weight: 3, fillOpacity: 1 }).addTo(map)
    meCircle = L.circle(ll, { radius: myPos.value.acc || 30, color: '#2470d8', weight: 1, fillColor: '#2470d8', fillOpacity: 0.12 }).addTo(map)
  } else {
    meMarker.setLatLng(ll); meCircle.setLatLng(ll); meCircle.setRadius(myPos.value.acc || 30)
  }
}
function toggleFollow() {
  follow.value = !follow.value
  if (follow.value && myPos.value && map) map.flyTo([myPos.value.lat, myPos.value.lon], 16)
}

/* ───────── 样地 ───────── */
const plots = ref([]), layers = ref([]), activeLayerIds = ref([])
const selPlot = ref(null)
function hav(a, b) { const R = 6371, r = Math.PI / 180
  const h = Math.sin((b[0] - a[0]) * r / 2) ** 2 + Math.cos(a[0] * r) * Math.cos(b[0] * r) * Math.sin((b[1] - a[1]) * r / 2) ** 2
  return 2 * R * Math.asin(Math.sqrt(h)) }
function distTo(p) { return myPos.value ? hav([myPos.value.lat, myPos.value.lon], [p.lat, p.lon]) : null }
function fmtDist(km) { if (km == null) return '—'; return km >= 1 ? km.toFixed(2) + ' km' : Math.round(km * 1000) + ' m' }
function bearingText(p) {
  if (!myPos.value) return ''
  const r = Math.PI / 180
  const y = Math.sin((p.lon - myPos.value.lon) * r) * Math.cos(p.lat * r)
  const x = Math.cos(myPos.value.lat * r) * Math.sin(p.lat * r) - Math.sin(myPos.value.lat * r) * Math.cos(p.lat * r) * Math.cos((p.lon - myPos.value.lon) * r)
  let brg = (Math.atan2(y, x) / r + 360) % 360
  return ['北', '东北', '东', '东南', '南', '西南', '西', '西北'][Math.round(brg / 45) % 8] + ' ' + Math.round(brg) + '°'
}
const nearestPlots = computed(() => {
  if (!myPos.value) return plots.value.slice(0, 4)
  return [...plots.value].sort((a, b) => distTo(a) - distTo(b)).slice(0, 4)
})
function selectPlot(p) { selPlot.value = p; flyTo(p.lat, p.lon) }

function renderPlots() {
  if (!plotLayer) return
  plotLayer.clearLayers()
  if (!showPlots.value) return
  plots.value.forEach(p => {
    const done = p.status === 'done'
    const col = done ? '#2E9E63' : '#e8873a'
    const m = L.circleMarker([p.lat, p.lon], { radius: 9, fillColor: col, color: '#fff', weight: 2, fillOpacity: 0.92 })
    m.on('click', () => { selPlot.value = p })
    m.bindTooltip(p.code, { direction: 'top', offset: [0, -8], className: 'mf-plot-tip' })
    m.addTo(plotLayer)
    if (p.radius > 0) L.circle([p.lat, p.lon], { radius: p.radius, color: col, weight: 1.2, dashArray: '5 4', fillOpacity: 0.06 }).addTo(plotLayer)
  })
}
watch(showPlots, renderPlots)

/* ───────── 共享矢量图层 ───────── */
function parseVecContent(ly) {
  const txt = ly.content || ''
  if (ly.fmt === 'geojson' || txt.trim().startsWith('{')) {
    try { return { type: 'geojson', data: JSON.parse(txt) } } catch (e) { return null }
  }
  if (ly.fmt === 'kml' || txt.includes('<kml')) {
    try {
      const doc = new DOMParser().parseFromString(txt, 'text/xml')
      const feats = []
      ;[...doc.getElementsByTagName('Placemark')].forEach(pm => {
        const name = pm.getElementsByTagName('name')[0]?.textContent || ''
        const c = pm.getElementsByTagName('coordinates')[0]
        if (!c) return
        const pts = c.textContent.trim().split(/\s+/).map(s => { const a = s.split(','); return [+a[0], +a[1]] })
        if (!pts.length) return
        const isPoly = pm.getElementsByTagName('Polygon').length > 0
        feats.push({ type: 'Feature', properties: { name }, geometry: isPoly ? { type: 'Polygon', coordinates: [pts] } : pts.length > 1 ? { type: 'LineString', coordinates: pts } : { type: 'Point', coordinates: pts[0] } })
      })
      return { type: 'geojson', data: { type: 'FeatureCollection', features: feats } }
    } catch (e) { return null }
  }
  if (ly.fmt === 'gpx' || txt.includes('<gpx')) {
    try {
      const doc = new DOMParser().parseFromString(txt, 'text/xml')
      const feats = []
      ;[...doc.getElementsByTagName('trk')].forEach(trk => {
        const pts = [...trk.getElementsByTagName('trkpt')].map(p => [+p.getAttribute('lon'), +p.getAttribute('lat')])
        if (pts.length > 1) feats.push({ type: 'Feature', properties: { name: trk.getElementsByTagName('name')[0]?.textContent || '' }, geometry: { type: 'LineString', coordinates: pts } })
      })
      ;[...doc.getElementsByTagName('wpt')].forEach(w => feats.push({ type: 'Feature', properties: { name: w.getElementsByTagName('name')[0]?.textContent || '' }, geometry: { type: 'Point', coordinates: [+w.getAttribute('lon'), +w.getAttribute('lat')] } }))
      return { type: 'geojson', data: { type: 'FeatureCollection', features: feats } }
    } catch (e) { return null }
  }
  return null
}
function renderVecLayers() {
  if (!vecLayer) return
  vecLayer.clearLayers()
  layers.value.filter(ly => activeLayerIds.value.includes(ly.id)).forEach(ly => {
    const parsed = parseVecContent(ly)
    if (!parsed) return
    L.geoJSON(parsed.data, {
      style: { color: ly.color || '#e67e22', weight: 2.5, fillOpacity: 0.08 },
      pointToLayer: (f, ll) => L.circleMarker(ll, { radius: 6, fillColor: ly.color || '#e67e22', color: '#fff', weight: 1.5, fillOpacity: 0.9 }),
      onEachFeature: (f, l) => { if (f.properties?.name) l.bindTooltip(String(f.properties.name), { className: 'mf-plot-tip' }) },
    }).addTo(vecLayer)
  })
}
watch(activeLayerIds, renderVecLayers)

/* ───────── 拍照 + AI 识别 ───────── */
const camInputRef = ref(null), albumInputRef = ref(null)
const camInput = { click: () => camInputRef.value?.click() }
const albumInput = { click: () => albumInputRef.value?.click() }
const preview = ref('')

function parseExifGPS(buf) {
  const dv = new DataView(buf)
  if (dv.getUint16(0) !== 0xFFD8) return null
  let off = 2
  while (off < dv.byteLength - 4) {
    if (dv.getUint8(off) !== 0xFF) break
    const marker = dv.getUint8(off + 1)
    if (marker === 0xE1) {
      if (dv.getUint32(off + 4) !== 0x45786966) { off += 2 + dv.getUint16(off + 2); continue }
      const t0 = off + 10
      const le = dv.getUint16(t0) === 0x4949
      const u16 = o => le ? dv.getUint16(t0 + o, true) : dv.getUint16(t0 + o)
      const u32 = o => le ? dv.getUint32(t0 + o, true) : dv.getUint32(t0 + o)
      if (u16(2) !== 42) return null
      const TSZ = { 1: 1, 2: 1, 3: 2, 4: 4, 5: 8, 7: 1, 9: 4, 10: 8 }
      const readIFD = base => { const m = {}; const n = u16(base)
        for (let i = 0; i < n; i++) { const e = base + 2 + i * 12, tag = u16(e), type = u16(e + 2), cnt = u32(e + 4)
          const sz = (TSZ[type] || 1) * cnt, vo = sz <= 4 ? e + 8 : u32(e + 8)
          m[tag] = { type, cnt, o: vo } } return m }
      const rat = (o, i) => { const a = u32(o + i * 8), b = u32(o + i * 8 + 4); return b ? a / b : 0 }
      const str = e => { let s = ''; for (let i = 0; i < e.cnt; i++) s += String.fromCharCode(dv.getUint8(t0 + e.o + i)); return s.replace(/\0/g, '').trim() }
      const ifd0 = readIFD(u32(4))
      if (!ifd0[0x8825]) return null
      const gps = readIFD(u32(ifd0[0x8825].o))
      if (!gps[2] || !gps[4]) return null
      const dms = e => rat(e.o, 0) + rat(e.o, 1) / 60 + rat(e.o, 2) / 3600
      let lat = dms(gps[2]), lon = dms(gps[4])
      if (gps[1] && str(gps[1]).toUpperCase() === 'S') lat = -lat
      if (gps[3] && str(gps[3]).toUpperCase() === 'W') lon = -lon
      let alt = null
      if (gps[6]) { alt = rat(gps[6].o, 0); if (gps[5] && dv.getUint8(t0 + gps[5].o) === 1) alt = -alt }
      return { lat, lon, alt }
    }
    if (marker === 0xDA || marker === 0xD9) break
    off += 2 + dv.getUint16(off + 2)
  }
  return null
}
function makeThumb(f) {
  return new Promise(res => {
    const img = new Image(), url = URL.createObjectURL(f)
    img.onload = () => { const s = 200 / Math.max(img.width, img.height), cv = document.createElement('canvas')
      cv.width = img.width * s; cv.height = img.height * s
      cv.getContext('2d').drawImage(img, 0, 0, cv.width, cv.height)
      URL.revokeObjectURL(url); res(cv.toDataURL('image/jpeg', .7)) }
    img.onerror = () => { URL.revokeObjectURL(url); res('') }
    img.src = url
  })
}

async function onPhoto(e) {
  const files = [...e.target.files]; e.target.value = ''
  if (!files.length) return
  for (const f of files) {
    const buf = await f.arrayBuffer()
    let meta = null
    try { meta = parseExifGPS(buf) } catch (err) { /* ignore */ }
    const thumb = await makeThumb(f)
    const rec = {
      id: uid(), name: f.name, time: new Date(f.lastModified).toISOString().slice(5, 16).replace('T', ' '),
      lat: meta?.lat ?? myPos.value?.lat ?? null, lon: meta?.lon ?? myPos.value?.lon ?? null,
      alt: meta?.alt ?? myPos.value?.alt ?? null,
      thumb, serverUrl: '', serverId: null,
      species: '', sci: '', conf: null, family: '', features: '',
      identifying: false, identifyError: '', _edit: false, _file: f,
    }
    photos.value.unshift(rec)
    saveLocal(); renderPhotos()
    await uploadOne(rec)
  }
}

async function uploadOne(p) {
  try {
    const fd = new FormData()
    fd.append('project_id', 0)
    fd.append('file', p._file)
    const res = await fetch('/api/v1/patrol-photos/upload', {
      method: 'POST', body: fd,
      headers: { Authorization: `Bearer ${localStorage.getItem('lasa_token') || ''}` },
    })
    if (!res.ok) throw new Error('HTTP ' + res.status)
    const j = await res.json()
    p.serverId = j.id
    p.serverUrl = j.file_path
    if (p.lat == null && j.lat != null) { p.lat = j.lat; p.lon = j.lon; p.alt = j.altitude }
    saveLocal(); renderPhotos()
    identify(p)
  } catch (err) {
    p.identifyError = '上传失败：' + (err.message || err)
    ElMessage.error('照片上传失败，可稍后点「重传」')
  }
  saveLocal()
}

async function identify(p) {
  if (!p.serverId || p.identifying) return
  p.identifying = true; p.identifyError = ''
  try {
    const r = await patrolPhotoApi.identify(p.serverId, '拉萨南北山绿化工程区，高原山地造林')
    p.species = r.species || ''
    p.sci = r.scientific_name || ''
    p.conf = r.species_confidence
    p.family = r.species_family || ''
    p.features = r.species_features || ''
    if (!p.species) p.identifyError = r.identification?.note || '未能识别出植物'
  } catch (err) {
    p.identifyError = String(err).slice(0, 80)
  }
  p.identifying = false
  saveLocal(); renderPhotos()
}

async function saveSpecies(p) {
  p._edit = false
  if (p.serverId) {
    try { await patrolPhotoApi.updateSpecies(p.serverId, { species: p.species, scientific_name: p.sci }) } catch (e) { /* ignore */ }
  }
  saveLocal(); renderPhotos()
  ElMessage.success('物种标记已保存')
}

function delPhoto(id) {
  const p = photos.value.find(x => x.id === id)
  if (p?.serverId) patrolPhotoApi.remove(p.serverId).catch(() => {})
  photos.value = photos.value.filter(x => x.id !== id)
  saveLocal(); renderPhotos()
}

function renderPhotos() {
  if (!photoLayer) return
  photoLayer.clearLayers()
  if (!showPhotos.value) return
  photos.value.forEach(p => {
    if (p.lat == null) return
    const m = L.circleMarker([p.lat, p.lon], { radius: 7, fillColor: p.species ? '#2E9E63' : '#f2c94c', color: '#b8860b', weight: 2, fillOpacity: 0.9 }).addTo(photoLayer)
    m.bindPopup(`<b>${p.species ? '🌿 ' + p.species : p.name}</b><br>${p.lat.toFixed(6)}, ${p.lon.toFixed(6)}${p.thumb ? `<br><img src="${p.thumb}" style="width:130px;border-radius:6px;margin-top:4px">` : ''}`)
  })
}
watch(showPhotos, renderPhotos)

/* ───────── 样地调查 ───────── */
const survey = ref({ plot_id: null, species: '', height_m: '', dbh_cm: '', canopy: '', cover_pct: '', note: '', linkPhoto: true })
const submitting = ref(false)
function startSurveyFor(p) {
  survey.value.plot_id = p.id
  tab.value = 'survey'
  if (photos.value.length && photos.value[0].species && !survey.value.species) survey.value.species = photos.value[0].species
}
async function submitSurvey() {
  if (submitting.value) return
  submitting.value = true
  const pl = plots.value.find(x => x.id === survey.value.plot_id)
  const payload = {
    project_id: 0,
    plot_id: survey.value.plot_id,
    plot_code: pl?.code || '',
    lon: myPos.value?.lon ?? pl?.lon ?? null,
    lat: myPos.value?.lat ?? pl?.lat ?? null,
    altitude: myPos.value?.alt ?? null,
    species: survey.value.species || '',
    height_m: survey.value.height_m !== '' ? +survey.value.height_m : null,
    dbh_cm: survey.value.dbh_cm !== '' ? +survey.value.dbh_cm : null,
    canopy_density: survey.value.canopy !== '' ? +survey.value.canopy : null,
    cover_pct: survey.value.cover_pct !== '' ? +survey.value.cover_pct : null,
    note: survey.value.note || '',
    photo_id: (survey.value.linkPhoto && photos.value.length && photos.value[0].serverId) ? photos.value[0].serverId : null,
  }
  try {
    const r = await fieldOpsApi.createSurvey(payload)
    surveys.value.unshift({ ...r, _local: false })
    ElMessage.success(`调查记录已提交${payload.plot_code ? '（' + payload.plot_code + '）' : ''}`)
    survey.value = { plot_id: survey.value.plot_id, species: '', height_m: '', dbh_cm: '', canopy: '', cover_pct: '', note: '', linkPhoto: true }
    loadPlots()  // 刷新样地状态
  } catch (e) {
    surveys.value.unshift({ ...payload, id: uid(), surveyor: userName.value, created_at: new Date().toISOString(), _local: true })
    ElMessage.warning('网络异常，记录已存本机，稍后到「调查」页会重试同步')
  }
  submitting.value = false
  saveLocal(); renderSurveys()
}
async function delSurvey(s) {
  if (s._local) { surveys.value = surveys.value.filter(x => x.id !== s.id) }
  else {
    try { await fieldOpsApi.removeSurvey(s.id) } catch (e) { /* ignore */ }
    surveys.value = surveys.value.filter(x => x.id !== s.id)
  }
  saveLocal(); renderSurveys()
}
function renderSurveys() {
  if (!surveyLayer) return
  surveyLayer.clearLayers()
  if (!showSurveys.value) return
  surveys.value.forEach(s => {
    if (s.lat == null) return
    const m = L.circleMarker([s.lat, s.lon], { radius: 7, fillColor: '#0b8fa8', color: '#fff', weight: 2, fillOpacity: 0.9 }).addTo(surveyLayer)
    m.bindPopup(`<b>🌲 ${s.plot_code || '自由调查点'}</b>${s.species ? '<br>🌿 ' + s.species : ''}<br>${(s.created_at || '').slice(0, 16).replace('T', ' ')} · ${s.surveyor || ''}`)
  })
}
watch(showSurveys, renderSurveys)

/* ───────── 轨迹 ───────── */
const trackInputRef = ref(null)
const trackInput = { click: () => trackInputRef.value?.click() }
const recording = ref(false), recStatus = ref('点击开始后持续记录 GPS 轨迹')
const appRec = ref(false), appStatus = ref('App 后台模式：熄屏仍持续记录')
let recWatch = null, appTimer = null
const recPts = ref([])
let recStart = 0

function toggleRecord() {
  if (!recording.value) {
    if (!navigator.geolocation) { recStatus.value = '⚠️ 当前环境不支持定位'; return }
    recPts.value = []; recStart = Date.now(); recording.value = true
    recWatch = navigator.geolocation.watchPosition(pos => {
      recPts.value.push([pos.coords.latitude, pos.coords.longitude, pos.coords.altitude || null, new Date().toISOString()])
      recStatus.value = `🔴 记录中… ${recPts.value.length} 点 / ${trackDist(recPts.value).toFixed(2)} km`
      renderTracks()
    }, err => { recStatus.value = '⚠️ 定位失败：' + err.message; stopWatch() }, { enableHighAccuracy: true, maximumAge: 3000, timeout: 15000 })
  } else {
    stopWatch()
    if (recPts.value.length >= 2) {
      addTrack({ name: '实地记录 ' + new Date(recStart).toLocaleString('zh-CN', { month: '2-digit', day: '2-digit', hour: '2-digit', minute: '2-digit' }), src: 'record', pts: [...recPts.value] })
      recStatus.value = '✅ 轨迹已保存'
    } else recStatus.value = '轨迹点不足，未保存'
    recPts.value = []
  }
}
function stopWatch() { if (recWatch != null) { navigator.geolocation.clearWatch(recWatch); recWatch = null } recording.value = false }

function appToggleRecord() {
  if (!inApp) return
  if (!appRec.value) {
    let r = {}
    try { r = JSON.parse(window.AndroidBridge.startTrack() || '{}') } catch (e) { /* ignore */ }
    if (r.ok) {
      appRec.value = true
      appStatus.value = '🔴 App 记录中…（可熄屏、可切后台）'
      appTimer = setInterval(() => {
        try {
          const s = JSON.parse(window.AndroidBridge.getStatus() || '{}')
          if (s.recording) {
            appStatus.value = `🔴 App 记录中… ${s.points} 点 / ${(s.distanceM / 1000).toFixed(2)} km`
            if (s.last) { myPos.value = { lat: s.last.lat, lon: s.last.lon, acc: s.last.acc, alt: s.last.alt }; renderMe(); recPts.value = [[s.last.lat, s.last.lon]]; renderTracks() }
          }
        } catch (e) { /* ignore */ }
      }, 3000)
    } else ElMessage.error('启动原生记录失败：' + (r.msg || '未知原因'))
  } else {
    let r = {}
    try { r = JSON.parse(window.AndroidBridge.stopTrack() || '{}') } catch (e) { /* ignore */ }
    appRec.value = false
    if (appTimer) { clearInterval(appTimer); appTimer = null }
    const pts = (r.points || []).map(p => [p.lat, p.lon, p.alt ?? null, p.time || null])
    if (r.ok && pts.length >= 2) {
      addTrack({ name: 'App记录 ' + new Date().toLocaleString('zh-CN', { month: '2-digit', day: '2-digit', hour: '2-digit', minute: '2-digit' }), src: 'app', pts })
      appStatus.value = `✅ 轨迹已保存并同步（${pts.length} 点）`
    } else appStatus.value = '轨迹点不足，未保存'
  }
}

async function onTrackFiles(e) {
  const files = [...e.target.files]; e.target.value = ''
  let n = 0
  for (const f of files) {
    const ext = f.name.split('.').pop().toLowerCase()
    try {
      if (ext === 'gpx') { n += importGPX(await f.text(), f.name) ? 1 : 0 }
      else if (ext === 'kml') { n += importKML(await f.text(), f.name) ? 1 : 0 }
      else if (ext === 'csv' || ext === 'txt') { n += importCSV(await f.text(), f.name) ? 1 : 0 }
      else ElMessage.warning('不支持的格式：' + f.name)
    } catch (err) { ElMessage.error(f.name + ' 解析失败：' + err.message) }
  }
  if (n) ElMessage.success(`成功导入 ${n} 条轨迹`)
}
function importGPX(xml, name) {
  const doc = new DOMParser().parseFromString(xml, 'text/xml')
  if (doc.querySelector('parsererror')) throw new Error('GPX XML 格式错误')
  let pts = [...doc.getElementsByTagName('trkpt')].map(p => [+p.getAttribute('lat'), +p.getAttribute('lon'),
    p.getElementsByTagName('ele')[0]?.textContent ?? null, p.getElementsByTagName('time')[0]?.textContent ?? null])
  let src = 'gpx'
  if (pts.length < 2) { pts = [...doc.getElementsByTagName('rtept'), ...doc.getElementsByTagName('wpt')].map(p => [+p.getAttribute('lat'), +p.getAttribute('lon'), null, null]); src = 'gpx-wpt' }
  if (pts.length < 2) throw new Error('未找到轨迹点')
  addTrack({ name: name.replace(/\.gpx$/i, ''), src, pts }); return true
}
function importKML(xml, name) {
  const doc = new DOMParser().parseFromString(xml, 'text/xml')
  const c = doc.getElementsByTagName('coordinates')[0]
  if (!c) throw new Error('未找到 coordinates')
  const pts = c.textContent.trim().split(/\s+/).map(s => { const a = s.split(','); return [+a[1], +a[0], +a[2] || null, null] })
  if (pts.length < 2) throw new Error('轨迹点不足')
  addTrack({ name: name.replace(/\.kml$/i, ''), src: 'kml', pts }); return true
}
function importCSV(text, name) {
  const lines = text.split(/\r?\n/).filter(l => l.trim()); if (lines.length < 2) throw new Error('行数不足')
  const delim = /\t/.test(lines[0]) ? /\t/ : /,|，|;|；/.test(lines[0]) ? /[,，;；]/ : /\s+/
  const rows = lines.map(l => l.trim().split(delim))
  let ci = -1, li = -1
  rows[0].forEach((h, i) => { const k = h.toLowerCase()
    if (/lon|经度|^x$|lng|east/i.test(k)) ci = i
    if (/lat|纬度|^y$|north/i.test(k)) li = i })
  let data = rows
  if (ci > -1 && li > -1) { data = rows.slice(1) }
  else { const a = parseFloat(rows[0][0]), b = parseFloat(rows[0][1])
    if (isNaN(a) || isNaN(b)) throw new Error('无法识别坐标列')
    if (a > 80 && a < 100) { ci = 0; li = 1 } else { ci = 1; li = 0 } }
  const pts = data.map(r => { let lon = parseFloat(r[ci]), lat = parseFloat(r[li])
      if (lat > 80 && lon < 40) [lat, lon] = [lon, lat]; return [lat, lon, null, null] })
    .filter(p => !isNaN(p[0]) && !isNaN(p[1]) && Math.abs(p[0]) <= 90 && Math.abs(p[1]) <= 180)
  if (pts.length < 2) throw new Error('有效坐标点不足')
  addTrack({ name: name.replace(/\.(csv|txt)$/i, ''), src: 'csv', pts }); return true
}

function trackDist(pts) { let d = 0; for (let i = 1; i < pts.length; i++) d += hav(pts[i - 1], pts[i]); return d }
function trackDur(pts) { const t = pts.map(p => Date.parse(p[3])).filter(x => !isNaN(x))
  if (t.length < 2) return null; const m = Math.round((Math.max(...t) - Math.min(...t)) / 60000)
  return m >= 60 ? (m / 60).toFixed(1) + ' h' : m + ' min' }
function durationMin(pts) { const t = pts.map(p => Date.parse(p[3])).filter(x => !isNaN(x))
  if (t.length < 2) return null; return Math.round((Math.max(...t) - Math.min(...t)) / 60000) }
function trackGain(pts) { let g = 0; for (let i = 1; i < pts.length; i++) { const d = (+pts[i][2] || 0) - (+pts[i - 1][2] || 0); if (d > 0) g += d } return g }
function srcName(s) { return { record: '实地记录', app: 'App后台', gpx: 'GPX', 'gpx-wpt': 'GPX航点', kml: 'KML', csv: '坐标表' }[s] || '导入' }
function nowStr() { return new Date().toISOString().slice(0, 16).replace('T', ' ') }

function trackPayload(t) {
  return { name: t.name, src: t.src, points_json: JSON.stringify(t.pts),
    point_count: t.pts.length, distance_km: +trackDist(t.pts).toFixed(3),
    duration_min: durationMin(t.pts), gain_m: trackGain(t.pts) > 1 ? Math.round(trackGain(t.pts)) : null }
}
async function addTrack(o) {
  const rec = { id: uid(), serverId: null, name: o.name, src: o.src, pts: o.pts, time: nowStr() }
  tracks.value.unshift(rec)
  saveLocal(); renderTracks()
  try { const r = await fieldTrackApi.create(trackPayload(rec)); rec.serverId = r.id; saveLocal() } catch (e) { /* 离线保留本地 */ }
}
function delTrack(id) {
  const t = tracks.value.find(x => x.id === id)
  if (t?.serverId) fieldTrackApi.remove(t.serverId).catch(() => {})
  tracks.value = tracks.value.filter(x => x.id !== id)
  saveLocal(); renderTracks()
}
function focusTrack(i) {
  const t = tracks.value[i]; if (!t || !map) return
  follow.value = false
  map.fitBounds(L.latLngBounds(t.pts.map(p => [p[0], p[1]])), { padding: [40, 40] })
}
function exportGPX(i) {
  const t = tracks.value[i]; if (!t) return
  const esc = s => String(s || '').replace(/[&<>"]/g, c => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;' }[c]))
  const g = `<?xml version="1.0" encoding="UTF-8"?>\n<gpx version="1.1" creator="LhasaFieldApp" xmlns="http://www.topografix.com/GPX/1/1"><trk><name>${esc(t.name)}</name><trkseg>\n` +
    t.pts.map(p => `<trkpt lat="${p[0]}" lon="${p[1]}">${p[2] != null ? `<ele>${p[2]}</ele>` : ''}${p[3] ? `<time>${p[3]}</time>` : ''}</trkpt>`).join('\n') +
    `\n</trkseg></trk></gpx>`
  const a = document.createElement('a')
  a.href = URL.createObjectURL(new Blob([g], { type: 'application/gpx+xml' }))
  a.download = t.name.replace(/[\\/:*?"<>|]/g, '_') + '.gpx'
  a.click(); URL.revokeObjectURL(a.href)
  ElMessage.success('已导出 GPX')
}

function renderTracks() {
  if (!trackLayer) return
  trackLayer.clearLayers()
  tracks.value.forEach((t, i) => {
    if (t.pts.length < 2) return
    const col = TCOLORS[i % 6]
    const ll = t.pts.map(p => [p[0], p[1]])
    L.polyline(ll, { color: col, weight: 4, opacity: 0.85 }).addTo(trackLayer).bindPopup(`<b>${t.name}</b><br>${trackDist(t.pts).toFixed(2)} km · ${t.pts.length} 点`)
    L.circleMarker(ll[0], { radius: 5, fillColor: '#2E9E63', color: '#fff', weight: 2, fillOpacity: 1 }).addTo(trackLayer)
    L.circleMarker(ll[ll.length - 1], { radius: 5, fillColor: '#dc3535', color: '#fff', weight: 2, fillOpacity: 1 }).addTo(trackLayer)
  })
  if ((recording.value || appRec.value) && recPts.value.length > 1) {
    L.polyline(recPts.value.map(p => [p[0], p[1]]), { color: '#2470d8', weight: 3, dashArray: '7 5' }).addTo(trackLayer)
  }
}

/* ───────── 数据加载 ───────── */
async function loadPlots() {
  try { plots.value = await fieldOpsApi.plots(0); renderPlots() } catch (e) { /* ignore */ }
}
async function loadLayers() {
  try {
    layers.value = await fieldOpsApi.layers(0)
    activeLayerIds.value = layers.value.map(l => l.id)  // 默认全部打开
    renderVecLayers()
  } catch (e) { /* ignore */ }
}
async function loadSurveys() {
  try {
    const server = await fieldOpsApi.surveys(0)
    if (Array.isArray(server)) {
      const locals = surveys.value.filter(s => s._local)
      surveys.value = [...locals, ...server]
      saveLocal(); renderSurveys()
    }
  } catch (e) { /* ignore */ }
}
async function loadTracks() {
  try {
    const server = await fieldTrackApi.list()
    if (Array.isArray(server) && server.length) {
      tracks.value = server.map(s => ({ id: uid(), serverId: s.id, name: s.name, src: s.src,
        pts: JSON.parse(s.points_json || '[]'), time: (s.created_at || '').slice(0, 16).replace('T', ' ') }))
      saveLocal(); renderTracks()
    }
  } catch (e) { /* ignore */ }
}

onMounted(() => {
  initMap()
  startLocate()
  loadPlots(); loadLayers(); loadSurveys(); loadTracks()
  renderPhotos(); renderTracks()
  window.addEventListener('resize', onWinResize)
})
function onWinResize() { if (map) map.invalidateSize() }
onUnmounted(() => {
  window.removeEventListener('resize', onWinResize)
  stopWatch(); if (appTimer) clearInterval(appTimer)
  if (posWatch != null) navigator.geolocation.clearWatch(posWatch)
  if (map) { map.remove(); map = null }
})
</script>

<style scoped>
.mf-root { position: fixed; inset: 0; display: flex; flex-direction: column; background: #eef5f0; }
.mf-map { flex: 1; width: 100%; }

/* 顶栏 */
.mf-topbar { position: absolute; top: 0; left: 0; right: 0; z-index: 600; display: flex; align-items: center; gap: 8px;
  padding: calc(env(safe-area-inset-top, 0px) + 8px) 12px 8px;
  background: linear-gradient(180deg, rgba(255,255,255,0.92), rgba(255,255,255,0.75)); backdrop-filter: blur(10px);
  border-bottom: 1px solid rgba(15,60,40,0.08); }
.mf-title { font-size: 15px; font-weight: 700; color: #0f2e1f; white-space: nowrap; }
.mf-gps { flex: 1; font-size: 11px; color: #7a968a; overflow: hidden; text-overflow: ellipsis; white-space: nowrap; }
.mf-gps.ok { color: #2470d8; }
.mf-user { font-size: 12px; color: #0e9f6e; font-weight: 600; white-space: nowrap; }
.mf-usermenu { position: absolute; top: 100%; right: 10px; background: #fff; border-radius: 10px; padding: 10px 18px;
  font-size: 13px; color: #dc3535; box-shadow: 0 8px 24px rgba(46,125,82,0.18); border: 1px solid rgba(15,60,40,0.08); }

/* 浮动按钮 */
.mf-fabs { position: absolute; right: 10px; top: calc(env(safe-area-inset-top, 0px) + 56px); z-index: 600; display: flex; flex-direction: column; gap: 8px; }
.mf-fab { width: 42px; height: 42px; border-radius: 12px; border: 1px solid rgba(15,60,40,0.1); background: rgba(255,255,255,0.92);
  font-size: 18px; box-shadow: 0 4px 14px rgba(46,125,82,0.15); }
.mf-fab.active { background: #2470d8; }

/* 图层面板 */
.mf-layers { position: absolute; right: 60px; top: calc(env(safe-area-inset-top, 0px) + 56px); z-index: 600;
  background: rgba(255,255,255,0.96); border-radius: 14px; padding: 12px 14px; min-width: 180px; max-height: 60vh; overflow-y: auto;
  box-shadow: 0 8px 28px rgba(46,125,82,0.2); border: 1px solid rgba(15,60,40,0.08); }
.mf-layers-title { font-size: 11px; font-weight: 700; color: #7a968a; margin: 8px 0 4px; }
.mf-layers-title:first-child { margin-top: 0; }
.mf-lrow { display: flex; align-items: center; gap: 6px; font-size: 13px; color: #1e3a2f; padding: 5px 0; }

/* 样地卡片 */
.mf-plotcard { position: absolute; left: 10px; right: 10px; bottom: 76px; z-index: 590;
  background: rgba(255,255,255,0.96); border-radius: 16px; padding: 12px 14px;
  box-shadow: 0 10px 30px rgba(46,125,82,0.22); border: 1px solid rgba(15,60,40,0.08); }
.mf-pc-head { display: flex; align-items: center; gap: 6px; font-size: 15px; color: #0f2e1f; }
.mf-pc-status { margin-left: auto; font-size: 11px; padding: 2px 8px; border-radius: 8px; }
.mf-pc-status.done { background: rgba(46,158,99,0.12); color: #2E9E63; }
.mf-pc-status.pending { background: rgba(232,135,58,0.12); color: #c77f0a; }
.mf-pc-x { border: none; background: none; font-size: 14px; color: #7a968a; padding: 4px; }
.mf-pc-body { display: flex; flex-direction: column; gap: 3px; font-size: 12px; color: #3d5a4c; margin: 6px 0; }
.mf-pc-note { color: #7a968a; }
.mf-pc-acts { display: flex; gap: 8px; }

/* 最近样地 */
.mf-near { position: absolute; left: 10px; bottom: 76px; z-index: 590; display: flex; flex-direction: column; gap: 6px; }
.mf-near-item { display: flex; align-items: center; gap: 8px; background: rgba(255,255,255,0.92); border-radius: 12px;
  padding: 7px 12px; box-shadow: 0 4px 14px rgba(46,125,82,0.14); border: 1px solid rgba(15,60,40,0.07); }
.mf-near-code { font-size: 13px; font-weight: 700; color: #c77f0a; }
.mf-near-code.done { color: #2E9E63; }
.mf-near-dist { font-size: 12px; color: #3d5a4c; }

/* 底部抽屉 */
.mf-sheet { position: absolute; left: 0; right: 0; bottom: 62px; z-index: 580; max-height: 52vh;
  background: rgba(255,255,255,0.95); backdrop-filter: blur(12px);
  border-radius: 18px 18px 0 0; border-top: 1px solid rgba(15,60,40,0.08);
  box-shadow: 0 -8px 30px rgba(46,125,82,0.15); overflow-y: auto; -webkit-overflow-scrolling: touch; }
.mf-pane { padding: 14px 14px 18px; }
.mf-tip { font-size: 11px; color: #7a968a; line-height: 1.6; margin: 8px 2px 10px; }
.mf-empty { text-align: center; color: #9ab5a8; font-size: 12px; padding: 20px; }

/* 按钮 */
.mf-btn { border: 1px solid rgba(15,60,40,0.12); background: rgba(255,255,255,0.85); color: #1e3a2f;
  border-radius: 12px; padding: 9px 14px; font-size: 14px; font-weight: 600; }
.mf-btn.primary { background: linear-gradient(135deg, #10b981, #0e9f6e); color: #fff; border: none;
  box-shadow: 0 4px 14px rgba(14,159,110,0.3); }
.mf-btn.danger { background: linear-gradient(135deg, #ef6a5e, #dc3535); color: #fff; border: none; }
.mf-btn.big { width: 100%; padding: 13px; font-size: 15px; }
.mf-btn.small { padding: 6px 10px; font-size: 12px; flex: 1; }
.mf-btn:disabled { opacity: 0.6; }
.mf-cam-btns { display: flex; gap: 10px; }
.mf-cam-btns .mf-btn { flex: 1; }
.mf-rec { font-size: 12px; color: #5a7a6a; margin: 8px 2px; }
.mf-rec.live { color: #dc3535; font-weight: 600; }

/* 列表项 */
.mf-list { display: flex; flex-direction: column; gap: 8px; margin-top: 10px; }
.mf-item { display: flex; gap: 10px; padding: 8px; border-radius: 12px; background: rgba(255,255,255,0.7); border: 1px solid rgba(15,60,40,0.06); }
.mf-thumb { width: 58px; height: 58px; border-radius: 10px; overflow: hidden; flex-shrink: 0; display: flex; align-items: center;
  justify-content: center; background: #e6efe9; font-size: 22px; }
.mf-thumb img { width: 100%; height: 100%; object-fit: cover; }
.mf-thumb.sv { background: rgba(46,158,99,0.12); }
.mf-item-body { flex: 1; min-width: 0; }
.mf-item-name { font-size: 13px; font-weight: 700; color: #0f2e1f; }
.mf-conf { color: #0e9f6e; font-size: 11px; }
.mf-item-sub { font-size: 11px; color: #5a7a6a; line-height: 1.7; }
.mf-item-feat { font-size: 11px; color: #0d9862; background: rgba(16,185,129,0.08); border-radius: 8px; padding: 3px 8px; margin-top: 3px; line-height: 1.5; }
.mf-item-acts { display: flex; gap: 4px; margin-top: 5px; flex-wrap: wrap; }
.mf-mini { border: 1px solid rgba(15,60,40,0.1); background: rgba(255,255,255,0.8); border-radius: 8px;
  padding: 3px 8px; font-size: 11px; color: #2470d8; }
.mf-mini.danger { color: #dc3535; }
.mf-edit { display: flex; flex-direction: column; gap: 6px; margin-top: 6px; }

/* 表单 */
.mf-form { display: flex; flex-direction: column; gap: 8px; }
.mf-form-row { display: flex; gap: 8px; }
.mf-form-row .mf-input { flex: 1; }
.mf-input { width: 100%; border: 1px solid rgba(15,60,40,0.12); border-radius: 10px; padding: 10px 12px;
  font-size: 14px; background: rgba(255,255,255,0.85); color: #0f2e1f; font-family: inherit; }
.mf-input:focus { outline: 2px solid rgba(14,159,110,0.35); }
.mf-form-loc { font-size: 11px; color: #5a7a6a; display: flex; align-items: center; gap: 10px; flex-wrap: wrap; }
.mf-form-photo { color: #0e9f6e; display: flex; align-items: center; gap: 4px; }

/* 标签栏 */
.mf-tabbar { position: absolute; left: 0; right: 0; bottom: 0; z-index: 600; height: calc(62px + env(safe-area-inset-bottom, 0px));
  padding-bottom: env(safe-area-inset-bottom, 0px);
  display: flex; background: rgba(255,255,255,0.96); backdrop-filter: blur(12px); border-top: 1px solid rgba(15,60,40,0.08); }
.mf-tab { flex: 1; border: none; background: none; display: flex; flex-direction: column; align-items: center; justify-content: center;
  gap: 2px; font-size: 10px; color: #7a968a; }
.mf-tab-ico { font-size: 20px; }
.mf-tab.on { color: #0e9f6e; font-weight: 700; }

/* 全屏预览 */
.mf-preview { position: fixed; inset: 0; z-index: 900; background: rgba(0,0,0,0.9); display: flex; align-items: center; justify-content: center; }
.mf-preview img { max-width: 96vw; max-height: 92vh; border-radius: 8px; }

:deep(.mf-plot-tip) { background: rgba(255,255,255,0.92) !important; border: 1px solid rgba(15,60,40,0.1) !important;
  color: #1e3a2f !important; font-size: 11px; font-weight: 600; border-radius: 6px !important; box-shadow: 0 2px 8px rgba(46,125,82,0.12) !important; }
:deep(.leaflet-popup-content-wrapper) { background: rgba(255,255,255,0.97) !important; border-radius: 10px !important; color: #1e3a2f !important; }
:deep(.leaflet-popup-tip) { background: rgba(255,255,255,0.97) !important; }
:deep(.leaflet-container) { background: #dfeae3 !important; }
</style>
