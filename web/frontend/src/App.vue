<template>
  <n-config-provider :theme="darkTheme" :theme-overrides="themeOverrides">
    <n-message-provider>
      <n-notification-provider>
        <n-loading-bar-provider>
          <app-layout>
            <router-view />
          </app-layout>
        </n-loading-bar-provider>
      </n-notification-provider>
    </n-message-provider>
  </n-config-provider>
</template>

<script setup lang="ts">
import { darkTheme, type GlobalThemeOverrides } from 'naive-ui'
import AppLayout from '@/components/layout/AppLayout.vue'

// 主题定制
const themeOverrides: GlobalThemeOverrides = {
  common: {
    primaryColor: '#8B0000',
    primaryColorHover: '#A52A2A',
    primaryColorPressed: '#6B0000',
    primaryColorSuppl: '#B22222',
    infoColor: '#2D1B69',
    successColor: '#4A5D23',
    warningColor: '#8B4513',
    errorColor: '#DC143C',
    textColor1: '#E0E0E0',
    textColor2: '#CCCCCC',
    textColor3: '#999999',
    bodyColor: '#0A0A0A',
    cardColor: '#1A1A1A',
    modalColor: '#1A1A1A',
    popoverColor: '#2A2A2A',
    tagColor: '#2A2A2A',
    borderColor: '#333333',
    dividerColor: '#2A2A2A',
    inputColor: '#1A1A1A',
    codeColor: '#2A2A2A',
    tabColor: '#1A1A1A',
    actionColor: '#2A2A2A',
    tableColor: '#1A1A1A',
    tableHeaderColor: '#2A2A2A',
    hoverColor: '#2A2A2A',
    clearColor: '#333333',
    placeholderColor: '#666666'
  }
}
</script>

<style lang="scss">
* {
  margin: 0;
  padding: 0;
  box-sizing: border-box;
}

html,
body {
  height: 100%;
  overflow: hidden;
}

#app {
  height: 100%;
  font-family: 'Courier New', monospace, '楷体', serif;
  -webkit-font-smoothing: antialiased;
  -moz-osx-font-smoothing: grayscale;
}

/* 全局滚动条样式 */
::-webkit-scrollbar {
  width: 8px;
  height: 8px;
}

::-webkit-scrollbar-track {
  background: #1a1a1a;
}

::-webkit-scrollbar-thumb {
  background: #444;
  border-radius: 4px;
}

::-webkit-scrollbar-thumb:hover {
  background: #555;
}

/* 全局动画 */
@keyframes fadeIn {
  from {
    opacity: 0;
    transform: translateY(10px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

.fade-in {
  animation: fadeIn 0.3s ease-out;
}

/* 恐怖氛围效果 */
.horror-glow {
  text-shadow: 0 0 10px #8b0000, 0 0 20px #8b0000, 0 0 30px #8b0000;
}

.blood-drip {
  position: relative;
  &::after {
    content: '';
    position: absolute;
    bottom: -5px;
    left: 50%;
    transform: translateX(-50%);
    width: 2px;
    height: 10px;
    background: linear-gradient(to bottom, #8b0000, transparent);
    animation: drip 2s ease-in-out infinite;
  }
}

@keyframes drip {
  0%, 100% {
    height: 10px;
    opacity: 0;
  }
  50% {
    height: 20px;
    opacity: 1;
  }
}
</style>
