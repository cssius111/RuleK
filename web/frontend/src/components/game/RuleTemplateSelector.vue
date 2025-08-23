<template>
  <div class="rule-template-selector">
    <n-grid :cols="1" :y-gap="16">
      <!-- 搜索和筛选 -->
      <n-gi>
        <n-space>
          <n-input
            v-model:value="searchText"
            placeholder="搜索规则模板..."
            clearable
            style="width: 200px"
          >
            <template #prefix>
              <n-icon :component="Search" />
            </template>
          </n-input>
          
          <n-select
            v-model:value="selectedCategory"
            placeholder="选择类别"
            :options="categoryOptions"
            clearable
            style="width: 150px"
          />
          
          <n-select
            v-model:value="selectedDifficulty"
            placeholder="选择难度"
            :options="difficultyOptions"
            clearable
            style="width: 120px"
          />
        </n-space>
      </n-gi>
      
      <!-- 模板列表 -->
      <n-gi>
        <n-scrollbar style="max-height: 400px">
          <n-grid :cols="2" :x-gap="12" :y-gap="12">
            <n-gi v-for="template in filteredTemplates" :key="template.id">
              <n-card
                :title="template.name"
                hoverable
                :class="{ 'selected': selectedTemplate?.id === template.id }"
                @click="selectTemplate(template)"
              >
                <template #header-extra>
                  <n-tag :type="getDifficultyType(template.difficulty)" size="small">
                    {{ template.difficulty }}
                  </n-tag>
                </template>
                
                <n-space vertical>
                  <n-text depth="3">{{ template.description }}</n-text>
                  
                  <n-space>
                    <n-tag type="info" size="small">
                      {{ template.category }}
                    </n-tag>
                    <n-tag type="warning" size="small">
                      成本: {{ template.cost }}
                    </n-tag>
                  </n-space>
                  
                  <!-- 效果预览 -->
                  <div v-if="selectedTemplate?.id === template.id" class="effect-preview">
                    <n-divider />
                    <n-text type="success">触发条件:</n-text>
                    <n-ul>
                      <n-li>类型: {{ template.trigger.type }}</n-li>
                      <n-li>概率: {{ (template.trigger.probability * 100).toFixed(0) }}%</n-li>
                      <n-li v-if="template.cooldown">冷却: {{ template.cooldown }}回合</n-li>
                    </n-ul>
                    
                    <n-text type="success">效果:</n-text>
                    <n-ul>
                      <n-li v-for="(effect, idx) in template.effects" :key="idx">
                        {{ getEffectDescription(effect) }}
                      </n-li>
                    </n-ul>
                  </div>
                </n-space>
              </n-card>
            </n-gi>
          </n-grid>
        </n-scrollbar>
      </n-gi>
      
      <!-- 底部按钮 -->
      <n-gi>
        <n-space justify="space-between" align="center">
          <div>
            <n-text v-if="selectedTemplate" type="warning">
              需要 {{ selectedTemplate.cost }} 恐惧点
            </n-text>
            <n-text v-if="!canAfford" type="error" style="margin-left: 16px">
              恐惧点不足！
            </n-text>
          </div>
          
          <n-space>
            <n-button @click="$emit('cancel')">取消</n-button>
            <n-button
              type="primary"
              :disabled="!selectedTemplate || !canAfford"
              @click="confirmSelection"
            >
              创建规则
            </n-button>
          </n-space>
        </n-space>
      </n-gi>
    </n-grid>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import {
  NGrid, NGi, NCard, NSpace, NText, NTag, NButton,
  NScrollbar, NInput, NSelect, NIcon, NDivider, NUl, NLi
} from 'naive-ui'
import { Search } from '@vicons/ionicons5'
import { useGameStore } from '@/stores/game'
import { useRulesStore } from '@/stores/rules'

const emit = defineEmits(['select', 'cancel'])

const gameStore = useGameStore()
const rulesStore = useRulesStore()

// 状态
const searchText = ref('')
const selectedCategory = ref<string | null>(null)
const selectedDifficulty = ref<string | null>(null)
const selectedTemplate = ref<any>(null)

// 选项
const categoryOptions = [
  { label: '时间触发', value: '时间触发' },
  { label: '地点触发', value: '地点触发' },
  { label: '条件触发', value: '条件触发' },
  { label: '物品触发', value: '物品触发' },
  { label: '随机触发', value: '随机触发' }
]

const difficultyOptions = [
  { label: '简单', value: 'easy' },
  { label: '普通', value: 'normal' },
  { label: '困难', value: 'hard' }
]

// 计算属性
const filteredTemplates = computed(() => {
  let templates = rulesStore.templates || []
  
  // 搜索过滤
  if (searchText.value) {
    const search = searchText.value.toLowerCase()
    templates = templates.filter(t => 
      t.name.toLowerCase().includes(search) ||
      t.description.toLowerCase().includes(search)
    )
  }
  
  // 类别过滤
  if (selectedCategory.value) {
    templates = templates.filter(t => t.category === selectedCategory.value)
  }
  
  // 难度过滤
  if (selectedDifficulty.value) {
    templates = templates.filter(t => t.difficulty === selectedDifficulty.value)
  }
  
  return templates
})

const canAfford = computed(() => {
  if (!selectedTemplate.value) return false
  return gameStore.gameState?.fear_points >= selectedTemplate.value.cost
})

// 方法
function selectTemplate(template: any) {
  selectedTemplate.value = template
}

function confirmSelection() {
  if (selectedTemplate.value && canAfford.value) {
    emit('select', selectedTemplate.value)
  }
}

function getDifficultyType(difficulty: string) {
  switch (difficulty) {
    case 'easy': return 'success'
    case 'normal': return 'warning'
    case 'hard': return 'error'
    default: return 'default'
  }
}

function getEffectDescription(effect: any) {
  switch (effect.type) {
    case 'fear_increase':
      return `恐惧值 +${effect.value} (${effect.target})`
    case 'sanity_decrease':
      return `理智值 -${Math.abs(effect.value)} (${effect.target})`
    case 'instant_death':
      return `立即死亡 (${effect.target})`
    case 'teleport':
      return `传送 (${effect.target})`
    case 'continuous_damage':
      return `持续伤害 ${effect.value}/回合 x ${effect.duration}回合`
    default:
      return `${effect.type} (${effect.target})`
  }
}

// 生命周期
onMounted(async () => {
  try {
    await rulesStore.loadTemplates()
  } catch (error) {
    console.error('Failed to load templates:', error)
  }
})
</script>

<style scoped>
.rule-template-selector {
  padding: 16px;
}

.n-card {
  cursor: pointer;
  transition: all 0.3s;
}

.n-card:hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
}

.n-card.selected {
  border-color: var(--n-color-primary);
  background-color: rgba(24, 160, 88, 0.05);
}

.effect-preview {
  margin-top: 12px;
  padding: 12px;
  background: rgba(0, 0, 0, 0.05);
  border-radius: 4px;
}

:deep(.n-ul) {
  margin: 8px 0;
  padding-left: 20px;
}
</style>
