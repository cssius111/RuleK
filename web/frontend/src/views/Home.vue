<template>
  <div class="home-container">
    <div class="horror-card game-card">
      <!-- 游戏标题 -->
      <div class="game-header">
        <h1 class="game-title blood-text horror-flicker">RuleK</h1>
        <p class="game-subtitle">规则怪谈管理者</p>
        <div class="blood-decoration"></div>
      </div>

      <!-- 游戏简介 -->
      <div class="game-intro">
        <p class="intro-text">欢迎来到诡异空间</p>
        <p class="intro-text">创建恐怖规则，收割恐惧，成为终极管理者</p>
        <div class="warning-text horror-shake">⚠ 警告：此游戏包含恐怖元素 ⚠</div>
      </div>

      <!-- 主菜单按钮 -->
      <div class="menu-buttons">
        <button @click="startNewGame" class="menu-btn horror-button primary pulse-horror">
          <span class="btn-icon">💀</span>
          <span>开始新游戏</span>
        </button>
        
        <button @click="loadGame" class="menu-btn horror-button secondary">
          <span class="btn-icon">🩸</span>
          <span>加载存档</span>
        </button>
        
        <button @click="showHelp" class="menu-btn horror-button info">
          <span class="btn-icon">👁</span>
          <span>帮助说明</span>
        </button>
      </div>

      <!-- 版本信息 -->
      <div class="version-info">
        <span>版本 0.1.0</span>
        <span class="separator">|</span>
        <span>© 2024 RuleK</span>
      </div>

      <!-- 恐怖装饰元素 -->
      <div class="horror-decorations">
        <div class="blood-splatter blood-1"></div>
        <div class="blood-splatter blood-2"></div>
        <div class="crack crack-1"></div>
        <div class="crack crack-2"></div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { useRouter } from 'vue-router'
import { onMounted } from 'vue'

const router = useRouter()

// 页面加载时添加恐怖音效（可选）
onMounted(() => {
  // 添加随机的闪烁效果
  const card = document.querySelector('.game-card')
  if (card) {
    setInterval(() => {
      if (Math.random() > 0.95) {
        card.classList.add('horror-flicker')
        setTimeout(() => card.classList.remove('horror-flicker'), 200)
      }
    }, 3000)
  }
})

// 开始新游戏
const startNewGame = () => {
  console.log('开始新游戏 - 进入恐怖世界')
  router.push('/new-game')
}

// 加载存档
const loadGame = () => {
  console.log('加载存档 - 继续噩梦')
  router.push('/load-game')
}

// 显示帮助
const showHelp = () => {
  console.log('显示帮助 - 了解恐怖规则')
  router.push('/help')
}
</script>

<style scoped>
.home-container {
  min-height: 100vh;
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 20px;
  position: relative;
}

/* 添加恐怖背景雾效 */
.home-container::before {
  content: '';
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: radial-gradient(circle at center, transparent 0%, rgba(0, 0, 0, 0.8) 100%);
  pointer-events: none;
  animation: fog-move 20s ease-in-out infinite;
}

@keyframes fog-move {
  0%, 100% { opacity: 0.3; }
  50% { opacity: 0.6; }
}

.game-card {
  background: linear-gradient(135deg, rgba(20, 10, 10, 0.98), rgba(40, 0, 0, 0.95));
  border: 2px solid var(--horror-border);
  border-radius: 0;
  box-shadow: 
    0 20px 60px rgba(139, 0, 0, 0.6),
    inset 0 0 120px rgba(0, 0, 0, 0.9);
  padding: 60px 50px;
  max-width: 500px;
  width: 100%;
  text-align: center;
  position: relative;
  z-index: 1;
}

/* 游戏标题 - 恐怖风格 */
.game-header {
  margin-bottom: 30px;
  position: relative;
}

.game-title {
  font-size: 4rem;
  font-weight: 900;
  margin: 0;
  letter-spacing: 3px;
  text-transform: uppercase;
  color: var(--horror-accent);
  text-shadow: 
    0 0 20px rgba(220, 20, 60, 0.8),
    0 0 40px rgba(139, 0, 0, 0.6),
    0 5px 10px rgba(0, 0, 0, 0.9);
  animation: blood-drip 3s ease-in-out infinite;
}

.game-subtitle {
  font-size: 1.2rem;
  color: var(--horror-text-secondary);
  margin-top: 10px;
  letter-spacing: 6px;
  text-transform: uppercase;
  opacity: 0.8;
}

/* 血迹装饰 */
.blood-decoration {
  position: absolute;
  bottom: -10px;
  left: 50%;
  transform: translateX(-50%);
  width: 200px;
  height: 3px;
  background: linear-gradient(90deg, 
    transparent, 
    var(--horror-accent) 20%, 
    var(--horror-primary) 50%, 
    var(--horror-accent) 80%,
    transparent);
  filter: blur(1px);
  animation: blood-flow 3s ease-in-out infinite;
}

@keyframes blood-flow {
  0%, 100% { opacity: 0.5; width: 150px; }
  50% { opacity: 1; width: 250px; }
}

/* 游戏简介 - 恐怖风格 */
.game-intro {
  margin: 40px 0;
  position: relative;
}

.intro-text {
  color: var(--horror-text);
  line-height: 1.8;
  margin: 10px 0;
  font-size: 1.1rem;
  opacity: 0.9;
  text-shadow: 0 2px 4px rgba(0, 0, 0, 0.5);
}

.warning-text {
  margin-top: 20px;
  color: var(--horror-danger);
  font-size: 0.9rem;
  text-transform: uppercase;
  letter-spacing: 2px;
  opacity: 0.8;
  text-shadow: 0 0 10px rgba(255, 0, 0, 0.5);
}

/* 菜单按钮 - 恐怖风格 */
.menu-buttons {
  display: flex;
  flex-direction: column;
  gap: 20px;
  margin: 40px 0;
}

.menu-btn {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 12px;
  padding: 18px 35px;
  border: 2px solid;
  border-radius: 0;
  font-size: 1.1rem;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.3s ease;
  letter-spacing: 2px;
  text-transform: uppercase;
  position: relative;
  overflow: hidden;
}

.btn-icon {
  font-size: 1.5rem;
  filter: drop-shadow(0 0 5px currentColor);
}

/* 主按钮样式 */
.menu-btn.primary {
  background: linear-gradient(135deg, var(--horror-primary) 0%, var(--horror-accent) 100%);
  border-color: var(--horror-accent);
  color: var(--horror-text);
}

.menu-btn.primary:hover {
  transform: translateY(-3px) scale(1.02);
  box-shadow: 
    0 15px 40px rgba(220, 20, 60, 0.4),
    0 0 60px rgba(139, 0, 0, 0.3),
    inset 0 0 30px rgba(255, 0, 0, 0.2);
  border-color: var(--horror-danger);
}

/* 次要按钮样式 */
.menu-btn.secondary {
  background: linear-gradient(135deg, rgba(40, 0, 0, 0.9), rgba(80, 0, 0, 0.9));
  border-color: var(--horror-primary);
  color: var(--horror-text);
}

.menu-btn.secondary:hover {
  transform: translateY(-2px);
  box-shadow: 
    0 10px 30px rgba(139, 0, 0, 0.5),
    inset 0 0 20px rgba(220, 20, 60, 0.3);
  background: linear-gradient(135deg, rgba(60, 0, 0, 0.9), rgba(100, 0, 0, 0.9));
}

/* 信息按钮样式 */
.menu-btn.info {
  background: linear-gradient(135deg, rgba(20, 20, 20, 0.9), rgba(40, 20, 20, 0.9));
  border-color: #444;
  color: var(--horror-text-secondary);
}

.menu-btn.info:hover {
  transform: translateY(-2px);
  box-shadow: 
    0 10px 30px rgba(100, 100, 100, 0.3),
    inset 0 0 20px rgba(200, 200, 200, 0.1);
  border-color: #666;
  color: var(--horror-text);
}

/* 按钮悬停波纹效果 */
.menu-btn::before {
  content: '';
  position: absolute;
  top: 50%;
  left: 50%;
  width: 0;
  height: 0;
  border-radius: 50%;
  background: radial-gradient(circle, rgba(220, 20, 60, 0.6) 0%, transparent 70%);
  transform: translate(-50%, -50%);
  transition: width 0.6s, height 0.6s;
}

.menu-btn:hover::before {
  width: 300px;
  height: 300px;
}

/* 版本信息 */
.version-info {
  margin-top: 40px;
  color: var(--horror-text-secondary);
  font-size: 0.85rem;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 10px;
  opacity: 0.6;
}

.separator {
  color: var(--horror-primary);
}

/* 恐怖装饰元素 */
.horror-decorations {
  pointer-events: none;
  position: absolute;
  inset: 0;
}

/* 血迹效果 */
.blood-splatter {
  position: absolute;
  background: radial-gradient(circle, var(--horror-accent) 20%, transparent 70%);
  filter: blur(2px);
  opacity: 0.3;
  animation: blood-pulse 4s ease-in-out infinite;
}

.blood-1 {
  width: 80px;
  height: 60px;
  top: 10%;
  right: 5%;
  transform: rotate(-30deg);
}

.blood-2 {
  width: 100px;
  height: 80px;
  bottom: 15%;
  left: 3%;
  transform: rotate(45deg);
}

/* 裂纹效果 */
.crack {
  position: absolute;
  background: linear-gradient(
    to bottom,
    transparent,
    rgba(0, 0, 0, 0.3) 40%,
    rgba(0, 0, 0, 0.1) 60%,
    transparent
  );
  opacity: 0.5;
}

.crack-1 {
  width: 2px;
  height: 150px;
  top: 20%;
  left: 10%;
  transform: rotate(15deg);
}

.crack-2 {
  width: 1px;
  height: 100px;
  bottom: 30%;
  right: 15%;
  transform: rotate(-20deg);
}

/* 响应式设计 */
@media (max-width: 768px) {
  .game-card {
    padding: 40px 30px;
  }
  
  .game-title {
    font-size: 3rem;
  }
  
  .game-subtitle {
    font-size: 1rem;
    letter-spacing: 3px;
  }
  
  .menu-btn {
    padding: 15px 25px;
    font-size: 1rem;
  }
}

@media (max-width: 480px) {
  .game-title {
    font-size: 2.5rem;
  }
  
  .game-subtitle {
    font-size: 0.9rem;
  }
  
  .intro-text {
    font-size: 1rem;
  }
}
</style>
