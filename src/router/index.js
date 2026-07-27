import { createRouter, createWebHistory } from 'vue-router'
import Home from '@/views/Home.vue'
import ImportPage from '@/views/Import.vue'
import ModuleImportView from '@/views/ModuleImportView.vue'
import Settings from '@/views/Settings.vue'

const routes = [
  { path: '/', name: 'Home', component: Home },
  { path: '/import', name: 'Import', component: ImportPage },
  { path: '/import/:module', name: 'ModuleImport', component: ModuleImportView, props: true },
  { path: '/settings', name: 'Settings', component: Settings },
]

const router = createRouter({
  history: createWebHistory(),
  routes,
})

export default router
