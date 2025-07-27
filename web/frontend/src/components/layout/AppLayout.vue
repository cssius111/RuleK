<template>
  <n-layout class="app-layout">
    <n-layout-header bordered>
      <div class="header-content">
        <div class="logo" @click="goHome">
          <span class="horror-glow">规则怪谈</span>
        </div>
        
        <nav class="nav-menu">
          <router-link to="/" class="nav-link">主页</router-link>
          <router-link to="/settings" class="nav-link">设置</router-link>
        </nav>
        
        <div class="header-actions">
          <n-button 
            v-if="gameStore.gameId"
            @click="handleSaveGame"
            :loading="isSaving"
            size="small"
          >
            保存游戏
          </n-button>
        </div>
      </div>
    </n-layout-header>
    
    <n-layout-content class="main-content">
      <slot />
    </n-layout-content>
  </n-layout>
</template>

<script setup lang="ts">
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import { NLayout, NLayoutHeader, NLayoutContent, NButton, useMessage } from 'naive-ui'
import { useGameStore } from '@/stores/game'

const router = useRouter()
const message = useMessage()
const gameStore = useGameStore()

const isSaving = ref(false)

function goHome() {
  router.push('/')
}

async function handleSaveGame() {
  isSaving.value = true
  try {
    await gameStore.saveGame()
    message.success('游戏已保存')
  } catch (e: any) {
    message.error(e.message || '保存失败')
  } finally {
    isSaving.value = false
  }
}
</script>

<style lang="scss" scoped>
.app-layout {
  height: 100vh;
  
  .header-content {
    height: 60px;
    display: flex;
    align-items: center;
    justify-content: space-between;
    padding: 0 2rem;
    background: rgba(26, 26, 26, 0.95);
    
    .logo {
      font-size: 1.5rem;
      font-weight: bold;
      cursor: pointer;
      user-select: none;
      
      &:hover {
        opacity: 0.8;
      }
    }
    
    .nav-menu {
      display: flex;
      gap: 2rem;
      
      .nav-link {
        color: #ccc;
        text-decoration: none;
        transition: color 0.3s;
        
        &:hover {
          color: #fff;
        }
        
        &.router-link-active {
          color: #8b0000;
        }
      }
    }
    
    .header-actions {
      display: flex;
      gap: 1rem;
    }
  }
  
  .main-content {
    background: #0a0a0a;
    overflow: auto;
  }
}
</style>
