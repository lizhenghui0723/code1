import { createRouter, createWebHistory } from 'vue-router'

// 路由配置（可根据实际页面补充）
const routes = [
  // 示例：
  // { path: '/', component: () => import('./views/DashboardView.vue') }
]

const router = createRouter({
  history: createWebHistory(),
  routes
})

export default router 