import { createRouter, createWebHistory } from 'vue-router'
import Dashboard from './views/Dashboard.vue'
import MapView from './views/MapView.vue'
import DataCatalog from './views/DataCatalog.vue'
import Indicators from './views/Indicators.vue'
import Alarms from './views/Alarms.vue'
import Reports from './views/Reports.vue'
import Equipment from './views/Equipment.vue'
import PhasePlan from './views/PhasePlan.vue'
import PatrolPhotos from './views/PatrolPhotos.vue'
import FieldSurvey from './views/FieldSurvey.vue'
import OpsBoard from './views/OpsBoard.vue'
import Instructions from './views/Instructions.vue'
import Login from './views/Login.vue'
import Users from './views/Users.vue'

const routes = [
  { path: '/login', name: 'Login', component: Login, meta: { title: '登录', public: true } },
  { path: '/', name: 'Dashboard', component: Dashboard, meta: { title: '工作台' } },
  { path: '/map', name: 'MapView', component: MapView, meta: { title: '生态一张图' } },
  { path: '/data', name: 'DataCatalog', component: DataCatalog, meta: { title: '数据目录' } },
  { path: '/indicators', name: 'Indicators', component: Indicators, meta: { title: '评估指标' } },
  { path: '/equipment', name: 'Equipment', component: Equipment, meta: { title: '设备清单' } },
  { path: '/phase-plan', name: 'PhasePlan', component: PhasePlan, meta: { title: '阶段计划' } },
  { path: '/patrol-photos', name: 'PatrolPhotos', component: PatrolPhotos, meta: { title: '巡检照片' } },
  { path: '/field', name: 'FieldSurvey', component: FieldSurvey, meta: { title: '野外科考' } },
  { path: '/ops', name: 'OpsBoard', component: OpsBoard, meta: { title: '外业看板' } },
  { path: '/alarms', name: 'Alarms', component: Alarms, meta: { title: '偏离度预警' } },
  { path: '/reports', name: 'Reports', component: Reports, meta: { title: '评估报告' } },
  { path: '/users', name: 'Users', component: Users, meta: { title: '用户管理', admin: true } },
  { path: '/ins', name: 'Instructions', component: Instructions, meta: { title: '使用说明' } },
]

const router = createRouter({
  history: createWebHistory(),
  routes,
})

// 全局守卫：未登录跳登录页；用户管理仅管理员
router.beforeEach((to) => {
  const token = localStorage.getItem('lasa_token')
  if (to.path === '/login') return token ? '/' : true
  if (!token) return '/login'
  if (to.meta.admin) {
    try {
      const u = JSON.parse(localStorage.getItem('lasa_user') || '{}')
      if (u.role !== 'admin') return '/'
    } catch { return '/login' }
  }
  return true
})

export default router
