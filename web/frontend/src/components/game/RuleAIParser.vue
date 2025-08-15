<template>
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
