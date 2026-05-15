import { defineStore } from 'pinia'
import { ref } from 'vue'

export const useAuthStore = defineStore('auth', () => {
  const isAuthenticated = ref(false)
  const user = ref<{ name: string; role: string } | null>(null)
  const currentPassword = ref('admin123')

  function login(password: string) {
    if (password === currentPassword.value) {
      isAuthenticated.value = true
      user.value = { name: 'Admin', role: 'System Administrator' }
      return true
    }
    return false
  }

  function changePassword(newPassword: string) {
    if (newPassword && newPassword.length >= 6) {
      currentPassword.value = newPassword
      return true
    }
    return false
  }

  function logout() {
    isAuthenticated.value = false
    user.value = null
  }

  return { isAuthenticated, user, login, logout, changePassword, currentPassword }
})
