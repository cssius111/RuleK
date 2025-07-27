<template>
  <n-card 
    class="npc-card" 
    :class="{ dead: !npc.is_alive }"
    hoverable
    @click="$emit('click', npc)"
  >
    <div class="npc-header">
      <h4 class="npc-name">{{ npc.name }}</h4>
      <n-tag 
        v-if="!npc.is_alive" 
        type="error" 
        size="small"
      >
        已死亡
      </n-tag>
    </div>
    
    <div class="npc-stats">
      <div class="stat-row">
        <span class="stat-label">HP</span>
        <n-progress 
          type="line"
          :percentage="hpPercentage"
          :color="hpColor"
          :show-indicator="false"
        />
        <span class="stat-value">{{ npc.hp }}/100</span>
      </div>
      
      <div class="stat-row">
        <span class="stat-label">理智</span>
        <n-progress 
          type="line"
          :percentage="sanityPercentage"
          :color="sanityColor"
          :show-indicator="false"
        />
        <span class="stat-value">{{ npc.sanity }}/100</span>
      </div>
      
      <div class="stat-row">
        <span class="stat-label">恐惧</span>
        <n-progress 
          type="line"
          :percentage="npc.fear"
          :color="fearColor"
          :show-indicator="false"
        />
        <span class="stat-value">{{ npc.fear }}/100</span>
      </div>
    </div>
    
    <div class="npc-info">
      <div class="info-item">
        <span class="info-label">位置:</span>
        <span class="info-value">{{ locationName }}</span>
      </div>
      
      <div v-if="npc.status_effects.length > 0" class="info-item">
        <span class="info-label">状态:</span>
        <n-space size="small">
          <n-tag 
            v-for="effect in npc.status_effects" 
            :key="effect"
            size="small"
            :type="getEffectType(effect)"
          >
            {{ effect }}
          </n-tag>
        </n-space>
      </div>
    </div>
  </n-card>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import { NCard, NTag, NProgress, NSpace } from 'naive-ui'
import type { NPCStatus } from '@/types/game'

const props = defineProps<{
  npc: NPCStatus
}>()

defineEmits<{
  click: [npc: NPCStatus]
}>()

// 计算属性
const hpPercentage = computed(() => props.npc.hp)
const sanityPercentage = computed(() => props.npc.sanity)

const hpColor = computed(() => {
  if (props.npc.hp > 70) return '#52c41a'
  if (props.npc.hp > 30) return '#faad14'
  return '#f5222d'
})

const sanityColor = computed(() => {
  if (props.npc.sanity > 70) return '#1890ff'
  if (props.npc.sanity > 30) return '#faad14'
  return '#722ed1'
})

const fearColor = '#8b0000'

const locationName = computed(() => {
  const locationMap: Record<string, string> = {
    'living_room': '客厅',
    'bedroom_a': '卧室A',
    'bedroom_b': '卧室B',
    'kitchen': '厨房',
    'bathroom': '浴室',
    'corridor': '走廊'
  }
  return locationMap[props.npc.location] || props.npc.location
})

function getEffectType(effect: string) {
  // 根据效果类型返回不同的标签类型
  if (effect.includes('诅咒') || effect.includes('中毒')) return 'error'
  if (effect.includes('保护') || effect.includes('祝福')) return 'success'
  return 'warning'
}
</script>

<style lang="scss" scoped>
.npc-card {
  background: rgba(26, 26, 26, 0.9);
  border: 1px solid #333;
  transition: all 0.3s;
  
  &:hover {
    border-color: #8b0000;
    transform: translateY(-2px);
  }
  
  &.dead {
    opacity: 0.6;
    filter: grayscale(100%);
  }
  
  .npc-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 1rem;
    
    .npc-name {
      margin: 0;
      color: #e0e0e0;
    }
  }
  
  .npc-stats {
    display: flex;
    flex-direction: column;
    gap: 0.5rem;
    margin-bottom: 1rem;
    
    .stat-row {
      display: flex;
      align-items: center;
      gap: 0.5rem;
      
      .stat-label {
        width: 40px;
        font-size: 0.8rem;
        color: #999;
      }
      
      :deep(.n-progress) {
        flex: 1;
        height: 8px;
      }
      
      .stat-value {
        width: 50px;
        text-align: right;
        font-size: 0.8rem;
        color: #ccc;
      }
    }
  }
  
  .npc-info {
    display: flex;
    flex-direction: column;
    gap: 0.5rem;
    
    .info-item {
      display: flex;
      align-items: center;
      gap: 0.5rem;
      
      .info-label {
        font-size: 0.8rem;
        color: #999;
      }
      
      .info-value {
        font-size: 0.8rem;
        color: #ccc;
      }
    }
  }
}
</style>
