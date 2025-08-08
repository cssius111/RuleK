import apiClient from './index'
import type { 
  GameConfig, 
  CreateGameRequest, 
  CreateGameResponse,
  GameState,
  GameSave,
  ApiResponse 
} from '@/types/game'

// 游戏API服务
class GameApiService {
  // 创建新游戏
  async createGame(config: GameConfig): Promise<CreateGameResponse> {
    try {
      const response = await apiClient.post<any, CreateGameResponse>('/games', {
        config
      })
      return response
    } catch (error) {
      console.error('创建游戏失败:', error)
      // 如果后端未实现，返回模拟数据
      if (error?.statusCode === 404 || error?.statusCode === 500) {
        return this.mockCreateGame(config)
      }
      throw error
    }
  }

  // 获取游戏状态
  async getGameState(gameId: string): Promise<GameState> {
    try {
      const response = await apiClient.get<any, GameState>(`/games/${gameId}`)
      return response
    } catch (error) {
      console.error('获取游戏状态失败:', error)
      throw error
    }
  }

  // 初始化AI（如果启用）
  async initializeAI(gameId: string): Promise<ApiResponse<any>> {
    try {
      const response = await apiClient.post<any, ApiResponse<any>>(`/games/${gameId}/ai/init`)
      return response
    } catch (error) {
      console.error('初始化AI失败:', error)
      // 返回成功以便继续测试
      return { success: true, message: 'AI初始化成功（模拟）' }
    }
  }

  // 获取存档列表
  async getSavesList(): Promise<GameSave[]> {
    try {
      const response = await apiClient.get<any, GameSave[]>('/saves')
      return response
    } catch (error) {
      console.error('获取存档列表失败:', error)
      // 返回空列表
      return []
    }
  }

  // 加载存档
  async loadSave(saveId: string): Promise<GameState> {
    try {
      const response = await apiClient.get<any, GameState>(`/saves/${saveId}`)
      return response
    } catch (error) {
      console.error('加载存档失败:', error)
      throw error
    }
  }

  // 保存游戏
  async saveGame(gameId: string, saveName: string): Promise<ApiResponse<GameSave>> {
    try {
      const response = await apiClient.post<any, ApiResponse<GameSave>>(`/games/${gameId}/save`, {
        name: saveName
      })
      return response
    } catch (error) {
      console.error('保存游戏失败:', error)
      throw error
    }
  }

  // 推进回合
  async advanceTurn(gameId: string): Promise<GameState> {
    try {
      const response = await apiClient.post<any, GameState>(`/games/${gameId}/turn`)
      return response
    } catch (error) {
      console.error('推进回合失败:', error)
      throw error
    }
  }

  // 模拟创建游戏（用于开发测试）
  private mockCreateGame(config: GameConfig): CreateGameResponse {
    const gameId = `game_${Date.now()}`
    const npcs = []
    
    // 生成NPC
    for (let i = 0; i < config.initialNPCCount; i++) {
      npcs.push({
        id: `npc_${i}`,
        name: `NPC_${i + 1}`,
        hp: 100,
        sanity: 100,
        fear: 0,
        location: '大厅',
        isAlive: true,
        status: '正常'
      })
    }

    const gameState: GameState = {
      gameId,
      turn: 1,
      day: 1,
      phase: 'setup',
      mode: 'backstage',
      fearPoints: config.initialFearPoints,
      npcs,
      rules: [],
      events: [
        {
          id: 'event_1',
          turn: 0,
          type: 'game_start',
          description: '游戏开始了，诡异的氛围笼罩着整个空间...',
          timestamp: Date.now()
        }
      ],
      isGameOver: false
    }

    return {
      gameId,
      config,
      state: gameState,
      message: '游戏创建成功！'
    }
  }
}

// 导出单例
export const gameApi = new GameApiService()
