<template>
  <div class="home-page">
    <div class="hero-section">
      <h1 class="title horror-glow">规则怪谈管理者</h1>
      <p class="subtitle">创造规则，收割恐惧，主宰命运</p>
    </div>
    
    <div class="main-content">
      <n-card class="game-options-card">
        <h2>开始游戏</h2>
        
        <n-space vertical size="large">
          <!-- 新游戏选项 -->
          <div class="option-section">
            <h3>创建新游戏</h3>
            <n-form ref="formRef" :model="newGameForm" :rules="rules">
              <n-form-item label="游戏难度" path="difficulty">
                <n-radio-group v-model:value="newGameForm.difficulty">
                  <n-space>
                    <n-radio value="easy">简单</n-radio>
                    <n-radio value="normal">普通</n-radio>
                    <n-radio value="hard">困难</n-radio>
                  </n-space>
                </n-radio-group>
              </n-form-item>
              
              <n-form-item label="NPC数量" path="npcCount">
                <n-slider 
                  v-model:value="newGameForm.npcCount"
                  :min="2"
                  :max="6"
                  :marks="{2: '2', 4: '4', 6: '6'}"
                />
              </n-form-item>
              
              <n-button 
                type="primary" 
                size="large"
                :loading="isCreating"
                @click="handleCreateGame"
                block
              >
                开始新游戏
              </n-button>
            </n-form>
          </div>
          
          <!-- 加载存档 -->
          <n-divider />
          
          <div class="option-section">
            <h3>加载存档</h3>
            <n-space vertical>
              <n-empty 
                v-if="saves.length === 0"
                description="暂无存档"
              />
              <n-list v-else>
                <n-list-item v-for="save in saves" :key="save.filename">
                  <n-thing>
                    <template #header>
                      {{ save.filename }}
                    </template>
                    <template #description>
                      回合 {{ save.turn }} - {{ save.description }}
                    </template>
                    <template #footer>
                      <n-space>
                        <n-button size="small" @click="handleLoadGame(save.filename)">
                          加载
                        </n-button>
                        <n-button size="small" type="error" @click="handleDeleteSave(save.filename)">
                          删除
                        </n-button>
                      </n-space>
                    </template>
                  </n-thing>
                </n-list-item>
              </n-list>
            </n-space>
          </div>
        </n-space>
      </n-card>
      
      <!-- 游戏说明 -->
      <n-card class="info-card">
        <h3>游戏说明</h3>
        <n-text>
          在《规则怪谈管理者》中，你将扮演一个诡异空间的幕后主宰。
          通过消耗恐惧积分创造致命规则，操纵NPC的命运，收集更多恐惧能量。
          你既可以在幕后观察，也可以亲自下场引导剧情。
          小心！聪明的NPC可能会发现规则的破绽...
        </n-text>
      </n-card>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { NCard, NButton, NSpace, NDivider, NForm, NFormItem, NRadioGroup, NRadio, NSlider, NList, NListItem, NThing, NEmpty, NText, useMessage } from 'naive-ui'
import { useGameStore } from '@/stores/game'

const router = useRouter()
const message = useMessage()
const gameStore = useGameStore()

// 表单数据
const formRef = ref()
const newGameForm = reactive({
  difficulty: 'normal' as 'easy' | 'normal' | 'hard',
  npcCount: 4
})

const rules = {
  difficulty: {
    required: true,
    message: '请选择游戏难度'
  },
  npcCount: {
    required: true,
    type: 'number' as const,
    message: '请选择NPC数量'
  }
}

// 状态
const isCreating = ref(false)
const saves = ref<any[]>([])

// 创建新游戏
async function handleCreateGame() {
  try {
    await formRef.value?.validate()
    
    isCreating.value = true
    const gameState = await gameStore.createGame(
      newGameForm.difficulty,
      newGameForm.npcCount
    )
    
    message.success('游戏创建成功！')
    
    // 跳转到游戏页面
    router.push({
      name: 'game',
      params: { gameId: gameState.game_id }
    })
  } catch (e: any) {
    message.error(e.message || '创建游戏失败')
  } finally {
    isCreating.value = false
  }
}

// 加载游戏
async function handleLoadGame(filename: string) {
  try {
    // TODO: 实现加载存档功能
    message.info('加载存档功能开发中...')
  } catch (e: any) {
    message.error(e.message || '加载存档失败')
  }
}

// 删除存档
async function handleDeleteSave(filename: string) {
  try {
    // TODO: 实现删除存档功能
    message.info('删除存档功能开发中...')
  } catch (e: any) {
    message.error(e.message || '删除存档失败')
  }
}

// 加载存档列表
async function loadSaves() {
  // TODO: 从API加载存档列表
  saves.value = []
}

onMounted(() => {
  loadSaves()
})
</script>

<style lang="scss" scoped>
.home-page {
  min-height: 100vh;
  padding: 2rem;
  background: linear-gradient(180deg, #0a0a0a 0%, #1a0a0a 100%);
  
  .hero-section {
    text-align: center;
    margin-bottom: 3rem;
    
    .title {
      font-size: 3.5rem;
      margin-bottom: 1rem;
      color: #8b0000;
      font-weight: bold;
      letter-spacing: 0.1em;
      animation: pulse 2s ease-in-out infinite;
    }
    
    .subtitle {
      font-size: 1.2rem;
      color: #666;
      font-style: italic;
    }
  }
  
  .main-content {
    max-width: 800px;
    margin: 0 auto;
    display: grid;
    gap: 2rem;
    
    .game-options-card {
      background: rgba(26, 26, 26, 0.9);
      border: 1px solid #333;
      
      h2 {
        color: #8b0000;
        margin-bottom: 1.5rem;
      }
      
      h3 {
        color: #ccc;
        margin-bottom: 1rem;
      }
      
      .option-section {
        padding: 1rem;
        background: rgba(42, 42, 42, 0.5);
        border-radius: 8px;
      }
    }
    
    .info-card {
      background: rgba(26, 26, 26, 0.9);
      border: 1px solid #333;
      
      h3 {
        color: #8b0000;
        margin-bottom: 1rem;
      }
    }
  }
}

@keyframes pulse {
  0%, 100% {
    transform: scale(1);
    opacity: 1;
  }
  50% {
    transform: scale(1.02);
    opacity: 0.9;
  }
}
</style>
