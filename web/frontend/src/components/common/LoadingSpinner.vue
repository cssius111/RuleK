<template>
  <div class="loading-container" v-if="visible">
    <div class="loading-overlay" v-if="overlay"></div>
    <div class="loading-content" :class="{ 'with-overlay': overlay }">
      <div class="spinner-wrapper">
        <div class="blood-spinner"></div>
        <div class="pentagram-spinner"></div>
      </div>
      <p v-if="text" class="loading-text blood-text horror-flicker">{{ text }}</p>
    </div>
  </div>
</template>

<script setup lang="ts">
interface Props {
  visible?: boolean
  text?: string
  overlay?: boolean
  size?: 'small' | 'medium' | 'large'
}

withDefaults(defineProps<Props>(), {
  visible: true,
  text: '召唤黑暗力量...',
  overlay: true,
  size: 'medium'
})
</script>

<style scoped>
.loading-container {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  z-index: 9999;
  display: flex;
  align-items: center;
  justify-content: center;
}

.loading-overlay {
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(10, 0, 0, 0.9);
  backdrop-filter: blur(3px);
}

.loading-content {
  position: relative;
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 25px;
}

.loading-content.with-overlay {
  z-index: 1;
}

.spinner-wrapper {
  display: flex;
  align-items: center;
  justify-content: center;
  position: relative;
  width: 80px;
  height: 80px;
}

/* 血色旋转圈 */
.blood-spinner {
  position: absolute;
  width: 60px;
  height: 60px;
  border: 4px solid rgba(139, 0, 0, 0.2);
  border-top-color: var(--horror-accent);
  border-right-color: var(--horror-primary);
  border-radius: 50%;
  animation: blood-spin 1.5s linear infinite;
  box-shadow: 
    0 0 30px rgba(220, 20, 60, 0.8),
    inset 0 0 20px rgba(139, 0, 0, 0.5);
}

/* 五芒星内圈 */
.pentagram-spinner {
  position: absolute;
  width: 40px;
  height: 40px;
  animation: reverse-spin 3s linear infinite;
}

.pentagram-spinner::before {
  content: '⛥';
  position: absolute;
  top: 50%;
  left: 50%;
  transform: translate(-50%, -50%);
  font-size: 30px;
  color: var(--horror-primary);
  text-shadow: 0 0 20px currentColor;
  animation: pulse-glow 2s ease-in-out infinite;
}

@keyframes blood-spin {
  0% { 
    transform: rotate(0deg);
    filter: brightness(1);
  }
  50% {
    filter: brightness(1.3);
  }
  100% { 
    transform: rotate(360deg);
    filter: brightness(1);
  }
}

@keyframes reverse-spin {
  0% { transform: rotate(0deg); }
  100% { transform: rotate(-360deg); }
}

@keyframes pulse-glow {
  0%, 100% { 
    opacity: 0.6;
    transform: translate(-50%, -50%) scale(1);
  }
  50% { 
    opacity: 1;
    transform: translate(-50%, -50%) scale(1.1);
  }
}

.loading-text {
  font-size: 1.2rem;
  margin: 0;
  text-transform: uppercase;
  letter-spacing: 3px;
  font-weight: 600;
  animation: text-pulse 2s ease-in-out infinite;
}

@keyframes text-pulse {
  0%, 100% { 
    transform: scale(1);
    opacity: 0.8;
  }
  50% { 
    transform: scale(1.05);
    opacity: 1;
  }
}

/* Size variations */
.loading-container[data-size="small"] .blood-spinner {
  width: 40px;
  height: 40px;
  border-width: 3px;
}

.loading-container[data-size="small"] .pentagram-spinner::before {
  font-size: 20px;
}

.loading-container[data-size="large"] .blood-spinner {
  width: 100px;
  height: 100px;
  border-width: 5px;
}

.loading-container[data-size="large"] .pentagram-spinner::before {
  font-size: 50px;
}

/* 添加血滴装饰 */
.loading-content::after {
  content: '';
  position: absolute;
  bottom: -30px;
  left: 50%;
  transform: translateX(-50%);
  width: 6px;
  height: 20px;
  background: linear-gradient(to bottom, var(--horror-accent), transparent);
  border-radius: 50% 50% 50% 50% / 60% 60% 40% 40%;
  animation: blood-drip 2s ease-in-out infinite;
}

@keyframes blood-drip {
  0%, 100% {
    transform: translateX(-50%) translateY(0) scaleY(1);
    opacity: 0;
  }
  20% {
    opacity: 1;
  }
  80% {
    transform: translateX(-50%) translateY(20px) scaleY(1.5);
    opacity: 0.4;
  }
}
</style>
