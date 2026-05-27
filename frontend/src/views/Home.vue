<template>
  <div class="page">
    <div class="container">
      <div class="banner">
        <h1>专业电竞装备商城</h1>
        <p>鼠标 · 键盘 · 耳机 · 鼠标垫 · 电竞椅 — 为胜利而生</p>
      </div>

      <div class="cat-nav">
        <router-link v-for="c in categories" :key="c.id"
          :to="{ name: 'Products', query: { categoryId: c.id } }">
          {{ c.name }}
        </router-link>
        <span v-if="categories.length === 0" style="color:#999;">加载分类中...</span>
      </div>

      <h2 style="font-size:20px;margin-bottom:16px;">🔥 热门商品</h2>
      <div class="product-grid">
        <ProductCard v-for="p in hotProducts" :key="p.spuId" :spu="p" />
      </div>

      <h2 style="font-size:20px;margin:32px 0 16px;">🆕 全部商品</h2>
      <div class="product-grid">
        <ProductCard v-for="p in products" :key="p.id" :spu="p" />
      </div>
      <div class="pagination">
        <button :disabled="page <= 1" @click="page--; loadProducts()">上一页</button>
        <button class="active">{{ page }}</button>
        <button @click="page++; loadProducts()">下一页</button>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { getSpuList, getHotProducts, getCategories, getBrands } from '../api/index.js'
import ProductCard from '../components/ProductCard.vue'

const products = ref([])
const hotProducts = ref([])
const categories = ref([])
const brands = ref({})
const page = ref(1)

onMounted(async () => {
  try {
    const [cats, brandsRes] = await Promise.all([getCategories(), getBrands()])
    categories.value = cats.data || []
    ;(brandsRes.data || []).forEach(b => brands.value[b.id] = b.name)
  } catch (e) {
    console.error('Failed to load categories/brands:', e)
  }
  loadProducts()
  loadHot()
})

async function loadProducts() {
  const res = await getSpuList({ page: page.value, size: 12 })
  const list = res.data?.records || []
  list.forEach(p => {
    p._category = categories.value.find(c => c.id === p.categoryId)?.name || ''
    p._brand = brands.value[p.brandId] || ''
    p._minPrice = p.minPrice ?? '--'
  })
  products.value = list
}

async function loadHot() {
  try {
    const res = await getHotProducts({ limit: 8 })
    hotProducts.value = (res.data || []).map(p => ({
      id: p.id || p.spuId,
      name: p.name || p.spuName || '未知商品',
      _minPrice: p.minPrice ?? p._minPrice ?? '--',
      _brand: p.brandName || p._brand || '',
      _category: p.categoryId ? (categories.value.find(c => c.id === p.categoryId)?.name || '') : '',
    }))
  } catch (e) {
    hotProducts.value = []
  }
}
</script>
