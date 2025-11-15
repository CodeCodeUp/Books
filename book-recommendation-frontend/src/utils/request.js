import axios from 'axios'
import { ElMessage } from 'element-plus'
import { useUserStore } from '../stores/user'
import router from '../router'

const request = axios.create({
  baseURL: '/api',
  timeout: 10000
})

// 请求拦截器
request.interceptors.request.use(
  config => {
    const userStore = useUserStore()
    if (userStore.token) {
      config.headers.Authorization = `Bearer ${userStore.token}`
    }
    return config
  },
  error => {
    return Promise.reject(error)
  }
)

// 响应拦截器
request.interceptors.response.use(
  response => {
    const res = response.data

    if (res.code === 200) {
      return res
    } else {
      ElMessage.error(res.message || '请求失败')
      return Promise.reject(new Error(res.message || '请求失败'))
    }
  },
  error => {
    const userStore = useUserStore()

    // 处理HTTP状态码错误
    if (error.response) {
      const { status, data } = error.response

      // Token过期或未授权
      if (status === 401 || status === 403) {
        ElMessage.error('登录已过期，请重新登录')

        // 清除用户信息
        userStore.logout()

        // 跳转到登录页
        router.push('/login')

        return Promise.reject(new Error('登录已过期'))
      }

      // 其他错误
      ElMessage.error(data?.message || error.message || '请求失败')
    } else {
      // 网络错误或超时
      ElMessage.error(error.message || '网络错误')
    }

    return Promise.reject(error)
  }
)

export default request