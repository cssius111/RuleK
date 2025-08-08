// 游戏相关类型定义

// 游戏难度枚举
export enum GameDifficulty {
  EASY = 'easy',
  NORMAL = 'normal', 
  HARD = 'hard',
  NIGHTMARE = 'nightmare'
}

// 游戏配置接口
export interface GameConfig {
  difficulty: GameDifficulty
  initialFearPoints: number
  initialNPCCount: number
  aiEnabled: boolean
  playerName?: string
}

// 游戏创建请求
export interface CreateGameRequest {
  config: GameConfig
}

// 游戏创建响应
export interface CreateGameResponse {
  gameId: string
  config: GameConfig
  state: GameState
  message: string
}

// NPC状态
export interface NPC {
  id: string
  name: string
  hp: number
  sanity: number
  fear: number
  location: string
  isAlive: boolean
  status?: string
}

// 规则定义
export interface Rule {
  id: string
  name: string
  description: string
  cost: number
  level: number
  triggerType: string
  effect: string
  cooldown: number
  currentCooldown: number
  isActive: boolean
}

// 游戏事件
export interface GameEvent {
  id: string
  turn: number
  type: string
  description: string
  timestamp: number
}

// 游戏状态
export interface GameState {
  gameId: string
  turn: number
  day: number
  phase: string
  mode: string
  fearPoints: number
  npcs: NPC[]
  rules: Rule[]
  events: GameEvent[]
  isGameOver: boolean
  winner?: string
}

// API响应包装
export interface ApiResponse<T> {
  success: boolean
  data?: T
  error?: string
  message?: string
}

// 游戏存档
export interface GameSave {
  id: string
  name: string
  gameState: GameState
  config: GameConfig
  createdAt: string
  updatedAt: string
}

// 表单验证规则
export interface ValidationRule {
  required?: boolean
  min?: number
  max?: number
  pattern?: RegExp
  message: string
}

// 难度配置预设
export const DIFFICULTY_PRESETS = {
  [GameDifficulty.EASY]: {
    fearPoints: 1500,
    npcCount: 3,
    description: '适合新手，NPC较少，恐惧点数充足'
  },
  [GameDifficulty.NORMAL]: {
    fearPoints: 1000,
    npcCount: 4,
    description: '标准难度，平衡的游戏体验'
  },
  [GameDifficulty.HARD]: {
    fearPoints: 750,
    npcCount: 5,
    description: '困难模式，需要精心策划'
  },
  [GameDifficulty.NIGHTMARE]: {
    fearPoints: 500,
    npcCount: 6,
    description: '噩梦难度，只有大师才能生存'
  }
}

// 游戏配置限制
export const GAME_CONFIG_LIMITS = {
  fearPoints: { min: 100, max: 5000 },
  npcCount: { min: 1, max: 10 },
  playerNameLength: { min: 1, max: 20 }
}
