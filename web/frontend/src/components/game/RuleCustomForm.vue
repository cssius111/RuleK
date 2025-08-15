<template>
  <div class="rule-custom-form">
    <n-form ref="formRef" :model="formData" :rules="rules">
      <n-form-item label="规则名称" path="name">
        <n-input
          v-model:value="formData.name"
          placeholder="输入规则名称"
          maxlength="30"
          show-count
        />
      </n-form-item>
      
      <n-form-item label="规则描述" path="description">
        <n-input
          v-model:value="formData.description"
          type="textarea"
          placeholder="描述规则的效果和触发条件"
          :rows="3"
          maxlength="200"
          show-count
        />
      </n-form-item>
      
      <n-form-item label="触发类型" path="trigger.type">
        <n-select
          v-model:value="formData.trigger.type"
          :options="triggerTypeOptions"
          placeholder="选择触发类型"
        />
      </n-form-item>
      
      <!-- 根据触发类型显示不同的条件输入 -->
      <n-form-item v-if="formData.trigger.type === 'time'" label="触发时间">
        <n-time-picker
          v-model:value="formData.trigger.conditions.time"
          format="HH:mm"
        />
      </n-form-item>
      
      <n-form-item v-if="formData.trigger.type === 'location'" label="触发地点">
        <n-select
          v-model:value="formData.trigger.conditions.location"
          :options="locationOptions"
          placeholder="选择地点"
        />
      </n-form-item>
      
      <n-form-item v-if="formData.trigger.type === 'action'" label="触发动作">
        <n-input
          v-model:value="formData.trigger.conditions.action"
          placeholder="例如: open_door, look_mirror"
        />
      </n-form-item>
      
      <n-form-item label="触发概率" path="trigger.probability">
        <n-slider
          v-model:value="formData.trigger.probability"
          :min="0"
          :max="1"
          :step="0.1"
          :format-tooltip="(value: number) => `${(value * 100).toFixed(0)}%`"
        />
      </n-form-item>
      
      <n-form-item label="效果类型" path="effectType">
        <n-select
          v-model:value="selectedEffectType"
          :options="effectTypeOptions"
          placeholder="选择效果类型"
        />
      </n-form-item>
      
      <n-form-item v-if="needsEffectValue" label="效果数值">
        <n-input-number
          v-model:value="effectValue"
          :min="1"
          :max="100"
          placeholder="输入数值"
        />
      </n-form-item>
      
      <n-form-item label="冷却回合" path="cooldown">
        <n-input-number
          v-model:value="formData.cooldown"
          :min="0"
          :max="10"
          placeholder="0表示无冷却"
        />
      </n-form-item>
      
      <n-divider />
      
      <n-space justify="space-between" align="center">
        <div>
          <n-text type="warning">
            预估成本: {{ estimatedCost }} 恐惧点
          </n-text>
          <n-text v-if="!canAfford" type="error" style="margin-left: 16px">
            恐惧点不足！
          </n-text>
        </div>
        
        <n-space>
          <n-button @click="$emit('cancel')">取消</n-button>
          <n-button
            type="primary"
            :disabled="!canCreate"
            @click="handleSubmit"
          >
            创建规则
          </n-button>
        </n-space>
      </n-space>
    </n-form>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, watch } from 'vue'
import {
  NForm, NFormItem, NInput, NInputNumber, NSelect,
  NSlider, NButton, NSpace, NText, NDivider, NTimePicker
} from 'naive-ui'
import { useGameStore } from '@/stores/game'
import { useRulesStore } from '@/stores/rules'

const emit = defineEmits(['create', 'cancel'])

const gameStore = useGameStore()
const rulesStore = useRulesStore()

const formRef = ref()
const formData = ref({
  name: '',
  description: '',
  trigger: {
    type: 'action',
    conditions: {},
    probability: 0.8
  },
  effects: [],
  cooldown: 0
})

const selectedEffectType = ref('fear_increase')
const effectValue = ref(30)

const triggerTypeOptions = [
  { label: '动作触发', value: 'action' },
  { label: '时间触发', value: 'time' },
  { label: '地点触发', value: 'location' },
  { label: '物品触发', value: 'item' },
  { label: '条件触发', value: 'condition' }
]

const effectTypeOptions = [
  { label: '增加恐惧', value: 'fear_increase' },
  { label: '降低理智', value: 'sanity_decrease' },
  { label: '即死', value: 'instant_death' },
  { label: '传送', value: 'teleport' },
  { label: '持续伤害', value: 'continuous_damage' }
]

const locationOptions = [
  { label: '走廊', value: 'corridor' },
  { label: '房间', value: 'room' },
  { label: '大厅', value: 'hall' },
  { label: '地下室', value: 'basement' },
  { label: '阁楼', value: 'attic' }
]

const rules = {
  name: {
    required: true,
    message: '请输入规则名称',
    trigger: 'blur'
  },
  description: {
    required: true,
    message: '请输入规则描述',
    trigger: 'blur'
  }
}

const needsEffectValue = computed(() => {
  return ['fear_increase', 'sanity_decrease', 'continuous_damage'].includes(selectedEffectType.value)
})

const estimatedCost = ref(100)

// 计算预估成本
watch([formData, selectedEffectType, effectValue], async () => {
  // 构建效果数组
  const effects = [{
    type: selectedEffectType.value,
    value: needsEffectValue.value ? effectValue.value : undefined,
    target: 'trigger_npc'
  }]
  
  const ruleData = {
    ...formData.value,
    effects
  }
  
  estimatedCost.value = await rulesStore.calculateRuleCost(ruleData)
}, { deep: true })

const canAfford = computed(() => {
  return gameStore.gameState?.fear_points >= estimatedCost.value
})

const canCreate = computed(() => {
  return formData.value.name && formData.value.description && canAfford.value
})

async function handleSubmit() {
  try {
    await formRef.value?.validate()
    
    // 构建完整的规则数据
    const effects = [{
      type: selectedEffectType.value,
      value: needsEffectValue.value ? effectValue.value : undefined,
      target: 'trigger_npc'
    }]
    
    const ruleData = {
      ...formData.value,
      effects
    }
    
    emit('create', ruleData)
  } catch (error) {
    console.error('Form validation failed:', error)
  }
}
</script>

<style scoped>
.rule-custom-form {
  padding: 16px;
}

:deep(.n-form-item) {
  margin-bottom: 24px;
}
</style>
