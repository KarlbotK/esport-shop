<template>
  <div class="page">
    <div class="container">
      <div class="seckill-header">
        <h2>⚡ 限时秒杀</h2>
        <p style="margin-top:8px;">手快有，手慢无 — 极致性价比电竞装备</p>
      </div>
      <div v-if="loading" style="text-align:center;padding:40px;">加载秒杀商品...</div>
      <div v-else>
        <div v-for="sku in seckillSkus" :key="sku.id" class="seckill-item">
          <div style="flex:1;">
            <div style="font-size:16px;font-weight:600;">{{ sku.skuName }}</div>
            <div style="font-size:13px;color:var(--text-light);margin-top:4px;">
              {{ sku._spuName || '' }}
            </div>
            <div style="margin-top:8px;">
              <span class="sku-price">¥{{ sku.seckillPrice || sku.price }}</span>
              <span class="sku-old" style="margin-left:8px;">¥{{ sku.price }}</span>
            </div>
            <div style="font-size:12px;color:var(--text-light);margin-top:4px;">
              剩余库存: {{ sku._redisStock !== undefined ? sku._redisStock : sku.stock }}
            </div>
          </div>
          <button class="btn btn-primary btn-lg" @click="doSeckill(sku)" :disabled="seckilling">
            {{ seckilling === sku.id ? '抢购中...' : '立即抢购' }}
          </button>
        </div>
        <div v-if="msg" :class="['alert', msgType === 'ok' ? 'alert-success' : 'alert-error']">{{ msg }}</div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { getSpuList, doSeckill } from '../api/index.js'

const router = useRouter()
const seckillSkus = ref([])
const loading = ref(true)
const seckilling = ref(false)
const msg = ref('')
const msgType = ref('ok')

onMounted(async () => {
  try {
    const res = await getSpuList({ page: 1, size: 20 })
    const spus = res.data?.records || []
    const allSkus = []
    spus.forEach(spu => {
      (spu.skuList || []).forEach(sku => {
        allSkus.push({ ...sku, _spuName: spu.name })
      })
    })
    seckillSkus.value = allSkus.slice(0, 6)
  } finally {
    loading.value = false
  }
})

async function doS(sku) {
  if (!localStorage.getItem('token')) { router.push('/login'); return }
  seckilling.value = sku.id
  try {
    await doSeckill(sku.id)
    msg.value = '抢购成功！订单处理中...'
    msgType.value = 'ok'
  } catch (e) {
    msg.value = e.message
    msgType.value = 'err'
  } finally {
    seckilling.value = false
  }
}
</script>
