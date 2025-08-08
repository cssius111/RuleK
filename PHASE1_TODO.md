# Phase 1: 基础框架实施指南

## 🎯 当前任务：将默认Vite页面替换为RuleK游戏界面

### 📍 准确位置
```
项目根目录: /Users/chenpinle/Desktop/杂/pythonProject/RuleK/
前端目录: /Users/chenpinle/Desktop/杂/pythonProject/RuleK/web/frontend/
需要修改的文件: web/frontend/src/App.vue (当前是Vite默认模板)
```

### 🔄 需要替换/创建的文件（按顺序）

#### 1️⃣ 更新主入口文件 `web/frontend/src/main.ts`
```typescript
import { createApp } from 'vue'
import { createPinia } from 'pinia'
import router from './router'
import App from './App.vue'

// Naive UI的样式
import 'vfonts/Lato.css'
import 'vfonts/FiraCode.css'

// 全局样式
import './assets/styles/main.css'

const app = createApp(App)

app.use(createPinia())
app.use(router)

app.mount('#app')
```

#### 2️⃣ 替换 `web/frontend/src/App.vue`
```vue
<template>
  <n-config-provider :theme="darkTheme" :theme-overrides="themeOverrides">
    <n-message-provider>
      <n-notification-provider>
        <n-dialog-provider>
          <router-view />
        </n-dialog-provider>
      </n-notification-provider>
    </n-message-provider>
  </n-config-provider>
</template>

<script setup lang="ts">
import { darkTheme } from 'naive-ui'

const themeOverrides = {
  common: {
    primaryColor: '#8b5cf6',
    primaryColorHover: '#7c3aed',
    primaryColorPressed: '#6d28d9',
    primaryColorSuppl: '#a78bfa'
  }
}
</script>
```

#### 3️⃣ 创建路由配置 `web/frontend/src/router/index.ts`
```typescript
import { createRouter, createWebHistory } from 'vue-router'

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes: [
    {
      path: '/',
      name: 'Home',
      component: () => import('@/views/Home.vue')
    },
    {
      path: '/new-game',
      name: 'NewGame',
      component: () => import('@/views/NewGame.vue')
    },
    {
      path: '/load-game',
      name: 'LoadGame',
      component: () => import('@/views/LoadGame.vue')
    },
    {
      path: '/game/:gameId/dashboard',
      name: 'GameDashboard',
      component: () => import('@/views/GameDashboard.vue')
    }
  ]
})

export default router
```

#### 4️⃣ 创建首页 `web/frontend/src/views/Home.vue`
```vue
<template>
  <div class="home-container">
    <div class="content">
      <h1 class="title">RuleK</h1>
      <p class="subtitle">规则怪谈管理者</p>
      
      <n-space vertical size="large" class="buttons">
        <n-button 
          type="primary" 
          size="large"
          @click="router.push('/new-game')"
        >
          开始新游戏
        </n-button>
        
        <n-button 
          size="large"
          @click="router.push('/load-game')"
        >
          加载存档
        </n-button>
        
        <n-button 
          size="large"
          @click="showHelp"
        >
          帮助说明
        </n-button>
      </n-space>
    </div>
  </div>
</template>

<script setup lang="ts">
import { useRouter } from 'vue-router'
import { useMessage } from 'naive-ui'
import { NButton, NSpace } from 'naive-ui'

const router = useRouter()
const message = useMessage()

function showHelp() {
  message.info('帮助功能开发中...')
}
</script>

<style scoped>
.home-container {
  min-height: 100vh;
  display: flex;
  align-items: center;
  justify-content: center;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
}

.content {
  text-align: center;
}

.title {
  font-size: 4rem;
  font-weight: bold;
  color: white;
  margin-bottom: 1rem;
}

.subtitle {
  font-size: 1.5rem;
  color: rgba(255, 255, 255, 0.9);
  margin-bottom: 3rem;
}

.buttons {
  margin-top: 2rem;
}
</style>
```

#### 5️⃣ 创建全局样式 `web/frontend/src/assets/styles/main.css`
```css
@import 'tailwindcss/base';
@import 'tailwindcss/components';
@import 'tailwindcss/utilities';

body {
  margin: 0;
  font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
}

#app {
  min-height: 100vh;
}
```

#### 6️⃣ 创建基础Store `web/frontend/src/stores/game.ts`
```typescript
import { defineStore } from 'pinia'
import { ref } from 'vue'

export const useGameStore = defineStore('game', () => {
  const gameId = ref<string | null>(null)
  const currentTurn = ref(0)
  const fearPoints = ref(1000)
  
  function createGame(config: any) {
    // TODO: 调用API创建游戏
    gameId.value = 'test-game-id'
    currentTurn.value = 0
    fearPoints.value = config.fearPoints || 1000
  }
  
  return {
    gameId,
    currentTurn,
    fearPoints,
    createGame
  }
})
```

### 📦 需要安装的额外依赖（如果缺失）

```bash
cd web/frontend
npm install naive-ui vfonts
```

### ✅ 验证成功的标志

1. 访问 http://localhost:5173 应该看到：
   - RuleK 标题
   - 规则怪谈管理者 副标题
   - 三个按钮：开始新游戏、加载存档、帮助说明

2. 点击按钮应该：
   - 开始新游戏 → 跳转到 /new-game（会显示404）
   - 加载存档 → 跳转到 /load-game（会显示404）
   - 帮助说明 → 显示"帮助功能开发中..."消息

### 🧪 测试命令

```bash
cd web/frontend
npm run dev  # 启动开发服务器
# 浏览器访问 http://localhost:5173 查看效果
```

### 📝 Phase 1 完成标准

- [ ] 默认Vite页面被替换
- [ ] 显示RuleK首页
- [ ] 路由系统工作
- [ ] Pinia状态管理就绪
- [ ] Naive UI集成成功
- [ ] 按钮可点击并导航

### 🚨 常见问题

1. **找不到模块错误**
   ```bash
   npm install naive-ui vfonts
   ```

2. **样式不生效**
   - 确保Tailwind配置正确
   - 检查main.css是否被引入

3. **路由不工作**
   - 确保vue-router已安装
   - 检查main.ts中是否use(router)

---

**给下一个AI的一句话**：
"请按照上面的文件列表，依次创建/替换这6个文件，将Vite默认页面改为RuleK游戏首页。"
