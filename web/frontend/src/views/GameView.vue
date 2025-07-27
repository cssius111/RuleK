<template>
  <div class="game-view">
    <div class="game-header">
      <GameStatePanel />
    </div>
    
    <div class="game-main">
      <div class="left-panel">
        <NPCGrid />
      </div>
      
      <div class="center-panel">
        <EventLog />
      </div>
      
      <div class="right-panel">
        <RuleList />
        <ActionButtons />
      </div>
    </div>
    
    <!-- 规则创建对话框 -->
    <RuleCreatorModal 
      v-model:show="showRuleCreator"
      @created="handleRuleCreated"
    />
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, onUnmounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useGameStore } from '@/stores/game'
import { useMessage } from 'naive-ui'

// 导入组件
import GameStatePanel from '@/components/game/GameStatePanel.vue'
import NPCGrid from '@/components/game/NPCGrid.vue'
import EventLog from '@/components/game/EventLog.vue'
import RuleList from '@/components/game/RuleList.vue'
import ActionButtons from '@/components/game/ActionButtons.vue'
import RuleCreatorModal from '@/components/game/RuleCreatorModal.vue'

const route = useRoute()
const router = useRouter()
const gameStore = useGameStore()
const message = useMessage()

// 状态
const showRuleCreator = ref(false)

// 加载游戏
async function loadGame() {
  const gameId = route.params.gameId as string
  if (!gameId) {
    message.error('游戏ID无效')
    router.push({ name: 'home' })
    return
  }
  
  try {
    await gameStore.loadGame(gameId)
  } catch (e: any) {
    message.error(e.message || '加载游戏失败')
    router.push({ name: 'home' })
  }
}

// 处理规则创建
function handleRuleCreated() {
  showRuleCreator.value = false
  message.success('规则创建成功！')
}

// 键盘快捷键
function handleKeyPress(event: KeyboardEvent) {
  // Space - 推进回合
  if (event.code === 'Space' && !event.target) {
    event.preventDefault()
    gameStore.advanceTurn()
  }
  // R - 创建规则
  else if (event.code === 'KeyR' && !event.target) {
    event.preventDefault()
    showRuleCreator.value = true
  }
}

onMounted(() => {
  loadGame()
  window.addEventListener('keydown', handleKeyPress)
})

onUnmounted(() => {
  window.removeEventListener('keydown', handleKeyPress)
  gameStore.clearGame()
})
</script>

<style lang="scss" scoped>
.game-view {
  height: 100vh;
  display: flex;
  flex-direction: column;
  background: #0a0a0a;
  overflow: hidden;
  
  .game-header {
    flex-shrink: 0;
    border-bottom: 1px solid #333;
  }
  
  .game-main {
    flex: 1;
    display: flex;
    overflow: hidden;
    
    .left-panel {
      width: 350px;
      padding: 1rem;
      border-right: 1px solid #333;
      overflow-y: auto;
    }
    
    .center-panel {
      flex: 1;
      padding: 1rem;
      overflow-y: auto;
    }
    
    .right-panel {
      width: 300px;
      padding: 1rem;
      border-left: 1px solid #333;
      display: flex;
      flex-direction: column;
      gap: 1rem;
    }
  }
}

// 响应式布局
@media (max-width: 1200px) {
  .game-view .game-main {
    .left-panel {
      width: 300px;
    }
    
    .right-panel {
      width: 250px;
    }
  }
}

@media (max-width: 768px) {
  .game-view .game-main {
    flex-direction: column;
    
    .left-panel,
    .right-panel {
      width: 100%;
      border: none;
      border-bottom: 1px solid #333;
    }
  }
}
</style>
