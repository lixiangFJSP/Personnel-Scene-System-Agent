<template>
 <div class="import-page">
    <div class="page-header">
      <div class="header-row">
        <div class="header-text">
          <h2>数据导入与报表生成</h2>
          <p>选择模块上传数据文件，系统将自动解析并生成同格式的分析报表。</p>
        </div>
        <router-link to="/" class="btn-back-home">
          <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M3 9l9-7 9 7v11a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2z"/><polyline points="9 22 9 12 15 12 15 22"/></svg>
          返回主页
        </router-link>
      </div>
    </div>

    <div class="module-cards">
      <router-link v-for="(mod, idx) in modules" :key="idx"
        :to="'/import/' + mod.key" class="mod-card" :style="{ borderTopColor: mod.color }">
        <div class="mod-icon" :style="{ background: mod.bg }" v-html="mod.icon"></div>
        <div class="mod-info">
          <h3>{{ mod.label }}</h3>
          <p>{{ mod.shortDesc }}</p>
        </div>
        <div class="mod-status">
          <span v-if="mod.hasData" class="tag has-data">已导入 {{ mod.rows }} 行</span>
          <span v-else class="tag no-data">未导入</span>
        </div>
        <span class="mod-arrow">&rarr;</span>
      </router-link>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { getAllModulesStatus } from '@/utils/dataStore.js'

const modules = ref([])

const moduleMeta = {
  attendance: { label: '无感考勤', icon: '<svg width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><circle cx="12" cy="12" r="10"/><polyline points="12 6 12 12 16 14"/></svg>', color: '#2563eb', bg: '#eff6ff', shortDesc: '上传考勤数据，生成出勤趋势、异常诊断报表' },
  safety: { label: '劳保穿戴', icon: '<svg width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M22 12h-4l-3 9L9 3l-3 9H2"/></svg>', color: '#d97706', bg: '#fef3c7', shortDesc: '上传劳保违规数据，生成违规分布、趋势报表' },
  operations: { label: '作业组合', icon: '<svg width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><rect x="3" y="3" width="18" height="18" rx="2" ry="2"/><line x1="3" y1="9" x2="21" y2="9"/><line x1="9" y1="21" x2="9" y2="9"/></svg>', color: '#16a34a', bg: '#f0fdf4', shortDesc: '上传 MOP/ST 工时数据，生成周期对比报表' },
  workhours: { label: '工时统计', icon: '<svg width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"/><polyline points="14 2 14 8 20 8"/><line x1="16" y1="13" x2="8" y2="13"/><line x1="16" y1="17" x2="8" y2="17"/></svg>', color: '#7c3aed', bg: '#f5f3ff', shortDesc: '上传工时数据，生成工时节拍、分工步对比报表' },
}

function refresh() {
  const stats = getAllModulesStatus()
  modules.value = stats.map(s => ({
    key: s.key, ...moduleMeta[s.key],
    hasData: s.hasData, rows: s.rows,
  }))
}
onMounted(refresh)
</script>

<style scoped>
.page-header{margin-bottom:24px}
.header-row{display:flex;align-items:flex-start;justify-content:space-between;gap:16px}
.header-text{flex:1;min-width:0}
.page-header h2{font-size:20px;font-weight:700;margin-bottom:6px}
.page-header p{font-size:14px;color:#64748b;line-height:1.6}
.btn-back-home{
  display:inline-flex;align-items:center;gap:6px;
  padding:8px 16px;border-radius:8px;
  background:#fff;border:1px solid #e2e8f0;
  color:#475569;text-decoration:none;
  font-size:13px;font-weight:600;
  white-space:nowrap;
  transition:all .15s;
  flex-shrink:0;
}
.btn-back-home:hover{
  background:#f8fafc;border-color:#cbd5e1;color:#2563eb;
}
.module-cards{display:flex;flex-direction:column;gap:14px}
.mod-card{
  display:flex;align-items:center;gap:16px;
  background:#fff;border-radius:12px;padding:20px 22px;
  border:1px solid #e2e8f0;border-top:3px solid #2563eb;
  text-decoration:none;color:inherit;
  transition:transform .15s,box-shadow .15s;
}
.mod-card:hover{transform:translateY(-2px);box-shadow:0 6px 16px rgba(0,0,0,.08)}
.mod-icon{
  width:48px;height:48px;border-radius:10px;
  display:flex;align-items:center;justify-content:center;
  flex-shrink:0;
}
.mod-info{flex:1;min-width:0}
.mod-info h3{font-size:16px;font-weight:700;margin-bottom:3px}
.mod-info p{font-size:13px;color:#64748b;line-height:1.5}
.mod-status{flex-shrink:0}
.tag{font-size:12px;padding:3px 10px;border-radius:6px;font-weight:600}
.tag.has-data{background:#f0fdf4;color:#16a34a}
.tag.no-data{background:#f1f5f9;color:#94a3b8}
.mod-arrow{font-size:18px;color:#cbd5e1;flex-shrink:0}
</style>
