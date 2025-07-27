<template>
  <div class="game-state-panel">
    <div class="state-item fear-points">
      <div class="label">恐惧积分</div>
      <div class="value horror-glow">{{ gameStore.fearPoints }}</div>
    </div>
    
    <div class="state-item">
      <div class="label">回合</div>
      <div class="value">{{ gameStore.gameState?.current_turn || 0 }}</div>
    </div>
    
    <div class="state-item">
      <div class="label">阶段</div>
      <div class="value">{{ phaseText }}</div>
    </div>
    
    <div class="state-item">
      <div class="label">时间</div>
      <div class="value">{{ timeText }}</div>
    </div>
    
    <div class="state-item">
      <div class="label">模式</div>
      <div class="value">{{ modeText }}</div>
    </div>
    
    <div class="state-item">
      <div class="label">存活NPC</div>
      <div class="value">{{ gameStore.aliveNPCs.length }} / {{ gameStore.npcs.length }}</div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import { useGameStore } from '@/stores/game'

const gameStore = useGameStore()

const phaseText = computed(() => {
  const phaseMap: Record<string, string> = {
    'setup': '准备',
    'morning_dialogue': '早间对话',
    'evening_dialogue': '夜间对话',
    'action': '行动',
    'resolution': '结算'
  }
  return phaseMap[gameStore.currentPhase] || gameStore.currentPhase
})

const timeText = computed(() => {
  const timeMap: Record<string, string> = {
    'morning': '早晨',
    'afternoon': '下午',
    'evening': '傍晚',
    'night': '深夜'
  }
  return timeMap[gameStore.gameState?.time_of_day || ''] || '未知'
})

const modeText = computed(() => {
  const modeMap: Record<string, string> = {
    'backstage': '幕后',
    'in_scene': '下场'
  }
  return modeMap[gameStore.gameState?.mode || ''] || '未知'
})
</script>

<style lang="scss" scoped>
.game-state-panel {
  display: flex;
  align-items: center;
  gap: 2rem;
  padding: 1rem 2rem;
  background: rgba(26, 26, 26, 0.95);
  
  .state-item {
    display: flex;
    flex-direction: column;
    align-items: center;
    
    .label {
      font-size: 0.8rem;
      color: #666;
      margin-bottom: 0.25rem;
    }
    
    .value {
      font-size: 1.2rem;
      font-weight: bold;
      color: #e0e0e0;
    }
    
    &.fear-points {
      .value {
        font-size: 1.5rem;
        color: #8b0000;
      }
    }
  }
}

@media (max-width: 768px) {
  .game-state-panel {
    flex-wrap: wrap;
    gap: 1rem;
    padding: 0.75rem 1rem;
    
    .state-item {
      min-width: 80px;
    }
  }
}
</style>
