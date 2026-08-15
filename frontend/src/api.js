import axios from 'axios'

const api = axios.create({
  baseURL: '/api/v1',
  timeout: 30000,
})

// 请求拦截：自动携带登录令牌
api.interceptors.request.use((config) => {
  const token = localStorage.getItem('lasa_token')
  if (token) config.headers.Authorization = `Bearer ${token}`
  return config
})

api.interceptors.response.use(
  (res) => res.data,
  (err) => {
    const status = err.response?.status
    if (status === 401 && !location.pathname.startsWith('/login')) {
      localStorage.removeItem('lasa_token')
      localStorage.removeItem('lasa_user')
      location.href = '/login'
      return Promise.reject('登录已过期，请重新登录')
    }
    const msg = err.response?.data?.detail || err.message || '请求失败'
    return Promise.reject(msg)
  },
)

export default api

export const healthApi = () => api.get('/health')
export const infoApi = () => api.get('/info')

export const authApi = {
  login: (data) => api.post('/auth/login', data),
  me: () => api.get('/auth/me'),
  logout: () => api.post('/auth/logout'),
}

export const userApi = {
  list: () => api.get('/users'),
  create: (data) => api.post('/users', data),
  update: (id, data) => api.put(`/users/${id}`, data),
  remove: (id) => api.delete(`/users/${id}`),
}

export const projectApi = {
  list: () => api.get('/projects'),
  create: (data) => api.post('/projects', data),
  update: (id, data) => api.put(`/projects/${id}`, data),
  remove: (id) => api.delete(`/projects/${id}`),
}

export const dataSourceApi = {
  list: (projectId) => api.get('/data-sources', { params: { project_id: projectId } }),
  upload: (formData) => api.post('/data-sources/upload', formData, { headers: { 'Content-Type': 'multipart/form-data' } }),
  remove: (id) => api.delete(`/data-sources/${id}`),
}

export const observationApi = {
  list: (params) => api.get('/observations', { params }),
  create: (data) => api.post('/observations', data),
  batchCreate: (data) => api.post('/observations/batch', data),
}

export const indicatorApi = {
  list: (projectId) => api.get('/indicators', { params: { project_id: projectId } }),
  meta: () => api.get('/indicators/meta'),
  compute: (data) => api.post('/indicators/compute', data),
}

export const equipmentApi = {
  list: (projectId) => api.get('/equipments', { params: { project_id: projectId } }),
  create: (data) => api.post('/equipments', data),
  update: (id, data) => api.put(`/equipments/${id}`, data),
  remove: (id) => api.delete(`/equipments/${id}`),
}

export const phasePlanApi = {
  list: (projectId) => api.get('/phase-plans', { params: { project_id: projectId } }),
  create: (data) => api.post('/phase-plans', data),
  update: (id, data) => api.put(`/phase-plans/${id}`, data),
  remove: (id) => api.delete(`/phase-plans/${id}`),
}

export const alarmApi = {
  list: (projectId) => api.get('/alarms', { params: { project_id: projectId } }),
  create: (data) => api.post('/alarms', data),
  handle: (id) => api.post(`/alarms/${id}/handle`),
  remove: (id) => api.delete(`/alarms/${id}`),
}

export const reportApi = {
  list: (projectId) => api.get('/reports', { params: { project_id: projectId } }),
  create: (data) => api.post('/reports', data),
  html: (id) => `/api/v1/reports/${id}/html?token=${encodeURIComponent(localStorage.getItem('lasa_token') || '')}`,
  remove: (id) => api.delete(`/reports/${id}`),
}

export const mapApi = {
  layers: () => api.get('/map/layers'),
  summary: (projectId) => api.get(`/map/projects/${projectId}/summary`),
}

export const fieldTrackApi = {
  list: () => api.get('/field/tracks'),
  create: (data) => api.post('/field/tracks', data),
  remove: (id) => api.delete(`/field/tracks/${id}`),
}

export const patrolPhotoApi = {
  list: (projectId) => api.get('/patrol-photos', { params: { project_id: projectId } }),
  grouped: (projectId) => api.get('/patrol-photos/grouped', { params: { project_id: projectId } }),
  mapLayers: (projectId) => api.get('/patrol-photos/map-layers', { params: { project_id: projectId } }),
  stats: (projectId) => api.get('/patrol-photos/stats/summary', { params: { project_id: projectId } }),
  get: (id) => api.get(`/patrol-photos/${id}`),
  updateDefect: (id, data) => api.put(`/patrol-photos/${id}/defect`, data, { headers: { 'Content-Type': 'application/x-www-form-urlencoded' } }),
  updateLocation: (id, data) => api.patch(`/patrol-photos/${id}/location`, data),
  identify: (id, context) => api.post(`/patrol-photos/${id}/identify`, { context: context || '' }, { timeout: 150000 }),
  updateSpecies: (id, data) => api.put(`/patrol-photos/${id}/species`, data),
  batchDelete: (ids) => api.post('/patrol-photos/batch-delete', ids),
  remove: (id) => api.delete(`/patrol-photos/${id}`),
}

export const voiceApi = {
  list: (projectId, photoId) => api.get('/voice', { params: { project_id: projectId, photo_id: photoId } }),
  remove: (id) => api.delete(`/voice/${id}`),
}

export const fieldOpsApi = {
  plots: (projectId) => api.get('/field/plots', { params: { project_id: projectId } }),
  createPlot: (data) => api.post('/field/plots', data),
  importPlots: (projectId, geojson) => api.post(`/field/plots/import?project_id=${projectId}`, { geojson }),
  removePlot: (id) => api.delete(`/field/plots/${id}`),
  layers: (projectId) => api.get('/field/layers', { params: { project_id: projectId } }),
  createLayer: (data) => api.post('/field/layers', data),
  removeLayer: (id) => api.delete(`/field/layers/${id}`),
  surveys: (projectId, plotId) => api.get('/field/surveys', { params: { project_id: projectId, plot_id: plotId } }),
  createSurvey: (data) => api.post('/field/surveys', data),
  removeSurvey: (id) => api.delete(`/field/surveys/${id}`),
  teamStatus: () => api.get('/field/team-status'),
  tracks: () => api.get('/field/tracks'),
}
