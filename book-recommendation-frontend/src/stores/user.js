import { defineStore } from 'pinia'
import { ref, computed } from 'vue'

export const useUserStore = defineStore('user', () => {
  const user = ref(null)
  const token = ref(localStorage.getItem('token') || '')
  
  const isLoggedIn = computed(() => !!user.value && !!token.value)
  
  const setUser = (userData) => {
    user.value = userData
  }
  
  const setToken = (tokenValue) => {
    token.value = tokenValue
    localStorage.setItem('token', tokenValue)
  }
  
  const logout = () => {
    user.value = null
    token.value = ''
    localStorage.removeItem('token')
  }
  
  const getUserInfo = () => {
    return user.value
  }
  
  return {
    user,
    token,
    isLoggedIn,
    setUser,
    setToken,
    logout,
    getUserInfo
  }
})