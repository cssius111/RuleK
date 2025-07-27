import { createApp } from 'vue'
import { createPinia } from 'pinia'
import App from './App.vue'
import router from './router'

// 全局样式
import './styles/main.scss'

// 创建应用实例
const app = createApp(App)

// 使用 Pinia 状态管理
app.use(createPinia())

// 使用路由
app.use(router)

// 挂载应用
app.mount('#app')
