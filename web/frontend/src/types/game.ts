// 游戏相关类型定义

// ==================== 请求类型 ====================

export interface GameCreateRequest {
  difficulty: 'easy' | 'normal' | 'hard'
  npc_count: number
}

export interface RuleCreateRequest {
  name: string
  description: string
  requirements: Record<string, any>
  trigger: Record<string, any>
  effect: Record<string, any>
  cost: number
}

export interface ActionRequest {
  action_type: string
  target?: string
  params?: Record<string, any>
}

// ==================== 响应类型 ====================

export interface NPCStatus {
  id: string
  name: string
  hp: number
  sanity: number
  fear: number
  location: string
  status_effects: string[]
  is_alive: boolean
}

export interface RuleInfo {
  id: string
  name: string
  description: string
  level: number
  cost: number
  is_active: boolean
  times_triggered: number
  loopholes: Array<{
    id: string
    description: string
    patched: boolean
  }>
}

export interface GameStateResponse {
  game_id: string
  started_at: string
  current_turn: number
  fear_points: number
  phase: string
  mode: string
  time_of_day: string
  npcs: NPCStatus[]
  active_rules: number
  total_fear_gained: number
  npcs_died: number
}

export interface TurnResult {
  turn: number
  events: Array<{
    type: string
    [key: string]: any
  }>
  fear_gained: number
  npcs_affected: string[]
  rules_triggered: string[]
  narrative?: string
}

export interface GameUpdate {
  update_type: 'state' | 'event' | 'npc' | 'rule' | 'dialogue'
  game_id: string
  data: any
  timestamp: string
  type?: string // for ping/pong
}

// ==================== 游戏模型 ====================

export interface GameState {
  game_id: string
  started_at: string
  current_turn: number
  fear_points: number
  phase: GamePhase
  mode: GameMode
  time_of_day: TimeOfDay
  npcs: NPCStatus[]
  active_rules: number
  total_fear_gained: number
  npcs_died: number
}

export interface NPC {
  id: string
  name: string
  hp: number
  sanity: number
  fear: number
  suspicion: number
  location: string
  is_alive: boolean
  death_cause?: string
  death_turn?: number
  inventory: string[]
  memory: any[]
  relationships: Record<string, number>
  personality: {
    rationality: number
    courage: number
    curiosity: number
    sociability: number
    loophole_sense: number
    observation: number
  }
  behavior_weights: {
    investigate: number
    escape: number
    cooperate: number
    selfish: number
  }
}

export interface Rule {
  id: string
  name: string
  description: string
  level: number
  cost: number
  is_active: boolean
  times_triggered: number
  requirements: {
    items?: string[]
    areas?: string[]
    time?: {
      from: string
      to: string
    }
    actor_traits?: Record<string, any>
  }
  trigger: {
    action: string
    location?: string[]
    time_range?: {
      from: string
      to: string
    }
    extra_conditions?: string[]
    probability: number
  }
  effect: {
    type: string
    fear_gain?: number
    sanity_loss?: number
    damage?: number
    side_effects?: string[]
  }
  loopholes: Array<{
    id: string
    description: string
    discovery_difficulty: number
    patched: boolean
  }>
}

export interface Area {
  id: string
  name: string
  description: string
  connections: string[]
  items: any[]
  effects: any[]
  properties: {
    light_level: number
    temperature: number
    safety_rating: number
  }
}

// ==================== 枚举类型 ====================

export enum GamePhase {
  SETUP = 'setup',
  MORNING_DIALOGUE = 'morning_dialogue',
  EVENING_DIALOGUE = 'evening_dialogue',
  ACTION = 'action',
  RESOLUTION = 'resolution'
}

export enum GameMode {
  BACKSTAGE = 'backstage',
  IN_SCENE = 'in_scene'
}

export enum TimeOfDay {
  MORNING = 'morning',
  AFTERNOON = 'afternoon',
  EVENING = 'evening',
  NIGHT = 'night'
}

export enum EffectType {
  INSTANT_DEATH = 'instant_death',
  DAMAGE = 'damage',
  FEAR_GAIN = 'fear_gain',
  SANITY_LOSS = 'sanity_loss',
  TELEPORT = 'teleport',
  TRANSFORM = 'transform',
  CURSE = 'curse'
}

// ==================== UI 相关类型 ====================

export interface Notification {
  id: string
  type: 'success' | 'warning' | 'error' | 'info'
  title: string
  message?: string
  duration?: number
}

export interface DialogueMessage {
  speaker: string
  content: string
  emotion?: string
  timestamp: string
}

export interface EventLog {
  id: string
  type: string
  description: string
  timestamp: string
  important: boolean
}
