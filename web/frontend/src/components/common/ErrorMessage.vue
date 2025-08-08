<template>
  <transition name="horror-fade">
    <div v-if="visible" class="horror-message" :class="typeClass">
      <div class="message-icon">
        <span v-if="type === 'error'">💀</span>
        <span v-else-if="type === 'warning'">⚠️</span>
        <span v-else-if="type === 'success'">🩸</span>
        <span v-else>👁</span>
      </div>
      <div class="message-content">
        <h4 v-if="title" class="message-title">{{ title }}</h4>
        <p class="message-text">{{ message }}</p>
      </div>
      <button v-if="closable" @click="handleClose" class="message-close">
        ✕
      </button>
      
      <!-- 恐怖装饰 -->
      <div class="horror-effects">
        <div class="blood-corner"></div>
        <div class="scratch-mark"></div>
      </div>
    </div>
  </transition>
</template>

<script setup lang="ts">
import { computed } from 'vue'

interface Props {
  message: string
  title?: string
  type?: 'error' | 'warning' | 'success' | 'info'
  visible?: boolean
  closable?: boolean
}

const props = withDefaults(defineProps<Props>(), {
  type: 'error',
  visible: true,
  closable: true
})

const emit = defineEmits<{
  close: []
}>()

const typeClass = computed(() => `horror-message--${props.type}`)

const handleClose = () => {
  emit('close')
}
</script>

<style scoped>
.horror-message {
  display: flex;
  align-items: flex-start;
  gap: 15px;
  padding: 18px 20px;
  margin: 20px 0;
  position: relative;
  animation: rise-from-grave 0.5s ease-out;
  background: linear-gradient(135deg, rgba(20, 10, 10, 0.95), rgba(40, 0, 0, 0.9));
  border: 2px solid;
  box-shadow: 0 10px 40px rgba(0, 0, 0, 0.5);
  overflow: hidden;
}

@keyframes rise-from-grave {
  from {
    transform: translateY(30px) scale(0.95);
    opacity: 0;
  }
  to {
    transform: translateY(0) scale(1);
    opacity: 1;
  }
}

/* 恐怖消息类型 */
.horror-message--error {
  background: linear-gradient(135deg, 
    rgba(40, 0, 0, 0.95), 
    rgba(60, 0, 0, 0.9));
  border-color: var(--horror-danger);
  color: var(--horror-text);
  box-shadow: 
    0 10px 40px rgba(255, 0, 0, 0.3),
    inset 0 0 30px rgba(139, 0, 0, 0.5);
}

.horror-message--warning {
  background: linear-gradient(135deg, 
    rgba(40, 20, 0, 0.95), 
    rgba(60, 30, 0, 0.9));
  border-color: #8b4500;
  color: var(--horror-text);
  box-shadow: 
    0 10px 40px rgba(255, 140, 0, 0.2),
    inset 0 0 30px rgba(139, 69, 0, 0.5);
}

.horror-message--success {
  background: linear-gradient(135deg, 
    rgba(20, 10, 10, 0.95), 
    rgba(40, 0, 0, 0.9));
  border-color: var(--horror-primary);
  color: var(--horror-text);
  box-shadow: 
    0 10px 40px rgba(139, 0, 0, 0.4),
    inset 0 0 30px rgba(100, 0, 0, 0.5);
}

.horror-message--info {
  background: linear-gradient(135deg, 
    rgba(10, 10, 20, 0.95), 
    rgba(20, 20, 40, 0.9));
  border-color: #2a2a4a;
  color: var(--horror-text);
  box-shadow: 
    0 10px 40px rgba(42, 42, 74, 0.3),
    inset 0 0 30px rgba(20, 20, 40, 0.5);
}

/* 消息内容 */
.message-icon {
  font-size: 1.8rem;
  flex-shrink: 0;
  filter: drop-shadow(0 0 10px currentColor);
  animation: icon-pulse 2s ease-in-out infinite;
}

@keyframes icon-pulse {
  0%, 100% { transform: scale(1); }
  50% { transform: scale(1.1); }
}

.message-content {
  flex: 1;
}

.message-title {
  margin: 0 0 6px 0;
  font-size: 1.1rem;
  font-weight: 700;
  text-transform: uppercase;
  letter-spacing: 1px;
  color: var(--horror-text);
  text-shadow: 0 2px 4px rgba(0, 0, 0, 0.5);
}

.message-text {
  margin: 0;
  font-size: 0.95rem;
  line-height: 1.6;
  color: var(--horror-text-secondary);
  text-shadow: 0 1px 2px rgba(0, 0, 0, 0.3);
}

.message-close {
  position: absolute;
  top: 12px;
  right: 12px;
  background: rgba(0, 0, 0, 0.5);
  border: 1px solid var(--horror-border);
  font-size: 1rem;
  cursor: pointer;
  color: var(--horror-text-secondary);
  opacity: 0.7;
  transition: all 0.3s;
  padding: 4px 8px;
  line-height: 1;
}

.message-close:hover {
  opacity: 1;
  color: var(--horror-accent);
  background: rgba(139, 0, 0, 0.3);
  box-shadow: 0 0 10px rgba(220, 20, 60, 0.5);
  transform: scale(1.1);
}

/* 恐怖装饰效果 */
.horror-effects {
  pointer-events: none;
  position: absolute;
  inset: 0;
}

.blood-corner {
  position: absolute;
  top: -10px;
  right: -10px;
  width: 60px;
  height: 60px;
  background: radial-gradient(circle, var(--horror-accent) 10%, transparent 60%);
  filter: blur(15px);
  opacity: 0.3;
  animation: blood-pulse 3s ease-in-out infinite;
}

@keyframes blood-pulse {
  0%, 100% { 
    transform: scale(1);
    opacity: 0.3;
  }
  50% { 
    transform: scale(1.2);
    opacity: 0.5;
  }
}

.scratch-mark {
  position: absolute;
  bottom: 5px;
  left: 30%;
  width: 100px;
  height: 2px;
  background: repeating-linear-gradient(
    90deg,
    transparent,
    transparent 5px,
    rgba(139, 0, 0, 0.2) 5px,
    rgba(139, 0, 0, 0.2) 7px
  );
  transform: rotate(-2deg);
  opacity: 0.5;
}

/* 恐怖过渡动画 */
.horror-fade-enter-active,
.horror-fade-leave-active {
  transition: all 0.5s ease;
}

.horror-fade-enter-from {
  opacity: 0;
  transform: translateY(30px) scale(0.8);
  filter: blur(10px);
}

.horror-fade-leave-to {
  opacity: 0;
  transform: translateY(-20px) scale(0.8) rotate(2deg);
  filter: blur(10px);
}

/* 错误消息特殊效果 */
.horror-message--error::before {
  content: '';
  position: absolute;
  top: 0;
  left: -100%;
  width: 100%;
  height: 100%;
  background: linear-gradient(90deg, 
    transparent, 
    rgba(255, 0, 0, 0.3), 
    transparent);
  animation: danger-sweep 3s ease-in-out infinite;
}

@keyframes danger-sweep {
  0% { left: -100%; }
  100% { left: 100%; }
}

/* 成功消息特殊效果 */
.horror-message--success::after {
  content: '';
  position: absolute;
  bottom: 0;
  left: 0;
  right: 0;
  height: 2px;
  background: linear-gradient(90deg,
    transparent,
    var(--horror-accent) 20%,
    var(--horror-primary) 50%,
    var(--horror-accent) 80%,
    transparent);
  animation: blood-flow 3s ease-in-out infinite;
}

@keyframes blood-flow {
  0%, 100% { 
    opacity: 0.5;
    transform: scaleX(0.8);
  }
  50% { 
    opacity: 1;
    transform: scaleX(1);
  }
}
</style>
