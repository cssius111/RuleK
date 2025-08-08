import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import { gameApi } from '@/api/gameApi'
import type { GameConfig, GameState, GameSave } from '@/types/game'
import mockData from '@/utils/mockData'

// 是否使用mock数据（开发模式）
const USE_MOCK_DATA = import.meta.env.DEV && !import.meta.env.VITE_USE_REAL_API

export const useGameStore = defineStore('game', () => {
  // 游戏状态
  const gameState = ref<GameState | null>(USE_MOCK_DATA ? mockData.gameState as any : null)
  const gameConfig = ref<GameConfig | null>(null)
  const isLoading = ref(false)
  const error = ref<string | null>(null)
  const currentGameId = ref<string | null>(USE_MOCK_DATA ? 'test-game-001' : null)
  
  // 计算属性
  const isGameStarted = computed(() => gameState.value !== null)
  const aliveNPCs = computed(() => gameState.value?.npcs?.filter(npc => npc.is_alive) || [])
  const currentTurn = computed(() => gameState.value?.current_turn || 0)
  const currentPhase = computed(() => gameState.value?.phase || 'SETUP')
  const fearPoints = computed(() => gameState.value?.fear_points || 0)
  
  // 初始化游戏
  const initGame = async (config: GameConfig) => {
    isLoading.value = true
    error.value = null
    
    try {
      if (USE_MOCK_DATA) {
        // 使用mock数据
        await new Promise(resolve => setTimeout(resolve, 1000)) // 模拟延迟
        gameState.value = { ...mockData.gameState } as any
        gameConfig.value = config
        currentGameId.value = 'test-game-001'
        return mockData.apiResponses.createGame
      }
      
      // 调用真实API
      const response = await gameApi.createGame(config)
      
      // 保存游戏状态
      gameState.value = response.state
      gameConfig.value = config
      currentGameId.value = response.gameId
      
      // 如果启用AI，初始化AI
      if (config.aiEnabled && response.gameId) {
        await gameApi.initializeAI(response.gameId)
      }
      
      return response
    } catch (err: any) {
      error.value = err.error || err.message || '创建游戏失败'
      throw err
    } finally {
      isLoading.value = false
    }
  }
  
  // 获取游戏状态
  const fetchGameState = async (gameId: string) => {
    isLoading.value = true
    error.value = null
    
    try {
      if (USE_MOCK_DATA) {
        await new Promise(resolve => setTimeout(resolve, 500))
        return gameState.value
      }
      
      const response = await gameApi.getGameState(gameId)
      gameState.value = response
      return response
    } catch (err: any) {
      error.value = err.error || err.message || '获取游戏状态失败'
      throw err
    } finally {
      isLoading.value = false
    }
  }
  
  // 刷新游戏状态
  const refreshGameState = async () => {
    if (!currentGameId.value) return
    
    if (USE_MOCK_DATA) {
      // 模拟状态更新
      await new Promise(resolve => setTimeout(resolve, 300))
      // 随机更新一些NPC状态
      if (gameState.value?.npcs) {
        gameState.value.npcs = gameState.value.npcs.map(npc => 
          mockData.updateNPCStatus({ ...npc })
        )
      }
      return
    }
    
    await fetchGameState(currentGameId.value)
  }
  
  // 推进回合
  const advanceTurn = async () => {
    if (!currentGameId.value) throw new Error('游戏未开始')
    
    isLoading.value = true
    error.value = null
    
    try {
      if (USE_MOCK_DATA) {
        await new Promise(resolve => setTimeout(resolve, 1500))
        // 更新回合数
        if (gameState.value) {
          gameState.value.current_turn += 1
          // 添加随机事件
          gameState.value.events_history.unshift(mockData.generateRandomEvent())
          // 更新NPC状态
          gameState.value.npcs = gameState.value.npcs.map(npc => 
            mockData.updateNPCStatus({ ...npc })
          )
        }
        return mockData.apiResponses.advanceTurn
      }
      
      const response = await gameApi.advanceTurn(currentGameId.value)
      
      // 更新游戏状态
      if (response.state) {
        gameState.value = response.state
      }
      
      return response
    } catch (err: any) {
      error.value = err.error || err.message || '推进回合失败'
      throw err
    } finally {
      isLoading.value = false
    }
  }
  
  // 创建规则
  const createRule = async (ruleData: any) => {
    if (!currentGameId.value) throw new Error('游戏未开始')
    
    isLoading.value = true
    error.value = null
    
    try {
      if (USE_MOCK_DATA) {
        await new Promise(resolve => setTimeout(resolve, 1000))
        // 添加新规则到状态
        if (gameState.value) {
          const newRule = {
            id: `rule-${Date.now()}`,
            name: ruleData.name || '新规则',
            description: ruleData.description || '神秘的规则',
            on_cooldown: false,
            cooldown_remaining: 0
          }
          gameState.value.rules.push(newRule)
          // 扣除恐惧点数
          gameState.value.fear_points -= 100
        }
        return mockData.apiResponses.createRule
      }
      
      const response = await gameApi.createRule(currentGameId.value, ruleData)
      
      // 更新游戏状态
      await refreshGameState()
      
      return response
    } catch (err: any) {
      error.value = err.error || err.message || '创建规则失败'
      throw err
    } finally {
      isLoading.value = false
    }
  }
  
  // 保存游戏
  const saveGame = async (saveName?: string) => {
    if (!currentGameId.value || !gameState.value) throw new Error('游戏未开始')
    
    isLoading.value = true
    error.value = null
    
    try {
      if (USE_MOCK_DATA) {
        await new Promise(resolve => setTimeout(resolve, 800))
        console.log('游戏已保存（Mock）:', saveName)
        return mockData.apiResponses.saveGame
      }
      
      const response = await gameApi.saveGame(currentGameId.value, saveName)
      return response
    } catch (err: any) {
      error.value = err.error || err.message || '保存游戏失败'
      throw err
    } finally {
      isLoading.value = false
    }
  }
  
  // 加载游戏
  const loadGame = async (saveId: string) => {
    isLoading.value = true
    error.value = null
    
    try {
      if (USE_MOCK_DATA) {
        await new Promise(resolve => setTimeout(resolve, 1000))
        gameState.value = { ...mockData.gameState } as any
        currentGameId.value = 'test-game-001'
        return { success: true }
      }
      
      const response = await gameApi.loadGame(saveId)
      
      gameState.value = response.state
      currentGameId.value = response.gameId
      
      return response
    } catch (err: any) {
      error.value = err.error || err.message || '加载游戏失败'
      throw err
    } finally {
      isLoading.value = false
    }
  }
  
  // 获取存档列表
  const getSavesList = async () => {
    try {
      if (USE_MOCK_DATA) {
        await new Promise(resolve => setTimeout(resolve, 500))
        return [
          {
            id: 'save-001',
            name: '恐怖之夜 - 第5回合',
            timestamp: new Date(Date.now() - 3600000),
            turn: 5,
            aliveNPCs: 3
          },
          {
            id: 'save-002',
            name: '血月降临 - 第12回合',
            timestamp: new Date(Date.now() - 7200000),
            turn: 12,
            aliveNPCs: 1
          }
        ]
      }
      
      return await gameApi.getSavesList()
    } catch (err: any) {
      error.value = err.error || err.message || '获取存档列表失败'
      throw err
    }
  }
  
  // 重置游戏
  const resetGame = () => {
    gameState.value = null
    gameConfig.value = null
    currentGameId.value = null
    error.value = null
  }
  
  // 添加测试数据生成器（仅开发模式）
  const addRandomEvent = () => {
    if (USE_MOCK_DATA && gameState.value) {
      gameState.value.events_history.unshift(mockData.generateRandomEvent())
    }
  }
  
  return {
    // 状态
    gameState,
    gameConfig,
    isLoading,
    error,
    currentGameId,
    
    // 计算属性
    isGameStarted,
    aliveNPCs,
    currentTurn,
    currentPhase,
    fearPoints,
    
    // 方法
    initGame,
    fetchGameState,
    refreshGameState,
    advanceTurn,
    createRule,
    saveGame,
    loadGame,
    getSavesList,
    resetGame,
    
    // 开发工具
    ...(USE_MOCK_DATA ? { addRandomEvent } : {})
  }
})
