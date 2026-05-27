import axios from 'axios'

const api = axios.create({
  baseURL: '/api',
  timeout: 30000,
})

api.interceptors.request.use(config => {
  const token = localStorage.getItem('token')
  if (token) config.headers.Authorization = `Bearer ${token}`
  return config
})

api.interceptors.response.use(
  res => res.data,
  err => {
    const msg = err.response?.data?.msg || '网络错误'
    return Promise.reject(new Error(msg))
  }
)

// -- User --
export const login = (data) => api.post('/user/login', data)
export const register = (data) => api.post('/user/register', data)

// -- SPU --
export const getSpuList = (params) => api.get('/spu/list', { params })
export const getSpuDetail = (id) => api.get(`/spu/detail/${id}`)
export const getHotProducts = (params) => api.get('/spu/hot', { params })
export const getSimilar = (spuId) => api.get(`/spu/similar/${spuId}`)
export const getCollaborative = (spuId) => api.get(`/spu/collaborative/${spuId}`)
export const getUserProfile = () => api.get('/user/profile')

// -- Category --
export const getCategories = () => api.get('/category/list')
export const getBrands = () => api.get('/category/brands')

// -- Order --
export const createOrder = (data) => api.post('/order/create', data)
export const getOrders = () => api.get('/order/list')

// -- Seckill --
export const doSeckill = (skuId) => api.post(`/seckill/${skuId}`)

// -- Recommend --
export const chatRecommend = (message) => api.post('/recommend/chat', { message }, { timeout: 120000 })

// -- Sales --
export const addSpu = (data) => api.post('/sales/spu', data)
export const updateSpu = (id, data) => api.put(`/sales/spu/${id}`, data)
export const updateStock = (id, stock) => api.put(`/sales/sku/${id}/stock`, null, { params: { stock } })
export const addCategory = (data) => api.post('/sales/category', data)
export const deleteCategory = (id) => api.delete(`/sales/category/${id}`)
export const getBrowseLogs = (params) => api.get('/sales/browse-logs', { params })
export const getDashboard = () => api.get('/sales/dashboard')

// -- Admin --
export const addSales = (data) => api.post('/admin/sales', data)
export const deleteSales = (id) => api.delete(`/admin/sales/${id}`)
export const resetPwd = (id, newPassword) => api.put(`/admin/sales/${id}/pwd`, null, { params: { newPassword } })
export const getSalesReport = (params) => api.get('/admin/reports/sales', { params })
export const getRanking = (params) => api.get('/admin/reports/ranking', { params })
export const getTrend = (params) => api.get('/admin/reports/trend', { params })
export const getAnomaly = () => api.get('/admin/reports/anomaly')
export const deleteSpu = (id) => api.delete(`/sales/spu/${id}`)
export const getOrderList = () => api.get('/order/list')

export default api
