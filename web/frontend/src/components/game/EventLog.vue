<template>
  <div class="event-log">
    <div class="log-header">
      <h3 class="log-title blood-text">
        <span class="title-icon">📜</span>
        黑暗编年史
      </h3>
      <div class="log-controls">
        <button 
          @click="toggleAutoScroll" 
          class="control-btn"
          :class="{ active: autoScroll }"
          title="自动滚动"
        >
          {{ autoScroll ? '⏸' : '▶' }}
        </button>
        <button 
          @click="clearLog" 
          class="control-btn"
          title="清空日志"
        >
          🗑️
        </button>
      </div>
    </div>

    <div class="log-content" ref="logContent">
      <transition-group name="event-fade" tag="div">
        <div 
          v-for="(event, index) in displayEvents" 
          :key="`${event.id || index}-${event.timestamp}`"
          class="event-item"
          :class="getEventClass(event)"
        >
          <div class="event-time">
            {{ formatTime(event.timestamp) }}
          </div>
          <div class="event-icon">
            {{ getEventIcon(event.type) }}
          </div>
          <div class="event-message">
            {{ event.message }}
          </div>
        </div>
      </transition-group>

      <div v-if="displayEvents.length === 0" class="empty-log">
        <span class="empty-icon">📖</span>
        <span class="empty-text">黑暗的故事即将开始...</span>
      </div>
    </div>

    <!-- 血迹装饰 -->
    <div class="log-decorations">
      <div class="blood-splatter splatter-1"></div>
      <div class="blood-splatter splatter-2"></div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, watch, nextTick } from 'vue'

interface GameEvent {
  id?: string
  type: string
  message: string
  timestamp: string | Date
  severity?: 'info' | 'warning' | 'danger' | 'death'
}

interface Props {
  events: GameEvent[]
  maxEvents?: number
}

const props = withDefaults(defineProps<Props>(), {
  maxEvents: 20
})

const emit = defineEmits<{
  clearLog: []
}>()

// 状态
const autoScroll = ref(true)
const logContent = ref<HTMLElement>()

// 计算显示的事件（最新的在前）
const displayEvents = computed(() => {
  const sorted = [...props.events].sort((a, b) => {
    const timeA = new Date(a.timestamp).getTime()
    const timeB = new Date(b.timestamp).getTime()
    return timeB - timeA
  })
  return sorted.slice(0, props.maxEvents)
})

// 监听事件变化，自动滚动
watch(() => props.events.length, async () => {
  if (autoScroll.value && logContent.value) {
    await nextTick()
    logContent.value.scrollTop = 0
  }
})

// 格式化时间
const formatTime = (timestamp: string | Date) => {
  const date = new Date(timestamp)
  const hours = date.getHours().toString().padStart(2, '0')
  const minutes = date.getMinutes().toString().padStart(2, '0')
  const seconds = date.getSeconds().toString().padStart(2, '0')
  return `${hours}:${minutes}:${seconds}`
}

// 获取事件类名
const getEventClass = (event: GameEvent) => {
  const classes = ['event-' + event.type]
  if (event.severity) {
    classes.push('severity-' + event.severity)
  }
  return classes
}

// 获取事件图标
const getEventIcon = (type: string) => {
  const iconMap: Record<string, string> = {
    'death': '💀',
    'damage': '🩸',
    'fear': '😱',
    'rule_trigger': '⚡',
    'action': '🎯',
    'dialogue': '💬',
    'system': '⚙️',
    'warning': '⚠️',
    'info': 'ℹ️'
  }
  return iconMap[type] || '📝'
}

// 切换自动滚动
const toggleAutoScroll = () => {
  autoScroll.value = !autoScroll.value
}

// 清空日志
const clearLog = () => {
  emit('clearLog')
}
</script>

<style scoped>
.event-log {
  height: 100%;
  display: flex;
  flex-direction: column;
  position: relative;
}

.log-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding-bottom: 15px;
  margin-bottom: 20px;
  border-bottom: 2px solid var(--horror-border);
}

.log-title {
  margin: 0;
  font-size: 1.3rem;
  text-transform: uppercase;
  letter-spacing: 2px;
  display: flex;
  align-items: center;
  gap: 10px;
}

.title-icon {
  font-size: 1.5rem;
  filter: drop-shadow(0 0 10px currentColor);
  animation: page-turn 4s ease-in-out infinite;
}

@keyframes page-turn {
  0%, 100% { transform: rotateY(0deg); }
  50% { transform: rotateY(20deg); }
}

.log-controls {
  display: flex;
  gap: 10px;
}

.control-btn {
  width: 32px;
  height: 32px;
  background: rgba(139, 0, 0, 0.3);
  border: 1px solid var(--horror-border);
  color: var(--horror-text-secondary);
  font-size: 1rem;
  cursor: pointer;
  transition: all 0.3s;
  display: flex;
  align-items: center;
  justify-content: center;
}

.control-btn:hover {
  background: rgba(220, 20, 60, 0.3);
  border-color: var(--horror-accent);
  color: var(--horror-text);
}

.control-btn.active {
  background: var(--horror-primary);
  border-color: var(--horror-accent);
  color: var(--horror-text);
}

/* 日志内容 */
.log-content {
  flex: 1;
  overflow-y: auto;
  padding-right: 5px;
  position: relative;
}

/* 自定义滚动条 */
.log-content::-webkit-scrollbar {
  width: 8px;
}

.log-content::-webkit-scrollbar-track {
  background: rgba(139, 0, 0, 0.1);
  box-shadow: inset 0 0 5px rgba(0, 0, 0, 0.5);
}

.log-content::-webkit-scrollbar-thumb {
  background: linear-gradient(180deg, var(--horror-primary), var(--horror-accent));
  box-shadow: 0 0 5px rgba(220, 20, 60, 0.3);
}

/* 事件项 */
.event-item {
  display: flex;
  gap: 12px;
  padding: 12px;
  margin-bottom: 10px;
  background: rgba(0, 0, 0, 0.5);
  border-left: 3px solid var(--horror-border);
  transition: all 0.3s;
  animation: event-appear 0.5s ease-out;
}

@keyframes event-appear {
  from {
    opacity: 0;
    transform: translateX(-20px);
  }
  to {
    opacity: 1;
    transform: translateX(0);
  }
}

.event-item:hover {
  background: rgba(139, 0, 0, 0.2);
  border-left-color: var(--horror-accent);
  transform: translateX(5px);
}

/* 事件时间 */
.event-time {
  color: var(--horror-text-secondary);
  font-size: 0.8rem;
  font-family: monospace;
  opacity: 0.7;
  min-width: 60px;
}

/* 事件图标 */
.event-icon {
  font-size: 1.2rem;
  filter: drop-shadow(0 0 5px currentColor);
  min-width: 25px;
  text-align: center;
}

/* 事件消息 */
.event-message {
  flex: 1;
  color: var(--horror-text);
  line-height: 1.4;
}

/* 事件类型样式 */
.event-death {
  border-left-color: var(--horror-danger);
  background: rgba(139, 0, 0, 0.1);
}

.event-death .event-icon {
  color: var(--horror-danger);
  animation: death-pulse 1s ease-in-out;
}

@keyframes death-pulse {
  0%, 100% { transform: scale(1); }
  50% { transform: scale(1.3); }
}

.event-damage {
  border-left-color: var(--horror-accent);
}

.event-damage .event-icon {
  color: var(--horror-accent);
}

.event-fear {
  border-left-color: #ff9800;
}

.event-fear .event-icon {
  color: #ff9800;
}

.event-rule_trigger {
  border-left-color: #ffeb3b;
  background: rgba(255, 235, 59, 0.05);
}

.event-rule_trigger .event-icon {
  color: #ffeb3b;
  animation: lightning 0.5s ease-out;
}

@keyframes lightning {
  0%, 100% { opacity: 1; }
  50% { opacity: 0.3; }
}

/* 严重程度样式 */
.severity-danger {
  background: rgba(255, 0, 0, 0.1);
}

.severity-danger .event-message {
  color: var(--horror-accent);
  font-weight: 600;
}

.severity-death {
  background: linear-gradient(90deg, rgba(139, 0, 0, 0.3), rgba(0, 0, 0, 0.5));
  animation: death-flash 1s ease-out;
}

@keyframes death-flash {
  0% { background: rgba(255, 0, 0, 0.5); }
  100% { background: linear-gradient(90deg, rgba(139, 0, 0, 0.3), rgba(0, 0, 0, 0.5)); }
}

/* 空日志 */
.empty-log {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  gap: 15px;
  padding: 40px;
  color: var(--horror-text-secondary);
  opacity: 0.5;
  text-align: center;
}

.empty-icon {
  font-size: 3rem;
  filter: drop-shadow(0 0 10px rgba(139, 0, 0, 0.5));
}

.empty-text {
  font-style: italic;
  text-transform: uppercase;
  letter-spacing: 2px;
}

/* 过渡动画 */
.event-fade-enter-active,
.event-fade-leave-active {
  transition: all 0.3s ease;
}

.event-fade-enter-from {
  opacity: 0;
  transform: translateX(-30px);
}

.event-fade-leave-to {
  opacity: 0;
  transform: translateX(30px);
}

/* 装饰元素 */
.log-decorations {
  pointer-events: none;
  position: absolute;
  inset: 0;
}

.blood-splatter {
  position: absolute;
  background: radial-gradient(circle, var(--horror-accent) 20%, transparent 70%);
  filter: blur(15px);
  opacity: 0.1;
}

.splatter-1 {
  width: 150px;
  height: 100px;
  top: 10%;
  right: -30px;
  transform: rotate(45deg);
}

.splatter-2 {
  width: 100px;
  height: 80px;
  bottom: 20%;
  left: -20px;
  transform: rotate(-30deg);
}
</style>
