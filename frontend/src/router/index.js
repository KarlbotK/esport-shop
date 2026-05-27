import { createRouter, createWebHistory } from 'vue-router'

const routes = [
  { path: '/', name: 'Home', component: () => import('../views/Home.vue') },
  { path: '/products', name: 'Products', component: () => import('../views/ProductList.vue') },
  { path: '/product/:id', name: 'ProductDetail', component: () => import('../views/ProductDetail.vue') },
  { path: '/login', name: 'Login', component: () => import('../views/Login.vue') },
  { path: '/register', name: 'Register', component: () => import('../views/Register.vue') },
  { path: '/cart', name: 'Cart', component: () => import('../views/Cart.vue'), meta: { auth: true } },
  { path: '/orders', name: 'Orders', component: () => import('../views/Orders.vue'), meta: { auth: true } },
  { path: '/seckill', name: 'Seckill', component: () => import('../views/Seckill.vue') },
  { path: '/recommend', name: 'Recommend', component: () => import('../views/Recommend.vue') },
  { path: '/admin', name: 'Admin', component: () => import('../views/Admin.vue'), meta: { role: 'ADMIN' } },
  { path: '/sales', name: 'Sales', component: () => import('../views/Sales.vue'), meta: { role: 'SALES' } },
]

const router = createRouter({
  history: createWebHistory(),
  routes,
})

router.beforeEach((to) => {
  const token = localStorage.getItem('token')
  const role = localStorage.getItem('role')
  if (to.meta.auth && !token) return '/login'
  if (to.meta.role && role !== to.meta.role) return '/'
})

router.onError((error) => {
  console.error('Router error:', error)
})

export default router
