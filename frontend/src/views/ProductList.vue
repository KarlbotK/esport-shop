<template>
  <div class="page">
    <div class="container">
      <div class="breadcrumb">
        <router-link to="/">首页</router-link>
        <span>/</span>
        <span>全部商品</span>
      </div>
      <div class="filter-bar">
        <select v-model="categoryId" @change="search">
          <option value="">全部分类</option>
          <option v-for="c in categories" :key="c.id" :value="c.id">{{ c.name }}</option>
        </select>
        <select v-model="brandId" @change="search">
          <option value="">全部品牌</option>
          <option v-for="b in brands" :key="b.id" :value="b.id">{{ b.name }}</option>
        </select>
        <input v-model="keyword" placeholder="搜索商品..." @keyup.enter="search" style="padding:8px 12px;border:1px solid #e8e8e8;border-radius:6px;width:200px;" />
        <button class="btn btn-primary btn-sm" @click="search">筛选</button>
      </div>
      <div v-if="error" class="alert alert-error">{{ error }}</div>
      <div v-if="loading" style="text-align:center;padding:60px;">加载中...</div>
      <div v-else-if="products.length === 0" style="text-align:center;padding:60px;color:#999;">
        暂无商品
      </div>
      <div v-else class="product-grid">
        <ProductCard v-for="p in products" :key="p.id" :spu="p" />
      </div>
      <div class="pagination" v-if="total > size">
        <button :disabled="page <= 1" @click="page--; search()">上一页</button>
        <template v-for="i in totalPages" :key="i">
          <button :class="{ active: i === page }" @click="page = i; search()">{{ i }}</button>
        </template>
        <button :disabled="page >= totalPages" @click="page++; search()">下一页</button>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, computed, watch } from 'vue'
import { useRoute } from 'vue-router'
import { getSpuList, getCategories, getBrands } from '../api/index.js'
import ProductCard from '../components/ProductCard.vue'

const route = useRoute()
const products = ref([])
const categories = ref([])
const brands = ref([])
const categoryId = ref('')
const brandId = ref('')
const keyword = ref('')
const page = ref(1)
const size = 12
const total = ref(0)
const loading = ref(true)
const error = ref('')

const totalPages = computed(() => Math.ceil(total.value / size))

function syncQueryFromRoute() {
  categoryId.value = String(route.query.categoryId || '')
  brandId.value = String(route.query.brandId || '')
  keyword.value = String(route.query.keyword || '')
}

onMounted(async () => {
  try {
    const [cats, bds] = await Promise.all([getCategories(), getBrands()])
    categories.value = cats.data || []
    brands.value = bds.data || []
  } catch (e) {
    console.error('Failed to load filters:', e)
  }
  syncQueryFromRoute()
  search()
})

watch(() => route.fullPath, () => {
  syncQueryFromRoute()
  page.value = 1
  search()
})

async function search() {
  loading.value = true
  error.value = ''
  try {
    const params = { page: page.value, size }
    if (categoryId.value) params.categoryId = categoryId.value
    if (brandId.value) params.brandId = brandId.value
    if (keyword.value) params.keyword = keyword.value
    const res = await getSpuList(params)
    products.value = (res.data?.records || []).map(p => ({
      ...p,
      _category: categories.value.find(c => c.id === p.categoryId)?.name || '',
      _brand: brands.value.find(b => b.id === p.brandId)?.name || '',
      _minPrice: '查看详情'
    }))
    total.value = res.data?.total || 0
  } catch (e) {
    console.error('Search failed:', e)
    error.value = '加载商品失败：' + e.message
  } finally {
    loading.value = false
  }
}
</script>
