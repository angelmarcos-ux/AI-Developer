import { defineStore } from 'pinia'
import { ref } from 'vue'

export const useAuthStore = defineStore('auth', () => {
  const isAuthenticated = ref(false)
  const user = ref<{ name: string; role: string } | null>(null)

  function login(password: string) {
    if (password === 'admin123') {
      isAuthenticated.value = true
      user.value = { name: 'Admin', role: 'System Administrator' }
      return true
    }
    return false
  }

  function logout() {
    isAuthenticated.value = false
    user.value = null
  }

  return { isAuthenticated, user, login, logout }
})
