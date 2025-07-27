import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import type { GameState, NPC, Rule, GameUpdate } from '@/types/game'
import { api } from '@/api/client'
import { useWebSocket } from '@/api/websocket'

export const useGameStore = defineStore('game', () => {
  // 状态
  const gameId = ref<string | null>(null)
  const gameState = ref<GameState | null>(null)
  const npcs = ref<NPC[]>([])
  const rules = ref<Rule[]>([])
  const events = ref<any[]>([])
  const isLoading = ref(false)
  const error = ref<string | null>(null)
  
  // WebSocket 连接
  const ws = useWebSocket()
  
  // 计算属性
  const aliveNPCs = computed(() => npcs.value.filter(npc => npc.is_alive))
  const activeRules = computed(() => rules.value.filter(rule => rule.is_active))
  const currentPhase = computed(() => gameState.value?.phase || 'setup')
  const fearPoints = computed(() => gameState.value?.fear_points || 0)
  
  // 创建新游戏
  async function createGame(difficulty: string = 'normal', npcCount: number = 4) {
    isLoading.value = true
    error.value = null
    
    try {
      const response = await api.createGame({ difficulty, npc_count: npcCount })
      gameId.value = response.game_id
      gameState.value = response
      npcs.value = response.npcs
      
      // 连接 WebSocket
      await ws.connect(response.game_id)
      setupWebSocketHandlers()
      
      return response
    } catch (e: any) {
      error.value = e.message || '创建游戏失败'
      throw e
    } finally {
      isLoading.value = false
    }
  }
  
  // 加载游戏状态
  async function loadGame(id: string) {
    isLoading.value = true
    error.value = null
    
    try {
      const response = await api.getGameState(id)
      gameId.value = id
      gameState.value = response
      npcs.value = response.npcs
      
      // 加载规则列表
      const rulesResponse = await api.getRules(id)
      rules.value = rulesResponse
      
      // 连接 WebSocket
      await ws.connect(id)
      setupWebSocketHandlers()
      
      return response
    } catch (e: any) {
      error.value = e.message || '加载游戏失败'
      throw e
    } finally {
      isLoading.value = false
    }
  }
  
  // 推进回合
  async function advanceTurn() {
    if (!gameId.value) return
    
    isLoading.value = true
    error.value = null
    
    try {
      const result = await api.advanceTurn(gameId.value)
      events.value.push(...result.events)
      return result
    } catch (e: any) {
      error.value = e.message || '推进回合失败'
      throw e
    } finally {
      isLoading.value = false
    }
  }
  
  // 创建规则
  async function createRule(ruleData: any) {
    if (!gameId.value) return
    
    isLoading.value = true
    error.value = null
    
    try {
      const result = await api.createRule(gameId.value, ruleData)
      
      // 刷新规则列表
      const rulesResponse = await api.getRules(gameId.value)
      rules.value = rulesResponse
      
      return result
    } catch (e: any) {
      error.value = e.message || '创建规则失败'
      throw e
    } finally {
      isLoading.value = false
    }
  }
  
  // 保存游戏
  async function saveGame() {
    if (!gameId.value) return
    
    try {
      const result = await api.saveGame(gameId.value)
      return result
    } catch (e: any) {
      error.value = e.message || '保存游戏失败'
      throw e
    }
  }
  
  // 设置 WebSocket 事件处理
  function setupWebSocketHandlers() {
    ws.on('state', (data: GameState) => {
      gameState.value = data
      npcs.value = data.npcs
    })
    
    ws.on('event', (data: any) => {
      events.value.push(data)
    })
    
    ws.on('npc', (data: any) => {
      // 更新单个 NPC
      const index = npcs.value.findIndex(n => n.id === data.id)
      if (index >= 0) {
        npcs.value[index] = data
      }
    })
    
    ws.on('rule', (data: any) => {
      if (data.action === 'created') {
        rules.value.push(data.rule)
      } else if (data.action === 'updated') {
        const index = rules.value.findIndex(r => r.id === data.rule.id)
        if (index >= 0) {
          rules.value[index] = data.rule
        }
      }
    })
    
    ws.on('dialogue', (data: any) => {
      events.value.push({
        type: 'dialogue',
        data: data
      })
    })
  }
  
  // 清理游戏状态
  function clearGame() {
    gameId.value = null
    gameState.value = null
    npcs.value = []
    rules.value = []
    events.value = []
    ws.disconnect()
  }
  
  return {
    // 状态
    gameId,
    gameState,
    npcs,
    rules,
    events,
    isLoading,
    error,
    
    // 计算属性
    aliveNPCs,
    activeRules,
    currentPhase,
    fearPoints,
    
    // 方法
    createGame,
    loadGame,
    advanceTurn,
    createRule,
    saveGame,
    clearGame
  }
})
