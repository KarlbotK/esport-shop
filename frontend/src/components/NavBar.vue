<template>
  <nav class="navbar">
    <div class="container">
      <router-link to="/" class="logo">⚡ 电竞装备商城</router-link>
      <div class="search-box">
        <input v-model="keyword" placeholder="搜罗技GPW、磁轴键盘、电竞耳机..." @keyup.enter="search" />
        <button @click="search">搜索</button>
      </div>
      <div class="nav-links">
        <router-link to="/" :class="{ active: $route.path === '/' }">首页</router-link>
        <router-link to="/seckill" :class="{ active: $route.path === '/seckill' }">秒杀</router-link>
        <router-link to="/recommend" :class="{ active: $route.path === '/recommend' }">AI推荐</router-link>
        <router-link to="/cart" class="nav-link-cart" :class="{ active: $route.path === '/cart' }">
          购物车
          <span v-if="cart.count > 0" class="cart-badge">{{ cart.count }}</span>
        </router-link>
        <template v-if="auth.isLoggedIn()">
          <router-link to="/orders">订单</router-link>
          <router-link v-if="auth.isAdmin()" to="/admin">管理</router-link>
          <router-link v-if="auth.isSales() || auth.isAdmin()" to="/sales">销售</router-link>
          <a href="#" @click.prevent="doLogout">退出</a>
        </template>
        <template v-else>
          <router-link to="/login">登录</router-link>
          <router-link to="/register" class="btn btn-primary btn-sm">注册</router-link>
        </template>
      </div>
    </div>
  </nav>
</template>

<script setup>
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '../stores/auth.js'
import { useCartStore } from '../stores/cart.js'

const auth = useAuthStore()
const cart = useCartStore()
const router = useRouter()
const keyword = ref('')

function search() {
  if (keyword.value.trim()) {
    router.push({ name: 'Products', query: { keyword: keyword.value.trim() } })
  }
}

function doLogout() {
  auth.logout()
  router.push('/')
}
</script>
