<template>
  <n-card
    :title="rule.name"
    size="small"
    hoverable
    :segmented="{ content: true }"
  >
    <template #header-extra>
      <n-space align="center">
        <n-tag :type="rule.is_active ? 'success' : 'default'" size="small">
          {{ rule.is_active ? '激活' : '未激活' }}
        </n-tag>
        <n-tag type="info" size="small">
          Lv.{{ rule.level }}
        </n-tag>
      </n-space>
    </template>
    
    <n-text class="description">{{ rule.description }}</n-text>
    
    <template #footer>
      <n-space justify="space-between" align="center">
        <n-space size="small">
          <n-tag size="small" :bordered="false">
            <n-icon :component="Clock" />
            冷却: {{ rule.cooldown }}
          </n-tag>
        </n-space>
        
        <n-space size="small">
          <n-button
            size="tiny"
            :type="rule.is_active ? 'warning' : 'success'"
            @click="handleToggle"
          >
            {{ rule.is_active ? '禁用' : '启用' }}
          </n-button>
          <n-button
            size="tiny"
            type="info"
            :disabled="!canUpgrade"
            @click="handleUpgrade"
          >
            升级
          </n-button>
        </n-space>
      </n-space>
    </template>
  </n-card>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import { NCard, NSpace, NTag, NText, NButton, NIcon } from 'naive-ui'
import { Clock } from '@vicons/tabler'
import { useGameStore } from '@/stores/game'
import { useRulesStore } from '@/stores/rules'
import { useMessage } from 'naive-ui'

const props = defineProps<{
  rule: any
}>()

const message = useMessage()
const gameStore = useGameStore()
const rulesStore = useRulesStore()

const canUpgrade = computed(() => {
  const upgradeCost = props.rule.cost * props.rule.level
  return gameStore.gameState?.fear_points >= upgradeCost
})

async function handleToggle() {
  try {
    await rulesStore.toggleRule(gameStore.currentGameId!, props.rule.id)
    message.success(props.rule.is_active ? '规则已禁用' : '规则已启用')
  } catch (error) {
    message.error('操作失败')
  }
}

async function handleUpgrade() {
  try {
    await rulesStore.upgradeRule(gameStore.currentGameId!, props.rule.id)
    message.success(`规则升级到 Lv.${props.rule.level + 1}`)
  } catch (error: any) {
    message.error(error.message || '升级失败')
  }
}
</script>

<style scoped>
.description {
  display: block;
  font-size: 13px;
  line-height: 1.6;
  color: var(--n-text-color-3);
  margin-bottom: 8px;
}

:deep(.n-card__footer) {
  padding: 8px 16px;
  background: var(--n-color-embedded);
}
</style>
