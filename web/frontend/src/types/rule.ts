/**
 * 规则系统类型定义
 */

export type TriggerType = 'action' | 'time' | 'location' | 'item' | 'condition' | 'random'

export type EffectType = 
  | 'instant_death'
  | 'fear_increase'
  | 'sanity_decrease'
  | 'teleport'
  | 'item_grant'
  | 'continuous_damage'

export interface RuleTrigger {
  type: TriggerType
  conditions: Record<string, any>
  probability: number
}

export interface RuleEffect {
  type: EffectType
  value?: number
  target?: string
  duration?: number
  params?: Record<string, any>
}

export interface Rule {
  id: string
  name: string
  description: string
  cost: number
  trigger: RuleTrigger
  effects: RuleEffect[]
  cooldown: number
  is_active: boolean
  level: number
  category?: string
}

export interface RuleTemplate extends Rule {
  difficulty: 'easy' | 'normal' | 'hard'
}

export interface RuleCreationRequest {
  name: string
  description: string
  trigger: RuleTrigger
  effects: RuleEffect[]
  cooldown?: number
}

export interface AIRuleParseResult {
  rule_name: string
  description: string
  trigger: RuleTrigger
  effects: RuleEffect[]
  estimated_cost: number
  suggestions: string[]
}

export interface RuleCostBreakdown {
  base_cost: number
  effect_cost: number
  probability_modifier: number
  cooldown_modifier: number
}
