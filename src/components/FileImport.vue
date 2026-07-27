<template>
  <div class="import-container">
    <div class="dropzone" :class="{ 'dropzone-active': dragging }"
         @dragenter.prevent="dragging=true"
         @dragover.prevent="dragging=true"
         @dragleave.prevent="dragging=false"
         @drop.prevent="handleDrop">
      <div class="drop-icon">
        <svg width="40" height="40" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"><path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4"/><polyline points="7 10 12 15 17 10"/><line x1="12" y1="15" x2="12" y2="3"/></svg>
      </div>
      <p class="drop-text">{{ importing ? '正在处理...' : '拖拽文件到此处，或点击选择文件' }}</p>
      <p class="drop-hint">支持 .xlsx .xls .csv .json 格式</p>
      <input ref="fileInput" type="file" accept=".xlsx,.xls,.csv,.json" multiple
             @change="handleFiles" style="display:none">
      <button class="select-btn" @click="fileInput.click()" :disabled="importing">选择文件</button>
    </div>

    <div v-if="imported.length" class="result-area">
      <h3>已导入数据（{{ imported.length }} 项）</h3>
      <div v-for="(item, idx) in imported" :key="idx" class="data-item">
        <div class="data-header">
          <strong>{{ item.name }}</strong>
          <span class="data-meta">{{ item.rows }} 行 × {{ item.cols }} 列 · {{ item.size }}</span>
          <button class="del-btn" @click="removeItem(idx)" title="删除">✕</button>
        </div>
        <div class="data-preview">
          <table v-if="item.preview.length">
            <thead><tr><th v-for="(h,hi) in item.preview[0]" :key="hi">{{ h }}</th></tr></thead>
            <tbody>
              <tr v-for="(row, ri) in item.preview.slice(1, 6)" :key="ri">
                <td v-for="(cell, ci) in row" :key="ci">{{ cell }}</td>
              </tr>
            </tbody>
          </table>
          <p v-else class="empty-preview">无预览数据</p>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import * as XLSX from 'xlsx'

const dragging = ref(false)
const importing = ref(false)
const imported = ref([])
const fileInput = ref(null)

function formatSize(bytes) {
  if (bytes < 1024) return bytes + ' B'
  if (bytes < 1048576) return (bytes / 1024).toFixed(1) + ' KB'
  return (bytes / 1048576).toFixed(1) + ' MB'
}

async function parseExcel(file) {
  const ab = await file.arrayBuffer()
  const wb = XLSX.read(ab, { type: 'array' })
  const ws = wb.Sheets[wb.SheetNames[0]]
  const raw = XLSX.utils.sheet_to_json(ws, { header: 1, defval: '' })
  const data = raw.filter(r => r.some(c => c !== ''))
  return data
}

async function parseCSV(file) {
  const text = await file.text()
  const lines = text.split(/\r?\n/).filter(l => l.trim())
  const data = lines.map(l => l.split(',').map(c => c.trim().replace(/^"|"$/g, '')))
  return data
}

async function parseJSON(file) {
  const text = await file.text()
  const obj = JSON.parse(text)
  if (Array.isArray(obj) && obj.length && typeof obj[0] === 'object') {
    const headers = Object.keys(obj[0])
    return [headers, ...obj.map(row => headers.map(h => row[h] ?? ''))]
  }
  return [['key', 'value'], ...Object.entries(obj)]
}

async function processFiles(files) {
  importing.value = true
  for (const file of files) {
    try {
      let data = []
      const ext = file.name.split('.').pop().toLowerCase()
      if (['xlsx', 'xls'].includes(ext)) data = await parseExcel(file)
      else if (ext === 'csv') data = await parseCSV(file)
      else if (ext === 'json') data = await parseJSON(file)
      else continue

      if (!data.length) continue

      const headers = data[0] || []
      imported.value.push({
        name: file.name,
        rows: data.length - 1,
        cols: headers.length,
        size: formatSize(file.size),
        preview: data,
        raw: data,
      })
    } catch (e) {
      console.error('Parse error:', file.name, e)
    }
  }
  importing.value = false
}

function handleFiles(e) {
  processFiles(e.target.files)
  e.target.value = ''
}

function handleDrop(e) {
  dragging.value = false
  processFiles(e.dataTransfer.files)
}

function removeItem(idx) {
  imported.value.splice(idx, 1)
}
</script>

<style scoped>
.dropzone{
  border:2px dashed #cbd5e1;border-radius:14px;
  padding:48px 24px;text-align:center;
  background:#fafbfc;transition:all .2s;cursor:pointer;
}
.dropzone-active{
  border-color:#2563eb;background:#eff6ff;
}
.drop-icon{color:#94a3b8;margin-bottom:12px}
.dropzone-active .drop-icon{color:#2563eb}
.drop-text{font-size:15px;font-weight:600;color:#475569;margin-bottom:4px}
.drop-hint{font-size:13px;color:#94a3b8;margin-bottom:16px}
.select-btn{
  padding:10px 28px;border:none;border-radius:10px;
  background:#2563eb;color:#fff;font-size:14px;font-weight:600;
  cursor:pointer;transition:background .15s;
}
.select-btn:hover{background:#1d4ed8}
.select-btn:disabled{background:#93c5fd;cursor:not-allowed}
.result-area{margin-top:28px}
.result-area h3{font-size:17px;font-weight:700;margin-bottom:14px}
.data-item{
  background:#fff;border:1px solid #e2e8f0;border-radius:10px;
  margin-bottom:14px;overflow:hidden;
}
.data-header{
  display:flex;align-items:center;gap:12px;
  padding:12px 16px;background:#f8fafc;
  border-bottom:1px solid #e2e8f0;
}
.data-header strong{font-size:14px;flex:1;overflow:hidden;text-overflow:ellipsis;white-space:nowrap}
.data-meta{font-size:12px;color:#94a3b8;white-space:nowrap}
.del-btn{
  width:24px;height:24px;border:none;border-radius:6px;
  background:transparent;color:#94a3b8;cursor:pointer;
  font-size:14px;display:flex;align-items:center;justify-content:center;
}
.del-btn:hover{background:#fef2f2;color:#dc2626}
.data-preview{overflow-x:auto;padding:12px 16px}
.data-preview table{width:100%;border-collapse:collapse;font-size:12px}
.data-preview th,.data-preview td{
  border:1px solid #e2e8f0;padding:5px 8px;text-align:left;white-space:nowrap;
}
.data-preview th{background:#f8fafc;font-weight:600;color:#475569}
.empty-preview{color:#94a3b8;font-size:13px;text-align:center;padding:12px}
</style>
