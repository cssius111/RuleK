<template>
  <div class="action-buttons">
    <n-button 
      type="primary" 
      size="large"
      block
      :loading="gameStore.isLoading"
      @click="handleAdvanceTurn"
    >
      <template #icon>
        <n-icon>
          <PlayCircleOutline />
        </n-icon>
      </template>
      推进回合
    </n-button>
    
    <n-button 
      size="large"
      block
      @click="$emit('create-rule')"
    >
      <template #icon>
        <n-icon>
          <AddCircleOutline />
        </n-icon>
      </template>
      创建规则
    </n-button>
    
    <n-button 
      size="large"
      block
      :disabled="gameStore.gameState?.mode === 'in_scene'"
      @click="handleSwitchMode"
    >
      <template #icon>
        <n-icon>
          <SwapOutline />
        </n-icon>
      </template>
      {{ modeButtonText }}
    </n-button>
    
    <n-divider />
    
    <div class="quick-stats">
      <div class="stat-item">
        <span class="label">总恐惧收获:</span>
        <span class="value">{{ gameStore.gameState?.total_fear_gained || 0 }}</span>
      </div>
      <div class="stat-item">
        <span class="label">规则触发次数:</span>
        <span class="value">{{ totalRuleTriggers }}</span>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import { NButton, NIcon, NDivider, useMessage } from 'naive-ui'
import { PlayCircleOutline, AddCircleOutline, SwapOutline } from '@vicons/ionicons5'
import { useGameStore } from '@/stores/game'

const gameStore = useGameStore()
const message = useMessage()

defineEmits<{
  'create-rule': []
}>()

const modeButtonText = computed(() => {
  return gameStore.gameState?.mode === 'backstage' ? '亲自下场' : '回到幕后'
})

const totalRuleTriggers = computed(() => {
  return gameStore.rules.reduce((sum, rule) => sum + rule.times_triggered, 0)
})

async function handleAdvanceTurn() {
  try {
    const result = await gameStore.advanceTurn()
    
    if (result.narrative) {
      // TODO: 显示叙事文本
      console.log('Narrative:', result.narrative)
    }
    
    if (result.fear_gained > 0) {
      message.success(`获得 ${result.fear_gained} 点恐惧值！`)
    }
  } catch (e: any) {
    message.error(e.message || '推进回合失败')
  }
}

function handleSwitchMode() {
  // TODO: 实现模式切换
  message.info('模式切换功能开发中...')
}
</script>

<style lang="scss" scoped>
.action-buttons {
  display: flex;
  flex-direction: column;
  gap: 1rem;
  
  .quick-stats {
    display: flex;
    flex-direction: column;
    gap: 0.5rem;
    padding: 0.5rem;
    background: rgba(42, 42, 42, 0.5);
    border-radius: 4px;
    
    .stat-item {
      display: flex;
      justify-content: space-between;
      font-size: 0.9rem;
      
      .label {
        color: #999;
      }
      
      .value {
        color: #e0e0e0;
        font-weight: bold;
      }
    }
  }
}
</style>
