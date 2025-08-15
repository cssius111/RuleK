<template>
  <div class="rule-template-selector">
    <n-card title="选择规则模板" :bordered="false">
      <n-space vertical>
        <n-input
          v-model:value="searchText"
          placeholder="搜索规则模板..."
          clearable
        >
          <template #prefix>
            <n-icon :component="Search" />
          </template>
        </n-input>
        
        <n-tabs v-model:value="selectedCategory">
          <n-tab-pane name="all" tab="全部" />
          <n-tab-pane name="时间触发" tab="时间触发" />
          <n-tab-pane name="地点触发" tab="地点触发" />
          <n-tab-pane name="条件触发" tab="条件触发" />
          <n-tab-pane name="物品触发" tab="物品触发" />
        </n-tabs>
        
        <div class="template-grid">
          <n-card
            v-for="template in filteredTemplates"
            :key="template.id"
            :title="template.name"
            hoverable
            :class="{ selected: selectedTemplate?.id === template.id }"
            @click="selectTemplate(template)"
          >
            <template #header-extra>
              <n-tag :type="getDifficultyType(template.difficulty)">
                {{ template.difficulty }}
              </n-tag>
            </template>
            
            <n-space vertical>
              <n-text>{{ template.description }}</n-text>
              <n-space>
                <n-tag type="warning">
                  <n-icon :component="Coins" />
                  {{ template.cost }} 恐惧点
                </n-tag>
                <n-tag type="info">
                  冷却: {{ template.cooldown }}回合
                </n-tag>
              </n-space>
            </n-space>
          </n-card>
        </div>
        
        <div v-if="selectedTemplate" class="template-preview">
          <n-divider />
          <h4>预览: {{ selectedTemplate.name }}</h4>
          <n-descriptions :column="2">
            <n-descriptions-item label="类型">
              {{ selectedTemplate.trigger.type }}
            </n-descriptions-item>
            <n-descriptions-item label="触发概率">
              {{ (selectedTemplate.trigger.probability * 100).toFixed(0) }}%
            </n-descriptions-item>
            <n-descriptions-item label="效果数量">
              {{ selectedTemplate.effects.length }}
            </n-descriptions-item>
            <n-descriptions-item label="成本">
              {{ selectedTemplate.cost }} 恐惧点
            </n-descriptions-item>
          </n-descriptions>
        </div>
      </n-space>
      
      <template #footer>
        <n-space justify="end">
          <n-button @click="$emit('cancel')">取消</n-button>
          <n-button
            type="primary"
            :disabled="!selectedTemplate || !canAfford"
            @click="confirmSelection"
          >
            创建规则 ({{ selectedTemplate?.cost || 0 }} 恐惧点)
          </n-button>
        </n-space>
      </template>
    </n-card>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { NCard, NSpace, NInput, NIcon, NTabs, NTabPane, NTag, NDivider, NDescriptions, NDescriptionsItem, NButton } from 'naive-ui'
import { Search, Coins } from '@vicons/tabler'
import { useGameStore } from '@/stores/game'
import { useRulesStore } from '@/stores/rules'

const emit = defineEmits(['select', 'cancel'])

const gameStore = useGameStore()
const rulesStore = useRulesStore()

const searchText = ref('')
const selectedCategory = ref('all')
const selectedTemplate = ref(null)

const filteredTemplates = computed(() => {
  let templates = rulesStore.templates
  
  // 按类别筛选
  if (selectedCategory.value !== 'all') {
    templates = templates.filter(t => t.category === selectedCategory.value)
  }
  
  // 按搜索文本筛选
  if (searchText.value) {
    const search = searchText.value.toLowerCase()
    templates = templates.filter(t => 
      t.name.toLowerCase().includes(search) ||
      t.description.toLowerCase().includes(search)
    )
  }
  
  return templates
})

const canAfford = computed(() => {
  if (!selectedTemplate.value) return false
  return gameStore.fearPoints >= selectedTemplate.value.cost
})

function getDifficultyType(difficulty: string) {
  switch (difficulty) {
    case 'easy': return 'success'
    case 'normal': return 'warning'
    case 'hard': return 'error'
    default: return 'default'
  }
}

function selectTemplate(template: any) {
  selectedTemplate.value = template
}

function confirmSelection() {
  if (selectedTemplate.value && canAfford.value) {
    emit('select', selectedTemplate.value)
  }
}

onMounted(() => {
  rulesStore.loadTemplates()
})
</script>

<style scoped>
.template-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(300px, 1fr));
  gap: 16px;
  margin: 16px 0;
}

.template-grid .n-card {
  cursor: pointer;
  transition: all 0.3s;
}

.template-grid .n-card:hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
}

.template-grid .n-card.selected {
  border-color: var(--n-color-primary);
  background: var(--n-color-primary-lighter);
}

.template-preview {
  padding: 16px;
  background: var(--n-color-modal);
  border-radius: 8px;
}
</style>
