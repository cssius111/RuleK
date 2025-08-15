export const RULE_TEMPLATES = [
  {
    id: 'mirror_death',
    name: '午夜照镜死',
    description: '午夜12点照镜子会看到恐怖的景象',
    cost: 300,
    trigger: {
      action: 'look_mirror',
      time: '00:00'
    },
    effects: [{
      type: 'fear',
      value: 50
    }]
  },
  {
    id: 'corridor_whisper',
    name: '走廊低语',
    description: '晚上10点后在走廊会听到诡异的低语声',
    cost: 200,
    trigger: {
      action: 'move',
      location: 'corridor',
      time_range: '22:00-06:00'
    },
    effects: [{
      type: 'fear',
      value: 30
    }]
  },
  {
    id: 'shadow_follower',
    name: '影子跟随者',
    description: '独自一人时，影子会做出不同的动作',
    cost: 400,
    trigger: {
      condition: 'alone'
    },
    effects: [{
      type: 'sanity',
      value: -20
    }]
  },
  {
    id: 'door_knock',
    name: '敲门声',
    description: '深夜会听到房门被敲响，但门外没有人',
    cost: 250,
    trigger: {
      time_range: '02:00-04:00',
      probability: 0.3
    },
    effects: [{
      type: 'fear',
      value: 40
    }]
  }
]

export function getRuleTemplate(id: string) {
  return RULE_TEMPLATES.find(t => t.id === id)
}

export function calculateRuleCost(rule: any): number {
  let baseCost = 100
  
  // 根据效果类型增加成本
  if (rule.effects) {
    rule.effects.forEach((effect: any) => {
      if (effect.type === 'death') baseCost += 500
      else if (effect.type === 'fear') baseCost += effect.value * 2
      else if (effect.type === 'sanity') baseCost += Math.abs(effect.value) * 3
    })
  }
  
  // 根据触发条件调整
  if (rule.trigger) {
    if (rule.trigger.probability && rule.trigger.probability < 0.5) {
      baseCost *= rule.trigger.probability * 2
    }
  }
  
  return Math.floor(baseCost)
}
