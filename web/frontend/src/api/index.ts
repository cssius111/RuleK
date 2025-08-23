// 简化的 API 客户端，避免类型导入问题
import axios from 'axios'

// API 基础配置
const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000'

// 创建 axios 实例
const apiClient = axios.create({
  baseURL: API_BASE_URL,
  timeout: 30000,
  headers: {
    'Content-Type': 'application/json'
  }
})

// 请求拦截器
apiClient.interceptors.request.use(
  (config) => {
    // 可以在这里添加认证信息
    return config
  },
  (error) => {
    console.error('Request error:', error)
    return Promise.reject(error)
  }
)

// 响应拦截器
apiClient.interceptors.response.use(
  (response) => {
    return response.data
  },
  (error) => {
    const message = error.response?.data?.message || error.message || '网络错误'
    console.error('API Error:', message)
    
    return Promise.reject({
      success: false,
      error: message,
      statusCode: error.response?.status
    })
  }
)

export default apiClient
export { apiClient as api }  // 添加命名导出，供 stores 使用
