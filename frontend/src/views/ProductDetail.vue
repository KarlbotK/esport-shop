<template>
  <div class="page">
    <div class="container">
      <div class="breadcrumb">
        <router-link to="/">首页</router-link>
        <span>/</span>
        <router-link :to="{ path: '/products', query: { categoryId: spu.categoryId } }">
          {{ spu._category }}
        </router-link>
        <span>/</span>
        <span>{{ spu.spuName }}</span>
      </div>
      <div class="detail-grid">
        <div class="detail-img" :style="{ background: `linear-gradient(135deg, ${color1}, ${color2})`, display: 'flex', alignItems: 'center', justifyContent: 'center', fontSize: '48px', color: '#fff' }">
          {{ (spu.spuName || '').slice(0, 4) || '🎮' }}
        </div>
        <div class="detail-info">
          <h1>{{ spu.spuName }}</h1>
          <p style="color:var(--text-light);margin-top:4px;">{{ spu._brand }} · {{ spu._category }}</p>
          <div class="detail-price">
            <div class="price">¥{{ selectedSku?.price || '--' }}</div>
            <div style="font-size:13px;color:var(--text-light);margin-top:4px;">
              {{ selectedSku?.skuName || '请选择规格' }}
            </div>
          </div>
          <div class="sku-selector" v-if="skus.length > 0">
            <h4>选择规格</h4>
            <div class="sku-options">
              <div v-for="sku in skus" :key="sku.id"
                :class="['sku-option', { selected: selectedSku?.id === sku.id }]"
                @click="selectSku(sku)">
                {{ sku.skuName }}
              </div>
            </div>
            <div class="stock-info" v-if="selectedSku">
              库存: {{ selectedSku.stock }} 件
            </div>
          </div>
          <div class="detail-actions">
            <button class="btn btn-outline btn-lg" @click="addToCart" :disabled="!selectedSku || selectedSku.stock <= 0">
              加入购物车
            </button>
            <button class="btn btn-primary btn-lg" @click="buyNow" :disabled="!selectedSku || selectedSku.stock <= 0">
              立即购买
            </button>
          </div>
          <div style="margin-top:24px;color:var(--text-light);font-size:13px;line-height:1.8;white-space:pre-wrap;">
            {{ spu.description }}
          </div>
        </div>
      </div>

      <h2 style="font-size:20px;margin:32px 0 16px;">看了此商品的人还看了</h2>
      <div class="product-grid">
        <ProductCard v-for="s in similar" :key="s.id" :spu="s" />
      </div>

      <h2 style="font-size:20px;margin:32px 0 16px;">🤖 协同过滤推荐</h2>
      <div class="product-grid">
        <ProductCard v-for="c in collaborative" :key="c.id" :spu="c" />
      </div>
      <div v-if="collaborative.length === 0" style="color:#999;font-size:13px;">系统正在学习用户偏好，推荐数据即将上线</div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, watch } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { getSpuDetail, getSimilar, getCollaborative, createOrder, getCategories, getBrands } from '../api/index.js'
import { useCartStore } from '../stores/cart.js'
import ProductCard from '../components/ProductCard.vue'

const route = useRoute()
const router = useRouter()
const cart = useCartStore()
const spu = ref({})
const skus = ref([])
const selectedSku = ref(null)
const similar = ref([])
const collaborative = ref([])
const color1 = '#' + Math.floor(Math.random()*16777215).toString(16)
const color2 = '#' + Math.floor(Math.random()*16777215).toString(16)

// Shared cache for lookups
const catMap = {}
const brdMap = {}

async function loadProduct(id) {
  // Load categories/brands once
  if (Object.keys(catMap).length === 0) {
    const [cats, bds] = await Promise.all([getCategories(), getBrands()])
    ;(cats.data || []).forEach(c => catMap[c.id] = c.name)
    ;(bds.data || []).forEach(b => brdMap[b.id] = b.name)
  }

  // Reset state
  selectedSku.value = null
  similar.value = []
  collaborative.value = []

  // Load SPU detail
  const res = await getSpuDetail(id)
  const vo = res.data || {}
  spu.value = vo
  spu.value._category = catMap[vo.categoryId] || ''
  spu.value._brand = brdMap[vo.brandId] || ''
  skus.value = vo.skuList || []
  if (skus.value.length > 0) selectedSku.value = skus.value[0]

  // Load similar products
  try {
    const simRes = await getSimilar(id)
    similar.value = (simRes.data || []).map(s => ({
      ...s,
      _category: catMap[s.categoryId] || '',
      _brand: brdMap[s.brandId] || '',
      _minPrice: '查看详情'
    }))
  } catch (e) { /* ignore */ }

  // Load collaborative filtering
  try {
    const colRes = await getCollaborative(id)
    collaborative.value = (colRes.data || []).map(s => ({
      ...s, _category: catMap[s.categoryId] || '', _brand: brdMap[s.brandId] || '', _minPrice: '查看详情'
    }))
  } catch (e) { /* 协同过滤数据可能为空 */ }
}

onMounted(() => loadProduct(route.params.id))

// Watch route param changes — navigate between similar products without refresh
watch(() => route.params.id, (newId) => {
  if (newId) loadProduct(newId)
})

function selectSku(sku) { selectedSku.value = sku }

function addToCart() {
  if (!selectedSku.value) return
  selectedSku.value._spuName = spu.value.spuName
  cart.addItem(selectedSku.value)
  alert('已加入购物车')
}

async function buyNow() {
  if (!selectedSku.value) return
  if (!localStorage.getItem('token')) return router.push('/login')
  try {
    await createOrder({ items: [{ skuId: selectedSku.value.id, quantity: 1 }] })
    router.push('/orders')
  } catch (e) { alert(e.message) }
}
</script>
