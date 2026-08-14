<template>
  <div class="field-page">
    <div class="page-title">野外科考采集</div>
    <div class="page-subtitle">手机拍照自动解析拍摄位置 · 物种与形态注释 · 轨迹实时记录 · 兼容两步路 / 行者 GPX、KML、经纬度坐标表导入</div>

    <div class="field-layout">
      <!-- 左侧操作面板 -->
      <div class="field-panel">
        <el-tabs v-model="tab" class="field-tabs">
          <!-- ════ 照片 ════ -->
          <el-tab-pane label="科考照片" name="photos">
            <div class="proj-row">
              <el-select v-model="projectId" placeholder="同步到项目（可选）" size="small" clearable style="flex:1">
                <el-option v-for="p in projects" :key="p.id" :label="p.name" :value="p.id" />
              </el-select>
            </div>
            <div class="up-actions">
              <el-button type="primary" :icon="Camera" class="up-btn" @click="camInput.click()">拍照上传</el-button>
              <el-button :icon="FolderOpened" class="up-btn ghost" @click="photoInput.click()">相册选择</el-button>
              <el-button :icon="VideoCamera" class="up-btn ghost" @click="vidInput.click()">录像</el-button>
            </div>
            <input ref="camInputRef" type="file" accept="image/*" capture="environment" multiple style="display:none" @change="e=>onPhotos(e,true)" />
            <input ref="photoInputRef" type="file" accept="image/jpeg,image/jpg,image/png,image/heic,image/heif,.heic,.heif,video/*,.mp4,.mov,.3gp" multiple style="display:none" @change="e=>onPhotos(e,false)" />
            <input ref="vidInputRef" type="file" accept="video/*" capture="environment" style="display:none" @change="onVideos" />
            <div class="up-tip">支持先拍照/录像后上传；JPG 自动解析 EXIF GPS 经纬度、海拔与拍摄时间（iPhone 建议「设置-相机-格式」选"兼容性最佳"）；从微信/QQ 保存的照片请用「原图」否则定位信息会被剥离；无定位的照片可点「📌 补标」在地图上选点；选择项目后可同步至「巡检照片」媒体库</div>

            <div class="photo-list">
              <div v-if="!photos.length" class="empty-tip">暂无科考照片</div>
              <div v-for="p in photos" :key="p.id" class="fitem">
                <div class="fthumb" @click="p.isVideo && playVid(p)">
                  <img v-if="p.thumb" :src="p.thumb" /><span v-else>{{ p.isVideo ? '🎬' : '🌄' }}</span>
                  <span v-if="p.isVideo" class="vplay">▶{{ p.duration ? ' ' + fmtDur(p.duration) : '' }}</span>
                </div>
                <div class="fbody">
                  <div class="fname">{{ p.isVideo ? '🎬 ' : '' }}{{ p.name }}</div>
                  <div class="fgeo">
                    <template v-if="p.lat != null">📍 {{ p.lat.toFixed(6) }}, {{ p.lon.toFixed(6) }}<template v-if="p.alt"> · 海拔 {{ p.alt }} m</template></template>
                    <template v-else-if="p.noGpsReason === 'heic'">📍 未定位（HEIC 格式，请转 JPG 或改用原图）</template>
                    <template v-else-if="p.noGpsReason === 'video'">📍 未定位（录像不含 EXIF，可点「补标」选点）</template>
                    <template v-else-if="p.noGpsReason === 'fmt'">📍 未定位（非 JPG 格式，无法读取 EXIF）</template>
                    <template v-else>📍 未定位（EXIF 无 GPS，可能被转存剥离或相机未开定位）</template>
                    <br />🕐 {{ p.time || '时间未知' }}
                    <el-tag v-if="p.synced" size="small" type="success" effect="plain" style="margin-left:4px">已同步</el-tag>
                  </div>
                  <div v-if="p.species || p.note || p.height" class="fnote">
                    {{ [p.species && '🌿 ' + p.species, p.height && `高 ${p.height} m`, p.dbh && `胸径/丛幅 ${p.dbh} cm`, p.cover && `盖度 ${p.cover}%`, p.note && '📝 ' + p.note].filter(Boolean).join(' · ') }}
                  </div>
                  <div class="facts">
                    <el-button size="small" text type="primary" @click="p._edit = !p._edit">✏️ 注释</el-button>
                    <el-button size="small" text :type="pickTarget?.id === p.id ? 'warning' : 'primary'" @click="startPick(p)">📌 {{ p.lat != null ? '改标' : '补标' }}</el-button>
                    <el-button v-if="p.lat != null" size="small" text @click="flyTo(p.lat, p.lon)">🗺️ 定位</el-button>
                    <el-button v-if="p.isVideo" size="small" text type="success" @click="playVid(p)">▶ 播放</el-button>
                    <el-button size="small" text type="danger" @click="delPhoto(p.id)">删除</el-button>
                  </div>
                  <div v-if="p._edit" class="anno-form">
                    <el-input v-model="p.species" size="small" placeholder="物种（如 油松 / 江孜沙棘）" />
                    <div class="arow">
                      <el-input v-model="p.height" size="small" type="number" placeholder="树高 m" />
                      <el-input v-model="p.dbh" size="small" type="number" placeholder="胸径/丛幅 cm" />
                    </div>
                    <div class="arow">
                      <el-input v-model="p.cover" size="small" type="number" placeholder="盖度 %" />
                      <el-button size="small" type="primary" @click="saveAnno(p)">💾 保存</el-button>
                    </div>
                    <el-input v-model="p.note" size="small" placeholder="备注（长势、病虫害、坡位等）" />
                  </div>
                </div>
              </div>
            </div>
          </el-tab-pane>

          <!-- ════ 轨迹 ════ -->
          <el-tab-pane label="考察轨迹" name="tracks">
            <template v-if="inApp">
              <el-button :type="appRec ? 'danger' : 'success'" :icon="Position" style="width:100%" @click="appToggleRecord">
                {{ appRec ? '⏸ 结束并保存轨迹（App）' : '● 开始记录轨迹（App 后台模式）' }}
              </el-button>
              <div class="rec-status" :class="{ live: appRec }">{{ appStatus }}</div>
              <el-divider content-position="left">浏览器定位（备用）</el-divider>
            </template>
            <el-button :type="recording ? 'danger' : 'primary'" :icon="Position" style="width:100%" @click="toggleRecord">
              {{ recording ? '⏸ 结束并保存轨迹' : '● 开始记录轨迹' }}
            </el-button>
            <div class="rec-status" :class="{ live: recording }">{{ recStatus }}</div>

            <el-divider content-position="left">导入轨迹 / 点位</el-divider>
            <el-button :icon="Upload" style="width:100%" class="up-btn ghost" @click="trackInput.click()">导入 GPX / KML / 坐标表 / 照片</el-button>
            <input ref="trackInputRef" type="file" accept=".gpx,.kml,.csv,.txt,.jpg,.jpeg" multiple style="display:none" @change="onTrackFiles" />
            <div class="up-tip">兼容两步路、行者、六只脚导出的 GPX；坐标表支持 lon/lat、经度/纬度、x/y 表头或无表头自动识别</div>

            <div class="track-list">
              <div v-if="!tracks.length" class="empty-tip">暂无轨迹</div>
              <div v-for="(t, i) in tracks" :key="t.id" class="fitem">
                <div class="fthumb trk" :style="{ background: TCOLORS[i % 6] + '22', color: TCOLORS[i % 6] }">🥾</div>
                <div class="fbody">
                  <div class="fname">{{ t.name }}</div>
                  <div class="fgeo">
                    📏 {{ trackDist(t.pts).toFixed(2) }} km · {{ t.pts.length }} 点
                    <template v-if="trackDur(t.pts)"> · ⏱ {{ trackDur(t.pts) }}</template>
                    <template v-if="trackGain(t.pts) > 1"> · ↗ {{ Math.round(trackGain(t.pts)) }} m</template>
                    <br />🕐 {{ t.time }} <el-tag size="small" effect="plain" style="margin-left:4px">{{ srcName(t.src) }}</el-tag>
                    <el-tag v-if="t.serverId" size="small" type="success" effect="plain" style="margin-left:4px">云端</el-tag>
                  </div>
                  <div class="facts">
                    <el-button size="small" text type="primary" @click="focusTrack(i)">🗺️ 图上查看</el-button>
                    <el-button size="small" text @click="exportGPX(i)">⬇ 导出 GPX</el-button>
                    <el-button size="small" text type="danger" @click="delTrack(t.id)">删除</el-button>
                  </div>
                </div>
              </div>
            </div>
          </el-tab-pane>
        </el-tabs>

        <div class="kpi-row">
          <div class="kpi"><b>{{ photos.length }}</b><span>照片</span></div>
          <div class="kpi"><b>{{ photosWithGps }}</b><span>已定位</span></div>
          <div class="kpi"><b>{{ tracks.length }}</b><span>轨迹</span></div>
          <div class="kpi"><b>{{ totalKm }}</b><span>总里程 km</span></div>
        </div>
      </div>

      <!-- 右侧地图 -->
      <div class="field-map-wrap">
        <div ref="mapEl" class="field-map"></div>
        <div v-if="pickTarget" class="pick-banner">
          <span>📌 正在为 <b>{{ pickTarget.name }}</b> 选点：点击地图放置拍摄位置</span>
          <el-button size="small" text type="danger" @click="cancelPick">取消</el-button>
        </div>
        <div class="map-legend">
          <span><i class="lg-line"></i>轨迹</span>
          <span><i class="lg-dot"></i>照片点位</span>
        </div>
      </div>
    </div>

    <!-- 录像播放弹窗 -->
    <el-dialog v-model="playVisible" :title="playName" width="720px" top="6vh" destroy-on-close>
      <video v-if="playUrl" :src="playUrl" controls autoplay style="width:100%;max-height:62vh;border-radius:8px;background:#000" />
      <div v-else class="empty-tip">该录像文件不在本机会话中（页面刷新后本地文件句柄失效）；已同步的录像请前往「巡检照片」媒体库播放</div>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, onUnmounted } from 'vue'
import L from 'leaflet'
import 'leaflet/dist/leaflet.css'
import { ElMessage } from 'element-plus'
import { Camera, FolderOpened, Upload, Position, VideoCamera } from '@element-plus/icons-vue'
import { projectApi, patrolPhotoApi, fieldTrackApi } from '../api.js'

/* ───────── 本地存储 ───────── */
const FKEY = 'lhasa_field_v1'
const photos = ref([])
const tracks = ref([])
try {
  const s = localStorage.getItem(FKEY)
  if (s) { const d = JSON.parse(s); photos.value = d.photos || []; tracks.value = d.tracks || [] }
} catch (e) { /* ignore */ }
function saveField() {
  try { localStorage.setItem(FKEY, JSON.stringify({ photos: photos.value, tracks: tracks.value })) }
  catch (e) { ElMessage.warning('本地存储已满，建议删除部分历史照片') }
}
const uid = () => 'f' + Date.now().toString(36) + Math.random().toString(36).slice(2, 6)

const TCOLORS = ['#2E9E63', '#2470d8', '#c77f0a', '#0b8fa8', '#7a4fd0', '#dc3535']
const tab = ref('photos')
const projects = ref([])
const projectId = ref(null)
const camInputRef = ref(null); const photoInputRef = ref(null); const trackInputRef = ref(null); const vidInputRef = ref(null)
const camInput = { click: () => camInputRef.value?.click() }
const photoInput = { click: () => photoInputRef.value?.click() }
const trackInput = { click: () => trackInputRef.value?.click() }
const vidInput = { click: () => vidInputRef.value?.click() }

/* 录像本地播放（对象 URL 仅本次会话有效） */
const vidUrls = {}
const playVisible = ref(false); const playUrl = ref(''); const playName = ref('')
function playVid(p) {
  playName.value = p.name
  playUrl.value = vidUrls[p.id] || ''
  playVisible.value = true
}
const fmtDur = s => { s = Math.round(s); return `${Math.floor(s / 60)}:${String(s % 60).padStart(2, '0')}` }

/* 地图选点补标 */
const pickTarget = ref(null)
let pickMarker = null
function startPick(p) {
  pickTarget.value = p
  ElMessage.info('请在右侧地图上点击该照片的实际拍摄位置')
}
function cancelPick() {
  pickTarget.value = null
  if (pickMarker && map) { map.removeLayer(pickMarker); pickMarker = null }
}
async function onMapPick(latlng) {
  const p = pickTarget.value
  if (!p) return
  p.lat = +latlng.lat.toFixed(7); p.lon = +latlng.lng.toFixed(7)
  p.noGpsReason = ''
  if (pickMarker && map) map.removeLayer(pickMarker)
  pickMarker = L.circleMarker([p.lat, p.lon], { radius: 9, fillColor: '#2470d8', color: '#fff', weight: 2, fillOpacity: 0.9 }).addTo(map)
  setTimeout(() => { if (pickMarker && map) { map.removeLayer(pickMarker); pickMarker = null } }, 1200)
  pickTarget.value = null
  saveField(); renderFieldMap()
  if (p.synced && p.serverId) {
    try { await patrolPhotoApi.updateLocation(p.serverId, { lon: p.lon, lat: p.lat, altitude: p.alt }) } catch (e) { /* ignore */ }
  }
  ElMessage.success(`已补标：${p.lat.toFixed(6)}, ${p.lon.toFixed(6)}`)
}

const photosWithGps = computed(() => photos.value.filter(p => p.lat != null).length)
const totalKm = computed(() => tracks.value.reduce((s, t) => s + trackDist(t.pts), 0).toFixed(1))

/* ───────── EXIF GPS 解析（自研轻量解析器，离线可用） ───────── */
function parseExifGPS(buf) {
  const dv = new DataView(buf)
  if (dv.getUint16(0) !== 0xFFD8) return null
  let off = 2
  while (off < dv.byteLength - 4) {
    if (dv.getUint8(off) !== 0xFF) break
    const marker = dv.getUint8(off + 1)
    if (marker === 0xE1) {
      // 非 Exif 的 APP1（如 XMP）跳过该段继续扫描，而不是直接放弃
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
      let time = null
      if (ifd0[0x8769]) { const ex = readIFD(u32(ifd0[0x8769].o))
        if (ex[0x9003]) { const s = str(ex[0x9003]); time = s.replace(/^(\d{4}):(\d{2}):(\d{2})/, '$1-$2-$3') } }
      return { lat, lon, alt, time }
    }
    if (marker === 0xDA || marker === 0xD9) break
    off += 2 + dv.getUint16(off + 2)
  }
  return null
}

/* 识别图片格式：jpeg / heic / png / other，用于诊断未定位原因 */
function detectImgFmt(buf) {
  const dv = new DataView(buf)
  if (dv.byteLength < 12) return 'other'
  if (dv.getUint16(0) === 0xFFD8) return 'jpeg'
  if (dv.getUint32(0) === 0x89504E47) return 'png'
  // HEIC/HEIF：ISO BMFF，第 4-8 字节为 'ftyp'，主品牌 heic/heix/hevc/mif1 等
  if (dv.getUint32(4) === 0x66747970) {
    const brand = String.fromCharCode(dv.getUint8(8), dv.getUint8(9), dv.getUint8(10), dv.getUint8(11))
    if (/^(heic|heix|hevc|hevx|mif1|msf1|heis|hevs)/i.test(brand)) return 'heic'
  }
  return 'other'
}

function makeThumb(f) {
  return new Promise(res => {
    const img = new Image(), url = URL.createObjectURL(f)
    img.onload = () => { const s = 180 / Math.max(img.width, img.height), cv = document.createElement('canvas')
      cv.width = img.width * s; cv.height = img.height * s
      cv.getContext('2d').drawImage(img, 0, 0, cv.width, cv.height)
      URL.revokeObjectURL(url); res(cv.toDataURL('image/jpeg', .72)) }
    img.onerror = () => { URL.revokeObjectURL(url); res('') }
    img.src = url
  })
}

/* ───────── 照片采集 ───────── */
async function onPhotos(e) {
  const files = [...e.target.files]; e.target.value = ''
  const vids = files.filter(f => /^video\/|\.(mp4|mov|m4v|3gp|avi|mkv|webm)$/i.test(f.type + f.name))
  const list = files.filter(f => !vids.includes(f) && /image|\.jpe?g$|\.heic|\.heif/i.test(f.type + f.name))
  if (vids.length) await handleVideos(vids)
  if (!list.length) { if (!vids.length) ElMessage.warning('请选择照片或录像文件'); return }
  let ok = 0, synced = 0, heicN = 0, noGpsN = 0
  for (const f of list) {
    const buf = await f.arrayBuffer()
    const fmt = detectImgFmt(buf)
    let meta = null
    if (fmt === 'jpeg') { try { meta = parseExifGPS(buf) } catch (err) { /* ignore */ } }
    const noGpsReason = meta ? '' : (fmt === 'heic' ? 'heic' : fmt === 'jpeg' ? 'nogps' : 'fmt')
    if (noGpsReason === 'heic') heicN++
    else if (noGpsReason) noGpsN++
    const thumb = await makeThumb(f)
    const rec = { id: uid(), name: f.name,
      time: meta?.time || new Date(f.lastModified).toISOString().replace('T', ' ').slice(0, 16),
      lat: meta?.lat ?? null, lon: meta?.lon ?? null, alt: meta?.alt ? Math.round(meta.alt) : null,
      noGpsReason,
      species: '', height: '', dbh: '', cover: '', note: '', thumb, synced: false, serverId: null, _edit: false }
    if (meta) ok++
    if (projectId.value) {
      try {
        const fd = new FormData()
        fd.append('project_id', projectId.value)
        fd.append('file', f)
        const res = await fetch('/api/v1/patrol-photos/upload', {
          method: 'POST', body: fd,
          headers: { Authorization: `Bearer ${localStorage.getItem('lasa_token') || ''}` },
        })
        if (res.ok) { const j = await res.json(); rec.synced = true; rec.serverId = j.id || j.photo_id || null; synced++
          // 前端未解析出 GPS 时，以服务端解析结果回填（服务端 Pillow 解析更全面）
          if (rec.lat == null && j.lat != null) { rec.lat = j.lat; rec.lon = j.lon; rec.alt = j.altitude ? Math.round(j.altitude) : null; rec.noGpsReason = '' }
        }
      } catch (err) { /* ignore */ }
    }
    photos.value.unshift(rec)
  }
  saveField(); renderFieldMap()
  let msg = `已导入 ${list.length} 张照片，${ok} 张解析出拍摄位置${projectId.value ? `，${synced} 张同步至平台` : ''}`
  if (heicN) msg += `；${heicN} 张为 HEIC 格式无法读取定位，请在 iPhone「设置-相机-格式」改为"兼容性最佳"或转 JPG`
  if (noGpsN) msg += `；${noGpsN} 张无 GPS 信息（可能经微信/QQ 转存被剥离，或未开启相机定位），请改用原图上传`
  if (heicN || noGpsN) ElMessage.warning(msg); else ElMessage.success(msg)
}

/* ───────── 录像采集 ───────── */
function onVideos(e) {
  const files = [...e.target.files]; e.target.value = ''
  if (files.length) handleVideos(files)
}

function makeVideoMeta(f) {
  return new Promise(res => {
    const url = URL.createObjectURL(f)
    const v = document.createElement('video')
    v.muted = true; v.playsInline = true; v.preload = 'metadata'
    v.onloadeddata = () => { v.currentTime = Math.min(0.5, (v.duration || 1) / 2) }
    v.onseeked = () => {
      const s = 180 / Math.max(v.videoWidth || 180, v.videoHeight || 180)
      const cv = document.createElement('canvas')
      cv.width = (v.videoWidth || 180) * s; cv.height = (v.videoHeight || 135) * s
      try { cv.getContext('2d').drawImage(v, 0, 0, cv.width, cv.height) } catch (err) { /* ignore */ }
      res({ thumb: cv.toDataURL('image/jpeg', .7), duration: v.duration || null, url })
    }
    v.onerror = () => res({ thumb: '', duration: null, url })
    setTimeout(() => res({ thumb: '', duration: v.duration || null, url }), 4000)
    v.src = url
  })
}

async function handleVideos(list) {
  let synced = 0
  for (const f of list) {
    const meta = await makeVideoMeta(f)
    const rec = { id: uid(), name: f.name, isVideo: true,
      time: new Date(f.lastModified).toISOString().replace('T', ' ').slice(0, 16),
      lat: null, lon: null, alt: null, noGpsReason: 'video',
      duration: meta.duration ? Math.round(meta.duration) : null,
      species: '', height: '', dbh: '', cover: '', note: '', thumb: meta.thumb, synced: false, serverId: null, _edit: false }
    vidUrls[rec.id] = meta.url
    if (projectId.value) {
      try {
        const fd = new FormData()
        fd.append('project_id', projectId.value)
        if (rec.duration) fd.append('duration', rec.duration)
        fd.append('file', f)
        const res = await fetch('/api/v1/patrol-photos/upload', {
          method: 'POST', body: fd,
          headers: { Authorization: `Bearer ${localStorage.getItem('lasa_token') || ''}` },
        })
        if (res.ok) { const j = await res.json(); rec.synced = true; rec.serverId = j.id || null; synced++ }
      } catch (err) { /* ignore */ }
    }
    photos.value.unshift(rec)
  }
  saveField(); renderFieldMap()
  ElMessage.success(`已导入 ${list.length} 段录像${projectId.value ? `，${synced} 段同步至平台媒体库` : ''}；录像不含定位，可用「📌 补标」在地图上选点`)
}

async function saveAnno(p) {
  p._edit = false
  saveField()
  if (p.synced && p.serverId) {
    try {
      const note = ['科考注释', p.species && `物种:${p.species}`, p.height && `树高:${p.height}m`, p.dbh && `胸径/丛幅:${p.dbh}cm`, p.cover && `盖度:${p.cover}%`, p.note && `备注:${p.note}`].filter(Boolean).join('；')
      await patrolPhotoApi.updateDefect(p.serverId, { defect_type: '', defect_desc: '', defect_confidence: 1, inspector_note: note })
    } catch (e) { /* ignore */ }
  }
  ElMessage.success('注释已保存')
}
function delPhoto(id) {
  photos.value = photos.value.filter(x => x.id !== id)
  saveField(); renderFieldMap()
}
function flyTo(lat, lon) { if (map) map.flyTo([lat, lon], 16, { duration: 0.8 }) }

/* ───────── 轨迹：实时记录 ───────── */
let recWatch = null
const recPts = ref([])
const recording = ref(false)
const recStatus = ref('点击开始后，本页将调用手机 GPS 连续记录考察轨迹')
let recStart = 0

function toggleRecord() {
  if (!recording.value) {
    if (!navigator.geolocation) { recStatus.value = '⚠️ 当前浏览器不支持定位；请改用「导入轨迹文件」'; return }
    recPts.value = []; recStart = Date.now(); recording.value = true
    recWatch = navigator.geolocation.watchPosition(pos => {
      recPts.value.push([pos.coords.latitude, pos.coords.longitude, pos.coords.altitude || null, new Date().toISOString()])
      recStatus.value = `🔴 记录中… 已采 ${recPts.value.length} 点，里程 ${trackDist(recPts.value).toFixed(2)} km`
      renderFieldMap()
    }, err => {
      recStatus.value = '⚠️ 定位失败：' + err.message + '（http 站点浏览器可能限制定位，可用两步路/行者记录后导入 GPX）'
      stopWatch()
    }, { enableHighAccuracy: true, maximumAge: 3000, timeout: 15000 })
  } else {
    stopWatch()
    if (recPts.value.length >= 2) {
      addTrack({ name: '实地记录 ' + new Date(recStart).toLocaleString('zh-CN', { month: '2-digit', day: '2-digit', hour: '2-digit', minute: '2-digit' }), src: 'record', pts: [...recPts.value] })
      recStatus.value = '✅ 轨迹已保存'
    } else recStatus.value = '轨迹点不足（<2），未保存'
    recPts.value = []
  }
}
function stopWatch() {
  if (recWatch != null) { navigator.geolocation.clearWatch(recWatch); recWatch = null }
  recording.value = false
}

/* ───────── App 原生轨迹（Android 壳内可用，后台防熄屏） ───────── */
const inApp = typeof window.AndroidBridge !== 'undefined'
const appRec = ref(false)
const appStatus = ref('App 后台模式：熄屏仍持续记录，由原生 GPS 服务供点')
let appTimer = null
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
            appStatus.value = `🔴 App 记录中… 已采 ${s.points} 点，约 ${(s.distanceM / 1000).toFixed(2)} km`
            if (s.last) { recPts.value = [[s.last.lat, s.last.lon, s.last.alt || null, s.last.time]]; renderFieldMap() }
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
    } else appStatus.value = '轨迹点不足（<2），未保存'
  }
}

/* ───────── 轨迹：导入解析 ───────── */
async function onTrackFiles(e) {
  const files = [...e.target.files]; e.target.value = ''
  if (!files.length) return
  let n = 0
  for (const f of files) {
    const ext = f.name.split('.').pop().toLowerCase()
    try {
      if (ext === 'gpx') { n += importGPX(await f.text(), f.name) ? 1 : 0 }
      else if (ext === 'kml') { n += importKML(await f.text(), f.name) ? 1 : 0 }
      else if (ext === 'csv' || ext === 'txt') { n += importCSV(await f.text(), f.name) ? 1 : 0 }
      else if (['jpg', 'jpeg'].includes(ext)) { const m = parseExifGPS(await f.arrayBuffer())
        if (m) n += importPhotoPoint(f.name, m) ? 1 : 0; else ElMessage.warning(`照片 ${f.name} 无 GPS 信息，已跳过`) }
      else ElMessage.warning('不支持的格式：' + f.name)
    } catch (err) { ElMessage.error(f.name + ' 解析失败：' + err.message) }
  }
  if (n) ElMessage.success(`成功导入 ${n} 条轨迹/点位`)
}
function importGPX(xml, name) {
  const doc = new DOMParser().parseFromString(xml, 'text/xml')
  if (doc.querySelector('parsererror')) throw new Error('GPX XML 格式错误')
  let pts = [...doc.getElementsByTagName('trkpt')].map(p => [+p.getAttribute('lat'), +p.getAttribute('lon'),
    p.getElementsByTagName('ele')[0]?.textContent ?? null, p.getElementsByTagName('time')[0]?.textContent ?? null])
  let src = 'gpx'
  if (pts.length < 2) {
    pts = [...doc.getElementsByTagName('rtept'), ...doc.getElementsByTagName('wpt')]
      .map(p => [+p.getAttribute('lat'), +p.getAttribute('lon'), null, null]); src = 'gpx-wpt'
  }
  if (pts.length < 2) throw new Error('未找到轨迹点（trkpt/rtept/wpt）')
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
  else {
    const a = parseFloat(rows[0][0]), b = parseFloat(rows[0][1])
    if (isNaN(a) || isNaN(b)) throw new Error('无法识别坐标列')
    if (a > 80 && a < 100) { ci = 0; li = 1 } else { ci = 1; li = 0 }
  }
  const pts = data.map(r => { let lon = parseFloat(r[ci]), lat = parseFloat(r[li])
      if (lat > 80 && lon < 40) [lat, lon] = [lon, lat]; return [lat, lon, null, null] })
    .filter(p => !isNaN(p[0]) && !isNaN(p[1]) && Math.abs(p[0]) <= 90 && Math.abs(p[1]) <= 180)
  if (pts.length < 2) throw new Error('有效坐标点不足')
  addTrack({ name: name.replace(/\.(csv|txt)$/i, ''), src: 'csv', pts }); return true
}
function importPhotoPoint(name, m) {
  let tr = tracks.value.find(t => t.src === 'photos')
  if (!tr) { tr = { id: uid(), serverId: null, name: '照片点位轨迹（EXIF 批量）', src: 'photos', pts: [], time: nowStr() }; tracks.value.unshift(tr) }
  tr.pts.push([m.lat, m.lon, m.alt, m.time])
  tr.pts.sort((a, b) => String(a[3]).localeCompare(String(b[3])))
  saveField(); renderFieldMap(); resyncTrack(tr); return true
}

/* ───────── 轨迹统计 ───────── */
function trackDist(pts) { let d = 0; for (let i = 1; i < pts.length; i++) d += hav(pts[i - 1], pts[i]); return d }
function hav(a, b) { const R = 6371, r = Math.PI / 180
  const h = Math.sin((b[0] - a[0]) * r / 2) ** 2 + Math.cos(a[0] * r) * Math.cos(b[0] * r) * Math.sin((b[1] - a[1]) * r / 2) ** 2
  return 2 * R * Math.asin(Math.sqrt(h)) }
function trackGain(pts) { let g = 0; for (let i = 1; i < pts.length; i++) { const d = (+pts[i][2] || 0) - (+pts[i - 1][2] || 0); if (d > 0) g += d } return g }
function trackDur(pts) { const t = pts.map(p => Date.parse(p[3])).filter(x => !isNaN(x))
  if (t.length < 2) return null; const m = Math.round((Math.max(...t) - Math.min(...t)) / 60000)
  return m >= 60 ? (m / 60).toFixed(1) + ' h' : m + ' min' }
function durationMin(pts) { const t = pts.map(p => Date.parse(p[3])).filter(x => !isNaN(x))
  if (t.length < 2) return null; return Math.round((Math.max(...t) - Math.min(...t)) / 60000) }
function srcName(s) { return { record: '实地记录', gpx: 'GPX 导入', 'gpx-wpt': 'GPX 航点', kml: 'KML 导入', csv: '坐标表导入', photos: '照片点位' }[s] || '导入' }
function nowStr() { return new Date().toISOString().slice(0, 16).replace('T', ' ') }

function trackPayload(t) {
  return { name: t.name, src: t.src, points_json: JSON.stringify(t.pts),
    point_count: t.pts.length, distance_km: +trackDist(t.pts).toFixed(3),
    duration_min: durationMin(t.pts), gain_m: trackGain(t.pts) > 1 ? Math.round(trackGain(t.pts)) : null }
}
async function addTrack(o) {
  const rec = { id: uid(), serverId: null, name: o.name, src: o.src, pts: o.pts, time: nowStr() }
  tracks.value.unshift(rec)
  saveField(); renderFieldMap()
  try { const r = await fieldTrackApi.create(trackPayload(rec)); rec.serverId = r.id; saveField() }
  catch (e) { /* 离线时保留本地，联网后重进本页自动以上服务端数据为准 */ }
}
async function resyncTrack(t) {
  try {
    if (t.serverId) { await fieldTrackApi.remove(t.serverId); t.serverId = null }
    const r = await fieldTrackApi.create(trackPayload(t)); t.serverId = r.id; saveField()
  } catch (e) { /* 离线忽略 */ }
}
function delTrack(id) {
  const t = tracks.value.find(x => x.id === id)
  if (t?.serverId) fieldTrackApi.remove(t.serverId).catch(() => {})
  tracks.value = tracks.value.filter(x => x.id !== id)
  saveField(); renderFieldMap()
}
function focusTrack(i) {
  const t = tracks.value[i]; if (!t || !map) return
  map.fitBounds(L.latLngBounds(t.pts.map(p => [p[0], p[1]])), { padding: [40, 40] })
}
function exportGPX(i) {
  const t = tracks.value[i]; if (!t) return
  const esc = s => String(s || '').replace(/[&<>"]/g, c => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;' }[c]))
  const g = `<?xml version="1.0" encoding="UTF-8"?>\n<gpx version="1.1" creator="LhasaMonitor" xmlns="http://www.topografix.com/GPX/1/1"><trk><name>${esc(t.name)}</name><trkseg>\n` +
    t.pts.map(p => `<trkpt lat="${p[0]}" lon="${p[1]}">${p[2] != null ? `<ele>${p[2]}</ele>` : ''}${p[3] ? `<time>${p[3]}</time>` : ''}</trkpt>`).join('\n') +
    `\n</trkseg></trk></gpx>`
  const a = document.createElement('a')
  a.href = URL.createObjectURL(new Blob([g], { type: 'application/gpx+xml' }))
  a.download = t.name.replace(/[\\/:*?"<>|]/g, '_') + '.gpx'
  a.click(); URL.revokeObjectURL(a.href)
  ElMessage.success('已导出 GPX，可回传两步路/行者')
}

/* ───────── 地图 ───────── */
const mapEl = ref(null)
let map = null
let layerGroup = null

function renderFieldMap() {
  if (!map || !layerGroup) return
  layerGroup.clearLayers()
  const bounds = []
  tracks.value.forEach((t, i) => {
    if (t.pts.length < 2) return
    const col = TCOLORS[i % 6]
    const ll = t.pts.map(p => [p[0], p[1]])
    L.polyline(ll, { color: col, weight: 4, opacity: 0.85 }).addTo(layerGroup).bindPopup(`<b>${t.name}</b><br>${trackDist(t.pts).toFixed(2)} km · ${t.pts.length} 点`)
    L.circleMarker(ll[0], { radius: 6, fillColor: '#2E9E63', color: '#fff', weight: 2, fillOpacity: 1 }).addTo(layerGroup).bindTooltip('起点')
    L.circleMarker(ll[ll.length - 1], { radius: 6, fillColor: '#dc3535', color: '#fff', weight: 2, fillOpacity: 1 }).addTo(layerGroup).bindTooltip('终点')
    bounds.push(...ll)
  })
  if (recPts.value.length > 1) {
    L.polyline(recPts.value.map(p => [p[0], p[1]]), { color: '#2470d8', weight: 3, dashArray: '7 5' }).addTo(layerGroup)
  }
  photos.value.forEach(p => {
    if (p.lat == null) return
    const m = L.circleMarker([p.lat, p.lon], { radius: 7, fillColor: '#f2c94c', color: '#b8860b', weight: 2, fillOpacity: 0.9 }).addTo(layerGroup)
    m.bindPopup(`<b>${p.name}</b><br>${p.lat.toFixed(6)}, ${p.lon.toFixed(6)}${p.alt ? ' · ' + p.alt + ' m' : ''}${p.species ? '<br>🌿 ' + p.species : ''}${p.thumb ? `<br><img src="${p.thumb}" style="width:140px;border-radius:6px;margin-top:4px">` : ''}`)
    bounds.push([p.lat, p.lon])
  })
  if (bounds.length) map.fitBounds(L.latLngBounds(bounds), { padding: [40, 40], maxZoom: 15 })
}

onMounted(async () => {
  try { projects.value = await projectApi.list() } catch (e) { /* ignore */ }
  try {
    const server = await fieldTrackApi.list()
    if (Array.isArray(server) && server.length) {
      tracks.value = server.map(s => ({ id: uid(), serverId: s.id, name: s.name, src: s.src,
        pts: JSON.parse(s.points_json || '[]'), time: (s.created_at || '').slice(0, 16).replace('T', ' ') }))
      saveField()
    }
  } catch (e) { /* 离线或接口不可用时使用本地缓存 */ }
  map = L.map(mapEl.value, { zoomControl: false }).setView([29.65, 91.1], 11)
  L.control.zoom({ position: 'bottomright' }).addTo(map)
  L.tileLayer('https://{s}.basemaps.cartocdn.com/light_all/{z}/{x}/{y}{r}.png', { attribution: '&copy;OpenStreetMap, &copy;CartoDB', maxZoom: 19, subdomains: 'abcd' }).addTo(map)
  layerGroup = L.layerGroup().addTo(map)
  map.on('click', e => { if (pickTarget.value) onMapPick(e.latlng) })
  renderFieldMap()
})
onUnmounted(() => { stopWatch(); if (appTimer) clearInterval(appTimer); if (map) { map.remove(); map = null } })
</script>

<style scoped>
.field-layout { display: grid; grid-template-columns: 400px 1fr; gap: 16px; height: calc(100vh - 160px); min-height: 480px; }
.field-panel {
  background: rgba(255,255,255,0.72); border: 1px solid rgba(255,255,255,0.85);
  border-radius: 16px; backdrop-filter: blur(12px); box-shadow: 0 4px 20px rgba(46,125,82,0.07);
  padding: 10px 14px; overflow-y: auto; display: flex; flex-direction: column;
}
.field-tabs :deep(.el-tabs__item) { color: #3d5a4c; }
.field-tabs :deep(.el-tabs__item.is-active) { color: #0d9862; font-weight: 600; }
.field-tabs :deep(.el-tabs__active-bar) { background: linear-gradient(90deg, #10b981, #0b8fa8); }

.proj-row { margin-bottom: 10px; }
.up-actions { display: flex; gap: 8px; }
.up-btn { flex: 1; }
.up-btn.ghost { background: rgba(255,255,255,0.65) !important; border: 1px solid rgba(15,60,40,0.12) !important; color: #3d5a4c !important; }
.up-tip { font-size: 11px; color: #7a968a; line-height: 1.6; margin: 8px 0 12px; }
.empty-tip { text-align: center; padding: 22px; color: #9ab5a8; font-size: 12px; }
.rec-status { font-size: 12px; color: #5a7a6a; margin: 8px 0; line-height: 1.6; }
.rec-status.live { color: #dc3535; font-weight: 600; }

.photo-list, .track-list { display: flex; flex-direction: column; gap: 8px; }
.fitem { display: flex; gap: 10px; padding: 8px; border-radius: 12px; background: rgba(255,255,255,0.55); border: 1px solid rgba(15,60,40,0.06); }
.fthumb { width: 56px; height: 56px; border-radius: 10px; overflow: hidden; flex-shrink: 0; display: flex; align-items: center; justify-content: center; background: #e6efe9; font-size: 22px; position: relative; }
.fthumb img { width: 100%; height: 100%; object-fit: cover; }
.vplay { position: absolute; inset: auto 0 0 0; background: rgba(0,0,0,0.55); color: #fff; font-size: 10px; text-align: center; padding: 1px 0; }
.pick-banner { position: absolute; top: 12px; left: 50%; transform: translateX(-50%); z-index: 500; background: rgba(255,251,235,0.96); border: 1px solid rgba(202,138,4,0.35); color: #854d0e; border-radius: 10px; padding: 6px 12px; font-size: 12px; display: flex; align-items: center; gap: 8px; box-shadow: 0 4px 16px rgba(120,90,10,0.18); max-width: 92%; }
.fbody { flex: 1; min-width: 0; }
.fname { font-size: 12px; font-weight: 600; color: #0f2e1f; white-space: nowrap; overflow: hidden; text-overflow: ellipsis; }
.fgeo { font-size: 11px; color: #5a7a6a; line-height: 1.7; margin-top: 2px; }
.fnote { font-size: 11px; color: #0d9862; background: rgba(16,185,129,0.08); border-radius: 8px; padding: 4px 8px; margin-top: 4px; line-height: 1.6; }
.facts { display: flex; gap: 2px; margin-top: 4px; }
.anno-form { display: flex; flex-direction: column; gap: 6px; margin-top: 6px; padding: 8px; border-radius: 10px; background: rgba(16,185,129,0.05); border: 1px dashed rgba(14,159,110,0.25); }
.arow { display: flex; gap: 6px; }

.kpi-row { display: grid; grid-template-columns: repeat(4, 1fr); gap: 8px; margin-top: 12px; padding-top: 12px; border-top: 1px solid rgba(15,60,40,0.07); }
.kpi { text-align: center; }
.kpi b { display: block; font-size: 18px; color: #0e9f6e; }
.kpi span { font-size: 10px; color: #7a968a; }

.field-map-wrap { position: relative; border-radius: 16px; overflow: hidden; border: 1px solid rgba(255,255,255,0.85); box-shadow: 0 4px 20px rgba(46,125,82,0.07); }
.field-map { width: 100%; height: 100%; }
.map-legend { position: absolute; bottom: 12px; left: 12px; background: rgba(255,255,255,0.88); border-radius: 8px; padding: 6px 12px; display: flex; gap: 14px; font-size: 11px; color: #3d5a4c; border: 1px solid rgba(255,255,255,0.9); box-shadow: 0 2px 10px rgba(46,125,82,0.1); z-index: 400; }
.lg-line { display: inline-block; width: 16px; height: 3px; background: #2E9E63; border-radius: 2px; vertical-align: middle; margin-right: 4px; }
.lg-dot { display: inline-block; width: 9px; height: 9px; border-radius: 50%; background: #f2c94c; border: 2px solid #b8860b; vertical-align: middle; margin-right: 4px; }

:deep(.leaflet-container) { background: #f2f7f4 !important; }
:deep(.leaflet-popup-content-wrapper) { background: rgba(255,255,255,0.96) !important; border-radius: 10px !important; box-shadow: 0 8px 24px rgba(46,125,82,0.15); color: #1e3a2f !important; }
:deep(.leaflet-popup-tip) { background: rgba(255,255,255,0.96) !important; }

@media (max-width: 900px) {
  /* 移动端：页面自然滚动，地图置顶且足够高，双指缩放地图、单指拖页 */
  .field-layout { grid-template-columns: 1fr; height: auto; min-height: 0; }
  .field-map-wrap {
    order: -1; height: 52vh; min-height: 340px; max-height: 70vh;
    resize: vertical; overflow: hidden;
  }
  .field-panel { max-height: none; overflow-y: visible; }
  .field-page { overflow-y: auto; }
  .page-title { font-size: 17px; }
  .page-subtitle { font-size: 11px; }
  .up-actions { flex-wrap: wrap; }
  .up-btn { flex: 1 1 30%; font-size: 12px; }
}
</style>
