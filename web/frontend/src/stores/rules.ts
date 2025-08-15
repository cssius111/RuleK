import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import { api } from '@/api'
import { useGameStore } from './game'
import type { Rule, RuleTemplate, RuleEffect } from '@/types/rule'

export const useRulesStore = defineStore('rules', () => {
  // 状态
  const rules = ref<Rule[]>([])
  const templates = ref<RuleTemplate[]>([])
  const selectedTemplate = ref<RuleTemplate | null>(null)
  const isCreating = ref(false)
  const isLoading = ref(false)
  
  // 计算属性
  const activeRules = computed(() => 
    rules.value.filter(r => r.is_active)
  )
  
  const totalRuleCost = computed(() =>
    rules.value.reduce((sum, rule) => sum + rule.cost, 0)
  )
  
  const canCreateRule = computed(() => {
    const gameStore = useGameStore()
    return (cost: number) => gameStore.gameState?.fear_points >= cost
  })
  
  // 方法
  async function loadTemplates() {
    isLoading.value = true
    try {
      const response = await api.get('/api/rules/templates')
      templates.value = response.data.templates
      return templates.value
    } catch (error) {
      console.error('Failed to load templates:', error)
      throw error
    } finally {
      isLoading.value = false
    }
  }
  
  async function loadGameRules(gameId: string) {
    isLoading.value = true
    try {
      const response = await api.get(`/api/games/${gameId}/rules`)
      rules.value = response.data.rules
      return rules.value
    } catch (error) {
      console.error('Failed to load game rules:', error)
      throw error
    } finally {
      isLoading.value = false
    }
  }
  
  async function createRuleFromTemplate(gameId: string, templateId: string) {
    isCreating.value = true
    try {
      const response = await api.post(`/api/games/${gameId}/rules/template`, {
        template_id: templateId
      })
      
      if (response.data.success) {
        rules.value.push(response.data.rule)
        
        // 更新游戏状态中的恐惧点数
        const gameStore = useGameStore()
        if (gameStore.gameState) {
          gameStore.gameState.fear_points = response.data.remaining_fear_points
        }
        
        return response.data.rule
      }
      throw new Error('Failed to create rule')
    } catch (error) {
      console.error('Failed to create rule from template:', error)
      throw error
    } finally {
      isCreating.value = false
    }
  }
  
  async function createCustomRule(gameId: string, ruleData: any) {
    isCreating.value = true
    try {
      const response = await api.post(`/api/games/${gameId}/rules/custom`, ruleData)
      
      if (response.data.success) {
        rules.value.push(response.data.rule)
        
        // 更新游戏状态中的恐惧点数
        const gameStore = useGameStore()
        if (gameStore.gameState) {
          gameStore.gameState.fear_points = response.data.remaining_fear_points
        }
        
        return response.data.rule
      }
      throw new Error('Failed to create custom rule')
    } catch (error) {
      console.error('Failed to create custom rule:', error)
      throw error
    } finally {
      isCreating.value = false
    }
  }
  
  async function parseRuleWithAI(description: string, gameId?: string) {
    isLoading.value = true
    try {
      const response = await api.post('/api/ai/parse-rule', {
        description,
        game_id: gameId
      })
      
      return response.data
    } catch (error) {
      console.error('Failed to parse rule with AI:', error)
      throw error
    } finally {
      isLoading.value = false
    }
  }
  
  async function toggleRule(gameId: string, ruleId: string) {
    try {
      const response = await api.put(`/api/games/${gameId}/rules/${ruleId}/toggle`)
      
      if (response.data.success) {
        const rule = rules.value.find(r => r.id === ruleId)
        if (rule) {
          rule.is_active = response.data.is_active
        }
        return response.data.is_active
      }
      throw new Error('Failed to toggle rule')
    } catch (error) {
      console.error('Failed to toggle rule:', error)
      throw error
    }
  }
  
  async function upgradeRule(gameId: string, ruleId: string) {
    isLoading.value = true
    try {
      const response = await api.post(`/api/games/${gameId}/rules/${ruleId}/upgrade`)
      
      if (response.data.success) {
        const index = rules.value.findIndex(r => r.id === ruleId)
        if (index !== -1) {
          rules.value[index] = { ...rules.value[index], ...response.data.rule }
        }
        
        // 更新恐惧点数
        const gameStore = useGameStore()
        if (gameStore.gameState) {
          gameStore.gameState.fear_points = response.data.remaining_fear_points
        }
        
        return response.data.rule
      }
      throw new Error('Failed to upgrade rule')
    } catch (error) {
      console.error('Failed to upgrade rule:', error)
      throw error
    } finally {
      isLoading.value = false
    }
  }
  
  async function calculateRuleCost(ruleData: any) {
    try {
      const response = await api.post('/api/rules/calculate-cost', ruleData)
      return response.data.cost
    } catch (error) {
      console.error('Failed to calculate rule cost:', error)
      return 100 // 默认成本
    }
  }
  
  function clearRules() {
    rules.value = []
    selectedTemplate.value = null
  }
  
  return {
    // 状态
    rules,
    templates,
    selectedTemplate,
    isCreating,
    isLoading,
    
    // 计算属性
    activeRules,
    totalRuleCost,
    canCreateRule,
    
    // 方法
    loadTemplates,
    loadGameRules,
    createRuleFromTemplate,
    createCustomRule,
    parseRuleWithAI,
    toggleRule,
    upgradeRule,
    calculateRuleCost,
    clearRules
  }
})
