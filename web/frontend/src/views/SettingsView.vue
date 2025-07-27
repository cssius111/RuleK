<template>
  <div class="settings-view">
    <n-card title="游戏设置">
      <n-form :model="settings" label-placement="left" label-width="120px">
        <n-form-item label="音效">
          <n-switch v-model:value="settings.soundEnabled" />
        </n-form-item>
        
        <n-form-item label="音量">
          <n-slider 
            v-model:value="settings.volume"
            :min="0"
            :max="100"
            :disabled="!settings.soundEnabled"
          />
        </n-form-item>
        
        <n-form-item label="动画效果">
          <n-switch v-model:value="settings.animationsEnabled" />
        </n-form-item>
        
        <n-form-item label="自动保存">
          <n-switch v-model:value="settings.autoSave" />
        </n-form-item>
        
        <n-form-item label="自动保存间隔">
          <n-select 
            v-model:value="settings.autoSaveInterval"
            :options="autoSaveOptions"
            :disabled="!settings.autoSave"
          />
        </n-form-item>
        
        <n-form-item label="语言">
          <n-select 
            v-model:value="settings.language"
            :options="languageOptions"
          />
        </n-form-item>
      </n-form>
      
      <template #footer>
        <n-space justify="end">
          <n-button @click="handleReset">重置</n-button>
          <n-button type="primary" @click="handleSave">保存设置</n-button>
        </n-space>
      </template>
    </n-card>
    
    <n-card title="关于" style="margin-top: 2rem;">
      <n-descriptions :column="1">
        <n-descriptions-item label="版本">
          0.3.0
        </n-descriptions-item>
        <n-descriptions-item label="开发者">
          RuleK Team
        </n-descriptions-item>
        <n-descriptions-item label="开源协议">
          MIT License
        </n-descriptions-item>
        <n-descriptions-item label="GitHub">
          <n-button text tag="a" href="https://github.com/yourusername/rulek" target="_blank">
            查看源码
          </n-button>
        </n-descriptions-item>
      </n-descriptions>
    </n-card>
  </div>
</template>

<script setup lang="ts">
import { reactive } from 'vue'
import { useRouter } from 'vue-router'
import { NCard, NForm, NFormItem, NSwitch, NSlider, NSelect, NButton, NSpace, NDescriptions, NDescriptionsItem, useMessage } from 'naive-ui'

const router = useRouter()
const message = useMessage()

// 设置数据
const settings = reactive({
  soundEnabled: true,
  volume: 50,
  animationsEnabled: true,
  autoSave: true,
  autoSaveInterval: 5,
  language: 'zh-CN'
})

// 选项
const autoSaveOptions = [
  { label: '每回合', value: 1 },
  { label: '每3回合', value: 3 },
  { label: '每5回合', value: 5 },
  { label: '每10回合', value: 10 }
]

const languageOptions = [
  { label: '简体中文', value: 'zh-CN' },
  { label: 'English', value: 'en-US' }
]

// 保存设置
function handleSave() {
  // TODO: 实际保存到本地存储或服务器
  localStorage.setItem('gameSettings', JSON.stringify(settings))
  message.success('设置已保存')
}

// 重置设置
function handleReset() {
  Object.assign(settings, {
    soundEnabled: true,
    volume: 50,
    animationsEnabled: true,
    autoSave: true,
    autoSaveInterval: 5,
    language: 'zh-CN'
  })
  message.info('设置已重置')
}

// 加载保存的设置
function loadSettings() {
  const saved = localStorage.getItem('gameSettings')
  if (saved) {
    try {
      Object.assign(settings, JSON.parse(saved))
    } catch (e) {
      console.error('Failed to load settings:', e)
    }
  }
}

// 初始化
loadSettings()
</script>

<style lang="scss" scoped>
.settings-view {
  max-width: 800px;
  margin: 0 auto;
  padding: 2rem;
}
</style>
