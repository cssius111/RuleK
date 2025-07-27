import { createRouter, createWebHistory, RouteRecordRaw } from 'vue-router'
import HomePage from '@/views/HomePage.vue'
import GameView from '@/views/GameView.vue'
import SettingsView from '@/views/SettingsView.vue'

const routes: Array<RouteRecordRaw> = [
  {
    path: '/',
    name: 'home',
    component: HomePage,
    meta: {
      title: '规则怪谈管理者'
    }
  },
  {
    path: '/game/:gameId',
    name: 'game',
    component: GameView,
    meta: {
      title: '游戏进行中',
      requiresGame: true
    }
  },
  {
    path: '/settings',
    name: 'settings',
    component: SettingsView,
    meta: {
      title: '设置'
    }
  },
  {
    path: '/:pathMatch(.*)*',
    redirect: '/'
  }
]

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes
})

// 路由守卫
router.beforeEach((to, from, next) => {
  // 设置页面标题
  document.title = `${to.meta.title || '规则怪谈管理者'}`
  
  // 检查游戏状态
  if (to.meta.requiresGame) {
    // TODO: 检查是否有有效的游戏会话
    const hasGame = true // 临时设置为true
    if (!hasGame) {
      next({ name: 'home' })
      return
    }
  }
  
  next()
})

export default router
