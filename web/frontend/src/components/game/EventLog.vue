<template>
  <div class="event-log">
    <h3 class="section-title">事件日志</h3>
    
    <div class="log-container">
      <n-scrollbar style="max-height: 600px">
        <n-timeline>
          <n-timeline-item
            v-for="(event, index) in reversedEvents"
            :key="index"
            :type="getEventType(event.type)"
            :title="getEventTitle(event)"
            :time="getEventTime(event)"
          >
            <div class="event-content" v-html="getEventContent(event)"></div>
          </n-timeline-item>
        </n-timeline>
        
        <n-empty 
          v-if="gameStore.events.length === 0"
          description="暂无事件发生"
        />
      </n-scrollbar>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import { NScrollbar, NTimeline, NTimelineItem, NEmpty } from 'naive-ui'
import { useGameStore } from '@/stores/game'

const gameStore = useGameStore()

// 反转事件顺序，最新的在上面
const reversedEvents = computed(() => [...gameStore.events].reverse())

function getEventType(type: string) {
  const typeMap: Record<string, 'success' | 'warning' | 'error' | 'info'> = {
    'rule_triggered': 'error',
    'npc_death': 'error',
    'npc_action': 'info',
    'dialogue': 'default',
    'random_event': 'warning',
    'rule_created': 'success'
  }
  return typeMap[type] || 'default'
}

function getEventTitle(event: any) {
  const titleMap: Record<string, string> = {
    'rule_triggered': '规则触发',
    'npc_death': 'NPC死亡',
    'npc_action': 'NPC行动',
    'dialogue': '对话',
    'random_event': '随机事件',
    'rule_created': '规则创建'
  }
  return titleMap[event.type] || event.type
}

function getEventTime(event: any) {
  if (event.timestamp) {
    const date = new Date(event.timestamp)
    return date.toLocaleTimeString()
  }
  return ''
}

function getEventContent(event: any) {
  switch (event.type) {
    case 'rule_triggered':
      return `<strong>${event.rule}</strong> 对 <strong>${event.npc}</strong> 生效<br/>
              效果：${event.result?.effect || '未知'}`
    
    case 'npc_death':
      return `<strong>${event.npc}</strong> 死亡<br/>
              死因：${event.cause || '未知'}`
    
    case 'npc_action':
      return `<strong>${event.npc}</strong> ${event.action}`
    
    case 'dialogue':
      if (event.data && Array.isArray(event.data)) {
        return event.data.map((msg: any) => 
          `<strong>${msg.speaker}:</strong> ${msg.content}`
        ).join('<br/>')
      }
      return event.content || '对话内容'
    
    case 'random_event':
      return event.description || '发生了奇怪的事情...'
    
    case 'rule_created':
      return `创建了新规则：<strong>${event.rule_name}</strong>`
    
    default:
      return event.description || JSON.stringify(event.data || {})
  }
}
</script>

<style lang="scss" scoped>
.event-log {
  height: 100%;
  display: flex;
  flex-direction: column;
  
  .section-title {
    color: #8b0000;
    margin-bottom: 1rem;
    padding-bottom: 0.5rem;
    border-bottom: 1px solid #333;
  }
  
  .log-container {
    flex: 1;
    overflow: hidden;
    
    :deep(.n-timeline) {
      padding: 1rem;
    }
    
    .event-content {
      color: #ccc;
      line-height: 1.5;
      
      :deep(strong) {
        color: #e0e0e0;
      }
    }
  }
}
</style>
