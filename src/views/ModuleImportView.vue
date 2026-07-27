<template>
  <div class="module-import">
    <div class="page-header">
      <div class="header-row">
        <div class="header-text">
          <h2>{{ moduleInfo.label }} — 数据导入与报表生成</h2>
          <p>{{ moduleInfo.desc }}</p>
        </div>
        <router-link to="/" class="btn-back-home">
          <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M3 9l9-7 9 7v11a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2z"/><polyline points="9 22 9 12 15 12 15 22"/></svg>
          返回主页
        </router-link>
      </div>
    </div>

    <!-- 数据导入区 -->
    <section class="section">
      <h3>📨 上传数据文件</h3>
      <div class="file-hint">{{ moduleInfo.fileHint }}</div>
      <div class="dropzone" :class="{ active: dragging }"
           @dragenter.prevent="dragging=true"
           @dragover.prevent="dragging=true"
           @dragleave.prevent="dragging=false"
           @drop.prevent="handleDrop">
        <svg width="36" height="36" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"><path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4"/><polyline points="7 10 12 15 17 10"/><line x1="12" y1="15" x2="12" y2="3"/></svg>
        <p>{{ importing ? '正在处理...' : '拖拽文件或点击选择' }}</p>
        <input ref="fileInput" type="file" :accept="moduleInfo.accept" @change="onFilePick" style="display:none">
        <button class="btn-select" @click="fileInput.click()" :disabled="importing">选择文件</button>
      </div>
    </section>

    <!-- 数据预览 -->
    <section v-if="parsedData" class="section">
      <h3>📋 数据预览（{{ totalRows }} 行）</h3>
      <div class="preview-box">
        <table v-if="previewRows.length"><thead><tr><th v-for="h in previewHeaders" :key="h">{{ h }}</th></tr></thead>
        <tbody><tr v-for="(row, ri) in previewRows" :key="ri"><td v-for="(c, ci) in row" :key="ci">{{ c }}</td></tr></tbody></table>
        <p v-else class="empty">暂无预览数据</p>
      </div>
      <div style="margin-top:12px;display:flex;gap:10px;flex-wrap:wrap">
        <button class="btn-primary" @click="generateReport">📊 生成报表</button>
        <button class="btn-primary btn-ai" @click="runAiAnalysis" :disabled="aiAnalyzing">
          {{ aiAnalyzing ? 'AI 分析中...' : '🤖 AI 智能分析' }}
        </button>
        <button class="btn-secondary" @click="clearData">🗑 清除数据</button>
      </div>
    </section>

    <!-- 报表区 -->
    <section v-if="showReport" class="section report-section">
      <h3>📱 自动生成报表</h3>
      <p class="report-time">生成时间：{{ reportTime }} | 数据行数：{{ totalRows }}</p>
      <div class="report-grid">
        <div v-for="(kpi, ki) in reportKpis" :key="'k'+ki" class="kpi-card" :style="{ borderLeftColor: kpi.color }">
          <div class="kpi-label">{{ kpi.label }}</div>
          <div class="kpi-value">{{ kpi.value }}<small>{{ kpi.unit }}</small></div>
        </div>
      </div>
      <div class="chart-grid">
        <div v-for="(chart, ci) in reportCharts" :key="'c'+ci" class="chart-box">
          <h4>{{ chart.title }}</h4>
          <canvas :ref="el => setChartRef(ci, el)"></canvas>
        </div>
      </div>
    </section>

    <!-- AI 分析区 -->
    <section v-if="aiResult || aiAnalyzing" class="section ai-section">
      <div class="ai-header">
        <span class="ai-badge">AI 分析</span>
        <h3>数据问题识别与改善建议</h3>
      </div>
      <div v-if="aiAnalyzing" class="ai-loading">
        <div class="spinner"></div>
        <p>AI 正在分析数据，识别问题并生成改善方案...</p>
      </div>
      <div v-else-if="aiError" class="ai-error">
        <p>{{ aiError }}</p>
        <button class="btn-secondary" @click="runAiAnalysis">重新分析</button>
      </div>
      <div v-else class="ai-result" v-html="renderedAiResult"></div>
    </section>
  </div>
</template>

<script setup>
import { ref, computed, onUnmounted } from 'vue'
import { nextTick } from 'vue'
import { useRoute } from 'vue-router'
import { parseFile, parseAttendanceData, parseSafetyData, parseOperationsData, parseWorkhoursData } from '@/utils/parsers.js'
import { loadModuleData, saveModuleData, clearModuleData } from '@/utils/dataStore.js'
import { Chart, registerables } from 'chart.js'
Chart.register(...registerables)

const route = useRoute()
const props = defineProps({ module: String })
const moduleName = computed(() => props.module || route.params.module)

const moduleConfig = {
  attendance: {
    label: '无感考勤', color: '#2563eb',
    desc: '上传考勤汇总表/统计表(Excel)，自动生成出勤趋势、异常诊断等分析报表。',
    fileHint: '推荐上传 考勤汇总表.xlsx（含姓名、部门、出勤天数、迟到次数等字段）',
    accept: '.xlsx,.xls,.csv',
    parseFn: (sheets) => parseAttendanceData(sheets),
    chartGen: (data) => generateAttendanceCharts(data),
    kpiGen: (data) => generateAttendanceKpis(data),
  },
  safety: {
    label: '劳保穿戴', color: '#d97706',
    desc: '上传劳保穿戴违规事件数据，自动生成违规类型分布、趋势分析报表。',
    fileHint: '推荐上传包含 部门、违规类型、发生日期 等字段的 Excel 或 JSON 文件',
    accept: '.xlsx,.xls,.csv,.json',
    parseFn: (raw) => parseSafetyData(raw),
    chartGen: (data) => generateSafetyCharts(data),
    kpiGen: (data) => generateSafetyKpis(data),
  },
  operations: {
    label: '作业组合', color: '#16a34a',
    desc: '上传 MOP/ST 工时周期明细数据，自动生成周期对比甘特图分析报表。',
    fileHint: '推荐上传 MOP工时周期明细.xlsx（工序级数据）和 ST工时周期明细.xlsx（工步级数据）',
    accept: '.xlsx,.xls',
    parseFn: (sheets) => parseOperationsData(sheets),
    chartGen: (data) => generateOperationsCharts(data),
    kpiGen: (data) => generateOperationsKpis(data),
  },
  workhours: {
    label: '工时统计', color: '#7c3aed',
    desc: '上传工时统计数据，自动生成工时节拍、分工步对比等分析报表。',
    fileHint: '推荐上传包含 工步、批次、工时 等字段的 Excel 或 JSON 文件',
    accept: '.xlsx,.xls,.csv,.json',
    parseFn: (sheets) => parseWorkhoursData(sheets),
    chartGen: (data) => generateWorkhoursCharts(data),
    kpiGen: (data) => generateWorkhoursKpis(data),
  },
}

const moduleInfo = computed(() => moduleConfig[moduleName.value] || moduleConfig.attendance)
const dragging = ref(false)
const importing = ref(false)
const parsedData = ref(null)
const rawParsed = ref(null)
const showReport = ref(false)
const reportTime = ref('')
const chartRefs = ref({})
const chartInstances = ref({})
const fileInput = ref(null)

// AI analysis state
const aiAnalyzing = ref(false)
const aiResult = ref('')
const aiError = ref('')

const renderedAiResult = computed(() => {
  if (!aiResult.value) return ''
  return aiResult.value
    .replace(/^### (.+)$/gm, '<h4 class="ai-h4">$1</h4>')
    .replace(/^## (.+)$/gm, '<h3 class="ai-h3">$1</h3>')
    .replace(/^- (.+)$/gm, '<li class="ai-li">$1</li>')
    .replace(/(<li class="ai-li">.*<\/li>\n?)+/g, '<ul class="ai-ul">$&</ul>')
    .replace(/\*\*(.+?)\*\*/g, '<strong>$1</strong>')
    .replace(/\n\n/g, '<br/><br/>')
})

// 加载已有数据
const saved = loadModuleData(moduleName.value)
if (saved) {
  parsedData.value = saved
  showReport.value = true
  reportTime.value = saved._reportTime || ''
  if (saved._aiResult) { aiResult.value = saved._aiResult }
}

function setChartRef(idx, el) { if (el) chartRefs.value[idx] = el }

const totalRows = computed(() => parsedData.value?.rowCount ?? 0)
const previewRows = computed(() => {
  const recs = parsedData.value?.records ?? []
  return recs.slice(0, 5).map(r => Object.values(r))
})
const previewHeaders = computed(() => {
  const recs = parsedData.value?.records ?? []
  return recs.length ? Object.keys(recs[0]) : []
})
const reportKpis = computed(() => parsedData.value?._kpis ?? [])
const reportCharts = computed(() => parsedData.value?._charts ?? [])

async function handleDrop(e) {
  dragging.value = false
  await processFiles(Array.from(e.dataTransfer.files))
}
async function onFilePick(e) {
  await processFiles(Array.from(e.target.files))
  e.target.value = ''
}

async function processFiles(files) {
  if (!files.length) return
  importing.value = true
  showReport.value = false
  aiResult.value = ''
  aiError.value = ''
  rawParsed.value = null
  try {
    let combined = null
    for (const file of files) {
      const result = await parseFile(file)
      combined = { ...combined, ...result }
    }
    const mod = moduleInfo.value
    rawParsed.value = combined
    const parsed = mod.parseFn(combined)
    if (parsed) parsedData.value = parsed
  } catch (e) { console.error(e) }
  importing.value = false
}

function generateReport() {
  if (!parsedData.value) return
  const mod = moduleInfo.value
  const kpis = mod.kpiGen(parsedData.value)
  const charts = mod.chartGen(parsedData.value)
  parsedData.value._kpis = kpis
  parsedData.value._charts = charts
  parsedData.value._reportTime = new Date().toLocaleString('zh-CN')
  reportTime.value = parsedData.value._reportTime
  showReport.value = true
  saveModuleData(moduleName.value, parsedData.value)
  nextTick(() => renderCharts())
}

async function runAiAnalysis() {
  if (!parsedData.value) return
  aiAnalyzing.value = true
  aiError.value = ''
  aiResult.value = ''
  try {
    const records = parsedData.value.records || []
    const resp = await fetch('/api/analyze', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ module: moduleName.value, data: records.slice(0, 200) }),
    })
    const data = await resp.json()
    if (data.success) {
      aiResult.value = data.analysis
      parsedData.value._aiResult = data.analysis
      saveModuleData(moduleName.value, parsedData.value)
    } else {
      aiError.value = data.error || '分析失败，请确认 AI 配置正确且后端服务已启动'
    }
  } catch (e) {
    aiError.value = '无法连接后端服务，请确认后端已启动（python backend/main.py）'
  }
  aiAnalyzing.value = false
}

function clearData() {
  clearModuleData(moduleName.value)
  parsedData.value = null
  showReport.value = false
  aiResult.value = ''
  aiError.value = ''
  rawParsed.value = null
  destroyCharts()
}

function destroyCharts() {
  Object.values(chartInstances.value).forEach(c => c?.destroy())
  chartInstances.value = {}
}

function renderCharts() {
  nextTick(() => {
    destroyCharts()
    const charts = parsedData.value?._charts ?? []
    charts.forEach((cfg, i) => {
      const el = chartRefs.value[i]
      if (!el) return
      const colors = ['#2563eb','#d97706','#16a34a','#dc2626','#7c3aed','#f59e0b','#64748b','#06b6d4']
      chartInstances.value[i] = new Chart(el, {
        type: cfg.type || 'bar',
        data: {
          labels: cfg.labels || [],
          datasets: (cfg.datasets || []).map((ds, di) => ({
            ...ds,
            backgroundColor: ds.backgroundColor || colors[di % colors.length],
            borderColor: ds.borderColor || colors[di % colors.length],
          })),
        },
        options: {
          responsive: true, maintainAspectRatio: false,
          plugins: { legend: { position: 'top', labels: { font: { family: 'Microsoft YaHei' } } } },
          scales: cfg.type === 'pie' || cfg.type === 'doughnut' ? {} : {
            y: { beginAtZero: true, ticks: { font: { family: 'Microsoft YaHei' } } },
            x: { ticks: { font: { family: 'Microsoft YaHei' }, maxRotation: 30 } },
          },
        },
      })
    })
  })
}

/* ---- KPI & Chart Generators ---- */
function generateAttendanceKpis(data) {
  const recs = data.records || []
  const lateCount = recs.filter(r => Number(r['迟到次数']) > 0).length
  const totalDays = recs.reduce((s, r) => s + (Number(r['出勤天数']) || 0), 0)
  return [
    { label: '总人数', value: recs.length, unit: '人', color: '#2563eb' },
    { label: '有迟到记录', value: lateCount, unit: '人', color: '#dc2626' },
    { label: '总出勤天数', value: totalDays.toLocaleString(), unit: '天', color: '#16a34a' },
    { label: '异常率', value: recs.length ? (lateCount / recs.length * 100).toFixed(1) : '0', unit: '%', color: '#d97706' },
  ]
}
function generateAttendanceCharts(data) {
  const recs = data.records || []
  const deptMap = {}
  recs.forEach(r => {
    const dept = r['部门'] || r['大部区'] || '未知'
    if (!deptMap[dept]) deptMap[dept] = { '迟到': 0, '早退': 0, '旷工': 0, '人数': 0 }
    deptMap[dept]['迟到'] += Number(r['迟到次数']) || 0
    deptMap[dept]['早退'] += Number(r['早退次数']) || 0
    deptMap[dept]['旷工'] += Number(r['旷工天数']) || 0
    deptMap[dept]['人数']++
  })
  const sorted = Object.entries(deptMap).sort((a, b) => (b[1]['迟到']+b[1]['早退']) - (a[1]['迟到']+a[1]['早退'])).slice(0, 12)
  return [
    { type: 'bar', title: '部门异常类型对比', labels: sorted.map(s => s[0]), datasets: [
      { label: '迟到', data: sorted.map(s => s[1]['迟到']) },
      { label: '早退', data: sorted.map(s => s[1]['早退']) },
    ]},
    { type: 'bar', title: '各部门人数分布', labels: sorted.map(s => s[0]), datasets: [{ label: '人数', data: sorted.map(s => s[1]['人数']) }] },
  ]
}

function generateSafetyKpis(data) {
  const recs = data.records || []
  const types = {}
  recs.forEach(r => { const t = r['违规类型'] || r['type'] || '其他'; types[t] = (types[t] || 0) + 1 })
  return [
    { label: '违规总数', value: recs.length, unit: '条', color: '#dc2626' },
    { label: '违规类型数', value: Object.keys(types).length, unit: '种', color: '#d97706' },
  ]
}
function generateSafetyCharts(data) {
  const recs = data.records || []
  const types = {}
  recs.forEach(r => { const t = r['违规类型'] || r['type'] || '其他'; types[t] = (types[t] || 0) + 1 })
  const entries = Object.entries(types).sort((a, b) => b[1] - a[1])
  return [
    { type: 'pie', title: '违规类型分布', labels: entries.map(e => e[0]), datasets: [{ data: entries.map(e => e[1]) }] },
    { type: 'bar', title: '违规类型统计', labels: entries.map(e => e[0]), datasets: [{ label: '次数', data: entries.map(e => e[1]) }] },
  ]
}

function generateOperationsKpis(data) {
  const mop = data.mop || []
  return [
    { label: 'MOP 工序数', value: mop.length, unit: '条', color: '#16a34a' },
    { label: 'ST 工步数', value: (data.st || []).length, unit: '条', color: '#2563eb' },
  ]
}
function generateOperationsCharts(data) {
  const mop = data.mop || []
  const byProc = {}
  mop.forEach(r => { const p = r['工序编码'] || r['工序'] || '未知'; byProc[p] = (byProc[p] || 0) + (Number(r['周期(分钟)']) || 0) })
  const entries = Object.entries(byProc).sort((a, b) => b[1] - a[1])
  return [
    { type: 'bar', title: '工序周期对比（分钟）', labels: entries.map(e => e[0]), datasets: [{ label: '周期', data: entries.map(e => e[1]) }] },
  ]
}

function generateWorkhoursKpis(data) {
  const recs = data.records || []
  const totalHours = recs.reduce((s, r) => s + (Number(r['工时']) || Number(r['工时_小时']) || 0), 0)
  return [
    { label: '记录数', value: recs.length, unit: '条', color: '#7c3aed' },
    { label: '总工时', value: totalHours.toFixed(1), unit: 'h', color: '#2563eb' },
  ]
}
function generateWorkhoursCharts(data) {
  const recs = data.records || []
  const stepMap = {}
  recs.forEach(r => { const s = r['工步'] || r['step'] || '未知'; stepMap[s] = (stepMap[s] || 0) + (Number(r['工时']) || Number(r['工时_小时']) || 0) })
  const entries = Object.entries(stepMap).sort((a, b) => b[1] - a[1])
  return [
    { type: 'bar', title: '分工步工时统计（h）', labels: entries.map(e => e[0]), datasets: [{ label: '工时', data: entries.map(e => e[1]) }] },
  ]
}

onUnmounted(() => destroyCharts())
</script>

<style scoped>
.module-import{max-width:960px;margin:0 auto}
.page-header{margin-bottom:24px}
.back-link{font-size:13px;color:#64748b;text-decoration:none;display:inline-block;margin-bottom:8px}
.back-link:hover{color:#2563eb}
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
.section{background:#fff;border-radius:12px;padding:24px;margin-bottom:20px;border:1px solid #e2e8f0}
.section h3{font-size:16px;font-weight:700;margin-bottom:14px}
.file-hint{font-size:12px;color:#94a3b8;margin-bottom:12px;padding:8px 12px;background:#f8fafc;border-radius:8px}
.dropzone{border:2px dashed #cbd5e1;border-radius:12px;padding:32px;text-align:center;cursor:pointer;transition:all .2s}
.dropzone.active{border-color:#2563eb;background:#eff6ff}
.dropzone svg{color:#94a3b8;margin-bottom:8px}
.dropzone.active svg{color:#2563eb}
.dropzone p{font-size:14px;color:#64748b;margin-bottom:12px}
.btn-select{padding:8px 24px;border:none;border-radius:8px;background:#2563eb;color:#fff;font-size:14px;font-weight:600;cursor:pointer}
.btn-select:disabled{background:#93c5fd;cursor:not-allowed}
.preview-box{overflow-x:auto;max-height:300px;overflow-y:auto}
.preview-box table{width:100%;border-collapse:collapse;font-size:12px}
.preview-box th,.preview-box td{border:1px solid #e2e8f0;padding:4px 8px;text-align:left;white-space:nowrap}
.preview-box th{background:#f8fafc;font-weight:600;color:#475569;position:sticky;top:0}
.empty{text-align:center;color:#94a3b8;padding:20px}
.btn-primary{padding:10px 28px;border:none;border-radius:10px;background:#2563eb;color:#fff;font-size:14px;font-weight:600;cursor:pointer}
.btn-primary:hover{background:#1d4ed8}
.btn-primary:disabled{background:#93c5fd;cursor:not-allowed}
.btn-ai{background:#7c3aed}
.btn-ai:hover{background:#6d28d9}
.btn-secondary{padding:10px 28px;border:1px solid #e2e8f0;border-radius:10px;background:#fff;color:#64748b;font-size:14px;cursor:pointer}
.btn-secondary:hover{background:#f8fafc;color:#475569}
.report-time{font-size:12px;color:#94a3b8;margin-bottom:16px}
.report-grid{display:grid;grid-template-columns:repeat(auto-fit,minmax(180px,1fr));gap:12px;margin-bottom:24px}
.kpi-card{background:#f8fafc;border-radius:10px;padding:16px 18px;border-left:4px solid #2563eb}
.kpi-label{font-size:12px;color:#64748b;margin-bottom:4px}
.kpi-value{font-size:24px;font-weight:700}
.kpi-value small{font-size:13px;font-weight:500;color:#64748b;margin-left:4px}
.chart-grid{display:grid;grid-template-columns:1fr 1fr;gap:16px}
.chart-box{background:#f8fafc;border-radius:10px;padding:16px;border:1px solid #e2e8f0}
.chart-box h4{font-size:14px;font-weight:600;margin-bottom:10px}
.chart-box canvas{max-height:280px;max-width:100%}
/* AI Analysis */
.ai-section{border-color:#7c3aed}
.ai-header{display:flex;align-items:center;gap:12px;margin-bottom:16px}
.ai-header h3{font-size:16px;font-weight:700;margin-bottom:0}
.ai-badge{
  display:inline-flex;align-items:center;
  background:linear-gradient(135deg,#7c3aed,#a855f7);
  color:#fff;font-size:12px;font-weight:700;
  padding:4px 14px;border-radius:20px;
  letter-spacing:.5px;
  white-space:nowrap;
}
.ai-loading{text-align:center;padding:40px 20px}
.spinner{width:40px;height:40px;border:3px solid #e2e8f0;border-top-color:#7c3aed;border-radius:50%;animation:spin .8s linear infinite;margin:0 auto 16px}
@keyframes spin{to{transform:rotate(360deg)}}
.ai-loading p{font-size:14px;color:#64748b}
.ai-error{text-align:center;padding:30px 20px;color:#dc2626;font-size:14px}
.ai-error .btn-secondary{margin-top:12px}
.ai-result{font-size:14px;line-height:1.8;color:#334155}
.ai-result :deep(.ai-h3){font-size:16px;font-weight:700;color:#1e293b;margin:20px 0 10px;padding-bottom:6px;border-bottom:1px solid #e2e8f0}
.ai-result :deep(.ai-h4){font-size:14px;font-weight:700;color:#475569;margin:14px 0 8px}
.ai-result :deep(.ai-ul){margin:8px 0 12px;padding-left:20px}
.ai-result :deep(.ai-li){margin-bottom:6px;line-height:1.7}
.ai-result :deep(strong){color:#7c3aed}
.ai-result :deep(code){background:#f1f5f9;padding:2px 6px;border-radius:4px;font-size:13px}
@media(max-width:720px){.chart-grid{grid-template-columns:1fr}}
</style>
