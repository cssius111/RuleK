<template>
  <div class="rule-list">
    <h3 class="section-title">
      活跃规则
      <n-badge :value="gameStore.activeRules.length" />
    </h3>
    
    <n-scrollbar style="max-height: 400px">
      <n-list>
        <n-list-item v-for="rule in gameStore.rules" :key="rule.id">
          <n-thing>
            <template #header>
              <div class="rule-header">
                <span class="rule-name">{{ rule.name }}</span>
                <n-tag 
                  v-if="!rule.is_active" 
                  size="small" 
                  type="warning"
                >
                  已失效
                </n-tag>
              </div>
            </template>
            
            <template #description>
              {{ rule.description }}
            </template>
            
            <div class="rule-stats">
              <n-space size="small">
                <n-tag size="small">
                  Lv.{{ rule.level }}
                </n-tag>
                <n-tag size="small" type="info">
                  触发{{ rule.times_triggered }}次
                </n-tag>
                <n-tag 
                  v-if="rule.loopholes.some(l => !l.patched)" 
                  size="small" 
                  type="error"
                >
                  有破绽
                </n-tag>
              </n-space>
            </div>
          </n-thing>
        </n-list-item>
      </n-list>
      
      <n-empty 
        v-if="gameStore.rules.length === 0"
        description="尚未创建任何规则"
      />
    </n-scrollbar>
  </div>
</template>

<script setup lang="ts">
import { NScrollbar, NList, NListItem, NThing, NTag, NSpace, NBadge, NEmpty } from 'naive-ui'
import { useGameStore } from '@/stores/game'

const gameStore = useGameStore()
</script>

<style lang="scss" scoped>
.rule-list {
  .section-title {
    color: #8b0000;
    margin-bottom: 1rem;
    padding-bottom: 0.5rem;
    border-bottom: 1px solid #333;
    display: flex;
    justify-content: space-between;
    align-items: center;
  }
  
  .rule-header {
    display: flex;
    align-items: center;
    gap: 0.5rem;
    
    .rule-name {
      font-weight: bold;
      color: #e0e0e0;
    }
  }
  
  .rule-stats {
    margin-top: 0.5rem;
  }
  
  :deep(.n-list-item) {
    padding: 0.75rem;
    margin-bottom: 0.5rem;
    background: rgba(42, 42, 42, 0.5);
    border-radius: 4px;
    
    &:hover {
      background: rgba(42, 42, 42, 0.8);
    }
  }
}
</style>
