<template>
  <div class="form-page">
    <div class="form-card">
      <h2>注册</h2>
      <div v-if="error" class="alert alert-error">{{ error }}</div>
      <div v-if="success" class="alert alert-success">{{ success }}</div>
      <div class="form-group"><label>用户名</label><input v-model="form.username" placeholder="至少3位" /></div>
      <div class="form-group"><label>密码</label><input v-model="form.password" type="password" placeholder="至少6位" /></div>
      <div class="form-group"><label>邮箱</label><input v-model="form.email" placeholder="可选" /></div>
      <div class="form-group"><label>手机号</label><input v-model="form.phone" placeholder="可选" /></div>
      <button class="btn btn-primary btn-lg" @click="doRegister" :disabled="loading">
        {{ loading ? '注册中...' : '注册' }}
      </button>
      <div class="form-link">已有账号？<router-link to="/login">去登录</router-link></div>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { register } from '../api/index.js'

const form = ref({ username: '', password: '', email: '', phone: '' })
const error = ref('')
const success = ref('')
const loading = ref(false)

async function doRegister() {
  error.value = ''
  success.value = ''
  if (form.value.username.length < 3) { error.value = '用户名至少3位'; return }
  if (form.value.password.length < 6) { error.value = '密码至少6位'; return }
  loading.value = true
  try {
    const res = await register(form.value)
    if (res.code !== 200) {
      error.value = res.msg || '注册失败'
      return
    }
    success.value = '注册成功！请登录'
  } catch (e) {
    error.value = e.message
  } finally {
    loading.value = false
  }
}
</script>
