<template>
  <div class="home">
    <div class="hero">
      <div class="hero-content">
        <h1>人员场景数据分析系统</h1>
        <p>数据驱动决策 — 覆盖考勤合规、安全穿戴、作业效率、工时成本四大场景</p>
      </div>
      <div class="hero-stats">
        <div class="stat-item">
          <span class="stat-num">{{ modules.length }}</span>
          <span class="stat-label">分析模块</span>
        </div>
        <div class="stat-item">
          <span class="stat-num">{{ dataModuleCount }}</span>
          <span class="stat-label">已导入数据</span>
        </div>
      </div>
    </div>

    <div class="toolbar">
      <router-link to="/import" class="tool-btn">
        <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4"/><polyline points="7 10 12 15 17 10"/><line x1="12" y1="15" x2="12" y2="3"/></svg>
        导入数据文件
      </router-link>
    </div>

    <div class="module-grid">
      <ModuleCard v-for="(mod, idx) in modules" :key="idx" :module="mod" />
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import ModuleCard from '@/components/ModuleCard.vue'
import { getAllModulesStatus } from '@/utils/dataStore.js'

const dataModuleCount = ref(0)

onMounted(() => {
  const stats = getAllModulesStatus()
  dataModuleCount.value = stats.filter(s => s.hasData).length
})

const modules = [
  {
    title: '无感考勤',
    desc: '全厂考勤数据汇总、趋势分析、异常诊断与改善建议。覆盖考勤趋势、出勤规律及异常率分析。',
    link: '无感考勤看板文件/无感考勤模块数据月度下钻分析.html',
    icon: '<svg width="26" height="26" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><circle cx="12" cy="12" r="10"/><polyline points="12 6 12 12 16 14"/></svg>',
    iconBg: '#eff6ff',
    iconColor: '#2563eb',
    btnBg: '#eff6ff',
    btnColor: '#2563eb',
  },
  {
    title: '劳保穿戴',
    desc: '劳保穿戴违规事件分析报表，识别高频违规类型、部门分布、趋势变化及重点人员追踪。',
    link: '劳保穿戴看板文件/劳保穿戴违规事件分析报表.html',
    icon: '<svg width="26" height="26" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M22 12h-4l-3 9L9 3l-3 9H2"/></svg>',
    iconBg: '#fef3c7',
    iconColor: '#d97706',
    btnBg: '#fef3c7',
    btnColor: '#d97706',
  },
  {
    title: '作业组合',
    desc: '以叶片流水号为索引的作业组合周期对比甘特图，分析 MOP 工序级与 ST 工步级周期差异。',
    link: '作业组合看板文件/作业组合周期对比甘特图.html',
    icon: '<svg width="26" height="26" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><rect x="3" y="3" width="18" height="18" rx="2" ry="2"/><line x1="3" y1="9" x2="21" y2="9"/><line x1="9" y1="21" x2="9" y2="9"/></svg>',
    iconBg: '#f0fdf4',
    iconColor: '#16a34a',
    btnBg: '#f0fdf4',
    btnColor: '#16a34a',
  },
  {
    title: '工时统计',
    desc: '壳体成型工段工时统计分析，包含单支节拍趋势、分工步工时对比、MES与场景系统人工时分析。',
    link: '工时统计看板文件/工时统计分析看板.html',
    icon: '<svg width="26" height="26" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"/><polyline points="14 2 14 8 20 8"/><line x1="16" y1="13" x2="8" y2="13"/><line x1="16" y1="17" x2="8" y2="17"/></svg>',
    iconBg: '#f5f3ff',
    iconColor: '#7c3aed',
    btnBg: '#f5f3ff',
    btnColor: '#7c3aed',
  },
]
</script>

<style scoped>
.hero{
  background: linear-gradient(135deg,#1e3a5f 0%,#244f8a 50%,#2563eb 100%);
  color:#fff;border-radius:12px;padding:36px 32px;
  margin-bottom:20px;box-shadow:0 8px 24px rgba(37,99,235,.25);
  display:flex;justify-content:space-between;align-items:flex-end;
  flex-wrap:wrap;gap:20px;
}
.hero-content{flex:1;min-width:240px}
.hero h1{font-size:26px;font-weight:700;letter-spacing:1px}
.hero p{margin-top:8px;font-size:14px;opacity:.85;line-height:1.6}
.hero-stats{display:flex;gap:24px}
.stat-item{text-align:center}
.stat-num{display:block;font-size:32px;font-weight:700}
.stat-label{font-size:12px;opacity:.75;margin-top:2px}

.toolbar{display:flex;gap:12px;margin-bottom:20px}
.tool-btn{
  display:inline-flex;align-items:center;gap:8px;
  padding:10px 22px;border-radius:10px;
  background:#fff;border:1px solid #e2e8f0;
  color:#2563eb;text-decoration:none;
  font-size:14px;font-weight:600;
  transition:box-shadow .2s,transform .15s;
}
.tool-btn:hover{
  box-shadow:0 4px 12px rgba(37,99,235,.15);
  transform:translateY(-1px);
}

.module-grid{display:grid;grid-template-columns:1fr 1fr;gap:20px}
@media(max-width:720px){
  .hero{padding:24px 20px;flex-direction:column;align-items:flex-start}
  .hero h1{font-size:22px}
  .hero-stats{flex-direction:row;width:100%;justify-content:flex-start;gap:32px}
  .stat-num{font-size:26px}
  .module-grid{grid-template-columns:1fr}
}
</style>
