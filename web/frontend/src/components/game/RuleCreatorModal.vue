<template>
  <n-modal
    v-model:show="showModal"
    preset="card"
    title="创建规则"
    :style="{ width: '800px' }"
    :mask-closable="false"
    @after-leave="handleClose"
  >
    <!-- 创建类型选择 -->
    <n-tabs v-model:value="creationType">
      <n-tab-pane name="template" tab="使用模板">
        <RuleTemplateSelector
          v-if="creationType === 'template'"
          @select="handleTemplateSelect"
          @cancel="showModal = false"
        />
      </n-tab-pane>
      
      <n-tab-pane name="custom" tab="自定义规则">
        <RuleCustomForm
          v-if="creationType === 'custom'"
          @create="handleCustomCreate"
          @cancel="showModal = false"
        />
      </n-tab-pane>
      
      <n-tab-pane name="ai" tab="AI解析">
        <RuleAIParser
          v-if="creationType === 'ai'"
          @create="handleAICreate"
          @cancel="showModal = false"
        />
      </n-tab-pane>
    </n-tabs>
  </n-modal>
</template>

<script setup lang="ts">
import { ref, computed, watch } from 'vue'
import { NModal, NTabs, NTabPane } from 'naive-ui'
import { useMessage } from 'naive-ui'
import { useGameStore } from '@/stores/game'
import { useRulesStore } from '@/stores/rules'
import RuleTemplateSelector from './RuleTemplateSelector.vue'
import RuleCustomForm from './RuleCustomForm.vue'
import RuleAIParser from './RuleAIParser.vue'

const props = defineProps<{
  show: boolean
}>()

const emit = defineEmits<{
  'update:show': [value: boolean]
  'created': [rule: any]
}>()

const message = useMessage()
const gameStore = useGameStore()
const rulesStore = useRulesStore()

const showModal = computed({
  get: () => props.show,
  set: (value) => emit('update:show', value)
})

const creationType = ref<'template' | 'custom' | 'ai'>('template')

// 处理模板选择
async function handleTemplateSelect(template: any) {
  try {
    const rule = await rulesStore.createRuleFromTemplate(
      gameStore.currentGameId!,
      template.id
    )
    message.success(`规则"${rule.name}"创建成功！`)
    emit('created', rule)
    showModal.value = false
  } catch (error: any) {
    message.error(error.message || '创建规则失败')
  }
}

// 处理自定义规则创建
async function handleCustomCreate(ruleData: any) {
  try {
    const rule = await rulesStore.createCustomRule(
      gameStore.currentGameId!,
      ruleData
    )
    message.success(`规则"${rule.name}"创建成功！`)
    emit('created', rule)
    showModal.value = false
  } catch (error: any) {
    message.error(error.message || '创建规则失败')
  }
}

// 处理AI规则创建
async function handleAICreate(ruleData: any) {
  try {
    const rule = await rulesStore.createCustomRule(
      gameStore.currentGameId!,
      ruleData
    )
    message.success(`规则"${rule.name}"创建成功！`)
    emit('created', rule)
    showModal.value = false
  } catch (error: any) {
    message.error(error.message || '创建规则失败')
  }
}

function handleClose() {
  creationType.value = 'template'
}
</script>

<style scoped>
:deep(.n-tabs-tab) {
  padding: 12px 20px;
  font-size: 15px;
}

:deep(.n-tab-pane) {
  padding-top: 20px;
  min-height: 400px;
}
</style>
