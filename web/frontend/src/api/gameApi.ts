import apiClient from './index'

// 游戏API服务
class GameApiService {
  // 创建新游戏
  async createGame(config: any) {
    try {
      // 转换前端格式到后端期望的格式
      const requestData = {
        difficulty: config.difficulty || 'normal',
        npc_count: config.initialNPCCount || config.npc_count || 4
      }
      const response = await apiClient.post('/api/games', requestData)
      return response
    } catch (error) {
      console.error('创建游戏失败:', error)
      // 如果后端不可用，返回模拟数据
      console.log('使用模拟数据代替')
      return this.mockCreateGame(config)
    }
  }

  // 获取游戏状态
  async getGameState(gameId: string) {
    try {
      const response = await apiClient.get(`/api/games/${gameId}`)
      return response
    } catch (error) {
      console.error('获取游戏状态失败:', error)
      throw error
    }
  }

  // 初始化AI
  async initializeAI(gameId: string) {
    try {
      const response = await apiClient.post(`/api/games/${gameId}/ai/init`)
      return response
    } catch (error) {
      console.error('初始化AI失败:', error)
      throw error
    }
  }

  // 执行游戏回合
  async executeTurn(gameId: string, action: any) {
    try {
      const response = await apiClient.post(`/api/games/${gameId}/turn`, action)
      return response
    } catch (error) {
      console.error('执行回合失败:', error)
      throw error
    }
  }

  // AI回合
  async executeAITurn(gameId: string) {
    try {
      const response = await apiClient.post(`/api/games/${gameId}/ai/turn`)
      return response
    } catch (error) {
      console.error('执行AI回合失败:', error)
      throw error
    }
  }

  // AI评估规则
  async evaluateRuleWithAI(gameId: string, ruleDescription: string) {
    try {
      const response = await apiClient.post(`/api/games/${gameId}/ai/evaluate-rule`, {
        description: ruleDescription
      })
      return response
    } catch (error) {
      console.error('AI评估规则失败:', error)
      throw error
    }
  }

  // 生成AI叙事
  async generateNarrative(gameId: string, events: any[]) {
    try {
      const response = await apiClient.post(`/api/games/${gameId}/ai/narrative`, {
        events
      })
      return response
    } catch (error) {
      console.error('生成叙事失败:', error)
      throw error
    }
  }

  // 保存游戏
  async saveGame(gameId: string, saveName: string) {
    try {
      const response = await apiClient.post(`/api/games/${gameId}/save`, {
        save_name: saveName
      })
      return response
    } catch (error) {
      console.error('保存游戏失败:', error)
      throw error
    }
  }

  // 加载游戏
  async loadGame(saveId: string) {
    try {
      const response = await apiClient.post(`/api/games/load/${saveId}`)
      return response
    } catch (error) {
      console.error('加载游戏失败:', error)
      throw error
    }
  }

  // 获取规则模板
  async getRuleTemplates() {
    try {
      const response = await apiClient.get('/api/rules/templates')
      return response
    } catch (error) {
      console.error('获取规则模板失败:', error)
      throw error
    }
  }

  // 创建规则（从模板）
  async createRuleFromTemplate(gameId: string, templateId: string) {
    try {
      const response = await apiClient.post(`/api/games/${gameId}/rules/template`, {
        template_id: templateId
      })
      return response
    } catch (error) {
      console.error('创建规则失败:', error)
      throw error
    }
  }

  // 创建自定义规则
  async createCustomRule(gameId: string, ruleData: any) {
    try {
      const response = await apiClient.post(`/api/games/${gameId}/rules/custom`, ruleData)
      return response
    } catch (error) {
      console.error('创建自定义规则失败:', error)
      throw error
    }
  }

  // 获取游戏规则列表
  async getGameRules(gameId: string) {
    try {
      const response = await apiClient.get(`/api/games/${gameId}/rules`)
      return response
    } catch (error) {
      console.error('获取规则列表失败:', error)
      throw error
    }
  }

  // 切换规则状态
  async toggleRule(gameId: string, ruleId: string) {
    try {
      const response = await apiClient.put(`/api/games/${gameId}/rules/${ruleId}/toggle`)
      return response
    } catch (error) {
      console.error('切换规则状态失败:', error)
      throw error
    }
  }

  // 升级规则
  async upgradeRule(gameId: string, ruleId: string) {
    try {
      const response = await apiClient.post(`/api/games/${gameId}/rules/${ruleId}/upgrade`)
      return response
    } catch (error) {
      console.error('升级规则失败:', error)
      throw error
    }
  }

  // AI解析规则
  async parseRuleWithAI(description: string, gameId?: string) {
    try {
      const response = await apiClient.post('/api/ai/parse-rule', {
        description,
        game_id: gameId
      })
      return response
    } catch (error) {
      console.error('AI解析规则失败:', error)
      throw error
    }
  }

  // 计算规则成本
  async calculateRuleCost(ruleData: any) {
    try {
      const response = await apiClient.post('/api/rules/calculate-cost', ruleData)
      return response
    } catch (error) {
      console.error('计算规则成本失败:', error)
      return { cost: 100 }
    }
  }

  // 模拟创建游戏（用于开发）
  private mockCreateGame(config: any) {
    const gameId = `game_${Date.now()}`
    // 返回与后端 GameStateResponse 格式一致的数据
    return {
      game_id: gameId,
      started_at: new Date().toISOString(),
      current_turn: 1,
      fear_points: config.initialFearPoints || 1000,
      phase: 'setup',
      mode: 'backstage',
      time_of_day: 'morning',
      npcs: this.generateMockNPCs(config.initialNPCCount || config.npc_count || 4),
      active_rules: 0,
      total_fear_gained: 0,
      npcs_died: 0,
      // 额外字段以便前端使用
      rules: [],
      events_history: []
    }
  }

  // 生成模拟NPC
  private generateMockNPCs(count: number) {
    const names = ['张三', '李四', '王五', '赵六', '钱七', '孙八']
    const npcs = []
    
    for (let i = 0; i < Math.min(count, names.length); i++) {
      npcs.push({
        id: `npc_${i}`,
        name: names[i],
        hp: 100,
        sanity: 100,
        fear: 0,
        location: 'main_hall',
        status_effects: [],
        is_alive: true
      })
    }
    
    return npcs
  }
}

export const gameApi = new GameApiService()
export default gameApi
