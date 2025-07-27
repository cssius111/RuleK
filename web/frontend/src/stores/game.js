import { defineStore } from 'pinia'
import { ref, computed } from 'vue'

export const useGameStore = defineStore('game', () => {
  // 游戏状态
  const gameState = ref({
    game_id: '',
    current_turn: 0,
    fear_points: 1000,
    phase: 'setup',
    mode: 'backstage',
    time_of_day: 'morning',
    active_rules: 0,
    total_fear_gained: 0,
    npcs_died: 0
  })

  // NPC列表
  const npcs = ref([])
  
  // 规则列表
  const rules = ref([])
  
  // 事件日志
  const events = ref([])
  
  // 计算属性
  const aliveNpcs = computed(() => 
    npcs.value.filter(npc => npc.is_alive)
  )
  
  const recentEvents = computed(() => 
    events.value.slice(-10)
  )
  
  // 方法
  function setGameState(state) {
    gameState.value = { ...state }
    npcs.value = state.npcs || []
  }
  
  function updateState(updates) {
    Object.assign(gameState.value, updates)
    if (updates.npcs) {
      npcs.value = updates.npcs
    }
  }
  
  function setNpcs(npcList) {
    npcs.value = npcList
  }
  
  function updateNpc(npcId, updates) {
    const index = npcs.value.findIndex(npc => npc.id === npcId)
    if (index !== -1) {
      Object.assign(npcs.value[index], updates)
    }
  }
  
  function setRules(ruleList) {
    rules.value = ruleList
  }
  
  function addRule(rule) {
    rules.value.push(rule)
    gameState.value.active_rules++
  }
  
  function setEvents(eventList) {
    events.value = eventList
  }
  
  function addEvent(event) {
    events.value.push({
      ...event,
      timestamp: new Date().toISOString()
    })
  }
  
  function addEvents(eventList) {
    eventList.forEach(addEvent)
  }
  
  function reset() {
    gameState.value = {
      game_id: '',
      current_turn: 0,
      fear_points: 1000,
      phase: 'setup',
      mode: 'backstage',
      time_of_day: 'morning',
      active_rules: 0,
      total_fear_gained: 0,
      npcs_died: 0
    }
    npcs.value = []
    rules.value = []
    events.value = []
  }

  return {
    // state
    gameState,
    npcs,
    rules,
    events,
    
    // getters
    aliveNpcs,
    recentEvents,
    
    // actions
    setGameState,
    updateState,
    setNpcs,
    updateNpc,
    setRules,
    addRule,
    setEvents,
    addEvent,
    addEvents,
    reset
  }
})
