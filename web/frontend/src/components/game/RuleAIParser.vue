<template>
  <div class="rule-ai-parser">
    <n-space vertical :size="20">
      <!-- AI解析说明 -->
      <n-alert type="info">
        <template #icon>
          <n-icon :component="BulbOutline" />
        </template>
        使用自然语言描述你想要的规则，AI将帮你解析并生成规则配置。
        例如："当NPC在午夜照镜子时，恐惧值增加50点"
      </n-alert>
      
      <!-- 输入区域 -->
      <n-form-item label="规则描述">
        <n-input
          v-model:value="ruleDescription"
          type="textarea"
          placeholder="详细描述你想要创建的规则..."
          :rows="6"
          maxlength="500"
          show-count
        />
      </n-form-item>
      
      <!-- 解析选项 -->
      <n-space>
        <n-checkbox v-model:checked="options.autoOptimize">
          自动优化规则平衡性
        </n-checkbox>
        <n-checkbox v-model:checked="options.suggestVariations">
          生成规则变体建议
        </n-checkbox>
      </n-space>
      
      <!-- 解析按钮 -->
      <n-button
        type="primary"
        block
        :loading="isParsing"
        :disabled="!ruleDescription.trim()"
        @click="parseRule"
      >
        <template #icon>
          <n-icon :component="Sparkles" />
        </template>
        AI 解析规则
      </n-button>
      
      <!-- 解析结果 -->
      <n-collapse-transition :show="!!parsedRule">
        <n-card title="解析结果" v-if="parsedRule">
          <n-space vertical>
            <!-- 基本信息 -->
            <n-descriptions :column="2">
              <n-descriptions-item label="规则名称">
                <n-input v-model:value="parsedRule.rule_name" />
              </n-descriptions-item>
              <n-descriptions-item label="预估成本">
                <n-tag type="warning">{{ parsedRule.estimated_cost }} 恐惧点</n-tag>
              </n-descriptions-item>
            </n-descriptions>
            
            <!-- 规则描述 -->
            <n-form-item label="规则描述">
              <n-input
                v-model:value="parsedRule.description"
                type="textarea"
                :rows="2"
              />
            </n-form-item>
            
            <!-- 触发条件 -->
            <n-card size="small" title="触发条件">
              <n-space vertical>
                <n-descriptions :column="2" size="small">
                  <n-descriptions-item label="触发类型">
                    {{ parsedRule.trigger?.type }}
                  </n-descriptions-item>
                  <n-descriptions-item label="触发概率">
                    {{ (parsedRule.trigger?.probability * 100).toFixed(0) }}%
                  </n-descriptions-item>
                </n-descriptions>
                
                <n-form-item label="触发条件" size="small">
                  <n-code :code="JSON.stringify(parsedRule.trigger?.conditions, null, 2)" language="json" />
                </n-form-item>
              </n-space>
            </n-card>
            
            <!-- 规则效果 -->
            <n-card size="small" title="规则效果">
              <n-list>
                <n-list-item v-for="(effect, idx) in parsedRule.effects" :key="idx">
                  <n-thing>
                    <template #header>
                      效果 {{ idx + 1 }}: {{ getEffectTypeName(effect.type) }}
                    </template>
                    <template #description>
                      <n-space>
                        <n-tag size="small">目标: {{ effect.target }}</n-tag>
                        <n-tag v-if="effect.value" size="small" type="info">
                          数值: {{ effect.value }}
                        </n-tag>
                      </n-space>
                    </template>
                  </n-thing>
                </n-list-item>
              </n-list>
            </n-card>
            
            <!-- AI建议 -->
            <n-card v-if="parsedRule.suggestions?.length" size="small" title="AI建议">
              <n-ul>
                <n-li v-for="(suggestion, idx) in parsedRule.suggestions" :key="idx">
                  {{ suggestion }}
                </n-li>
              </n-ul>
            </n-card>
            
            <!-- 操作按钮 -->
            <n-space justify="space-between">
              <n-button @click="resetParser">重新解析</n-button>
              <n-space>
                <n-button @click="$emit('cancel')">取消</n-button>
                <n-button
                  type="primary"
                  :disabled="!canCreate"
                  @click="confirmCreate"
                >
                  创建规则
                </n-button>
              </n-space>
            </n-space>
          </n-space>
        </n-card>
      </n-collapse-transition>
    </n-space>
  </div>
</template>

<script setup lang="ts">
import { ref, computed } from 'vue'
import {
  NSpace, NInput, NButton, NCard, NAlert, NIcon,
  NFormItem, NCheckbox, NCollapseTransition, NDescriptions,
  NDescriptionsItem, NTag, NList, NListItem, NThing,
  NCode, NUl, NLi, useMessage
} from 'naive-ui'
import { BulbOutline, Sparkles } from '@vicons/ionicons5'
import { useGameStore } from '@/stores/game'
import { useRulesStore } from '@/stores/rules'

const emit = defineEmits(['create', 'cancel'])

const message = useMessage()
const gameStore = useGameStore()
const rulesStore = useRulesStore()

// 状态
const ruleDescription = ref('')
const isParsing = ref(false)
const parsedRule = ref<any>(null)

const options = ref({
  autoOptimize: true,
  suggestVariations: false
})

// 计算属性
const canCreate = computed(() => {
  if (!parsedRule.value) return false
  const cost = parsedRule.value.estimated_cost || 100
  return gameStore.gameState?.fear_points >= cost
})

// 方法
async function parseRule() {
  if (!ruleDescription.value.trim()) {
    message.warning('请输入规则描述')
    return
  }
  
  isParsing.value = true
  try {
    const result = await rulesStore.parseRuleWithAI(
      ruleDescription.value,
      gameStore.currentGameId
    )
    
    if (result.success) {
      parsedRule.value = result
      message.success('AI解析完成！')
      
      // 如果自动优化选项开启，应用优化建议
      if (options.value.autoOptimize) {
        applyOptimizations()
      }
    } else {
      message.error('解析失败，请尝试更详细的描述')
    }
  } catch (error: any) {
    message.error(error.message || 'AI解析失败')
  } finally {
    isParsing.value = false
  }
}

function applyOptimizations() {
  if (!parsedRule.value) return
  
  // 应用一些基本的优化
  // 确保概率在合理范围内
  if (parsedRule.value.trigger?.probability > 0.8) {
    parsedRule.value.trigger.probability = 0.8
  }
  
  // 确保效果值在合理范围内
  parsedRule.value.effects?.forEach((effect: any) => {
    if (effect.type === 'fear_increase' && effect.value > 50) {
      effect.value = 50
    }
    if (effect.type === 'sanity_decrease' && Math.abs(effect.value) > 40) {
      effect.value = -40
    }
  })
}

function resetParser() {
  parsedRule.value = null
  ruleDescription.value = ''
}

function confirmCreate() {
  if (!parsedRule.value || !canCreate.value) return
  
  // 构建规则数据
  const ruleData = {
    name: parsedRule.value.rule_name,
    description: parsedRule.value.description,
    trigger: parsedRule.value.trigger,
    effects: parsedRule.value.effects,
    cooldown: parsedRule.value.cooldown || 0
  }
  
  emit('create', ruleData)
}

function getEffectTypeName(type: string) {
  const typeNames: Record<string, string> = {
    'fear_increase': '增加恐惧',
    'sanity_decrease': '降低理智',
    'instant_death': '立即死亡',
    'teleport': '传送',
    'continuous_damage': '持续伤害'
  }
  return typeNames[type] || type
}

// 预设示例
const examples = [
  "当NPC在午夜12点照镜子时，恐惧值增加50点",
  "如果NPC独自一人在走廊，每回合有30%概率听到诡异声音，理智下降20",
  "NPC拿起诅咒物品后，每回合损失10点生命值，持续5回合",
  "晚上10点后在地下室的NPC会被传送到随机房间"
]

// 可以添加一个方法来使用示例
function useExample(example: string) {
  ruleDescription.value = example
}
</script>

<style scoped>
.rule-ai-parser {
  padding: 16px;
}

:deep(.n-code) {
  font-size: 12px;
}

:deep(.n-ul) {
  margin: 8px 0;
  padding-left: 20px;
}

:deep(.n-list-item) {
  padding: 8px;
  background: rgba(0, 0, 0, 0.02);
  border-radius: 4px;
  margin-bottom: 8px;
}
</style>
