<template>
  <n-modal
    v-model:show="show"
    preset="card"
    title="创建新规则"
    style="width: 600px"
    :mask-closable="false"
  >
    <n-form
      ref="formRef"
      :model="formData"
      :rules="rules"
      label-placement="top"
    >
      <n-form-item label="规则名称" path="name">
        <n-input 
          v-model:value="formData.name"
          placeholder="例如：午夜照镜死"
          maxlength="50"
          show-count
        />
      </n-form-item>
      
      <n-form-item label="规则描述" path="description">
        <n-input
          v-model:value="formData.description"
          type="textarea"
          placeholder="详细描述规则的效果和触发条件"
          :rows="3"
          maxlength="500"
          show-count
        />
      </n-form-item>
      
      <n-form-item label="触发动作" path="trigger.action">
        <n-select
          v-model:value="formData.trigger.action"
          :options="actionOptions"
          placeholder="选择触发动作"
        />
      </n-form-item>
      
      <n-form-item label="地点限制" path="requirements.areas">
        <n-select
          v-model:value="formData.requirements.areas"
          multiple
          :options="areaOptions"
          placeholder="选择生效地点（可多选）"
        />
      </n-form-item>
      
      <n-form-item label="时间限制" path="requirements.time">
        <n-space>
          <n-time-picker
            v-model:value="formData.requirements.time.from"
            format="HH:mm"
            placeholder="开始时间"
          />
          <span>至</span>
          <n-time-picker
            v-model:value="formData.requirements.time.to"
            format="HH:mm"
            placeholder="结束时间"
          />
        </n-space>
      </n-form-item>
      
      <n-form-item label="效果类型" path="effect.type">
        <n-radio-group v-model:value="formData.effect.type">
          <n-space>
            <n-radio value="instant_death">即死</n-radio>
            <n-radio value="damage">伤害</n-radio>
            <n-radio value="fear_gain">恐惧</n-radio>
            <n-radio value="sanity_loss">理智损失</n-radio>
          </n-space>
        </n-radio-group>
      </n-form-item>
      
      <n-form-item 
        v-if="formData.effect.type === 'damage'"
        label="伤害值" 
        path="effect.damage"
      >
        <n-input-number
          v-model:value="formData.effect.damage"
          :min="10"
          :max="100"
          :step="10"
        />
      </n-form-item>
      
      <n-form-item 
        v-if="formData.effect.type === 'sanity_loss'"
        label="理智损失" 
        path="effect.sanity_loss"
      >
        <n-input-number
          v-model:value="formData.effect.sanity_loss"
          :min="10"
          :max="50"
          :step="5"
        />
      </n-form-item>
      
      <n-form-item label="恐惧值收益" path="effect.fear_gain">
        <n-input-number
          v-model:value="formData.effect.fear_gain"
          :min="50"
          :max="500"
          :step="50"
        />
      </n-form-item>
      
      <n-form-item label="消耗积分" path="cost">
        <n-input-number
          v-model:value="formData.cost"
          :min="50"
          :max="1000"
          :step="50"
        />
        <template #feedback>
          当前积分：{{ gameStore.fearPoints }}
        </template>
      </n-form-item>
    </n-form>
    
    <template #footer>
      <n-space justify="end">
        <n-button @click="handleCancel">取消</n-button>
        <n-button 
          type="primary" 
          :disabled="formData.cost > gameStore.fearPoints"
          :loading="isCreating"
          @click="handleCreate"
        >
          创建规则
        </n-button>
      </n-space>
    </template>
  </n-modal>
</template>

<script setup lang="ts">
import { ref, reactive, computed } from 'vue'
import { 
  NModal, NForm, NFormItem, NInput, NSelect, NRadioGroup, NRadio, 
  NInputNumber, NButton, NSpace, NTimePicker, useMessage, FormInst 
} from 'naive-ui'
import { useGameStore } from '@/stores/game'
import type { RuleCreateRequest } from '@/types/game'

const props = defineProps<{
  show: boolean
}>()

const emit = defineEmits<{
  'update:show': [value: boolean]
  'created': []
}>()

const message = useMessage()
const gameStore = useGameStore()

const formRef = ref<FormInst>()
const isCreating = ref(false)

// 表单数据
const formData = reactive({
  name: '',
  description: '',
  requirements: {
    areas: [] as string[],
    time: {
      from: null as number | null,
      to: null as number | null
    }
  },
  trigger: {
    action: ''
  },
  effect: {
    type: 'instant_death',
    fear_gain: 100,
    damage: 50,
    sanity_loss: 30
  },
  cost: 150
})

// 表单验证规则
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
  },
  'trigger.action': {
    required: true,
    message: '请选择触发动作',
    trigger: 'change'
  },
  'effect.type': {
    required: true,
    message: '请选择效果类型',
    trigger: 'change'
  }
}

// 选项
const actionOptions = [
  { label: '照镜子', value: 'look_mirror' },
  { label: '开门', value: 'open_door' },
  { label: '关灯', value: 'turn_off_light' },
  { label: '开灯', value: 'turn_on_light' },
  { label: '说话', value: 'speak' },
  { label: '独处', value: 'alone' },
  { label: '睡觉', value: 'sleep' },
  { label: '调查', value: 'investigate' }
]

const areaOptions = [
  { label: '客厅', value: 'living_room' },
  { label: '卧室A', value: 'bedroom_a' },
  { label: '卧室B', value: 'bedroom_b' },
  { label: '厨房', value: 'kitchen' },
  { label: '浴室', value: 'bathroom' },
  { label: '走廊', value: 'corridor' }
]

// 计算属性
const show = computed({
  get: () => props.show,
  set: (value) => emit('update:show', value)
})

// 方法
async function handleCreate() {
  try {
    await formRef.value?.validate()
    
    isCreating.value = true
    
    // 构建请求数据
    const requestData: RuleCreateRequest = {
      name: formData.name,
      description: formData.description,
      requirements: {
        areas: formData.requirements.areas.length > 0 ? formData.requirements.areas : undefined,
        time: (formData.requirements.time.from && formData.requirements.time.to) ? {
          from: new Date(formData.requirements.time.from).toTimeString().slice(0, 5),
          to: new Date(formData.requirements.time.to).toTimeString().slice(0, 5)
        } : undefined
      },
      trigger: {
        action: formData.trigger.action,
        probability: 0.8 // 默认触发概率
      },
      effect: {
        type: formData.effect.type,
        fear_gain: formData.effect.fear_gain,
        damage: formData.effect.type === 'damage' ? formData.effect.damage : undefined,
        sanity_loss: formData.effect.type === 'sanity_loss' ? formData.effect.sanity_loss : undefined
      },
      cost: formData.cost
    }
    
    await gameStore.createRule(requestData)
    
    message.success('规则创建成功！')
    emit('created')
    handleCancel()
    
  } catch (e: any) {
    message.error(e.message || '创建规则失败')
  } finally {
    isCreating.value = false
  }
}

function handleCancel() {
  show.value = false
  // 重置表单
  formData.name = ''
  formData.description = ''
  formData.requirements.areas = []
  formData.requirements.time.from = null
  formData.requirements.time.to = null
  formData.trigger.action = ''
  formData.effect.type = 'instant_death'
  formData.effect.fear_gain = 100
  formData.cost = 150
}
</script>
