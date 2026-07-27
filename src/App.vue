<template>
  <div id="app-root">
    <nav class="navbar">
      <div class="nav-inner">
        <router-link to="/" class="nav-brand">
          <svg width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M3 3h18v18H3z"/><path d="M3 9h18"/><path d="M9 21V9"/></svg>
          人员场景数据分析系统
        </router-link>
        <div class="nav-links">
          <router-link to="/" class="nav-link">首页</router-link>
          <router-link to="/import" class="nav-link">导入数据</router-link>
          <router-link to="/settings" class="nav-link">AI 配置</router-link>
        </div>
      </div>
    </nav>

    <!-- Breadcrumb bar for sub-pages -->
    <div v-if="showBreadcrumb" class="breadcrumb-bar">
      <div class="breadcrumb-inner">
        <router-link to="/" class="bc-home-btn" title="返回至主页">
          <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M3 9l9-7 9 7v11a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2z"/><polyline points="9 22 9 12 15 12 15 22"/></svg>
          返回至主页
        </router-link>
        <span class="bc-sep">›</span>
        <span class="bc-current">{{ breadcrumbTitle }}</span>
      </div>
    </div>

    <main class="main-content">
      <router-view />
    </main>
  </div>
</template>

<script setup>
import { computed } from 'vue'
import { useRoute } from 'vue-router'

const route = useRoute()

const showBreadcrumb = computed(() => route.path !== '/')

const breadcrumbTitle = computed(() => {
  const map = {
    '/import': '导入数据',
    '/settings': 'AI 配置',
  }
  if (map[route.path]) return map[route.path]
  if (route.path.startsWith('/import/')) {
    const labels = { attendance: '无感考勤', safety: '劳保穿戴', operations: '作业组合', workhours: '工时统计' }
    const mod = route.params.module || route.path.split('/').pop()
    return labels[mod] || mod
  }
  return ''
})
</script>

<style>
*{margin:0;padding:0;box-sizing:border-box}
body{
  font-family: 'Microsoft YaHei', -apple-system, 'Segoe UI', sans-serif;
  background: #f0f2f5;
  color: #1e293b;
  min-height: 100vh;
}
.navbar{
  background: linear-gradient(135deg,#1e3a5f 0%,#2c5282 50%,#2563eb 100%);
  color:#fff;
  box-shadow:0 2px 12px rgba(37,99,235,.2);
  position:sticky;top:0;z-index:100;
}
.nav-inner{
  max-width:1100px;margin:0 auto;
  display:flex;align-items:center;justify-content:space-between;
  padding:0 24px;height:56px;
}
.nav-brand{
  display:flex;align-items:center;gap:8px;
  color:#fff;text-decoration:none;
  font-size:17px;font-weight:700;letter-spacing:.5px;
}
.nav-links{display:flex;gap:6px}
.nav-link{
  color:rgba(255,255,255,.8);text-decoration:none;
  padding:6px 14px;border-radius:8px;
  font-size:14px;transition:all .15s;
}
.nav-link:hover,.nav-link.router-link-active{
  color:#fff;background:rgba(255,255,255,.15);
}

/* Breadcrumb */
.breadcrumb-bar{
  background:#fff;
  border-bottom:1px solid #e2e8f0;
}
.breadcrumb-inner{
  max-width:1100px;margin:0 auto;
  display:flex;align-items:center;gap:8px;
  padding:0 24px;height:44px;
  font-size:13px;
}
.bc-home-btn{
  display:inline-flex;align-items:center;gap:6px;
  color:#2563eb;text-decoration:none;font-weight:600;
  background:#eff6ff;border:1px solid #bfdbfe;
  padding:6px 14px;border-radius:8px;
  font-size:13px;
  transition:all .15s;
}
.bc-home-btn:hover{
  background:#2563eb;color:#fff;
  border-color:#2563eb;
}
.bc-sep{color:#cbd5e1;font-size:16px;font-weight:300}
.bc-current{color:#475569;font-weight:600}

.main-content{max-width:1100px;margin:0 auto;padding:28px 24px 40px}
@media(max-width:720px){
  .nav-inner{padding:0 16px}
  .nav-brand{font-size:15px}
  .main-content{padding:20px 16px 32px}
  .breadcrumb-inner{padding:0 16px}
}
</style>
