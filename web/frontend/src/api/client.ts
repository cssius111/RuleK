import axios, { AxiosInstance } from 'axios'
import type { 
  GameCreateRequest, 
  GameStateResponse, 
  RuleCreateRequest,
  TurnResult,
  NPCStatus,
  RuleInfo
} from '@/types/game'

class APIClient {
  private client: AxiosInstance
  
  constructor() {
    this.client = axios.create({
      baseURL: '/api',
      timeout: 30000,
      headers: {
        'Content-Type': 'application/json'
      }
    })
    
    // 请求拦截器
    this.client.interceptors.request.use(
      config => {
        // TODO: 添加认证 token
        return config
      },
      error => {
        return Promise.reject(error)
      }
    )
    
    // 响应拦截器
    this.client.interceptors.response.use(
      response => response.data,
      error => {
        if (error.response) {
          // 服务器返回错误
          const message = error.response.data?.detail || error.response.statusText
          console.error('API Error:', message)
          return Promise.reject(new Error(message))
        } else if (error.request) {
          // 请求发送失败
          console.error('Network Error:', error.message)
          return Promise.reject(new Error('网络连接失败'))
        } else {
          // 其他错误
          console.error('Error:', error.message)
          return Promise.reject(error)
        }
      }
    )
  }
  
  // 游戏管理
  async createGame(data: GameCreateRequest): Promise<GameStateResponse> {
    return this.client.post('/games', data)
  }
  
  async getGameState(gameId: string): Promise<GameStateResponse> {
    return this.client.get(`/games/${gameId}`)
  }
  
  async deleteGame(gameId: string): Promise<void> {
    return this.client.delete(`/games/${gameId}`)
  }
  
  // 游戏操作
  async advanceTurn(gameId: string): Promise<TurnResult> {
    return this.client.post(`/games/${gameId}/turn`)
  }
  
  // 规则管理
  async createRule(gameId: string, data: RuleCreateRequest): Promise<{ rule_id: string; cost: number }> {
    return this.client.post(`/games/${gameId}/rules`, data)
  }
  
  async getRules(gameId: string): Promise<RuleInfo[]> {
    return this.client.get(`/games/${gameId}/rules`)
  }
  
  // NPC管理
  async getNPCs(gameId: string): Promise<NPCStatus[]> {
    return this.client.get(`/games/${gameId}/npcs`)
  }
  
  // 存档管理
  async saveGame(gameId: string): Promise<{ filename: string; message: string }> {
    return this.client.post(`/games/${gameId}/save`)
  }
  
  async loadGame(filename: string): Promise<GameStateResponse> {
    return this.client.post('/games/load', null, {
      params: { filename }
    })
  }
  
  // 健康检查
  async healthCheck(): Promise<{ status: string; timestamp: string; active_games: number }> {
    return this.client.get('/health')
  }
}

// 导出单例
export const api = new APIClient()
