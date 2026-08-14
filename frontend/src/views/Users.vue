<template>
  <div>
    <div class="page-title">用户管理</div>
    <div class="page-subtitle">账户与用户组权限管理 —— 仅管理员可见 · 角色等级：管理员 &gt; 项目主管 &gt; 数据分析 &gt; 只读访客</div>

    <div class="glass-card">
      <div class="um-toolbar">
        <div class="role-legend">
          <span class="rl-item"><i class="rl-dot admin"></i>管理员：全部权限 + 用户管理</span>
          <span class="rl-item"><i class="rl-dot manager"></i>项目主管：数据读写 + 报告告警处置</span>
          <span class="rl-item"><i class="rl-dot analyst"></i>数据分析：数据读写</span>
          <span class="rl-item"><i class="rl-dot viewer"></i>只读访客：仅查看</span>
        </div>
        <el-button type="primary" :icon="Plus" @click="openCreate">新建用户</el-button>
      </div>

      <el-table :data="users" size="default">
        <el-table-column label="用户名" prop="username" width="140" />
        <el-table-column label="姓名" prop="display_name" min-width="140" />
        <el-table-column label="用户组" width="130">
          <template #default="{ row }">
            <span class="role-pill" :class="row.role">{{ roleName(row.role) }}</span>
          </template>
        </el-table-column>
        <el-table-column label="状态" width="90">
          <template #default="{ row }">
            <el-tag :type="row.is_active ? 'success' : 'info'" size="small">{{ row.is_active ? '启用' : '停用' }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column label="创建时间" width="160">
          <template #default="{ row }">{{ formatDate(row.created_at) }}</template>
        </el-table-column>
        <el-table-column label="操作" width="180">
          <template #default="{ row }">
            <el-button size="small" text type="primary" :icon="Edit" @click="openEdit(row)">编辑</el-button>
            <el-button size="small" text type="danger" :icon="Delete" @click="removeUser(row)">删除</el-button>
          </template>
        </el-table-column>
      </el-table>
    </div>

    <!-- 新建 -->
    <el-dialog v-model="createVisible" title="新建用户" width="420px">
      <el-form label-width="80px">
        <el-form-item label="用户名"><el-input v-model="createForm.username" placeholder="登录账号" /></el-form-item>
        <el-form-item label="姓名"><el-input v-model="createForm.display_name" placeholder="显示姓名（可空）" /></el-form-item>
        <el-form-item label="初始密码"><el-input v-model="createForm.password" type="password" show-password placeholder="至少 6 位" /></el-form-item>
        <el-form-item label="用户组">
          <el-select v-model="createForm.role" style="width: 100%">
            <el-option label="只读访客（仅查看）" value="viewer" />
            <el-option label="数据分析（读写）" value="analyst" />
            <el-option label="项目主管（读写+处置）" value="manager" />
            <el-option label="管理员（全部权限）" value="admin" />
          </el-select>
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="createVisible = false">取消</el-button>
        <el-button type="primary" :loading="saving" @click="submitCreate">创建</el-button>
      </template>
    </el-dialog>

    <!-- 编辑 -->
    <el-dialog v-model="editVisible" :title="`编辑用户：${editForm.username}`" width="420px">
      <el-form label-width="80px">
        <el-form-item label="姓名"><el-input v-model="editForm.display_name" /></el-form-item>
        <el-form-item label="用户组">
          <el-select v-model="editForm.role" style="width: 100%">
            <el-option label="只读访客（仅查看）" value="viewer" />
            <el-option label="数据分析（读写）" value="analyst" />
            <el-option label="项目主管（读写+处置）" value="manager" />
            <el-option label="管理员（全部权限）" value="admin" />
          </el-select>
        </el-form-item>
        <el-form-item label="重置密码"><el-input v-model="editForm.password" type="password" show-password placeholder="留空则不修改" /></el-form-item>
        <el-form-item label="状态">
          <el-switch v-model="editForm.is_active" active-text="启用" inactive-text="停用" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="editVisible = false">取消</el-button>
        <el-button type="primary" :loading="saving" @click="submitEdit">保存</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { Plus, Edit, Delete } from '@element-plus/icons-vue'
import { userApi } from '../api.js'

const users = ref([])
const createVisible = ref(false)
const editVisible = ref(false)
const saving = ref(false)
const createForm = ref({ username: '', display_name: '', password: '', role: 'viewer' })
const editForm = ref({ id: null, username: '', display_name: '', role: 'viewer', password: '', is_active: true })

const roleName = (r) => ({ admin: '管理员', manager: '项目主管', analyst: '数据分析', viewer: '只读访客' }[r] || r)
const formatDate = (t) => t ? new Date(t).toLocaleString('zh-CN', { year: 'numeric', month: '2-digit', day: '2-digit', hour: '2-digit', minute: '2-digit' }) : '-'

async function load() { users.value = await userApi.list() }
onMounted(load)

function openCreate() {
  createForm.value = { username: '', display_name: '', password: '', role: 'viewer' }
  createVisible.value = true
}
async function submitCreate() {
  saving.value = true
  try {
    await userApi.create(createForm.value)
    ElMessage.success('用户已创建')
    createVisible.value = false
    load()
  } catch (e) { ElMessage.error(String(e)) }
  finally { saving.value = false }
}
function openEdit(row) {
  editForm.value = { id: row.id, username: row.username, display_name: row.display_name, role: row.role, password: '', is_active: row.is_active }
  editVisible.value = true
}
async function submitEdit() {
  saving.value = true
  try {
    const payload = { display_name: editForm.value.display_name, role: editForm.value.role, is_active: editForm.value.is_active }
    if (editForm.value.password) payload.password = editForm.value.password
    await userApi.update(editForm.value.id, payload)
    ElMessage.success('已保存')
    editVisible.value = false
    load()
  } catch (e) { ElMessage.error(String(e)) }
  finally { saving.value = false }
}
async function removeUser(row) {
  try {
    await ElMessageBox.confirm(`确认删除用户「${row.username}」？`, '删除确认', { type: 'warning' })
  } catch { return }
  try {
    await userApi.remove(row.id)
    ElMessage.success('已删除')
    load()
  } catch (e) { ElMessage.error(String(e)) }
}
</script>

<style scoped>
.glass-card {
  background: rgba(255,255,255,0.72); border: 1px solid rgba(255,255,255,0.85);
  border-radius: 16px; backdrop-filter: blur(12px);
  box-shadow: 0 4px 20px rgba(46,125,82,0.07); padding: 16px 18px;
}
.um-toolbar { display: flex; align-items: center; justify-content: space-between; gap: 12px; margin-bottom: 14px; flex-wrap: wrap; }
.role-legend { display: flex; gap: 14px; flex-wrap: wrap; }
.rl-item { font-size: 11px; color: #5a7a6a; display: flex; align-items: center; gap: 5px; }
.rl-dot { width: 8px; height: 8px; border-radius: 50%; display: inline-block; }
.rl-dot.admin { background: #dc3535; }
.rl-dot.manager { background: #dd6a1a; }
.rl-dot.analyst { background: #2470d8; }
.rl-dot.viewer { background: #7a968a; }
.role-pill { padding: 2px 10px; border-radius: 10px; font-size: 11px; font-weight: 600; }
.role-pill.admin { background: rgba(220,53,53,0.1); color: #dc3535; }
.role-pill.manager { background: rgba(221,106,26,0.12); color: #dd6a1a; }
.role-pill.analyst { background: rgba(36,112,216,0.1); color: #2470d8; }
.role-pill.viewer { background: rgba(90,122,106,0.12); color: #5a7a6a; }
@media (max-width: 768px) {
  .um-toolbar { flex-direction: column; align-items: stretch; }
}
</style>
