<template>
  <div class="game-container">
    <!-- 顶部状态栏 -->
    <StatusBar 
      :gameState="gameStore.gameState"
      @toggleMode="handleToggleMode"
    />

    <!-- 主游戏区域 -->
    <div class="game-main">
      <!-- 左侧：NPC列表 -->
      <div class="game-sidebar left-sidebar">
        <div class="sidebar-header">
          <h3 class="section-title blood-text">
            <span class="title-icon">👥</span>
            祭品状态
          </h3>
          <div class="alive-count">
            存活: <span class="count-number">{{ aliveNPCCount }}</span>
          </div>
        </div>
        <div class="npc-list">
          <NPCCard 
            v-for="npc in gameStore.gameState?.npcs || []"
            :key="npc.id"
            :npc="npc"
            @click="handleNPCClick"
          />
        </div>
      </div>

      <!-- 中间：事件日志 -->
      <div class="game-center">
        <EventLog 
          :events="gameStore.gameState?.events_history || []"
          :maxEvents="10"
        />
      </div>

      <!-- 右侧：操作面板 -->
      <div class="game-sidebar right-sidebar">
        <ActionPanel 
          :gameState="gameStore.gameState"
          :isProcessing="isProcessing"
          @startTurn="handleStartTurn"
          @createRule="handleCreateRule"
          @saveGame="handleSaveGame"
        />
      </div>
    </div>

    <!-- 底部快捷栏 -->
    <div class="game-footer">
      <div class="quick-actions">
        <button class="quick-btn horror-button" @click="handleQuickSave">
          <span class="btn-icon">💾</span>
          快速保存
        </button>
        <button class="quick-btn horror-button" @click="toggleFullscreen">
          <span class="btn-icon">📺</span>
          {{ isFullscreen ? '退出全屏' : '全屏模式' }}
        </button>
        <button class="quick-btn horror-button-secondary" @click="showSettings">
          <span class="btn-icon">⚙️</span>
          设置
        </button>
        <router-link to="/" class="quick-btn horror-button-danger">
          <span class="btn-icon">🚪</span>
          退出游戏
        </router-link>
      </div>
    </div>

    <!-- 规则创建模态框 -->
    <RuleCreatorModal 
      v-model:show="showRuleCreator"
      @created="handleRuleCreated"
    />

    <!-- 加载遮罩 -->
    <LoadingSpinner 
      v-if="isLoading"
      text="执行黑暗仪式..."
    />

    <!-- 游戏结束遮罩 -->
    <div v-if="isGameOver" class="game-over-overlay">
      <div class="game-over-content horror-card">
        <h2 class="game-over-title blood-text horror-flicker">游戏结束</h2>
        <p class="game-over-reason">{{ gameOverReason }}</p>
        <div class="game-over-stats">
          <div class="stat-item">
            <span class="stat-label">存活回合：</span>
            <span class="stat-value blood-text">{{ gameStore.gameState?.current_turn || 0 }}</span>
          </div>
          <div class="stat-item">
            <span class="stat-label">收获恐惧：</span>
            <span class="stat-value blood-text">{{ totalFearHarvested }}</span>
          </div>
          <div class="stat-item">
            <span class="stat-label">击杀数量：</span>
            <span class="stat-value blood-text">{{ totalKills }}</span>
          </div>
        </div>
        <div class="game-over-actions">
          <button @click="handleRestartGame" class="horror-button">
            <span class="btn-icon">🔄</span>
            重新开始
          </button>
          <router-link to="/" class="horror-button-secondary">
            <span class="btn-icon">🏠</span>
            返回主菜单
          </router-link>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, onUnmounted } from 'vue'
import { useRouter } from 'vue-router'
import { useGameStore } from '@/stores/game'
import StatusBar from '@/components/game/StatusBar.vue'
import NPCCard from '@/components/game/NPCCard.vue'
import EventLog from '@/components/game/EventLog.vue'
import ActionPanel from '@/components/game/ActionPanel.vue'
import LoadingSpinner from '@/components/common/LoadingSpinner.vue'
import RuleCreatorModal from '@/components/game/RuleCreatorModal.vue'

const router = useRouter()
const gameStore = useGameStore()

// 状态
const isLoading = ref(false)
const isProcessing = ref(false)
const isFullscreen = ref(false)
const isGameOver = ref(false)
const gameOverReason = ref('')
const totalFearHarvested = ref(0)
const totalKills = ref(0)
const showRuleCreator = ref(false)

// 计算属性
const aliveNPCCount = computed(() => {
  return gameStore.gameState?.npcs?.filter(npc => npc.is_alive).length || 0
})

// 生命周期
onMounted(async () => {
  // 检查是否有游戏状态
  if (!gameStore.gameState) {
    router.push('/new-game')
    return
  }

  // 初始化游戏
  await initGame()

  // 设置定时刷新
  const refreshInterval = setInterval(checkGameStatus, 5000)
  
  // 清理
  onUnmounted(() => {
    clearInterval(refreshInterval)
  })
})

// 初始化游戏
const initGame = async () => {
  isLoading.value = true
  try {
    // 刷新游戏状态
    await gameStore.refreshGameState()
  } catch (error) {
    console.error('初始化游戏失败:', error)
  } finally {
    isLoading.value = false
  }
}

// 检查游戏状态
const checkGameStatus = () => {
  // 检查是否所有NPC死亡
  if (aliveNPCCount.value === 0) {
    endGame('所有祭品已被收割')
  }
  
  // 检查其他结束条件
  if (gameStore.gameState?.game_over) {
    endGame(gameStore.gameState.game_over_reason || '游戏结束')
  }
}

// 游戏结束
const endGame = (reason: string) => {
  isGameOver.value = true
  gameOverReason.value = reason
  calculateFinalStats()
}

// 计算最终统计
const calculateFinalStats = () => {
  if (!gameStore.gameState) return
  
  // 计算总恐惧收获
  totalFearHarvested.value = gameStore.gameState.fear_harvested || 0
  
  // 计算击杀数
  const deadNPCs = gameStore.gameState.npcs?.filter(npc => !npc.is_alive).length || 0
  totalKills.value = deadNPCs
}

// 处理NPC点击
const handleNPCClick = (npc: any) => {
  console.log('NPC clicked:', npc)
  // TODO: 显示NPC详情弹窗
}

// 切换模式
const handleToggleMode = () => {
  // TODO: 实现模式切换
  console.log('Toggle mode')
}

// 开始回合
const handleStartTurn = async () => {
  isProcessing.value = true
  try {
    await gameStore.advanceTurn()
    // 刷新游戏状态
    await gameStore.refreshGameState()
  } catch (error) {
    console.error('推进回合失败:', error)
  } finally {
    isProcessing.value = false
  }
}

// 创建规则
const handleCreateRule = () => {
  showRuleCreator.value = true
}

// 处理规则创建成功
const handleRuleCreated = () => {
  showRuleCreator.value = false
  // 刷新游戏状态以更新规则列表
  gameStore.refreshGameState()
}

// 保存游戏
const handleSaveGame = async () => {
  isProcessing.value = true
  try {
    await gameStore.saveGame()
    // TODO: 显示保存成功提示
  } catch (error) {
    console.error('保存游戏失败:', error)
  } finally {
    isProcessing.value = false
  }
}

// 快速保存
const handleQuickSave = async () => {
  await handleSaveGame()
}

// 切换全屏
const toggleFullscreen = () => {
  if (!document.fullscreenElement) {
    document.documentElement.requestFullscreen()
    isFullscreen.value = true
  } else {
    document.exitFullscreen()
    isFullscreen.value = false
  }
}

// 显示设置
const showSettings = () => {
  // TODO: 显示设置弹窗
  console.log('Show settings')
}

// 重新开始游戏
const handleRestartGame = () => {
  router.push('/new-game')
}
</script>

<style scoped>
.game-container {
  min-height: 100vh;
  background: var(--horror-black);
  display: flex;
  flex-direction: column;
  position: relative;
  overflow: hidden;
}

/* 背景恐怖效果 */
.game-container::before {
  content: '';
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: 
    radial-gradient(circle at 20% 30%, rgba(139, 0, 0, 0.15) 0%, transparent 50%),
    radial-gradient(circle at 80% 70%, rgba(220, 20, 60, 0.1) 0%, transparent 50%),
    radial-gradient(circle at 50% 50%, rgba(0, 0, 0, 0.5) 0%, transparent 100%);
  pointer-events: none;
  animation: horror-ambient 15s ease-in-out infinite;
}

@keyframes horror-ambient {
  0%, 100% { opacity: 0.5; }
  50% { opacity: 0.8; }
}

/* 主游戏区域 */
.game-main {
  flex: 1;
  display: grid;
  grid-template-columns: 280px 1fr 320px;
  gap: 20px;
  padding: 20px;
  position: relative;
  z-index: 1;
}

/* 侧边栏 */
.game-sidebar {
  background: linear-gradient(135deg, rgba(20, 10, 10, 0.95), rgba(30, 0, 0, 0.9));
  border: 1px solid var(--horror-border);
  box-shadow: 
    0 10px 40px rgba(139, 0, 0, 0.3),
    inset 0 0 50px rgba(0, 0, 0, 0.5);
  padding: 20px;
  overflow-y: auto;
  position: relative;
}

.sidebar-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
  padding-bottom: 15px;
  border-bottom: 1px solid var(--horror-border);
}

.section-title {
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
  filter: drop-shadow(0 0 5px currentColor);
}

.alive-count {
  color: var(--horror-text-secondary);
  font-size: 0.9rem;
  text-transform: uppercase;
  letter-spacing: 1px;
}

.count-number {
  color: var(--horror-accent);
  font-weight: 700;
  font-size: 1.1rem;
  text-shadow: 0 0 10px currentColor;
}

/* NPC列表 */
.npc-list {
  display: flex;
  flex-direction: column;
  gap: 15px;
}

/* 中央区域 */
.game-center {
  background: linear-gradient(135deg, rgba(15, 10, 10, 0.95), rgba(25, 0, 0, 0.9));
  border: 1px solid var(--horror-border);
  box-shadow: 
    0 10px 40px rgba(139, 0, 0, 0.3),
    inset 0 0 50px rgba(0, 0, 0, 0.5);
  padding: 20px;
  overflow-y: auto;
  position: relative;
}

/* 底部快捷栏 */
.game-footer {
  background: linear-gradient(135deg, rgba(10, 5, 5, 0.98), rgba(20, 0, 0, 0.95));
  border-top: 2px solid var(--horror-border);
  padding: 15px 20px;
  box-shadow: 0 -10px 30px rgba(139, 0, 0, 0.3);
  position: relative;
  z-index: 2;
}

.quick-actions {
  display: flex;
  gap: 15px;
  justify-content: center;
  align-items: center;
}

.quick-btn {
  padding: 10px 20px;
  font-size: 0.9rem;
  display: inline-flex;
  align-items: center;
  gap: 8px;
  text-transform: uppercase;
  letter-spacing: 1px;
  border: 1px solid;
  transition: all 0.3s;
  text-decoration: none;
  cursor: pointer;
}

.btn-icon {
  font-size: 1.1rem;
}

.horror-button-danger {
  background: linear-gradient(135deg, rgba(80, 0, 0, 0.9), rgba(120, 0, 0, 0.9));
  border-color: var(--horror-danger);
  color: var(--horror-text);
}

.horror-button-danger:hover {
  background: linear-gradient(135deg, rgba(100, 0, 0, 0.9), rgba(140, 0, 0, 0.9));
  box-shadow: 0 0 20px rgba(255, 0, 0, 0.5);
  transform: scale(1.05);
}

/* 游戏结束遮罩 */
.game-over-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0, 0, 0, 0.95);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 9999;
  animation: fade-in 0.5s ease-out;
}

.game-over-content {
  max-width: 500px;
  width: 90%;
  padding: 40px;
  text-align: center;
}

.game-over-title {
  font-size: 3rem;
  margin: 0 0 20px 0;
  text-transform: uppercase;
  letter-spacing: 4px;
}

.game-over-reason {
  color: var(--horror-text-secondary);
  font-size: 1.2rem;
  margin-bottom: 30px;
  text-transform: uppercase;
  letter-spacing: 2px;
}

.game-over-stats {
  display: flex;
  flex-direction: column;
  gap: 15px;
  margin: 30px 0;
  padding: 20px;
  background: rgba(0, 0, 0, 0.5);
  border: 1px solid var(--horror-border);
}

.stat-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.stat-label {
  color: var(--horror-text-secondary);
  text-transform: uppercase;
  letter-spacing: 1px;
}

.stat-value {
  font-size: 1.3rem;
  font-weight: 700;
}

.game-over-actions {
  display: flex;
  gap: 20px;
  justify-content: center;
  margin-top: 30px;
}

/* 响应式设计 */
@media (max-width: 1280px) {
  .game-main {
    grid-template-columns: 250px 1fr 280px;
  }
}

@media (max-width: 1024px) {
  .game-main {
    grid-template-columns: 1fr;
    grid-template-rows: auto 1fr auto;
  }
  
  .left-sidebar {
    order: 2;
  }
  
  .game-center {
    order: 1;
  }
  
  .right-sidebar {
    order: 3;
  }
}

@media (max-width: 640px) {
  .quick-actions {
    flex-wrap: wrap;
  }
  
  .quick-btn {
    flex: 1 1 calc(50% - 10px);
    min-width: 140px;
  }
}
</style>
