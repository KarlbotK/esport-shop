<template>
  <div class="page">
    <div class="container">
      <h1 class="page-title">我的订单</h1>
      <div v-if="loading" style="text-align:center;padding:60px;">加载中...</div>
      <div v-else-if="orders.length === 0" style="text-align:center;padding:80px;color:#999;">
        还没有订单
      </div>
      <div v-else class="table-wrapper">
        <table>
          <thead><tr><th>订单号</th><th>金额</th><th>状态</th><th>时间</th></tr></thead>
          <tbody>
            <tr v-for="o in orders" :key="o.id">
              <td>#{{ o.id }}</td>
              <td style="color:var(--primary);font-weight:600;">¥{{ o.totalAmount }}</td>
              <td><span :style="{ color: statusColor(o.status) }">{{ statusText(o.status) }}</span></td>
              <td>{{ o.createTime }}</td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { getOrders } from '../api/index.js'

const orders = ref([])
const loading = ref(true)

onMounted(async () => {
  try { const res = await getOrders(); orders.value = res.data || [] }
  catch (e) { /* empty */ }
  finally { loading.value = false }
})

const STATUS_MAP = { 0: '待付款', 1: '已付款', 2: '已发货', 3: '已完成', 4: '已取消' }
const STATUS_COLOR = { 0: '#ff5000', 1: '#1890ff', 2: '#52c41a', 3: '#999', 4: '#ccc' }
function statusText(s) { return STATUS_MAP[s] || '未知' }
function statusColor(s) { return STATUS_COLOR[s] || '#999' }
</script>
