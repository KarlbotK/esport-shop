<template>
  <div class="form-page">
    <div class="form-card">
      <h2>登录</h2>
      <div v-if="error" class="alert alert-error">{{ error }}</div>
      <div class="form-group"><label>用户名</label><input v-model="form.username" placeholder="请输入用户名" /></div>
      <div class="form-group"><label>密码</label><input v-model="form.password" type="password" placeholder="请输入密码" @keyup.enter="doLogin" /></div>
      <button class="btn btn-primary btn-lg" @click="doLogin" :disabled="loading">
        {{ loading ? '登录中...' : '登录' }}
      </button>
      <div class="form-link">还没有账号？<router-link to="/register">立即注册</router-link></div>
      <div class="form-link" style="margin-top:8px;">管理员演示: admin / admin123</div>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import { login } from '../api/index.js'
import { useAuthStore } from '../stores/auth.js'

const router = useRouter()
const auth = useAuthStore()
const form = ref({ username: '', password: '' })
const error = ref('')
const loading = ref(false)

async function doLogin() {
  error.value = ''
  loading.value = true
  try {
    const res = await login(form.value)
    if (res.code !== 200 || !res.data) {
      error.value = res.msg || '登录失败'
      return
    }
    auth.setAuth(res.data.token, res.data.role, form.value.username)
    router.push('/')
  } catch (e) {
    error.value = e.message
  } finally {
    loading.value = false
  }
}
</script>
