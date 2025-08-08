<template>
  <div 
    class="npc-card horror-card"
    :class="{ 
      dead: !npc.is_alive,
      panicking: npc.sanity < 30,
      terrified: npc.fear > 70
    }"
    @click="$emit('click', npc)"
  >
    <!-- NPC头像区域 -->
    <div class="npc-avatar">
      <div class="avatar-image">
        {{ npc.is_alive ? getAvatarEmoji(npc) : '💀' }}
      </div>
      <div v-if="!npc.is_alive" class="death-mark">✗</div>
    </div>

    <!-- NPC信息区域 -->
    <div class="npc-info">
      <div class="npc-header">
        <h4 class="npc-name">{{ npc.name }}</h4>
        <span class="npc-location">{{ npc.location }}</span>
      </div>

      <!-- 状态条 -->
      <div class="npc-stats">
        <!-- HP -->
        <div class="stat-bar">
          <span class="stat-icon">❤️</span>
          <div class="bar-container">
            <div 
              class="bar-fill hp-bar"
              :style="{ width: `${npc.hp}%` }"
            ></div>
            <span class="bar-text">{{ npc.hp }}/100</span>
          </div>
        </div>

        <!-- 理智 -->
        <div class="stat-bar">
          <span class="stat-icon">🧠</span>
          <div class="bar-container">
            <div 
              class="bar-fill sanity-bar"
              :style="{ width: `${npc.sanity}%` }"
            ></div>
            <span class="bar-text">{{ npc.sanity }}/100</span>
          </div>
        </div>

        <!-- 恐惧 -->
        <div class="stat-bar">
          <span class="stat-icon">😱</span>
          <div class="bar-container">
            <div 
              class="bar-fill fear-bar"
              :style="{ width: `${npc.fear}%` }"
            ></div>
            <span class="bar-text">{{ npc.fear }}/100</span>
          </div>
        </div>
      </div>

      <!-- 状态标签 -->
      <div class="npc-status">
        <span v-if="!npc.is_alive" class="status-tag dead-tag">死亡</span>
        <span v-else-if="npc.sanity < 20" class="status-tag insane-tag">疯狂</span>
        <span v-else-if="npc.fear > 80" class="status-tag terror-tag">极度恐惧</span>
        <span v-else-if="npc.hp < 30" class="status-tag injured-tag">重伤</span>
        <span v-else class="status-tag normal-tag">正常</span>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
interface NPC {
  id: string
  name: string
  hp: number
  sanity: number
  fear: number
  location: string
  is_alive: boolean
}

interface Props {
  npc: NPC
}

defineProps<Props>()
defineEmits<{
  click: [npc: NPC]
}>()

// 获取NPC头像表情
const getAvatarEmoji = (npc: NPC) => {
  if (npc.sanity < 20) return '🤪'
  if (npc.fear > 80) return '😱'
  if (npc.fear > 60) return '😰'
  if (npc.hp < 30) return '🤕'
  if (npc.fear > 40) return '😨'
  return '😐'
}
</script>

<style scoped>
.npc-card {
  background: linear-gradient(135deg, rgba(20, 10, 10, 0.95), rgba(30, 0, 0, 0.9));
  border: 1px solid var(--horror-border);
  padding: 15px;
  cursor: pointer;
  transition: all 0.3s;
  display: flex;
  gap: 15px;
  position: relative;
  overflow: hidden;
}

.npc-card:hover {
  transform: translateY(-2px);
  box-shadow: 0 8px 25px rgba(139, 0, 0, 0.5);
  border-color: var(--horror-primary);
}

/* 死亡状态 */
.npc-card.dead {
  opacity: 0.6;
  filter: grayscale(80%);
  background: linear-gradient(135deg, rgba(10, 10, 10, 0.95), rgba(20, 20, 20, 0.9));
}

.npc-card.dead::after {
  content: '';
  position: absolute;
  inset: 0;
  background: repeating-linear-gradient(
    45deg,
    transparent,
    transparent 10px,
    rgba(139, 0, 0, 0.1) 10px,
    rgba(139, 0, 0, 0.1) 11px
  );
  pointer-events: none;
}

/* 恐慌状态 */
.npc-card.panicking {
  animation: panic-shake 0.5s ease-in-out infinite;
}

@keyframes panic-shake {
  0%, 100% { transform: translateX(0); }
  25% { transform: translateX(-1px); }
  75% { transform: translateX(1px); }
}

/* 恐惧状态 */
.npc-card.terrified {
  border-color: var(--horror-danger);
  box-shadow: 0 0 20px rgba(255, 0, 0, 0.3);
}

/* NPC头像 */
.npc-avatar {
  position: relative;
  flex-shrink: 0;
}

.avatar-image {
  width: 50px;
  height: 50px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 2rem;
  background: radial-gradient(circle, rgba(0, 0, 0, 0.5), transparent);
  border-radius: 50%;
  filter: drop-shadow(0 2px 5px rgba(0, 0, 0, 0.5));
}

.death-mark {
  position: absolute;
  top: 50%;
  left: 50%;
  transform: translate(-50%, -50%);
  font-size: 3rem;
  color: var(--horror-danger);
  font-weight: bold;
  opacity: 0.7;
  text-shadow: 0 0 10px currentColor;
}

/* NPC信息 */
.npc-info {
  flex: 1;
  display: flex;
  flex-direction: column;
  gap: 10px;
}

.npc-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.npc-name {
  margin: 0;
  font-size: 1rem;
  font-weight: 600;
  color: var(--horror-text);
  text-transform: uppercase;
  letter-spacing: 1px;
}

.npc-location {
  font-size: 0.8rem;
  color: var(--horror-text-secondary);
  text-transform: uppercase;
  letter-spacing: 1px;
  opacity: 0.8;
}

/* 状态条 */
.npc-stats {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.stat-bar {
  display: flex;
  align-items: center;
  gap: 8px;
}

.stat-icon {
  font-size: 1rem;
  width: 20px;
  text-align: center;
  filter: drop-shadow(0 0 3px rgba(0, 0, 0, 0.5));
}

.bar-container {
  flex: 1;
  height: 18px;
  background: rgba(0, 0, 0, 0.7);
  border: 1px solid rgba(139, 0, 0, 0.3);
  position: relative;
  overflow: hidden;
}

.bar-fill {
  height: 100%;
  transition: width 0.5s ease;
  position: relative;
}

.bar-fill::after {
  content: '';
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: linear-gradient(
    180deg,
    rgba(255, 255, 255, 0.2) 0%,
    transparent 50%,
    rgba(0, 0, 0, 0.2) 100%
  );
}

.hp-bar {
  background: linear-gradient(90deg, #8b0000, #dc143c);
}

.sanity-bar {
  background: linear-gradient(90deg, #4a148c, #7b1fa2);
}

.fear-bar {
  background: linear-gradient(90deg, #ff6f00, #ff9800);
}

.bar-text {
  position: absolute;
  top: 50%;
  left: 50%;
  transform: translate(-50%, -50%);
  font-size: 0.75rem;
  color: var(--horror-text);
  font-weight: 600;
  text-shadow: 0 0 3px rgba(0, 0, 0, 0.8);
  pointer-events: none;
}

/* 状态标签 */
.npc-status {
  display: flex;
  gap: 8px;
  flex-wrap: wrap;
}

.status-tag {
  padding: 3px 10px;
  font-size: 0.75rem;
  text-transform: uppercase;
  letter-spacing: 1px;
  font-weight: 600;
  border: 1px solid;
}

.dead-tag {
  background: rgba(0, 0, 0, 0.8);
  border-color: var(--horror-danger);
  color: var(--horror-danger);
}

.insane-tag {
  background: rgba(74, 20, 140, 0.3);
  border-color: #7b1fa2;
  color: #ce93d8;
}

.terror-tag {
  background: rgba(255, 111, 0, 0.2);
  border-color: #ff9800;
  color: #ffb74d;
}

.injured-tag {
  background: rgba(139, 0, 0, 0.3);
  border-color: var(--horror-primary);
  color: var(--horror-accent);
}

.normal-tag {
  background: rgba(0, 60, 0, 0.2);
  border-color: #2e7d32;
  color: #66bb6a;
}

/* 悬停效果 */
.npc-card:hover .npc-name {
  color: var(--horror-accent);
  text-shadow: 0 0 5px currentColor;
}

.npc-card:hover .stat-bar {
  transform: scaleY(1.1);
}
</style>
