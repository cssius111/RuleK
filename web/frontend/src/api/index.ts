import axios, { AxiosInstance, AxiosError } from 'axios'
import type { ApiResponse } from '@/types/game'

// 创建axios实例
const apiClient: AxiosInstance = axios.create({
  baseURL: import.meta.env.VITE_API_URL || '/api',
  timeout: 10000,
  headers: {
    'Content-Type': 'application/json'
  }
})

// 请求拦截器
apiClient.interceptors.request.use(
  (config) => {
    // 可以在这里添加token等认证信息
    const token = localStorage.getItem('token')
    if (token) {
      config.headers.Authorization = `Bearer ${token}`
    }
    return config
  },
  (error) => {
    return Promise.reject(error)
  }
)

// 响应拦截器
apiClient.interceptors.response.use(
  (response) => {
    return response.data
  },
  (error: AxiosError) => {
    // 统一错误处理
    const message = error.response?.data?.message || error.message || '网络错误'
    console.error('API Error:', message)
    
    // 可以在这里添加全局错误提示
    if (error.response?.status === 401) {
      // 未授权，可能需要重新登录
      localStorage.removeItem('token')
      window.location.href = '/'
    }
    
    return Promise.reject({
      success: false,
      error: message,
      statusCode: error.response?.status
    })
  }
)

export default apiClient
