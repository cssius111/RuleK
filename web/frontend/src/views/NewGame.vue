<template>
  <div class="new-game-container">
    <!-- 加载中 -->
    <LoadingSpinner 
      v-if="isCreating" 
      text="正在召唤黑暗力量..."
    />

    <!-- 配置表单 -->
    <div v-else class="config-card horror-card">
      <!-- 返回按钮 -->
      <router-link to="/" class="back-button">
        <span class="blood-icon">☠</span> 逃离此地
      </router-link>

      <!-- 标题 -->
      <div class="page-header">
        <h1 class="page-title blood-text horror-flicker">召唤仪式</h1>
        <p class="page-subtitle">配置你的恐怖领域</p>
        <div class="blood-line"></div>
      </div>

      <!-- 错误提示 -->
      <ErrorMessage
        v-if="errorMessage"
        :message="errorMessage"
        @close="errorMessage = ''"
      />

      <!-- 成功提示 -->
      <ErrorMessage
        v-if="successMessage"
        :message="successMessage"
        type="success"
        @close="successMessage = ''"
      />

      <!-- 配置表单 -->
      <form @submit.prevent="handleCreateGame" class="config-form">
        <!-- 玩家名称 -->
        <div class="form-group">
          <label class="form-label">
            <span class="label-text">统治者之名</span>
            <span class="label-hint">（留空则匿名）</span>
          </label>
          <input
            v-model="formData.playerName"
            type="text"
            class="form-input horror-input"
            placeholder="输入你的黑暗称号..."
            maxlength="20"
          />
        </div>

        <!-- 难度选择 -->
        <div class="form-group">
          <label class="form-label">
            <span class="label-text">恐怖程度</span>
            <span class="label-required blood-text">*</span>
          </label>
          <div class="difficulty-options">
            <button
              v-for="diff in difficulties"
              :key="diff.value"
              type="button"
              @click="selectDifficulty(diff.value)"
              :class="['difficulty-btn', { active: formData.difficulty === diff.value }]"
              :style="{ '--color': diff.color }"
            >
              <span class="diff-icon">{{ diff.icon }}</span>
              <span class="diff-name">{{ diff.name }}</span>
            </button>
          </div>
          <p class="form-hint">{{ currentDifficultyDesc }}</p>
        </div>

        <!-- NPC数量 -->
        <div class="form-group">
          <label class="form-label">
            <span class="label-text">初始祭品数量</span>
            <span class="label-required blood-text">*</span>
          </label>
          <div class="slider-group">
            <input
              v-model.number="formData.initialNPCCount"
              type="range"
              class="form-slider horror-slider"
              :min="limits.npcCount.min"
              :max="limits.npcCount.max"
              step="1"
            />
            <div class="slider-value blood-text">{{ formData.initialNPCCount }}</div>
          </div>
          <p class="form-hint">更多祭品意味着更多恐惧可供收割</p>
        </div>

        <!-- 恐惧点数 -->
        <div class="form-group">
          <label class="form-label">
            <span class="label-text">黑暗能量储备</span>
            <span class="label-required blood-text">*</span>
          </label>
          <div class="input-group">
            <input
              v-model.number="formData.initialFearPoints"
              type="number"
              class="form-input horror-input"
              :min="limits.fearPoints.min"
              :max="limits.fearPoints.max"
              step="50"
            />
            <span class="input-suffix blood-text">灵魂</span>
          </div>
          <p class="form-hint">用于编织恐怖规则的黑暗资源</p>
        </div>

        <!-- AI功能开关 -->
        <div class="form-group">
          <label class="form-label">
            <span class="label-text">深渊意识增强</span>
            <span class="label-badge blood-badge">禁忌</span>
          </label>
          <div class="switch-group">
            <label class="switch horror-switch">
              <input
                v-model="formData.aiEnabled"
                type="checkbox"
                class="switch-input"
              />
              <span class="switch-slider"></span>
            </label>
            <span class="switch-label">
              {{ formData.aiEnabled ? '已觉醒' : '沉睡中' }}
            </span>
          </div>
          <p class="form-hint">
            唤醒深渊意识将获得更加诡异莫测的体验
          </p>
        </div>

        <!-- 配置预览 -->
        <div class="config-preview horror-preview">
          <h3 class="preview-title blood-text">仪式准备</h3>
          <div class="preview-grid">
            <div class="preview-item">
              <span class="preview-label">恐怖等级：</span>
              <span class="preview-value blood-text">{{ getDifficultyName(formData.difficulty) }}</span>
            </div>
            <div class="preview-item">
              <span class="preview-label">祭品：</span>
              <span class="preview-value blood-text">{{ formData.initialNPCCount }} 个灵魂</span>
            </div>
            <div class="preview-item">
              <span class="preview-label">黑暗能量：</span>
              <span class="preview-value blood-text">{{ formData.initialFearPoints }} 点</span>
            </div>
            <div class="preview-item">
              <span class="preview-label">深渊意识：</span>
              <span class="preview-value blood-text">{{ formData.aiEnabled ? '觉醒' : '沉睡' }}</span>
            </div>
          </div>
        </div>

        <!-- 提交按钮 -->
        <div class="form-actions">
          <router-link to="/" class="btn-cancel horror-button-secondary">
            <span class="btn-icon">🚪</span>
            放弃仪式
          </router-link>
          <button 
            type="submit" 
            class="btn-submit horror-button pulse-horror"
            :disabled="!isFormValid"
          >
            <span class="btn-icon">🩸</span>
            开启地狱之门
          </button>
        </div>
      </form>

      <!-- 恐怖装饰 -->
      <div class="horror-decorations">
        <div class="blood-drip drip-1"></div>
        <div class="blood-drip drip-2"></div>
        <div class="crack crack-1"></div>
        <div class="scratch scratch-1"></div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, reactive } from 'vue'
import { useRouter } from 'vue-router'
import { useGameStore } from '@/stores/game'
import { GameDifficulty, DIFFICULTY_PRESETS, GAME_CONFIG_LIMITS } from '@/types/game'
import LoadingSpinner from '@/components/common/LoadingSpinner.vue'
import ErrorMessage from '@/components/common/ErrorMessage.vue'

const router = useRouter()
const gameStore = useGameStore()

// 表单数据
const formData = reactive({
  playerName: '',
  difficulty: GameDifficulty.NORMAL,
  initialNPCCount: 4,
  initialFearPoints: 1000,
  aiEnabled: false
})

// 状态
const isCreating = ref(false)
const errorMessage = ref('')
const successMessage = ref('')

// 难度选项 - 恐怖主题
const difficulties = [
  { value: GameDifficulty.EASY, name: '不安', icon: '😨', color: '#4a0000' },
  { value: GameDifficulty.NORMAL, name: '恐惧', icon: '😰', color: '#8b0000' },
  { value: GameDifficulty.HARD, name: '绝望', icon: '😱', color: '#dc143c' },
  { value: GameDifficulty.NIGHTMARE, name: '噩梦', icon: '💀', color: '#ff0000' }
]

// 配置限制
const limits = GAME_CONFIG_LIMITS

// 当前难度描述
const currentDifficultyDesc = computed(() => {
  return DIFFICULTY_PRESETS[formData.difficulty]?.description || ''
})

// 表单验证
const isFormValid = computed(() => {
  return (
    formData.initialNPCCount >= limits.npcCount.min &&
    formData.initialNPCCount <= limits.npcCount.max &&
    formData.initialFearPoints >= limits.fearPoints.min &&
    formData.initialFearPoints <= limits.fearPoints.max
  )
})

// 选择难度
const selectDifficulty = (difficulty: GameDifficulty) => {
  formData.difficulty = difficulty
  const preset = DIFFICULTY_PRESETS[difficulty]
  if (preset) {
    formData.initialFearPoints = preset.fearPoints
    formData.initialNPCCount = preset.npcCount
  }
}

// 获取难度名称
const getDifficultyName = (difficulty: GameDifficulty) => {
  return difficulties.find(d => d.value === difficulty)?.name || '未知'
}

// 创建游戏
const handleCreateGame = async () => {
  if (!isFormValid.value) {
    errorMessage.value = '仪式参数有误，请重新检查'
    return
  }

  isCreating.value = true
  errorMessage.value = ''
  successMessage.value = ''

  try {
    // 调用store创建游戏
    const response = await gameStore.initGame({
      difficulty: formData.difficulty,
      initialFearPoints: formData.initialFearPoints,
      initialNPCCount: formData.initialNPCCount,
      aiEnabled: formData.aiEnabled,
      playerName: formData.playerName || undefined
    })

    successMessage.value = '地狱之门已开启...准备进入黑暗领域...'
    
    // 延迟跳转，让用户看到成功提示
    setTimeout(() => {
      router.push('/game')
    }, 1500)
    
  } catch (error: any) {
    errorMessage.value = error.message || '召唤失败，黑暗力量拒绝了你'
  } finally {
    isCreating.value = false
  }
}
</script>

<style scoped>
.new-game-container {
  min-height: 100vh;
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 20px;
  position: relative;
}

/* 添加血雾背景效果 */
.new-game-container::before {
  content: '';
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: 
    radial-gradient(circle at 30% 40%, rgba(139, 0, 0, 0.2) 0%, transparent 50%),
    radial-gradient(circle at 70% 60%, rgba(220, 20, 60, 0.15) 0%, transparent 50%);
  animation: blood-fog 10s ease-in-out infinite;
  pointer-events: none;
}

@keyframes blood-fog {
  0%, 100% { opacity: 0.5; transform: scale(1); }
  50% { opacity: 0.8; transform: scale(1.1); }
}

.config-card {
  position: relative;
  z-index: 1;
  max-width: 600px;
  width: 100%;
  padding: 50px 45px;
  animation: rise-from-hell 0.8s ease-out;
}

@keyframes rise-from-hell {
  from {
    opacity: 0;
    transform: translateY(50px) scale(0.95);
  }
  to {
    opacity: 1;
    transform: translateY(0) scale(1);
  }
}

/* 恐怖卡片样式 */
.horror-card {
  background: linear-gradient(135deg, rgba(26, 15, 15, 0.98), rgba(40, 0, 0, 0.95));
  border: 2px solid var(--horror-border);
  box-shadow: 
    0 30px 80px rgba(139, 0, 0, 0.7),
    inset 0 0 120px rgba(0, 0, 0, 0.9),
    0 0 100px rgba(139, 0, 0, 0.3);
  position: relative;
  overflow: hidden;
}

.horror-card::before {
  content: '';
  position: absolute;
  top: -50%;
  left: -50%;
  width: 200%;
  height: 200%;
  background: radial-gradient(circle, transparent 30%, rgba(139, 0, 0, 0.05) 70%);
  animation: horror-breathe 6s ease-in-out infinite;
  pointer-events: none;
}

/* 返回按钮 - 恐怖风格 */
.back-button {
  display: inline-flex;
  align-items: center;
  gap: 8px;
  color: var(--horror-text-secondary);
  text-decoration: none;
  font-size: 0.95rem;
  margin-bottom: 25px;
  transition: all 0.3s;
  text-transform: uppercase;
  letter-spacing: 1px;
}

.back-button:hover {
  color: var(--horror-accent);
  transform: translateX(-5px);
}

.blood-icon {
  font-size: 1.2rem;
  filter: drop-shadow(0 0 5px currentColor);
}

/* 页面标题 - 恐怖风格 */
.page-header {
  text-align: center;
  margin-bottom: 35px;
  position: relative;
}

.page-title {
  font-size: 3rem;
  font-weight: 900;
  margin: 0;
  text-transform: uppercase;
  letter-spacing: 4px;
}

.page-subtitle {
  color: var(--horror-text-secondary);
  margin-top: 10px;
  font-size: 1.1rem;
  letter-spacing: 3px;
  text-transform: uppercase;
  opacity: 0.8;
}

.blood-line {
  margin: 20px auto 0;
  width: 200px;
  height: 2px;
  background: linear-gradient(90deg, 
    transparent, 
    var(--horror-accent) 20%, 
    var(--horror-primary) 50%, 
    var(--horror-accent) 80%,
    transparent);
  animation: blood-flow 3s ease-in-out infinite;
}

/* 表单样式 - 恐怖主题 */
.config-form {
  display: flex;
  flex-direction: column;
  gap: 28px;
}

.form-group {
  display: flex;
  flex-direction: column;
  gap: 10px;
}

.form-label {
  display: flex;
  align-items: center;
  gap: 8px;
  font-weight: 600;
  color: var(--horror-text);
  text-transform: uppercase;
  letter-spacing: 1px;
  font-size: 0.9rem;
}

.label-text {
  color: var(--horror-text);
}

.label-required {
  font-size: 1.2rem;
}

.label-hint {
  color: var(--horror-text-secondary);
  font-size: 0.8rem;
  opacity: 0.7;
}

.blood-badge {
  background: linear-gradient(135deg, var(--horror-primary), var(--horror-accent));
  color: var(--horror-text);
  padding: 3px 10px;
  border-radius: 0;
  font-size: 0.7rem;
  font-weight: 700;
  text-transform: uppercase;
  letter-spacing: 1px;
  box-shadow: 0 0 10px rgba(220, 20, 60, 0.5);
}

/* 恐怖输入框 */
.horror-input {
  padding: 14px 18px;
  background: rgba(10, 0, 0, 0.7);
  border: 2px solid var(--horror-border);
  color: var(--horror-text);
  font-size: 1rem;
  transition: all 0.3s;
  box-shadow: inset 0 2px 5px rgba(0, 0, 0, 0.5);
}

.horror-input:focus {
  outline: none;
  border-color: var(--horror-accent);
  box-shadow: 
    0 0 20px rgba(220, 20, 60, 0.3),
    inset 0 2px 5px rgba(0, 0, 0, 0.5);
  background: rgba(20, 0, 0, 0.8);
}

.horror-input::placeholder {
  color: var(--horror-text-secondary);
  opacity: 0.5;
}

.form-hint {
  color: var(--horror-text-secondary);
  font-size: 0.85rem;
  margin: 0;
  font-style: italic;
  opacity: 0.8;
}

/* 难度选择 - 恐怖风格 */
.difficulty-options {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(120px, 1fr));
  gap: 15px;
}

.difficulty-btn {
  display: flex;
  flex-direction: column;
  align-items: center;
  padding: 18px;
  background: rgba(20, 10, 10, 0.8);
  border: 2px solid var(--horror-border);
  cursor: pointer;
  transition: all 0.3s;
  position: relative;
  overflow: hidden;
}

.difficulty-btn::before {
  content: '';
  position: absolute;
  top: 50%;
  left: 50%;
  width: 0;
  height: 0;
  background: radial-gradient(circle, var(--color) 0%, transparent 70%);
  transform: translate(-50%, -50%);
  transition: all 0.5s;
  opacity: 0.3;
}

.difficulty-btn:hover {
  transform: translateY(-3px);
  box-shadow: 0 10px 30px rgba(139, 0, 0, 0.5);
}

.difficulty-btn:hover::before {
  width: 200px;
  height: 200px;
}

.difficulty-btn.active {
  border-color: var(--color);
  background: linear-gradient(135deg, 
    rgba(20, 10, 10, 0.9),
    color-mix(in srgb, var(--color) 20%, black));
  box-shadow: 
    0 0 30px color-mix(in srgb, var(--color) 50%, transparent),
    inset 0 0 20px rgba(0, 0, 0, 0.5);
}

.diff-icon {
  font-size: 2.2rem;
  margin-bottom: 8px;
  filter: drop-shadow(0 2px 4px rgba(0, 0, 0, 0.5));
}

.diff-name {
  font-weight: 600;
  color: var(--horror-text);
  text-transform: uppercase;
  letter-spacing: 1px;
  font-size: 0.9rem;
}

/* 恐怖滑块 */
.slider-group {
  display: flex;
  align-items: center;
  gap: 25px;
}

.horror-slider {
  flex: 1;
  height: 8px;
  background: linear-gradient(90deg, 
    var(--horror-dark-red) 0%, 
    var(--horror-primary) 50%, 
    var(--horror-accent) 100%);
  border-radius: 0;
  outline: none;
  -webkit-appearance: none;
  position: relative;
  box-shadow: inset 0 2px 4px rgba(0, 0, 0, 0.5);
}

.horror-slider::-webkit-slider-thumb {
  -webkit-appearance: none;
  width: 24px;
  height: 24px;
  background: radial-gradient(circle, var(--horror-accent), var(--horror-primary));
  border: 2px solid var(--horror-danger);
  cursor: pointer;
  box-shadow: 
    0 0 20px rgba(220, 20, 60, 0.8),
    0 4px 8px rgba(0, 0, 0, 0.5);
  transition: all 0.3s;
}

.horror-slider::-webkit-slider-thumb:hover {
  transform: scale(1.2);
  box-shadow: 
    0 0 30px rgba(255, 0, 0, 0.9),
    0 4px 12px rgba(0, 0, 0, 0.7);
}

.slider-value {
  min-width: 50px;
  text-align: center;
  font-weight: 700;
  font-size: 1.5rem;
  text-shadow: 0 0 15px currentColor;
}

/* 输入组 */
.input-group {
  display: flex;
  align-items: center;
  gap: 12px;
}

.input-suffix {
  font-weight: 600;
  text-transform: uppercase;
  letter-spacing: 1px;
  font-size: 0.9rem;
}

/* 恐怖开关 */
.horror-switch {
  position: relative;
  display: inline-block;
  width: 60px;
  height: 32px;
}

.switch-input {
  opacity: 0;
  width: 0;
  height: 0;
}

.switch-slider {
  position: absolute;
  cursor: pointer;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: linear-gradient(135deg, var(--horror-dark-red), rgba(40, 0, 0, 0.9));
  transition: 0.4s;
  border: 2px solid var(--horror-border);
  box-shadow: inset 0 2px 5px rgba(0, 0, 0, 0.5);
}

.switch-slider:before {
  position: absolute;
  content: "";
  height: 22px;
  width: 22px;
  left: 3px;
  bottom: 3px;
  background: linear-gradient(135deg, #666, #333);
  transition: 0.4s;
  box-shadow: 0 2px 5px rgba(0, 0, 0, 0.5);
}

.switch-input:checked + .switch-slider {
  background: linear-gradient(135deg, var(--horror-primary), var(--horror-accent));
  box-shadow: 
    0 0 20px rgba(220, 20, 60, 0.5),
    inset 0 2px 5px rgba(0, 0, 0, 0.5);
}

.switch-input:checked + .switch-slider:before {
  transform: translateX(28px);
  background: linear-gradient(135deg, var(--horror-accent), var(--horror-danger));
  box-shadow: 0 0 10px rgba(255, 0, 0, 0.5);
}

.switch-label {
  font-weight: 600;
  color: var(--horror-text);
  text-transform: uppercase;
  letter-spacing: 1px;
  font-size: 0.9rem;
}

/* 配置预览 - 恐怖风格 */
.horror-preview {
  background: linear-gradient(135deg, rgba(10, 0, 0, 0.9), rgba(30, 0, 0, 0.8));
  border: 1px solid var(--horror-border);
  padding: 25px;
  position: relative;
  box-shadow: inset 0 0 30px rgba(139, 0, 0, 0.3);
}

.horror-preview::before {
  content: '⚠';
  position: absolute;
  top: 10px;
  right: 15px;
  font-size: 1.5rem;
  color: var(--horror-primary);
  opacity: 0.3;
  animation: horror-flicker 3s infinite;
}

.preview-title {
  margin: 0 0 20px 0;
  font-size: 1.2rem;
  text-transform: uppercase;
  letter-spacing: 2px;
  font-weight: 700;
}

.preview-grid {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 15px;
}

.preview-item {
  display: flex;
  justify-content: space-between;
  padding: 10px 0;
  border-bottom: 1px solid rgba(139, 0, 0, 0.2);
}

.preview-label {
  color: var(--horror-text-secondary);
  font-size: 0.9rem;
  text-transform: uppercase;
  letter-spacing: 1px;
}

.preview-value {
  font-weight: 700;
  text-transform: uppercase;
  letter-spacing: 1px;
  font-size: 0.95rem;
}

/* 表单操作 - 恐怖按钮 */
.form-actions {
  display: flex;
  gap: 20px;
  justify-content: center;
  margin-top: 30px;
}

.btn-cancel,
.btn-submit {
  padding: 16px 40px;
  font-size: 1rem;
  font-weight: 700;
  cursor: pointer;
  transition: all 0.3s;
  text-decoration: none;
  display: inline-flex;
  align-items: center;
  justify-content: center;
  gap: 10px;
  text-transform: uppercase;
  letter-spacing: 2px;
  border: 2px solid;
  position: relative;
  overflow: hidden;
}

.btn-icon {
  font-size: 1.3rem;
  filter: drop-shadow(0 0 5px currentColor);
}

.horror-button-secondary {
  background: linear-gradient(135deg, rgba(30, 10, 10, 0.9), rgba(50, 0, 0, 0.9));
  border-color: var(--horror-primary);
  color: var(--horror-text-secondary);
}

.horror-button-secondary:hover {
  background: linear-gradient(135deg, rgba(40, 10, 10, 0.9), rgba(60, 0, 0, 0.9));
  box-shadow: 0 10px 30px rgba(139, 0, 0, 0.5);
  transform: translateY(-2px);
  color: var(--horror-text);
}

.btn-submit:disabled {
  opacity: 0.4;
  cursor: not-allowed;
  animation: none;
}

/* 恐怖装饰元素 */
.horror-decorations {
  pointer-events: none;
  position: absolute;
  inset: 0;
}

/* 血滴效果 */
.blood-drip {
  position: absolute;
  width: 4px;
  background: linear-gradient(to bottom, 
    var(--horror-accent), 
    transparent);
  opacity: 0.6;
  animation: drip 5s ease-in-out infinite;
}

.drip-1 {
  height: 80px;
  top: 10%;
  right: 10%;
}

.drip-2 {
  height: 60px;
  top: 15%;
  left: 8%;
  animation-delay: 2s;
}

@keyframes drip {
  0%, 100% { 
    transform: translateY(0) scaleY(0);
    opacity: 0;
  }
  10% {
    transform: translateY(0) scaleY(0.3);
    opacity: 0.6;
  }
  80% {
    transform: translateY(100px) scaleY(1);
    opacity: 0.4;
  }
  90% {
    transform: translateY(120px) scaleY(0.8);
    opacity: 0.2;
  }
}

/* 裂纹效果 */
.crack {
  position: absolute;
  background: linear-gradient(
    to bottom,
    transparent,
    rgba(0, 0, 0, 0.4) 40%,
    rgba(0, 0, 0, 0.2) 60%,
    transparent
  );
  opacity: 0.6;
}

.crack-1 {
  width: 2px;
  height: 200px;
  bottom: 10%;
  right: 20%;
  transform: rotate(-15deg);
}

/* 划痕效果 */
.scratch {
  position: absolute;
  background: repeating-linear-gradient(
    90deg,
    transparent,
    transparent 2px,
    rgba(139, 0, 0, 0.2) 2px,
    rgba(139, 0, 0, 0.2) 3px
  );
  opacity: 0.5;
}

.scratch-1 {
  width: 150px;
  height: 3px;
  top: 30%;
  left: -20px;
  transform: rotate(10deg);
}

/* 响应式设计 */
@media (max-width: 640px) {
  .config-card {
    padding: 35px 25px;
  }
  
  .page-title {
    font-size: 2.2rem;
  }
  
  .difficulty-options {
    grid-template-columns: repeat(2, 1fr);
  }
  
  .preview-grid {
    grid-template-columns: 1fr;
  }
  
  .form-actions {
    flex-direction: column;
  }
  
  .btn-cancel,
  .btn-submit {
    width: 100%;
  }
}
</style>
