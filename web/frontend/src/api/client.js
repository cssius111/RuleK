import axios from 'axios'

// 创建axios实例
const apiClient = axios.create({
  baseURL: '/api',
  timeout: 30000,
  headers: {
    'Content-Type': 'application/json'
  }
})

// 请求拦截器
apiClient.interceptors.request.use(
  config => {
    // 可以在这里添加认证token等
    return config
  },
  error => {
    return Promise.reject(error)
  }
)

// 响应拦截器
apiClient.interceptors.response.use(
  response => response.data,
  error => {
    const message = error.response?.data?.detail || error.message || '请求失败'
    return Promise.reject(new Error(message))
  }
)

// 游戏API
export const gameApi = {
  // 创建新游戏
  createGame(config) {
    return apiClient.post('/games', config)
  },

  // 获取游戏状态
  getGameState(gameId) {
    return apiClient.get(`/games/${gameId}`)
  },

  // 删除游戏
  deleteGame(gameId) {
    return apiClient.delete(`/games/${gameId}`)
  },

  // 推进回合
  advanceTurn(gameId) {
    return apiClient.post(`/games/${gameId}/turn`)
  },

  // 创建规则
  createRule(gameId, ruleData) {
    return apiClient.post(`/games/${gameId}/rules`, ruleData)
  },

  // 获取规则列表
  getRules(gameId) {
    return apiClient.get(`/games/${gameId}/rules`)
  },

  // 获取NPC列表
  getNpcs(gameId) {
    return apiClient.get(`/games/${gameId}/npcs`)
  },

  // 保存游戏
  saveGame(gameId) {
    return apiClient.post(`/games/${gameId}/save`)
  },

  // 加载游戏
  loadGame(filename) {
    return apiClient.post('/games/load', null, {
      params: { filename }
    })
  },

  // 获取事件（如果有这个端点）
  getEvents(gameId) {
    // 这个端点可能需要在后端实现
    return Promise.resolve([])
  }
}

export default apiClient
