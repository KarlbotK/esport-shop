<template>
  <div class="page">
    <div class="container">
      <h1 class="page-title">📊 销售管理</h1>

      <!-- 统计卡片 -->
      <div class="stats-grid">
        <div class="stat-card"><div class="value">{{ dash.spuCount || 0 }}</div><div class="label">商品数</div></div>
        <div class="stat-card"><div class="value">{{ dash.skuCount || 0 }}</div><div class="label">SKU数</div></div>
        <div class="stat-card"><div class="value">{{ dash.browseCount || 0 }}</div><div class="label">今日浏览</div></div>
        <div class="stat-card"><div class="value">{{ todayOrders }}</div><div class="label">今日订单</div></div>
      </div>

      <!-- Tab 导航 -->
      <div class="tabs" style="display:flex;gap:8px;margin-bottom:20px;">
        <button v-for="tab in tabs" :key="tab.key" :class="['btn', activeTab === tab.key ? 'btn-primary' : 'btn-outline', 'btn-sm']" @click="activeTab = tab.key">{{ tab.label }}</button>
      </div>

      <!-- Tab: 商品管理 -->
      <div v-if="activeTab === 'products'">
        <div style="display:flex;gap:16px;margin-bottom:16px;">
          <input v-model="searchQuery" placeholder="搜索商品..." @keyup.enter="loadProducts" style="padding:8px 12px;border:1px solid var(--border);border-radius:6px;flex:1;" />
          <button class="btn btn-primary btn-sm" @click="showAddForm = !showAddForm">+ 添加商品</button>
        </div>

        <!-- 添加商品表单 -->
        <div v-if="showAddForm" class="table-wrapper" style="margin-bottom:16px;">
          <h3 style="margin-bottom:12px;">添加新商品</h3>
          <div style="display:grid;grid-template-columns:1fr 1fr;gap:12px;">
            <div class="form-group"><label>名称</label><input v-model="spuForm.name" /></div>
            <div class="form-group"><label>分类</label>
              <select v-model.number="spuForm.categoryId">
                <option v-for="c in categories" :key="c.id" :value="c.id">{{ c.name }}</option>
              </select>
            </div>
            <div class="form-group"><label>品牌ID</label><input v-model.number="spuForm.brandId" type="number" /></div>
            <div class="form-group"><label>状态</label>
              <select v-model.number="spuForm.publishStatus">
                <option :value="1">上架</option><option :value="0">下架</option>
              </select>
            </div>
          </div>
          <div class="form-group"><label>描述</label><textarea v-model="spuForm.description" rows="2"></textarea></div>
          <div style="display:flex;gap:8px;margin-top:12px;">
            <button class="btn btn-primary" @click="doAddSpu" :disabled="addingSpu">保存</button>
            <button class="btn btn-outline" @click="showAddForm = false">取消</button>
          </div>
          <div v-if="spuMsg" class="alert alert-success" style="margin-top:8px;">{{ spuMsg }}</div>
        </div>

        <!-- 商品列表 -->
        <div class="table-wrapper">
          <table>
            <thead><tr><th>ID</th><th>名称</th><th>分类</th><th>品牌</th><th>最低价</th><th>状态</th><th>操作</th></tr></thead>
            <tbody>
              <tr v-for="p in productList" :key="p.id">
                <td>{{ p.id }}</td>
                <td>{{ p.name }}</td>
                <td>{{ p._category }}</td>
                <td>{{ p._brand }}</td>
                <td>¥{{ p.minPrice ?? '--' }}</td>
                <td>{{ p.publishStatus === 1 ? '✅ 上架' : '⛔ 下架' }}</td>
                <td>
                  <button class="btn btn-sm btn-outline" @click="editProduct(p)" style="margin-right:4px;">编辑</button>
                  <button class="btn btn-sm btn-outline" style="color:#ef4444;border-color:#ef4444;" @click="doDeleteSpu(p.id)">删除</button>
                </td>
              </tr>
            </tbody>
          </table>
        </div>

        <!-- 编辑商品弹窗 -->
        <div v-if="editingSpu" class="modal-overlay" @click.self="editingSpu = null">
          <div class="modal" style="background:#fff;padding:24px;border-radius:12px;max-width:500px;margin:40px auto;">
            <h3 style="margin-bottom:16px;">编辑商品 #{{ editingSpu.id }}</h3>
            <div class="form-group"><label>名称</label><input v-model="editForm.name" /></div>
            <div class="form-group"><label>分类ID</label><input v-model.number="editForm.categoryId" type="number" /></div>
            <div class="form-group"><label>品牌ID</label><input v-model.number="editForm.brandId" type="number" /></div>
            <div class="form-group"><label>描述</label><textarea v-model="editForm.description" rows="2"></textarea></div>
            <div class="form-group"><label>状态</label>
              <select v-model.number="editForm.publishStatus">
                <option :value="1">上架</option><option :value="0">下架</option>
              </select>
            </div>
            <div style="display:flex;gap:8px;margin-top:12px;">
              <button class="btn btn-primary" @click="doEditSpu">保存</button>
              <button class="btn btn-outline" @click="editingSpu = null">取消</button>
            </div>
          </div>
        </div>
      </div>

      <!-- Tab: 库存管理 -->
      <div v-if="activeTab === 'stock'" class="table-wrapper">
        <h3 style="margin-bottom:16px;">修改库存</h3>
        <div style="display:grid;grid-template-columns:1fr 1fr;gap:12px;max-width:400px;">
          <div class="form-group"><label>SKU ID</label><input v-model.number="stockForm.skuId" type="number" /></div>
          <div class="form-group"><label>新库存</label><input v-model.number="stockForm.stock" type="number" /></div>
        </div>
        <button class="btn btn-primary" @click="doUpdateStock" style="margin-top:8px;">更新</button>
        <div v-if="stockMsg" class="alert alert-success" style="margin-top:8px;">{{ stockMsg }}</div>

        <h3 style="margin:24px 0 12px;">所有SKU库存</h3>
        <table>
          <thead><tr><th>SKU ID</th><th>名称</th><th>所属SPU</th><th>价格</th><th>库存</th></tr></thead>
          <tbody>
            <tr v-for="s in allSkus" :key="s.id">
              <td>{{ s.id }}</td><td>{{ s.skuName }}</td><td>{{ s._spuName }}</td><td>¥{{ s.price }}</td>
              <td :style="{ color: s.stock <= 5 ? '#ef4444' : 'inherit', fontWeight: s.stock <= 5 ? 'bold' : 'normal' }">
                {{ s.stock }} {{ s.stock <= 5 ? '⚠️' : '' }}
              </td>
            </tr>
          </tbody>
        </table>
      </div>

      <!-- Tab: 分类管理 -->
      <div v-if="activeTab === 'categories'" class="table-wrapper">
        <h3 style="margin-bottom:12px;">分类管理</h3>
        <div style="display:flex;gap:8px;margin-bottom:16px;">
          <input v-model="catForm.name" placeholder="新分类名称" style="padding:8px 12px;border:1px solid var(--border);border-radius:6px;" />
          <button class="btn btn-primary btn-sm" @click="doAddCat">添加</button>
        </div>
        <table>
          <thead><tr><th>ID</th><th>名称</th><th>排序</th><th>操作</th></tr></thead>
          <tbody>
            <tr v-for="c in categories" :key="c.id">
              <td>{{ c.id }}</td><td>{{ c.name }}</td><td>{{ c.sort }}</td>
              <td><button class="btn btn-sm btn-outline" style="color:#ef4444;border-color:#ef4444;" @click="doDeleteCat(c.id)">删除</button></td>
            </tr>
          </tbody>
        </table>
      </div>

      <!-- Tab: 浏览日志 -->
      <div v-if="activeTab === 'logs'" class="table-wrapper">
        <h3 style="margin-bottom:12px;">浏览日志（最近50条）</h3>
        <div v-if="logs.length === 0" style="color:#999;padding:20px;">暂无数据</div>
        <table v-else>
          <thead><tr><th>商品</th><th>停留</th><th>IP</th><th>时间</th></tr></thead>
          <tbody>
            <tr v-for="l in logs" :key="l.id">
              <td>{{ l.spuName || '已下架商品 #' + l.spuId }}</td>
              <td>{{ l.durationSeconds }}s</td>
              <td style="font-size:12px;color:var(--text-light);">{{ l.ipAddress || '--' }}</td>
              <td style="font-size:12px;color:var(--text-light);">{{ formatTime(l.createTime) }}</td>
            </tr>
          </tbody>
        </table>
      </div>

      <!-- Tab: 订单监控 -->
      <div v-if="activeTab === 'orders'" class="table-wrapper">
        <h3 style="margin-bottom:12px;">订单监控</h3>
        <div v-if="orders.length === 0" style="color:#999;padding:20px;">暂无订单</div>
        <table v-else>
          <thead><tr><th>订单ID</th><th>用户</th><th>金额</th><th>状态</th><th>时间</th></tr></thead>
          <tbody>
            <tr v-for="o in orders" :key="o.id">
              <td>#{{ o.id }}</td><td>用户#{{ o.userId }}</td>
              <td style="color:var(--primary);font-weight:bold;">¥{{ o.totalAmount }}</td>
              <td>{{ ['待付款','已付款','已发货','已完成','已取消'][o.status] || '未知' }}</td>
              <td style="font-size:12px;color:var(--text-light);">{{ formatTime(o.createTime) }}</td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import {
  getDashboard, getBrowseLogs, getSpuList, getCategories, getBrands,
  addSpu, updateSpu, deleteSpu, updateStock, addCategory, deleteCategory,
  getOrderList
} from '../api/index.js'

const activeTab = ref('products')
const tabs = [
  { key: 'products', label: '📦 商品管理' },
  { key: 'stock', label: '📊 库存管理' },
  { key: 'categories', label: '🏷️ 分类管理' },
  { key: 'logs', label: '👁️ 浏览日志' },
  { key: 'orders', label: '📋 订单监控' },
]

const dash = ref({})
const logs = ref([])
const productList = ref([])
const categories = ref([])
const brands = ref({})
const allSkus = ref([])
const orders = ref([])
const searchQuery = ref('')
const todayOrders = ref(0)

// Forms
const showAddForm = ref(false)
const spuForm = ref({ name: '', categoryId: 1, brandId: 1, description: '', publishStatus: 1 })
const stockForm = ref({ skuId: '', stock: 0 })
const catForm = ref({ name: '' })
const spuMsg = ref('')
const stockMsg = ref('')
const addingSpu = ref(false)

// Edit product
const editingSpu = ref(null)
const editForm = ref({ name: '', categoryId: 1, brandId: 1, description: '', publishStatus: 1 })

function formatTime(t) {
  if (!t) return '--'
  return t.slice(0, 19).replace('T', ' ')
}

async function loadAll() {
  try {
    const [d, l] = await Promise.all([
      getDashboard(),
      getBrowseLogs({ page: 1, size: 50 }),
      getCategories().catch(() => ({ data: [] })),
      getBrands().catch(() => ({ data: [] })),
    ].concat(dashResolves => dashResolves))
    // Actually let me do this properly
  } catch (e) { /* ignore */ }
}

onMounted(async () => {
  try {
    const [d, l, catsRes, brandsRes] = await Promise.all([
      getDashboard(), getBrowseLogs({ page: 1, size: 50 }),
      getCategories(), getBrands()
    ])
    dash.value = d.data || {}
    logs.value = (l.data?.records || [])
    categories.value = catsRes.data || []
    ;(brandsRes.data || []).forEach(b => brands.value[b.id] = b.name)
    await loadProducts()
    await loadAllSkus()
    await loadOrders()
  } catch (e) { console.error(e) }
})

async function loadProducts() {
  try {
    const params = { page: 1, size: 100 }
    if (searchQuery.value) params.keyword = searchQuery.value
    const res = await getSpuList(params)
    productList.value = (res.data?.records || []).map(p => ({
      ...p,
      _category: categories.value.find(c => c.id === p.categoryId)?.name || '',
      _brand: brands.value[p.brandId] || '',
    }))
  } catch (e) { productList.value = [] }
}

async function loadAllSkus() {
  try {
    const res = await getSpuList({ page: 1, size: 100 })
    const spus = res.data?.records || []
    const all = []
    for (const spu of spus.slice(0, 20)) {
      const detail = await (await import('../api/index.js')).getSpuDetail(spu.id)
      const skus = detail.data?.skuList || []
      skus.forEach(s => { s._spuName = spu.name })
      all.push(...skus)
    }
    allSkus.value = all
  } catch (e) { allSkus.value = [] }
}

async function loadOrders() {
  try {
    const res = await getOrderList()
    orders.value = res.data || []
    todayOrders.value = orders.value.filter(o => {
      if (!o.createTime) return false
      const today = new Date().toISOString().slice(0, 10)
      return o.createTime.slice(0, 10) === today
    }).length
  } catch (e) { orders.value = [] }
}

async function doAddSpu() {
  addingSpu.value = true
  try {
    await addSpu(spuForm.value)
    spuMsg.value = '✅ 商品添加成功'
    spuForm.value = { name: '', categoryId: 1, brandId: 1, description: '', publishStatus: 1 }
    await loadProducts()
  } catch (e) { spuMsg.value = '❌ ' + e.message }
  finally { addingSpu.value = false }
}

function editProduct(p) {
  editingSpu.value = p
  editForm.value = {
    name: p.name, categoryId: p.categoryId, brandId: p.brandId,
    description: p.description || '', publishStatus: p.publishStatus ?? 1,
  }
}

async function doEditSpu() {
  try {
    await updateSpu(editingSpu.value.id, editForm.value)
    editingSpu.value = null
    await loadProducts()
  } catch (e) { alert(e.message) }
}

async function doDeleteSpu(id) {
  if (!confirm('确定要删除此商品吗？')) return
  try {
    await deleteSpu(id)
    await loadProducts()
  } catch (e) { alert(e.message) }
}

async function doUpdateStock() {
  try {
    await updateStock(stockForm.value.skuId, stockForm.value.stock)
    stockMsg.value = '✅ 库存更新成功'
    await loadAllSkus()
  } catch (e) { stockMsg.value = '❌ ' + e.message }
}

async function doAddCat() {
  if (!catForm.value.name) return
  try {
    await addCategory({ name: catForm.value.name, parentId: 0, sort: 0 })
    catForm.value.name = ''
    const r = await getCategories()
    categories.value = r.data || []
  } catch (e) { alert(e.message) }
}

async function doDeleteCat(id) {
  if (!confirm('确定要删除此分类吗？')) return
  try {
    await deleteCategory(id)
    const r = await getCategories()
    categories.value = r.data || []
  } catch (e) { alert(e.message) }
}
</script>
