<template>
  <div class="data-catalog-modern">
    <div class="catalog-layout">
      <!-- 左侧项目面板 -->
      <div class="catalog-sidebar">
        <div class="panel-header">
          <div class="ph-glow" style="background: rgba(59,130,246,0.3);"></div>
          <el-icon :size="16" color="#2470d8"><FolderOpened /></el-icon>
          <span>项目列表</span>
          <el-button type="primary" size="small" class="new-btn" :icon="Plus" @click="openProjectDialog">新建</el-button>
        </div>
        <div class="project-list">
          <div class="project-item" v-for="p in projects" :key="p.id"
            :class="{ active: currentProject?.id === p.id }" @click="onProjectClick(p)">
            <div class="project-color" :style="{ background: projectColor(p.id) }"></div>
            <div class="project-info">
              <div class="project-name">{{ p.name }}</div>
              <div class="project-code">{{ p.code }}</div>
            </div>
            <el-icon v-if="currentProject?.id === p.id" :size="14" color="#10b981"><ArrowRight /></el-icon>
          </div>
        </div>
      </div>

      <!-- 右侧数据面板 -->
      <div class="catalog-main">
        <div class="catalog-toolbar">
          <div class="toolbar-title">
            <span class="t-label">数据源</span>
            <span class="t-project">{{ currentProject?.name || '全部项目' }}</span>
            <el-tag v-if="dataSources.length" type="info" size="small" effect="dark">{{ dataSources.length }} 个文件</el-tag>
          </div>
          <el-upload
            :disabled="!currentProject"
            action="/api/v1/data-sources/upload"
            :data="{ project_id: currentProject?.id, name: '上传文件', source_type: 'sample' }"
            :on-success="onUploadSuccess"
            :auto-upload="true"
            :show-file-list="false"
          >
            <el-button type="primary" :disabled="!currentProject" :icon="Upload">上传数据</el-button>
          </el-upload>
        </div>

        <div class="data-table-wrap">
          <el-table :data="dataSources" size="small" class="dark-table">
            <el-table-column prop="name" label="文件名" min-width="140">
              <template #default="scope">
                <div class="file-cell">
                  <div class="file-icon" :class="formatIcon(scope.row.format)">
                    <el-icon :size="14"><component :is="fileIcon(scope.row.format)" /></el-icon>
                  </div>
                  <span class="file-name">{{ scope.row.name }}</span>
                </div>
              </template>
            </el-table-column>
            <el-table-column prop="source_type" label="类型" width="90">
              <template #default="scope">
                <span class="type-badge">{{ scope.row.source_type }}</span>
              </template>
            </el-table-column>
            <el-table-column prop="format" label="格式" width="60">
              <template #default="scope">
                <span class="fmt-badge" :class="scope.row.format">{{ scope.row.format?.toUpperCase() }}</span>
              </template>
            </el-table-column>
            <el-table-column prop="quality_level" label="质量" width="70">
              <template #default="scope">
                <span class="ql-badge" :class="'q'+scope.row.quality_level">{{ scope.row.quality_level }}</span>
              </template>
            </el-table-column>
            <el-table-column prop="version" label="版本" width="60" />
            <el-table-column prop="naming_rule" label="命名规则" show-overflow-tooltip min-width="120" />
            <el-table-column prop="created_at" label="上传时间" width="140">
              <template #default="scope">{{ formatDate(scope.row.created_at) }}</template>
            </el-table-column>
            <el-table-column label="操作" width="70">
              <template #default="scope">
                <el-button type="danger" size="small" text :icon="Delete" @click="removeSource(scope.row)">删除</el-button>
              </template>
            </el-table-column>
          </el-table>
        </div>

        <!-- 数据规范说明 -->
        <div class="standard-box">
          <div class="std-header">
            <el-icon :size="14" color="#f59e0b"><WarningFilled /></el-icon>
            <span>数据规范（附录 B）</span>
          </div>
          <div class="std-body">
            <div class="std-item">
              <div class="std-dot" style="background: #3b82f6;"></div>
              <div><b>坐标系统</b> CGCS2000 国家大地坐标系，高程采用 1985 国家高程基准；平面投影为高斯-克吕格 3° 带，中央经线 91°30′E。</div>
            </div>
            <div class="std-item">
              <div class="std-dot" style="background: #10b981;"></div>
              <div><b>命名规则</b> 项目-类型-区域-时间-版本，五段式用下划线连接。示例：LSNS-NDVI-XYQ-202607-V1.0.tif</div>
            </div>
            <div class="std-item">
              <div class="std-dot" style="background: #f59e0b;"></div>
              <div><b>质量分级</b> A 级可直接用于模型计算；B 级可用于趋势分析；C 级仅作定性参考。</div>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- 新建项目弹窗 -->
    <el-dialog v-model="projectDialog" title="新建项目" width="520px">
      <el-form :model="projectForm" label-width="80px">
        <el-form-item label="名称"><el-input v-model="projectForm.name" placeholder="项目名称" /></el-form-item>
        <el-form-item label="编码"><el-input v-model="projectForm.code" placeholder="如 LSKJ202622-DEMO" /></el-form-item>
        <el-form-item label="描述"><el-input v-model="projectForm.description" type="textarea" rows="3" /></el-form-item>
        <el-form-item label="GeoJSON"><el-input v-model="projectForm.geometry_geojson" type="textarea" rows="4" placeholder="项目边界 GeoJSON Polygon" /></el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="projectDialog = false">取消</el-button>
        <el-button type="primary" @click="saveProject">保存</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, onMounted, watch } from 'vue'
import { ElMessage } from 'element-plus'
import {
  FolderOpened, Plus, ArrowRight, Upload, Delete,
  Document, Picture, Grid, WarningFilled
} from '@element-plus/icons-vue'
import { projectApi, dataSourceApi } from '../api.js'

const projects = ref([])
const dataSources = ref([])
const currentProject = ref(null)
const projectDialog = ref(false)
const projectForm = ref({ name: '', code: '', description: '', geometry_geojson: '' })

const colorPalette = ['#3b82f6', '#10b981', '#f59e0b', '#ef4444', '#8b5cf6', '#06b6d4']
function projectColor(id) { return colorPalette[(id - 1) % colorPalette.length] }

function formatIcon(fmt) {
  const map = { tif: 'raster', csv: 'table', xlsx: 'table', geojson: 'geo', json: 'code', jpg: 'image', png: 'image' }
  return map[fmt] || 'default'
}
function fileIcon(fmt) {
  const map = { tif: Picture, jpg: Picture, png: Picture, csv: Grid, xlsx: Grid, geojson: Document, json: Document }
  return map[fmt] || Document
}
function formatDate(t) {
  if (!t) return '-'
  return new Date(t).toLocaleString('zh-CN', { month: 'short', day: 'numeric', hour: '2-digit', minute: '2-digit' })
}

async function loadProjects() { projects.value = await projectApi.list() }
async function loadSources() { dataSources.value = await dataSourceApi.list(currentProject.value?.id || 0) }
function openProjectDialog() { projectForm.value = { name: '', code: '', description: '', geometry_geojson: '' }; projectDialog.value = true }
async function saveProject() { await projectApi.create(projectForm.value); projectDialog.value = false; await loadProjects() }
function onProjectClick(row) { currentProject.value = row; loadSources() }
async function onUploadSuccess() { ElMessage.success('上传成功'); await loadSources() }
async function removeSource(row) { await dataSourceApi.remove(row.id); await loadSources() }

onMounted(loadProjects)
watch(() => currentProject.value, loadSources)
</script>

<style scoped>
.data-catalog-modern { height: 100%; }
.catalog-layout { display: flex; gap: 16px; height: calc(100vh - 104px); }

/* 左侧项目面板 */
.catalog-sidebar {
  width: 260px; flex-shrink: 0;
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
.new-btn { margin-left: auto; font-size: 12px; }

.project-list { flex: 1; overflow-y: auto; padding: 8px; }
.project-item {
  display: flex; align-items: center; gap: 10px;
  padding: 10px 12px; border-radius: 10px;
  cursor: pointer; transition: all 0.2s;
  margin-bottom: 3px;
}
.project-item:hover { background: rgba(255,255,255,0.75); }
.project-item.active { background: rgba(59,130,246,0.08); border: 1px solid rgba(59,130,246,0.2); }
.project-color { width: 4px; height: 32px; border-radius: 2px; flex-shrink: 0; }
.project-info { flex: 1; min-width: 0; }
.project-name { font-size: 13px; font-weight: 500; color: #1e3a2f; white-space: nowrap; overflow: hidden; text-overflow: ellipsis; }
.project-code { font-size: 10px; color: #9ab5a8; margin-top: 1px; }

/* 右侧主面板 */
.catalog-main {
  flex: 1; display: flex; flex-direction: column; gap: 12px;
  min-width: 0;
}
.catalog-toolbar {
  display: flex; align-items: center; justify-content: space-between;
  padding: 12px 18px;
  background: rgba(255,255,255,0.6);
  border: 1px solid rgba(255,255,255,0.85);
  border-radius: 14px;
  backdrop-filter: blur(12px);
  box-shadow: 0 4px 20px rgba(46,125,82,0.07);
}
.toolbar-title { display: flex; align-items: center; gap: 10px; }
.t-label { font-size: 14px; font-weight: 600; color: #1e3a2f; }
.t-project { font-size: 13px; color: #5a7a6a; }

.data-table-wrap {
  flex: 1; overflow: auto;
  background: rgba(255,255,255,0.55);
  border: 1px solid rgba(255,255,255,0.85);
  border-radius: 14px;
  padding: 12px;
  box-shadow: 0 4px 20px rgba(46,125,82,0.06);
}

/* 文件单元格 */
.file-cell { display: flex; align-items: center; gap: 8px; }
.file-icon {
  width: 28px; height: 28px; border-radius: 7px;
  display: flex; align-items: center; justify-content: center;
  flex-shrink: 0;
  background: rgba(15,60,40,0.06);
}
.file-icon.raster { background: rgba(139,92,246,0.15); }
.file-icon.table { background: rgba(16,185,129,0.15); }
.file-icon.image { background: rgba(59,130,246,0.15); }
.file-icon.geo { background: rgba(245,158,11,0.15); }
.file-name { font-size: 12px; color: #1e3a2f; }

.type-badge {
  font-size: 10px; padding: 1px 7px; border-radius: 4px;
  background: rgba(15,60,40,0.06); color: #5a7a6a;
}
.fmt-badge {
  font-size: 9px; padding: 1px 5px; border-radius: 3px;
  background: rgba(15,60,40,0.06); color: #7a968a; font-weight: 600;
}
.ql-badge {
  font-size: 10px; padding: 1px 7px; border-radius: 4px; font-weight: 700;
}
.ql-badge.qA { background: rgba(16,185,129,0.15); color: #0d9862; }
.ql-badge.qB { background: rgba(245,158,11,0.15); color: #c77f0a; }
.ql-badge.qC { background: rgba(239,68,68,0.15); color: #dc3535; }

/* 规范说明 */
.standard-box {
  background: rgba(255,255,255,0.55);
  border: 1px solid rgba(255,255,255,0.85);
  border-radius: 14px;
  padding: 14px 18px;
  box-shadow: 0 4px 20px rgba(46,125,82,0.06);
}
.std-header { display: flex; align-items: center; gap: 6px; font-weight: 600; color: #c77f0a; font-size: 12px; margin-bottom: 10px; }
.std-body { display: flex; flex-direction: column; gap: 8px; }
.std-item { display: flex; gap: 10px; font-size: 11px; color: #5a7a6a; line-height: 1.6; }
.std-dot { width: 6px; height: 6px; border-radius: 50%; flex-shrink: 0; margin-top: 5px; }
.std-item b { color: #3d5a4c; }

@media (max-width: 900px) {
  .catalog-layout { flex-direction: column; height: auto; }
  .catalog-sidebar { width: 100%; max-height: 240px; }
}
</style>
