// 模拟游戏数据，用于测试前端界面
export const mockGameState = {
  game_id: "test-game-001",
  current_turn: 5,
  phase: "SETUP",
  mode: "BACKSTAGE",
  fear_points: 850,
  fear_harvested: 350,
  rules_triggered: 12,
  game_over: false,
  game_over_reason: null,
  
  npcs: [
    {
      id: "npc-001",
      name: "张三",
      hp: 75,
      sanity: 60,
      fear: 45,
      location: "走廊",
      is_alive: true
    },
    {
      id: "npc-002", 
      name: "李四",
      hp: 30,
      sanity: 20,
      fear: 85,
      location: "房间A",
      is_alive: true
    },
    {
      id: "npc-003",
      name: "王五",
      hp: 0,
      sanity: 0,
      fear: 100,
      location: "地下室",
      is_alive: false
    },
    {
      id: "npc-004",
      name: "赵六",
      hp: 90,
      sanity: 80,
      fear: 25,
      location: "大厅",
      is_alive: true
    }
  ],
  
  rules: [
    {
      id: "rule-001",
      name: "午夜诅咒",
      description: "午夜时分，走廊中的人将受到诅咒",
      on_cooldown: false,
      cooldown_remaining: 0
    },
    {
      id: "rule-002",
      name: "血月降临",
      description: "当有人死亡时，所有人恐惧值+20",
      on_cooldown: true,
      cooldown_remaining: 2
    },
    {
      id: "rule-003",
      name: "镜中恶魔",
      description: "照镜子的人理智-30",
      on_cooldown: false,
      cooldown_remaining: 0
    }
  ],
  
  events_history: [
    {
      id: "evt-001",
      type: "death",
      message: "王五在地下室被黑暗吞噬，永远消失了",
      timestamp: new Date(Date.now() - 60000),
      severity: "death"
    },
    {
      id: "evt-002",
      type: "rule_trigger",
      message: "【血月降临】规则触发！所有人恐惧值上升",
      timestamp: new Date(Date.now() - 120000),
      severity: "warning"
    },
    {
      id: "evt-003",
      type: "damage",
      message: "李四受到了严重伤害，HP -45",
      timestamp: new Date(Date.now() - 180000),
      severity: "danger"
    },
    {
      id: "evt-004",
      type: "fear",
      message: "张三目睹了恐怖的景象，恐惧值 +30",
      timestamp: new Date(Date.now() - 240000),
      severity: "warning"
    },
    {
      id: "evt-005",
      type: "dialogue",
      message: "李四: \"我...我不能再待在这里了...\"",
      timestamp: new Date(Date.now() - 300000),
      severity: "info"
    },
    {
      id: "evt-006",
      type: "action",
      message: "赵六尝试打开密室的门",
      timestamp: new Date(Date.now() - 360000),
      severity: "info"
    },
    {
      id: "evt-007",
      type: "system",
      message: "新的一天开始了...",
      timestamp: new Date(Date.now() - 420000),
      severity: "info"
    }
  ]
}

// 模拟API响应
export const mockApiResponses = {
  // 创建游戏
  createGame: {
    success: true,
    data: {
      game_id: "test-game-001",
      message: "游戏创建成功"
    }
  },
  
  // 推进回合
  advanceTurn: {
    success: true,
    data: {
      current_turn: 6,
      events: [
        {
          type: "dialogue",
          message: "张三: \"这里越来越诡异了...\""
        },
        {
          type: "action",
          message: "李四躲进了角落"
        }
      ]
    }
  },
  
  // 创建规则
  createRule: {
    success: true,
    data: {
      rule_id: "rule-004",
      name: "暗影低语",
      cost: 100,
      message: "规则创建成功"
    }
  },
  
  // 保存游戏
  saveGame: {
    success: true,
    data: {
      save_id: "save-001",
      timestamp: new Date(),
      message: "游戏已保存"
    }
  }
}

// 生成随机事件（用于测试动态更新）
export function generateRandomEvent() {
  const eventTypes = [
    { type: 'damage', message: '某人受到了伤害', severity: 'danger' },
    { type: 'fear', message: '恐惧在蔓延...', severity: 'warning' },
    { type: 'dialogue', message: '有人在低语...', severity: 'info' },
    { type: 'action', message: '某人做了一个危险的决定', severity: 'info' },
    { type: 'rule_trigger', message: '一条规则被触发了', severity: 'warning' }
  ]
  
  const randomEvent = eventTypes[Math.floor(Math.random() * eventTypes.length)]
  
  return {
    id: `evt-${Date.now()}`,
    type: randomEvent.type,
    message: randomEvent.message,
    timestamp: new Date(),
    severity: randomEvent.severity
  }
}

// 模拟NPC状态变化
export function updateNPCStatus(npc: any) {
  // 随机改变NPC状态
  if (npc.is_alive) {
    npc.hp = Math.max(0, npc.hp + Math.floor(Math.random() * 21) - 10)
    npc.sanity = Math.max(0, Math.min(100, npc.sanity + Math.floor(Math.random() * 21) - 10))
    npc.fear = Math.min(100, npc.fear + Math.floor(Math.random() * 11))
    
    if (npc.hp === 0) {
      npc.is_alive = false
    }
  }
  
  return npc
}

// 导出默认mock store
export default {
  gameState: mockGameState,
  apiResponses: mockApiResponses,
  generateRandomEvent,
  updateNPCStatus
}
