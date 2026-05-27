<template>
  <div class="page">
    <div class="container">
      <h1 class="page-title">购物车</h1>
      <div v-if="cart.items.length === 0" style="text-align:center;padding:80px;color:#999;">
        购物车是空的，<router-link to="/" style="color:var(--primary);">去逛逛</router-link>
      </div>
      <div v-else>

        <!-- Step 1: 购物车 -->
        <div v-if="step === 'cart'" class="table-wrapper">
          <table>
            <thead><tr><th>商品</th><th>规格</th><th>单价</th><th>数量</th><th>小计</th><th>操作</th></tr></thead>
            <tbody>
              <tr v-for="item in cart.items" :key="item.skuId">
                <td>{{ item.spuName || item.skuName }}</td>
                <td>{{ item.skuName }}</td>
                <td>¥{{ item.price }}</td>
                <td>{{ item.quantity }}</td>
                <td style="color:var(--primary);font-weight:600;">¥{{ (item.price * item.quantity).toFixed(2) }}</td>
                <td><button class="btn btn-sm btn-danger" @click="cart.removeItem(item.skuId)">删除</button></td>
              </tr>
            </tbody>
          </table>
        </div>

        <!-- Step 2: 确认订单 -->
        <div v-if="step === 'confirm'" class="table-wrapper">
          <h3 style="margin-bottom:16px;">确认订单信息</h3>
          <table>
            <thead><tr><th>商品</th><th>单价</th><th>数量</th><th>小计</th></tr></thead>
            <tbody>
              <tr v-for="item in cart.items" :key="item.skuId">
                <td>{{ item.spuName }} - {{ item.skuName }}</td>
                <td>¥{{ item.price }}</td>
                <td>{{ item.quantity }}</td>
                <td style="color:var(--primary);font-weight:600;">¥{{ (item.price * item.quantity).toFixed(2) }}</td>
              </tr>
            </tbody>
          </table>
        </div>

        <!-- Step 3: 付款 -->
        <div v-if="step === 'pay'">
          <div class="table-wrapper" style="text-align:center;padding:60px;">
            <div style="font-size:48px;margin-bottom:16px;">💳</div>
            <h3>订单已创建，模拟付款中...</h3>
            <p style="color:var(--text-light);margin-top:8px;">订单号: {{ orderId }}</p>
            <div style="margin-top:24px;">
              <button class="btn btn-primary btn-lg" @click="confirmPay">确认付款 ¥{{ cart.total.toFixed(2) }}</button>
            </div>
            <p style="color:var(--text-light);font-size:12px;margin-top:8px;">（课程设计模拟支付）</p>
          </div>
        </div>

        <!-- Step 4: 完成 -->
        <div v-if="step === 'done'">
          <div class="table-wrapper" style="text-align:center;padding:60px;">
            <div style="font-size:48px;margin-bottom:16px;">✅</div>
            <h3 style="color:#2e7d32;">付款成功！</h3>
            <p style="color:var(--text-light);margin-top:8px;">订单 #{{ orderId }} 已确认，邮件已发送</p>
            <button class="btn btn-primary" style="margin-top:24px;" @click="$router.push('/orders')">查看订单</button>
          </div>
        </div>

        <div style="text-align:right;margin-top:24px;font-size:18px;">
          合计: <span style="color:var(--primary);font-weight:700;font-size:24px;">¥{{ cart.total.toFixed(2) }}</span>
        </div>
        <div style="text-align:right;margin-top:16px;">
          <button v-if="step === 'cart'" class="btn btn-primary btn-lg" @click="step = 'confirm'">
            去结算
          </button>
          <button v-if="step === 'confirm'" class="btn btn-outline" @click="step = 'cart'" style="margin-right:8px;">
            返回购物车
          </button>
          <button v-if="step === 'confirm'" class="btn btn-primary btn-lg" @click="submitOrder" :disabled="submitting">
            {{ submitting ? '提交中...' : '提交订单' }}
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import { useCartStore } from '../stores/cart.js'
import { createOrder } from '../api/index.js'

const cart = useCartStore()
const router = useRouter()
const step = ref('cart')
const submitting = ref(false)
const orderId = ref(null)

async function submitOrder() {
  if (!localStorage.getItem('token')) return router.push('/login')
  submitting.value = true
  try {
    const res = await createOrder({
      items: cart.items.map(i => ({ skuId: i.skuId, quantity: i.quantity }))
    })
    orderId.value = res.data?.orderId
    step.value = 'pay'
  } catch (e) {
    alert(e.message)
  } finally {
    submitting.value = false
  }
}

function confirmPay() {
  cart.clear()
  step.value = 'done'
}
</script>
