<template>
  <n-card
    title="创建新规则"
    :bordered="false"
    size="large"
    role="dialog"
    aria-modal="true"
    style="width: 600px; max-width: 90vw"
  >
    <n-form
      ref="formRef"
      :model="formValue"
      :rules="rules"
      label-placement="top"
    >
      <n-form-item label="规则名称" path="name">
        <n-input
          v-model:value="formValue.name"
          placeholder="例如：午夜照镜死"
          maxlength="50"
          show-count
        />
      </n-form-item>
      
      <n-form-item label="规则描述" path="description">
        <n-input
          v-model:value="formValue.description"
          type="textarea"
          placeholder="详细描述规则的效果和触发条件"
          :rows="3"
          maxlength="500"
          show-count
        />
      </n-form-item>
      
      <n-form-item label="触发动作" path="trigger.action">
        <n-select
          v-model:value="formValue.trigger.action"
          :options="actionOptions"
          placeholder="选择触发动作"
        />
      </n-form-item>
      
      <n-form-item label="触发地点">
        <n-select
          v-model:value="formValue.requirements.areas"
          multiple
          :options="areaOptions"
          placeholder="选择触发地点（可多选）"
        />
      </n-form-item>
      
      <n-form-item label="时间限制">
        <n-space>
          <n-time-picker
            v-model:value="timeFrom"
            format="HH:mm"
            :actions="null"
            placeholder="开始时间"
          />
          <span>至</span>
          <n-time-picker
            v-model:value="timeTo"
            format="HH:mm"
            :actions="null"
            placeholder="结束时间"
          />
        </n-space>
      </n-form-item>
      
      <n-form-item label="效果类型" path="effect.type">
        <n-radio-group v-model:value="formValue.effect.type">
          <n-space>
            <n-radio value="instant_death">即死</n-radio>
            <n-radio value="sanity_loss">理智损失</n-radio>
            <n-radio value="fear_gain">恐惧增加</n-radio>
            <n-radio value="teleport">传送</n-radio>
          </n-space>
        </n-radio-group>
      </n-form-item>
      
      <n-form-item v-if="formValue.effect.type === 'sanity_loss'" label="理智损失值">
        <n-input-number
          v-model:value="formValue.effect.sanity_loss"
          :min="10"
          :max="100"
          :step="10"
        />
      </n-form-item>
      
      <n-form-item label="恐惧值收益">
        <n-input-number
          v-model:value="formValue.effect.fear_gain"
          :min="50"
          :max="500"
          :step="50"
        />
      </n-form-item>
      
      <n-form-item label="消耗积分" path="cost">
        <n-input-number
          v-model:value="formValue.cost"
          :min="50"
          :max="1000"
          :step="50"
        />
        <template #feedback>
          <span :style="{ color: formValue.cost > fearPoints ? '#d03050' : '#18a058' }">
            当前恐惧积分: {{ fearPoints }}
          </span>
        </template>
      </n-form-item>
    </n-form>
    
    <template #footer>
      <n-space justify="end">
        <n-button @click="$emit('cancel')">取消</n-button>
        <n-button
          type="primary"
          @click="handleSubmit"
          :disabled="formValue.cost > fearPoints"
        >
          创建规则
        </n-button>
      </n-space>
    </template>
  </n-card>
</template>

<script setup>
import { ref, computed } from 'vue'
import {
  NCard, NForm, NFormItem, NInput, NInputNumber,
  NSelect, NRadioGroup, NRadio, NSpace, NButton,
  NTimePicker, useMessage
} from 'naive-ui'

const props = defineProps({
  fearPoints: {
    type: Number,
    required: true
  }
})

const emit = defineEmits(['create', 'cancel'])

const message = useMessage()
const formRef = ref(null)
const timeFrom = ref(null)
const timeTo = ref(null)

const formValue = ref({
  name: '',
  description: '',
  requirements: {
    areas: [],
    items: []
  },
  trigger: {
    action: '',
    extra_conditions: []
  },
  effect: {
    type: 'instant_death',
    fear_gain: 200,
    sanity_loss: 50
  },
  cost: 150
})

const rules = {
  name: {
    required: true,
    trigger: ['blur', 'input'],
    message: '请输入规则名称'
  },
  description: {
    required: true,
    trigger: ['blur', 'input'],
    message: '请输入规则描述'
  },
  'trigger.action': {
    required: true,
    message: '请选择触发动作'
  },
  'effect.type': {
    required: true,
    message: '请选择效果类型'
  },
  cost: {
    required: true,
    type: 'number',
    message: '请设置消耗积分'
  }
}

const actionOptions = [
  { label: '照镜子', value: 'look_mirror' },
  { label: '开门', value: 'open_door' },
  { label: '关灯', value: 'turn_off_light' },
  { label: '独自行动', value: 'move_alone' },
  { label: '发出声音', value: 'make_noise' },
  { label: '触摸物品', value: 'touch_item' }
]

const areaOptions = [
  { label: '客厅', value: 'living_room' },
  { label: '卧室A', value: 'bedroom_a' },
  { label: '卧室B', value: 'bedroom_b' },
  { label: '厨房', value: 'kitchen' },
  { label: '浴室', value: 'bathroom' },
  { label: '走廊', value: 'corridor' }
]

async function handleSubmit() {
  try {
    await formRef.value?.validate()
    
    // 处理时间范围
    if (timeFrom.value && timeTo.value) {
      const fromTime = new Date(timeFrom.value)
      const toTime = new Date(timeTo.value)
      formValue.value.requirements.time = {
        from: `${fromTime.getHours().toString().padStart(2, '0')}:${fromTime.getMinutes().toString().padStart(2, '0')}`,
        to: `${toTime.getHours().toString().padStart(2, '0')}:${toTime.getMinutes().toString().padStart(2, '0')}`
      }
    }
    
    emit('create', formValue.value)
  } catch (errors) {
    message.error('请填写所有必填项')
  }
}
</script>

<style scoped>
:deep(.n-card) {
  background: rgba(26, 15, 31, 0.95);
  border: 1px solid rgba(139, 0, 0, 0.3);
}

:deep(.n-card-header) {
  border-bottom: 1px solid rgba(139, 0, 0, 0.2);
}

:deep(.n-form-item-label) {
  color: #dc143c;
  font-weight: 500;
}
</style>
