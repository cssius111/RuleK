<template>
  <div class="action-panel">
    <!-- 游戏控制 -->
    <div class="panel-section">
      <h3 class="section-title">
        <span class="title-icon">🎮</span>
        游戏控制
      </h3>
      
      <div class="action-buttons">
        <button 
          @click="$emit('advanceTurn')" 
          :disabled="loading || !canAdvanceTurn"
          class="action-btn primary pulse-horror"
        >
          <span class="btn-icon">⏭</span>
          <span class="btn-text">推进回合</span>
        </button>

        <button 
          @click="$emit('createRule')"
          :disabled="loading"
          class="action-btn secondary"
        >
          <span class="btn-icon">📜</span>
          <span class="btn-text">创建规则</span>
        </button>

        <button 
          v-if="gameState?.aiEnabled"
          @click="handleAITurn"
          :disabled="loading || !canAdvanceTurn"
          class="action-btn ai-btn"
        >
          <span class="btn-icon">🤖</span>
          <span class="btn-text">AI回合</span>
        </button>
      </div>
    </div>

    <!-- 规则信息 -->
    <div class="panel-section">
      <h3 class="section-title">
        <span class="title-icon">⚡</span>
        激活规则
      </h3>
      
      <div class="rules-list">
        <div v-if="activeRules.length === 0" class="no-rules">
          <p>暂无激活规则</p>
        </div>
        <div 
          v-else
          v-for="rule in activeRules" 
          :key="rule.id"
          class="rule-item"
        >
          <span class="rule-name">{{ rule.name }}</span>
          <span class="rule-cooldown" v-if="rule.cooldown > 0">
            冷却: {{ rule.cooldown }}
          </span>
        </div>
      </div>
    </div>

    <!-- 游戏统计 -->
    <div class="panel-section">
      <h3 class="section-title">
        <span class="title-icon">📊</span>
        游戏统计
      </h3>
      
      <div class="stats-grid">
        <div class="stat-item">
          <span class="stat-label">总击杀</span>
          <span class="stat-value blood-text">{{ gameState?.stats?.totalKills || 0 }}</span>
        </div>
        <div class="stat-item">
          <span class="stat-label">恐惧收集</span>
          <span class="stat-value">{{ gameState?.stats?.totalFear || 0 }}</span>
        </div>
        <div class="stat-item">
          <span class="stat-label">规则触发</span>
          <span class="stat-value">{{ gameState?.stats?.ruleTriggers || 0 }}</span>
        </div>
        <div class="stat-item">
          <span class="stat-label">存活时间</span>
          <span class="stat-value">{{ formatSurvivalTime() }}</span>
        </div>
      </div>
    </div>

    <!-- 系统操作 -->
    <div class="panel-section">
      <h3 class="section-title">
        <span class="title-icon">⚙️</span>
        系统操作
      </h3>
      
      <div class="system-buttons">
        <button 
          @click="$emit('saveGame')"
          :disabled="loading"
          class="system-btn save"
        >
          <span class="btn-icon">💾</span>
          <span class="btn-text">保存游戏</span>
        </button>

        <button 
          @click="handleSettings"
          :disabled="loading"
          class="system-btn settings"
        >
          <span class="btn-icon">⚙️</span>
          <span class="btn-text">游戏设置</span>
        </button>

        <button 
          @click="$emit('returnMenu')"
          class="system-btn quit"
        >
          <span class="btn-icon">🚪</span>
          <span class="btn-text">返回主菜单</span>
        </button>
      </div>
    </div>

    <!-- 恐怖装饰 -->
    <div class="panel-decoration">
      <div class="blood-stain blood-1"></div>
      <div class="blood-stain blood-2"></div>
      <div class="crack-effect"></div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue'

interface Props {
  gameState: any
  loading?: boolean
}

const props = defineProps<Props>()
const emit = defineEmits(['advanceTurn', 'createRule', 'saveGame', 'returnMenu'])

// 计算属性
const canAdvanceTurn = computed(() => {
  // 检查是否有存活的NPC
  return props.gameState?.npcs?.some(npc => npc.alive) ?? false
})

const activeRules = computed(() => {
  return props.gameState?.rules?.filter(rule => rule.active) || []
})

// 方法
const handleAITurn = async () => {
  console.log('执行AI回合')
  // TODO: 实现AI回合逻辑
}

const handleSettings = () => {
  console.log('打开游戏设置')
  // TODO: 实现设置界面
}

const formatSurvivalTime = () => {
  const days = props.gameState?.day || 0
  const turns = props.gameState?.turn || 0
  return `D${days} T${turns}`
}
</script>

<style scoped>
.action-panel {
  height: 100%;
  display: flex;
  flex-direction: column;
  padding: 20px;
  position: relative;
  overflow-y: auto;
}

/* 面板区块 */
.panel-section {
  margin-bottom: 25px;
  padding-bottom: 20px;
  border-bottom: 1px solid var(--horror-border);
}

.panel-section:last-child {
  border-bottom: none;
}

.section-title {
  display: flex;
  align-items: center;
  gap: 8px;
  margin: 0 0 15px 0;
  font-size: 1.1rem;
  color: var(--horror-accent);
  text-shadow: 0 0 10px rgba(220, 20, 60, 0.5);
  text-transform: uppercase;
  letter-spacing: 1px;
}

.title-icon {
  font-size: 1.2rem;
  filter: drop-shadow(0 0 5px currentColor);
}

/* 操作按钮 */
.action-buttons {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.action-btn {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 10px;
  padding: 14px 20px;
  border: 2px solid;
  font-size: 1rem;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.3s;
  text-transform: uppercase;
  letter-spacing: 1px;
  position: relative;
  overflow: hidden;
}

.action-btn:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.action-btn.primary {
  background: linear-gradient(135deg, var(--horror-primary), var(--horror-accent));
  border-color: var(--horror-accent);
  color: var(--horror-text);
}

.action-btn.primary:hover:not(:disabled) {
  transform: translateY(-2px);
  box-shadow: 0 0 30px rgba(220, 20, 60, 0.6);
  border-color: var(--horror-danger);
}

.action-btn.secondary {
  background: linear-gradient(135deg, rgba(40, 0, 0, 0.9), rgba(60, 0, 0, 0.8));
  border-color: var(--horror-primary);
  color: var(--horror-text);
}

.action-btn.secondary:hover:not(:disabled) {
  transform: translateY(-2px);
  box-shadow: 0 0 25px rgba(139, 0, 0, 0.5);
  background: linear-gradient(135deg, rgba(60, 0, 0, 0.9), rgba(80, 0, 0, 0.8));
}

.action-btn.ai-btn {
  background: linear-gradient(135deg, #2563eb, #7c3aed);
  border-color: #7c3aed;
  color: var(--horror-text);
}

.action-btn.ai-btn:hover:not(:disabled) {
  transform: translateY(-2px);
  box-shadow: 0 0 25px rgba(124, 58, 237, 0.6);
}

.btn-icon {
  font-size: 1.3rem;
  filter: drop-shadow(0 0 3px currentColor);
}

.btn-text {
  font-size: 0.95rem;
}

/* 规则列表 */
.rules-list {
  display: flex;
  flex-direction: column;
  gap: 8px;
  max-height: 150px;
  overflow-y: auto;
}

.no-rules {
  text-align: center;
  color: var(--horror-text-secondary);
  padding: 20px;
  opacity: 0.7;
  font-style: italic;
}

.rule-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 10px;
  background: rgba(0, 0, 0, 0.5);
  border: 1px solid var(--horror-border);
  transition: all 0.3s;
}

.rule-item:hover {
  transform: translateX(5px);
  border-color: var(--horror-accent);
  box-shadow: 0 0 15px rgba(220, 20, 60, 0.3);
}

.rule-name {
  color: var(--horror-text);
  font-size: 0.9rem;
}

.rule-cooldown {
  color: var(--horror-text-secondary);
  font-size: 0.85rem;
  padding: 2px 8px;
  background: rgba(139, 0, 0, 0.3);
  border: 1px solid var(--horror-border);
}

/* 统计网格 */
.stats-grid {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 12px;
}

.stat-item {
  display: flex;
  flex-direction: column;
  align-items: center;
  padding: 12px;
  background: rgba(0, 0, 0, 0.5);
  border: 1px solid var(--horror-border);
  transition: all 0.3s;
}

.stat-item:hover {
  transform: scale(1.05);
  box-shadow: 0 0 15px rgba(220, 20, 60, 0.3);
}

.stat-label {
  font-size: 0.8rem;
  color: var(--horror-text-secondary);
  text-transform: uppercase;
  letter-spacing: 1px;
  margin-bottom: 5px;
}

.stat-value {
  font-size: 1.3rem;
  font-weight: bold;
  color: var(--horror-text);
  font-family: 'Courier New', monospace;
}

.stat-value.blood-text {
  color: var(--horror-accent);
  text-shadow: 0 0 10px rgba(220, 20, 60, 0.5);
}

/* 系统按钮 */
.system-buttons {
  display: flex;
  flex-direction: column;
  gap: 10px;
}

.system-btn {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 8px;
  padding: 10px 16px;
  background: rgba(40, 40, 40, 0.8);
  border: 1px solid #444;
  color: var(--horror-text-secondary);
  cursor: pointer;
  transition: all 0.3s;
  font-size: 0.9rem;
  text-transform: uppercase;
  letter-spacing: 1px;
}

.system-btn:hover {
  transform: translateX(5px);
  color: var(--horror-text);
}

.system-btn.save:hover {
  border-color: #10b981;
  box-shadow: 0 0 20px rgba(16, 185, 129, 0.4);
  background: rgba(16, 185, 129, 0.1);
}

.system-btn.settings:hover {
  border-color: #6b7280;
  box-shadow: 0 0 20px rgba(107, 114, 128, 0.4);
}

.system-btn.quit:hover {
  border-color: var(--horror-danger);
  box-shadow: 0 0 20px rgba(255, 0, 0, 0.4);
  background: rgba(255, 0, 0, 0.1);
}

/* 装饰效果 */
.panel-decoration {
  position: absolute;
  inset: 0;
  pointer-events: none;
  opacity: 0.3;
}

.blood-stain {
  position: absolute;
  background: radial-gradient(circle, var(--horror-accent) 20%, transparent 70%);
  filter: blur(3px);
}

.blood-1 {
  width: 60px;
  height: 40px;
  top: 10%;
  right: 5%;
  transform: rotate(-30deg);
}

.blood-2 {
  width: 80px;
  height: 60px;
  bottom: 20%;
  left: 5%;
  transform: rotate(45deg);
}

.crack-effect {
  position: absolute;
  width: 2px;
  height: 100px;
  background: linear-gradient(to bottom, transparent, rgba(0, 0, 0, 0.5), transparent);
  top: 30%;
  right: 10%;
  transform: rotate(20deg);
}

/* 脉动效果 */
.pulse-horror {
  animation: pulse-red 2s infinite;
}

@keyframes pulse-red {
  0%, 100% {
    box-shadow: 0 0 20px rgba(139, 0, 0, 0.5);
  }
  50% {
    box-shadow: 0 0 40px rgba(220, 20, 60, 0.8);
  }
}

/* 响应式 */
@media (max-width: 1400px) {
  .action-panel {
    padding: 15px;
  }
  
  .stats-grid {
    grid-template-columns: 1fr;
  }
}

/* 滚动条样式 */
.action-panel::-webkit-scrollbar,
.rules-list::-webkit-scrollbar {
  width: 6px;
}

.action-panel::-webkit-scrollbar-track,
.rules-list::-webkit-scrollbar-track {
  background: rgba(139, 0, 0, 0.2);
}

.action-panel::-webkit-scrollbar-thumb,
.rules-list::-webkit-scrollbar-thumb {
  background: var(--horror-primary);
  border-radius: 0;
}

.action-panel::-webkit-scrollbar-thumb:hover,
.rules-list::-webkit-scrollbar-thumb:hover {
  background: var(--horror-accent);
}
</style>
