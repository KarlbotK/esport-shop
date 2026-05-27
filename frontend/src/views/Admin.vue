<template>
  <div class="page">
    <div class="container">
      <h1 class="page-title">🔧 管理员面板</h1>

      <!-- 统计卡片 -->
      <div class="stats-grid">
        <div class="stat-card"><div class="value">{{ totalRevenue }}</div><div class="label">总销售额</div></div>
        <div class="stat-card"><div class="value">{{ totalOrders }}</div><div class="label">总订单</div></div>
        <div class="stat-card">
          <div :class="['value', anomalyStatus === 'normal' ? '' : (anomalyStatus === 'surge' ? 'text-success' : 'text-danger')]">
            {{ anomalyCount || 0 }}
          </div>
          <div class="label">异常预警</div>
        </div>
        <div class="stat-card"><div class="value">{{ salesUserCount }}</div><div class="label">销售人员</div></div>
      </div>

      <!-- Tab 导航 -->
      <div class="tabs" style="display:flex;gap:8px;margin-bottom:20px;flex-wrap:wrap;">
        <button v-for="tab in tabs" :key="tab.key"
          :class="['btn', activeTab === tab.key ? 'btn-primary' : 'btn-outline', 'btn-sm']"
          @click="activeTab = tab.key">{{ tab.label }}</button>
      </div>

      <!-- Tab: 销售趋势 -->
      <div v-if="activeTab === 'trend'">
        <div style="display:flex;gap:8px;margin-bottom:16px;">
          <button v-for="p in ['daily','weekly','monthly']" :key="p"
            :class="['btn', trendPeriod === p ? 'btn-primary' : 'btn-outline', 'btn-sm']"
            @click="trendPeriod = p; loadTrend()">{{ {daily:'日',weekly:'周',monthly:'月'}[p] }}</button>
        </div>
        <div class="table-wrapper">
          <h3 style="margin-bottom:12px;">销售趋势图（{{ {daily:'日',weekly:'周',monthly:'月'}[trendPeriod] }}）</h3>
          <!-- 柱状图 -->
          <div v-if="trendData.length === 0" style="color:#999;padding:20px;text-align:center;">暂无销售数据</div>
          <div v-else style="display:flex;align-items:end;gap:4px;height:200px;padding:20px 0;border-bottom:2px solid #e8e8e8;overflow-x:auto;">
            <div v-for="t in trendData" :key="t.periodLabel"
              style="display:flex;flex-direction:column;align-items:center;min-width:50px;">
              <div style="font-size:11px;color:var(--text-light);margin-bottom:4px;">¥{{ t.revenue }}</div>
              <div :style="{
                width: '36px',
                height: Math.max(4, (t.revenue / maxRevenue) * 160) + 'px',
                background: 'linear-gradient(180deg, var(--primary), #f97316)',
                borderRadius: '4px 4px 0 0',
                cursor: 'pointer',
                transition: 'height 0.3s',
              }" :title="`${t.periodLabel}: ¥${t.revenue} (${t.orderCount}单)`"></div>
              <div style="font-size:10px;color:var(--text-light);margin-top:4px;transform:rotate(-30deg);white-space:nowrap;">
                {{ t.periodLabel?.slice(-5) }}
              </div>
            </div>
          </div>
          <!-- 表格 -->
          <table style="margin-top:16px;">
            <thead><tr><th>周期</th><th>销售额</th><th>订单数</th></tr></thead>
            <tbody>
              <tr v-for="t in trendData" :key="t.periodLabel">
                <td>{{ t.periodLabel }}</td><td style="color:var(--primary);font-weight:bold;">¥{{ t.revenue }}</td>
                <td>{{ t.orderCount }}</td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>

      <!-- Tab: 销售排行 -->
      <div v-if="activeTab === 'ranking'">
        <div style="display:flex;gap:8px;margin-bottom:16px;">
          <button v-for="p in ['daily','weekly','monthly']" :key="p"
            :class="['btn', rankingPeriod === p ? 'btn-primary' : 'btn-outline', 'btn-sm']"
            @click="rankingPeriod = p; loadRanking()">{{ {daily:'日',weekly:'周',monthly:'月'}[p] }}</button>
        </div>
        <div class="table-wrapper">
          <h3 style="margin-bottom:12px;">🏆 销售排行（{{ {daily:'日',weekly:'周',monthly:'月'}[rankingPeriod] }}）</h3>
          <div v-if="ranking.length === 0" style="color:#999;padding:20px;">暂无数据</div>
          <table v-else>
            <thead><tr><th>#</th><th>SKU</th><th>商品</th><th>销量</th><th>销售额</th></tr></thead>
            <tbody>
              <tr v-for="(r, i) in ranking" :key="r.skuId">
                <td style="text-align:center;">
                  <span v-if="i === 0" style="font-size:20px;">🥇</span>
                  <span v-else-if="i === 1" style="font-size:20px;">🥈</span>
                  <span v-else-if="i === 2" style="font-size:20px;">🥉</span>
                  <span v-else>{{ i + 1 }}</span>
                </td>
                <td>{{ r.skuName }}</td><td>{{ r.spuName }}</td>
                <td>{{ r.quantity }}</td>
                <td style="color:var(--primary);font-weight:bold;">¥{{ r.revenue }}</td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>

      <!-- Tab: 销售报表 -->
      <div v-if="activeTab === 'reports'" class="table-wrapper">
        <h3 style="margin-bottom:12px;">销售报表（按SKU汇总）</h3>
        <div v-if="reports.length === 0" style="color:#999;padding:20px;">暂无数据</div>
        <table v-else>
          <thead><tr><th>SKU</th><th>商品</th><th>销量</th><th>销售额</th><th>占比</th></tr></thead>
          <tbody>
            <tr v-for="r in reports" :key="r.skuId">
              <td>{{ r.skuName }}</td><td>{{ r.spuName }}</td><td>{{ r.quantity }}</td>
              <td style="color:var(--primary);font-weight:bold;">¥{{ r.revenue }}</td>
              <td>
                <div style="display:flex;align-items:center;gap:6px;">
                  <div :style="{ width: (r.revenue / maxReportRevenue * 100) + '%', height:'8px', background:'var(--primary)', borderRadius:'4px', maxWidth:'100px' }"></div>
                  <span style="font-size:12px;color:var(--text-light);">{{ (r.revenue / maxReportRevenue * 100).toFixed(1) }}%</span>
                </div>
              </td>
            </tr>
          </tbody>
        </table>
      </div>

      <!-- Tab: 异常检测 -->
      <div v-if="activeTab === 'anomaly'">
        <div class="table-wrapper" style="margin-bottom:16px;">
          <h3 style="margin-bottom:12px;">📊 3-Sigma 异常检测</h3>
          <div v-if="anomalyData.mean === undefined" style="color:#999;padding:20px;">暂无足够数据</div>
          <div v-else>
            <div class="stats-grid" style="margin-bottom:16px;">
              <div class="stat-card"><div class="value" style="font-size:18px;">{{ anomalyData.mean.toFixed(2) }}</div><div class="label">日均销售额</div></div>
              <div class="stat-card"><div class="value" style="font-size:18px;">{{ anomalyData.stddev.toFixed(2) }}</div><div class="label">标准差</div></div>
              <div class="stat-card"><div class="value" style="font-size:18px;color:#10b981;">{{ anomalyData.upperBound.toFixed(2) }}</div><div class="label">上限 (μ+3σ)</div></div>
              <div class="stat-card"><div class="value" style="font-size:18px;color:#ef4444;">{{ anomalyData.lowerBound.toFixed(2) }}</div><div class="label">下限 (μ-3σ)</div></div>
            </div>
            <div v-if="anomalyData.anomalies.length > 0">
              <h4 style="color:#ef4444;margin-bottom:8px;">⚠️ 检测到 {{ anomalyData.anomalies.length }} 个异常</h4>
              <table>
                <thead><tr><th>日期</th><th>销售额</th><th>类型</th></tr></thead>
                <tbody>
                  <tr v-for="a in anomalyData.anomalies" :key="a.date">
                    <td>{{ a.date }}</td>
                    <td :style="{ color: a.type === 'surge' ? '#10b981' : '#ef4444', fontWeight: 'bold' }">¥{{ a.revenue }}</td>
                    <td>
                      <span v-if="a.type === 'surge'" style="color:#10b981;">📈 激增</span>
                      <span v-else style="color:#ef4444;">📉 暴跌</span>
                    </td>
                  </tr>
                </tbody>
              </table>
            </div>
            <div v-else style="color:#10b981;font-weight:bold;padding:12px;">✅ 未检测到异常波动</div>
          </div>
        </div>
      </div>

      <!-- Tab: 销售人员管理 -->
      <div v-if="activeTab === 'sales'">
        <div class="table-wrapper">
          <h3 style="margin-bottom:12px;">添加销售人员</h3>
          <div style="display:grid;grid-template-columns:1fr 1fr;gap:12px;max-width:400px;">
            <div class="form-group"><label>用户名</label><input v-model="salesForm.username" /></div>
            <div class="form-group"><label>密码</label><input v-model="salesForm.password" type="password" /></div>
          </div>
          <button class="btn btn-primary" @click="addSalesman" :disabled="adding" style="margin-top:8px;">添加</button>
          <div v-if="salesMsg" class="alert alert-success" style="margin-top:12px;">{{ salesMsg }}</div>
        </div>
        <div class="table-wrapper" style="margin-top:16px;">
          <h3 style="margin-bottom:12px;">现有销售人员</h3>
          <div v-if="salesUsers.length === 0" style="color:#999;padding:20px;">暂无</div>
          <table v-else>
            <thead><tr><th>ID</th><th>用户名</th><th>邮箱</th><th>创建时间</th></tr></thead>
            <tbody>
              <tr v-for="u in salesUsers" :key="u.id">
                <td>{{ u.id }}</td><td>{{ u.username }}</td><td>{{ u.email || '--' }}</td>
                <td style="font-size:12px;">{{ formatTime(u.createTime) }}</td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import {
  getSalesReport, getRanking, getTrend, getAnomaly,
  addSales, deleteSales, resetPwd,
  getSpuList, getCategories, getBrands
} from '../api/index.js'

const activeTab = ref('trend')
const tabs = [
  { key: 'trend', label: '📈 销售趋势' },
  { key: 'ranking', label: '🏆 销售排行' },
  { key: 'reports', label: '📋 销售报表' },
  { key: 'anomaly', label: '⚠️ 异常检测' },
  { key: 'sales', label: '👥 人员管理' },
]

// Stats
const totalRevenue = ref('--')
const totalOrders = ref(0)
const anomalyCount = ref(0)
const anomalyStatus = ref('normal')
const salesUserCount = ref(0)

// Trend
const trendPeriod = ref('daily')
const trendData = ref([])
const maxRevenue = ref(1)

// Ranking
const rankingPeriod = ref('daily')
const ranking = ref([])
const reports = ref([])
const maxReportRevenue = ref(1)

// Anomaly
const anomalyData = ref({})

// Sales users
const salesUsers = ref([])
const salesForm = ref({ username: '', password: '' })
const salesMsg = ref('')
const adding = ref(false)

function formatTime(t) {
  if (!t) return '--'
  return t.slice(0, 19).replace('T', ' ')
}

onMounted(async () => {
  await Promise.all([loadTrend(), loadRanking(), loadReports(), loadAnomaly(), loadSalesUsers()])
})

async function loadTrend() {
  try {
    const res = await getTrend({ period: trendPeriod.value })
    trendData.value = res.data || []
    maxRevenue.value = Math.max(1, ...trendData.value.map(t => t.revenue))
  } catch (e) { trendData.value = [] }
}

async function loadRanking() {
  try {
    const res = await getRanking({ period: rankingPeriod.value })
    ranking.value = res.data || []
  } catch (e) { ranking.value = [] }
}

async function loadReports() {
  try {
    const [r, spuRes] = await Promise.all([
      getSalesReport(), getSpuList({ page: 1, size: 1 }).catch(() => ({ data: { records: [] } }))
    ])
    reports.value = r.data || []
    maxReportRevenue.value = Math.max(1, ...reports.value.map(r => r.revenue))
    totalOrders.value = reports.value.reduce((s, r) => s + r.quantity, 0)
    totalRevenue.value = reports.value.reduce((s, r) => s + r.revenue, 0).toFixed(2)
  } catch (e) { reports.value = [] }
}

async function loadAnomaly() {
  try {
    const res = await getAnomaly()
    anomalyData.value = res.data || {}
    anomalyCount.value = (res.data?.anomalies || []).length
    anomalyStatus.value = anomalyCount.value > 0 ? 'surge' : 'normal'
  } catch (e) { anomalyData.value = {} }
}

async function loadSalesUsers() {
  try {
    // Fetch all users with SALES role from the getSpuList or some endpoint
    // We don't have a list sales endpoint, so set a placeholder
    salesUserCount.value = '--'
  } catch (e) { /* ignore */ }
}

async function addSalesman() {
  adding.value = true
  try {
    await addSales(salesForm.value)
    salesMsg.value = '✅ 销售人员添加成功'
    salesForm.value = { username: '', password: '' }
    salesUserCount.value = typeof salesUserCount.value === 'number' ? salesUserCount.value + 1 : 1
  } catch (e) { salesMsg.value = '❌ ' + e.message }
  finally { adding.value = false }
}
</script>
