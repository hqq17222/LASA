<template>
  <div class="login-page">
    <div class="login-card">
      <div class="login-brand">
        <svg width="44" height="44" viewBox="0 0 32 32" fill="none">
          <defs>
            <linearGradient id="lgGrad" x1="0" y1="0" x2="32" y2="32">
              <stop offset="0%" stop-color="#10b981"/>
              <stop offset="100%" stop-color="#0b8fa8"/>
            </linearGradient>
          </defs>
          <circle cx="16" cy="16" r="14" stroke="url(#lgGrad)" stroke-width="2" fill="none"/>
          <path d="M16 6 L16 16 L24 20" stroke="url(#lgGrad)" stroke-width="2" stroke-linecap="round"/>
          <circle cx="16" cy="16" r="3" fill="url(#lgGrad)"/>
        </svg>
        <div class="login-title">拉萨南北山</div>
        <div class="login-sub">生态监测评估系统 · 用户登录</div>
      </div>
      <el-form @submit.prevent="doLogin">
        <el-form-item>
          <el-input v-model="username" size="large" placeholder="用户名" :prefix-icon="User" autocomplete="username"
            autocapitalize="none" autocorrect="off" spellcheck="false" />
        </el-form-item>
        <el-form-item>
          <el-input v-model="password" size="large" type="password" placeholder="密码" :prefix-icon="Lock"
            show-password autocomplete="current-password" @keyup.enter="doLogin" />
        </el-form-item>
        <el-button type="primary" size="large" style="width: 100%" :loading="loading" @click="doLogin">登 录</el-button>
      </el-form>
      <div class="login-tip">不同用户组权限不同：管理员 / 项目主管 / 数据分析 / 只读访客</div>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import { User, Lock } from '@element-plus/icons-vue'
import { authApi } from '../api.js'

const router = useRouter()
const username = ref('')
const password = ref('')
const loading = ref(false)

async function doLogin() {
  const un = username.value.trim()
  const pw = password.value.trim()
  if (!un || !pw) return ElMessage.warning('请输入用户名和密码')
  loading.value = true
  try {
    const res = await authApi.login({ username: un, password: pw })
    localStorage.setItem('lasa_token', res.token)
    localStorage.setItem('lasa_user', JSON.stringify(res.user))
    ElMessage.success(`欢迎，${res.user.display_name || res.user.username}`)
    // 安卓 App 壳内登录后直接进入外业移动页，而非桌面工作台
    router.push(typeof window.AndroidBridge !== 'undefined' ? '/m' : '/')
  } catch (e) {
    ElMessage.error(String(e))
  } finally {
    loading.value = false
  }
}
</script>

<style scoped>
.login-page {
  height: 100vh;
  display: flex; align-items: center; justify-content: center;
  padding: 20px;
}
.login-card {
  width: 380px; max-width: 100%;
  background: rgba(255,255,255,0.82);
  border: 1px solid rgba(255,255,255,0.9);
  border-radius: 20px;
  backdrop-filter: blur(20px);
  box-shadow: 0 16px 48px rgba(46,125,82,0.16);
  padding: 36px 32px 24px;
}
.login-brand { text-align: center; margin-bottom: 26px; }
.login-title {
  font-size: 22px; font-weight: 800; margin-top: 10px;
  background: linear-gradient(135deg, #0f2e1f, #2E9E63);
  -webkit-background-clip: text; -webkit-text-fill-color: transparent;
}
.login-sub { font-size: 12px; color: #7a968a; margin-top: 4px; }
.login-tip { text-align: center; font-size: 11px; color: #9ab5a8; margin-top: 16px; line-height: 1.7; }
</style>
