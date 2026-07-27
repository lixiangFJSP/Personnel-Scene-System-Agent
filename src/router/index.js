import { createRouter, createWebHistory } from 'vue-router'
import Home from '@/views/Home.vue'
import Import from '@/views/Import.vue'

const routes = [
  { path: '/', name: 'Home', component: Home },
  { path: '/import', name: 'Import', component: Import },
]

const router = createRouter({
  history: createWebHistory(),
  routes,
})

export default router
