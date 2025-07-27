<template>
  <div class="npc-grid">
    <h3 class="section-title">NPC状态</h3>
    
    <div class="npc-list">
      <NPCCard 
        v-for="npc in gameStore.npcs" 
        :key="npc.id"
        :npc="npc"
        @click="handleNPCClick(npc)"
      />
    </div>
  </div>
</template>

<script setup lang="ts">
import { useGameStore } from '@/stores/game'
import { useDialog } from 'naive-ui'
import NPCCard from './NPCCard.vue'
import type { NPC } from '@/types/game'

const gameStore = useGameStore()
const dialog = useDialog()

function handleNPCClick(npc: NPC) {
  // TODO: 显示NPC详细信息对话框
  console.log('NPC clicked:', npc)
}
</script>

<style lang="scss" scoped>
.npc-grid {
  .section-title {
    color: #8b0000;
    margin-bottom: 1rem;
    padding-bottom: 0.5rem;
    border-bottom: 1px solid #333;
  }
  
  .npc-list {
    display: grid;
    gap: 1rem;
  }
}
</style>
