import { defineStore } from 'pinia'
import { ref } from 'vue'

export const useAuthStore = defineStore('auth', () => {
  const token = ref(localStorage.getItem('token') || '')
  const role = ref(localStorage.getItem('role') || '')
  const username = ref(localStorage.getItem('username') || '')

  function setAuth(t, r, u) {
    token.value = t
    role.value = r
    username.value = u
    localStorage.setItem('token', t)
    localStorage.setItem('role', r)
    localStorage.setItem('username', u)
  }

  function logout() {
    token.value = ''
    role.value = ''
    username.value = ''
    localStorage.clear()
  }

  const isLoggedIn = () => !!token.value
  const isAdmin = () => role.value === 'ADMIN'
  const isSales = () => role.value === 'SALES'

  return { token, role, username, setAuth, logout, isLoggedIn, isAdmin, isSales }
})
