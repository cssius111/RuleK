"""
创建完整的前端规则组件套件
"""
import os

def create_rule_creator_modal():
    """创建完整的规则创建模态框"""
    modal_code = '''<template>
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
'''
    
    output_path = "web/frontend/src/components/game/RuleCreatorModal.vue"
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(modal_code)
    print(f"✅ 更新规则创建模态框: {output_path}")

def create_custom_form():
    """创建自定义规则表单组件"""
    form_code = '''<template>
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
'''
    
    output_path = "web/frontend/src/components/game/RuleCustomForm.vue"
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(form_code)
    print(f"✅ 创建自定义规则表单: {output_path}")

def create_ai_parser():
    """创建AI规则解析组件"""
    ai_parser_code = '''<template>
  <div class="rule-ai-parser">
    <n-space vertical :size="20">
      <n-alert type="info" :bordered="false">
        <template #icon>
          <n-icon :component="Sparkles" />
        </template>
        使用自然语言描述你想要的规则，AI会帮你解析成游戏规则
      </n-alert>
      
      <n-form-item label="规则描述">
        <n-input
          v-model:value="description"
          type="textarea"
          placeholder="例如：当NPC在深夜独自待在房间里时，会听到敲门声，恐惧值增加50点"
          :rows="5"
          maxlength="500"
          show-count
        />
      </n-form-item>
      
      <n-space>
        <n-button
          type="primary"
          :loading="isParsing"
          :disabled="!description.trim()"
          @click="parseRule"
        >
          <template #icon>
            <n-icon :component="Robot" />
          </template>
          AI解析
        </n-button>
        
        <n-button v-if="parsedRule" @click="reset">
          重新输入
        </n-button>
      </n-space>
      
      <!-- 解析结果 -->
      <div v-if="parsedRule" class="parse-result">
        <n-divider />
        
        <n-descriptions :column="2" bordered>
          <n-descriptions-item label="规则名称">
            {{ parsedRule.rule_name }}
          </n-descriptions-item>
          <n-descriptions-item label="预估成本">
            <n-tag type="warning">
              {{ parsedRule.estimated_cost }} 恐惧点
            </n-tag>
          </n-descriptions-item>
          <n-descriptions-item label="触发类型" :span="2">
            {{ parsedRule.trigger.type }}
          </n-descriptions-item>
          <n-descriptions-item label="触发概率" :span="2">
            {{ (parsedRule.trigger.probability * 100).toFixed(0) }}%
          </n-descriptions-item>
        </n-descriptions>
        
        <n-card title="效果" size="small" style="margin-top: 16px">
          <n-list>
            <n-list-item v-for="(effect, index) in parsedRule.effects" :key="index">
              <n-thing>
                <template #header>
                  {{ getEffectName(effect.type) }}
                </template>
                <template #description>
                  <n-space>
                    <n-tag v-if="effect.value" size="small">
                      数值: {{ effect.value }}
                    </n-tag>
                    <n-tag v-if="effect.target" size="small" type="info">
                      目标: {{ effect.target }}
                    </n-tag>
                  </n-space>
                </template>
              </n-thing>
            </n-list-item>
          </n-list>
        </n-card>
        
        <n-card v-if="parsedRule.suggestions?.length" title="AI建议" size="small" style="margin-top: 16px">
          <n-list>
            <n-list-item v-for="(suggestion, index) in parsedRule.suggestions" :key="index">
              <n-text>{{ index + 1 }}. {{ suggestion }}</n-text>
            </n-list-item>
          </n-list>
        </n-card>
        
        <n-divider />
        
        <n-space justify="space-between">
          <n-text v-if="!canAfford" type="error">
            恐惧点不足！当前: {{ gameStore.gameState?.fear_points || 0 }} / 需要: {{ parsedRule.estimated_cost }}
          </n-text>
          <div v-else />
          
          <n-space>
            <n-button @click="$emit('cancel')">取消</n-button>
            <n-button
              type="primary"
              :disabled="!canAfford"
              @click="confirmCreate"
            >
              确认创建
            </n-button>
          </n-space>
        </n-space>
      </div>
    </n-space>
  </div>
</template>

<script setup lang="ts">
import { ref, computed } from 'vue'
import {
  NSpace, NAlert, NIcon, NFormItem, NInput, NButton,
  NDivider, NDescriptions, NDescriptionsItem, NTag,
  NCard, NList, NListItem, NThing, NText
} from 'naive-ui'
import { Sparkles, Robot } from '@vicons/tabler'
import { useMessage } from 'naive-ui'
import { useGameStore } from '@/stores/game'
import { useRulesStore } from '@/stores/rules'

const emit = defineEmits(['create', 'cancel'])

const message = useMessage()
const gameStore = useGameStore()
const rulesStore = useRulesStore()

const description = ref('')
const isParsing = ref(false)
const parsedRule = ref<any>(null)

const canAfford = computed(() => {
  if (!parsedRule.value) return false
  return gameStore.gameState?.fear_points >= parsedRule.value.estimated_cost
})

async function parseRule() {
  if (!description.value.trim()) return
  
  isParsing.value = true
  try {
    const result = await rulesStore.parseRuleWithAI(
      description.value,
      gameStore.currentGameId
    )
    
    if (result.success) {
      parsedRule.value = result
      message.success('AI解析成功！')
    } else {
      message.error('AI解析失败，请重试')
    }
  } catch (error: any) {
    message.error(error.message || 'AI服务暂时不可用')
  } finally {
    isParsing.value = false
  }
}

function confirmCreate() {
  if (!parsedRule.value) return
  
  const ruleData = {
    name: parsedRule.value.rule_name,
    description: parsedRule.value.description || description.value,
    trigger: parsedRule.value.trigger,
    effects: parsedRule.value.effects,
    cooldown: 0
  }
  
  emit('create', ruleData)
}

function reset() {
  parsedRule.value = null
  description.value = ''
}

function getEffectName(type: string) {
  const effectNames: Record<string, string> = {
    'fear_increase': '增加恐惧',
    'sanity_decrease': '降低理智',
    'instant_death': '即死效果',
    'teleport': '传送',
    'continuous_damage': '持续伤害'
  }
  return effectNames[type] || type
}
</script>

<style scoped>
.rule-ai-parser {
  padding: 16px;
}

.parse-result {
  animation: fadeIn 0.3s ease-in;
}

@keyframes fadeIn {
  from { opacity: 0; transform: translateY(10px); }
  to { opacity: 1; transform: translateY(0); }
}

:deep(.n-card) {
  background: var(--n-color-modal);
}
</style>
'''
    
    output_path = "web/frontend/src/components/game/RuleAIParser.vue"
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(ai_parser_code)
    print(f"✅ 创建AI规则解析组件: {output_path}")

def create_rule_card():
    """创建规则卡片组件"""
    card_code = '''<template>
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
'''
    
    output_path = "web/frontend/src/components/game/RuleCard.vue"
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(card_code)
    print(f"✅ 创建规则卡片组件: {output_path}")

def main():
    """主函数"""
    print("=" * 60)
    print("🎨 创建前端规则组件套件")
    print("=" * 60)
    
    print("\n1️⃣ 更新规则创建模态框...")
    create_rule_creator_modal()
    
    print("\n2️⃣ 创建自定义规则表单...")
    create_custom_form()
    
    print("\n3️⃣ 创建AI规则解析组件...")
    create_ai_parser()
    
    print("\n4️⃣ 创建规则卡片组件...")
    create_rule_card()
    
    print("\n" + "=" * 60)
    print("✅ 前端组件创建完成!")

if __name__ == "__main__":
    main()
