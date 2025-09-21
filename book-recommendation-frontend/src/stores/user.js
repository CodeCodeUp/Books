import { defineStore } from 'pinia'
import { ref, computed } from 'vue'

export const useUserStore = defineStore('user', () => {
  // 从localStorage恢复用户信息
  const user = ref(JSON.parse(localStorage.getItem('user') || 'null'))
  const token = ref(localStorage.getItem('token') || '')
  
  const isLoggedIn = computed(() => !!user.value && !!token.value)
  
  const setUser = (userData) => {
    user.value = userData
    localStorage.setItem('user', JSON.stringify(userData))
  }
  
  const setToken = (tokenValue) => {
    token.value = tokenValue
    localStorage.setItem('token', tokenValue)
  }
  
  const logout = () => {
    user.value = null
    token.value = ''
    localStorage.removeItem('token')
    localStorage.removeItem('user')
  }
  
  const getUserInfo = () => {
    return user.value
  }
  
  // 检查用户资料是否完整
  const isProfileIncomplete = () => {
    if (!user.value) return false
    const { location, age, country } = user.value
    return !location || !age || !country
  }
  
  return {
    user,
    token,
    isLoggedIn,
    setUser,
    setToken,
    logout,
    getUserInfo,
    isProfileIncomplete
  }
})