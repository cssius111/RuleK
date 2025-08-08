<template>
  <div class="status-bar">
    <div class="status-section">
      <div class="status-item">
        <span class="status-label">回合</span>
        <span class="status-value blood-text">{{ gameState?.current_turn || 0 }}</span>
      </div>
      <div class="status-item">
        <span class="status-label">天数</span>
        <span class="status-value">第 {{ currentDay }} 天</span>
      </div>
      <div class="status-item">
        <span class="status-label">时段</span>
        <span class="status-value">{{ timeOfDayText }}</span>
      </div>
    </div>

    <div class="status-center">
      <div class="fear-counter">
        <span class="fear-icon">💀</span>
        <div class="fear-info">
          <div class="fear-label">恐惧能量</div>
          <div class="fear-value blood-text horror-flicker">
            {{ gameState?.fear_points || 0 }}
          </div>
        </div>
        <span class="fear-icon">💀</span>
      </div>
    </div>

    <div class="status-section">
      <div class="status-item">
        <span class="status-label">模式</span>
        <button 
          @click="$emit('toggleMode')" 
          class="mode-toggle"
          :class="{ backstage: gameState?.mode === 'BACKSTAGE' }"
        >
          {{ modeText }}
        </button>
      </div>
      <div class="status-item">
        <span class="status-label">存活</span>
        <span class="status-value">
          <span class="alive-count">{{ aliveCount }}</span>
          <span class="status-separator">/</span>
          <span class="total-count">{{ totalCount }}</span>
        </span>
      </div>
      <div class="status-item">
        <span class="status-label">状态</span>
        <span class="status-value phase-indicator">{{ phaseText }}</span>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue'

interface Props {
  gameState: any
}

const props = defineProps<Props>()
const emit = defineEmits<{
  toggleMode: []
}>()

// 计算当前天数
const currentDay = computed(() => {
  const turn = props.gameState?.current_turn || 0
  return Math.floor(turn / 3) + 1
})

// 时段文本
const timeOfDayText = computed(() => {
  const turn = props.gameState?.current_turn || 0
  const timeSlot = turn % 3
  const times = ['深夜', '黎明', '黄昏']
  return times[timeSlot] || '未知'
})

// 模式文本
const modeText = computed(() => {
  return props.gameState?.mode === 'BACKSTAGE' ? '幕后模式' : '亲临现场'
})

// 存活NPC数量
const aliveCount = computed(() => {
  return props.gameState?.npcs?.filter((npc: any) => npc.is_alive).length || 0
})

// 总NPC数量
const totalCount = computed(() => {
  return props.gameState?.npcs?.length || 0
})

// 阶段文本
const phaseText = computed(() => {
  const phase = props.gameState?.phase
  const phaseMap: any = {
    'SETUP': '准备',
    'ACTION': '行动',
    'RESOLUTION': '结算'
  }
  return phaseMap[phase] || '待机'
})
</script>

<style scoped>
.status-bar {
  background: linear-gradient(135deg, rgba(20, 10, 10, 0.98), rgba(40, 0, 0, 0.95));
  border-bottom: 2px solid var(--horror-border);
  padding: 15px 20px;
  display: flex;
  justify-content: space-between;
  align-items: center;
  box-shadow: 
    0 10px 30px rgba(139, 0, 0, 0.5),
    inset 0 -2px 10px rgba(0, 0, 0, 0.5);
  position: relative;
  z-index: 10;
}

/* 添加血迹纹理 */
.status-bar::before {
  content: '';
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: 
    repeating-linear-gradient(
      90deg,
      transparent,
      transparent 100px,
      rgba(139, 0, 0, 0.05) 100px,
      rgba(139, 0, 0, 0.05) 101px
    );
  pointer-events: none;
}

.status-section {
  display: flex;
  gap: 30px;
  align-items: center;
}

.status-item {
  display: flex;
  align-items: center;
  gap: 10px;
}

.status-label {
  color: var(--horror-text-secondary);
  font-size: 0.85rem;
  text-transform: uppercase;
  letter-spacing: 1px;
  opacity: 0.8;
}

.status-value {
  color: var(--horror-text);
  font-size: 1.1rem;
  font-weight: 600;
  text-transform: uppercase;
  letter-spacing: 1px;
}

/* 中央恐惧计数器 */
.status-center {
  flex: 0 0 auto;
}

.fear-counter {
  display: flex;
  align-items: center;
  gap: 20px;
  padding: 10px 30px;
  background: linear-gradient(135deg, rgba(139, 0, 0, 0.2), rgba(220, 20, 60, 0.1));
  border: 2px solid var(--horror-primary);
  box-shadow: 
    0 0 30px rgba(220, 20, 60, 0.4),
    inset 0 0 20px rgba(139, 0, 0, 0.3);
  position: relative;
  animation: fear-pulse 3s ease-in-out infinite;
}

@keyframes fear-pulse {
  0%, 100% { 
    box-shadow: 
      0 0 30px rgba(220, 20, 60, 0.4),
      inset 0 0 20px rgba(139, 0, 0, 0.3);
  }
  50% { 
    box-shadow: 
      0 0 50px rgba(220, 20, 60, 0.6),
      inset 0 0 30px rgba(139, 0, 0, 0.5);
  }
}

.fear-icon {
  font-size: 1.5rem;
  filter: drop-shadow(0 0 10px rgba(220, 20, 60, 0.8));
  animation: skull-float 4s ease-in-out infinite;
}

.fear-icon:nth-child(3) {
  animation-delay: 2s;
}

@keyframes skull-float {
  0%, 100% { transform: translateY(0); }
  50% { transform: translateY(-3px); }
}

.fear-info {
  text-align: center;
}

.fear-label {
  color: var(--horror-text-secondary);
  font-size: 0.8rem;
  text-transform: uppercase;
  letter-spacing: 2px;
  margin-bottom: 5px;
}

.fear-value {
  font-size: 2rem;
  font-weight: 900;
  text-shadow: 
    0 0 20px currentColor,
    0 2px 4px rgba(0, 0, 0, 0.8);
  letter-spacing: 2px;
}

/* 模式切换按钮 */
.mode-toggle {
  background: linear-gradient(135deg, var(--horror-primary), var(--horror-accent));
  border: 1px solid var(--horror-accent);
  color: var(--horror-text);
  padding: 5px 15px;
  font-size: 0.9rem;
  text-transform: uppercase;
  letter-spacing: 1px;
  cursor: pointer;
  transition: all 0.3s;
  font-weight: 600;
  position: relative;
  overflow: hidden;
}

.mode-toggle:hover {
  transform: scale(1.05);
  box-shadow: 0 0 20px rgba(220, 20, 60, 0.5);
}

.mode-toggle.backstage {
  background: linear-gradient(135deg, rgba(40, 40, 40, 0.9), rgba(60, 60, 60, 0.9));
  border-color: #666;
}

.mode-toggle::before {
  content: '';
  position: absolute;
  top: 50%;
  left: -100%;
  width: 100%;
  height: 100%;
  background: linear-gradient(90deg, transparent, rgba(255, 255, 255, 0.2), transparent);
  transition: left 0.5s;
}

.mode-toggle:hover::before {
  left: 100%;
}

/* 存活计数 */
.alive-count {
  color: var(--horror-accent);
  font-weight: 700;
  text-shadow: 0 0 5px currentColor;
}

.status-separator {
  color: var(--horror-text-secondary);
  margin: 0 2px;
}

.total-count {
  color: var(--horror-text-secondary);
}

/* 阶段指示器 */
.phase-indicator {
  padding: 4px 12px;
  background: rgba(139, 0, 0, 0.3);
  border: 1px solid var(--horror-border);
  font-size: 0.9rem;
}

/* 响应式设计 */
@media (max-width: 1024px) {
  .status-bar {
    flex-direction: column;
    gap: 15px;
    padding: 10px;
  }
  
  .status-section {
    width: 100%;
    justify-content: center;
  }
  
  .fear-counter {
    padding: 8px 20px;
  }
  
  .fear-value {
    font-size: 1.5rem;
  }
}

@media (max-width: 640px) {
  .status-section {
    flex-wrap: wrap;
    gap: 15px;
  }
  
  .status-item {
    flex: 1 1 auto;
    min-width: 80px;
    flex-direction: column;
    gap: 5px;
    text-align: center;
  }
  
  .fear-counter {
    padding: 5px 15px;
  }
  
  .fear-icon {
    display: none;
  }
}
</style>
