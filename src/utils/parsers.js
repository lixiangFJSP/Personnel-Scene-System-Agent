import * as XLSX from 'xlsx'

export async function parseFile(file) {
  const ext = file.name.split('.').pop().toLowerCase()
  if (['xlsx', 'xls'].includes(ext)) return parseExcel(file)
  if (ext === 'csv') return parseCSV(file)
  if (ext === 'json') return parseJSON(file)
  throw new Error('不支持的文件格式')
}

async function parseExcel(file) {
  const ab = await file.arrayBuffer()
  const wb = XLSX.read(ab, { type: 'array' })
  const sheets = {}
  for (const name of wb.SheetNames) {
    const ws = wb.Sheets[name]
    const raw = XLSX.utils.sheet_to_json(ws, { header: 1, defval: '' })
    sheets[name] = raw.filter(r => r.some(c => c !== ''))
  }
  return sheets
}

async function parseCSV(file) {
  const text = await file.text()
  const lines = text.split(/\r?\n/).filter(l => l.trim())
  const data = lines.map(l => l.split(',').map(c => c.trim().replace(/^"|"$/g, '')))
  return { [file.name]: data }
}

async function parseJSON(file) {
  const text = await file.text()
  return { data: JSON.parse(text) }
}

/* ---- 无感考勤 解析 ---- */
export function parseAttendanceData(sheets) {
  const records = []
  const summarySheet = sheets['考勤汇总表'] || sheets[Object.keys(sheets)[0]]
  if (!summarySheet || summarySheet.length < 3) return null
  const headers = summarySheet[2]
  for (let i = 3; i < summarySheet.length; i++) {
    const row = summarySheet[i]
    const obj = {}
    headers.forEach((h, idx) => { obj[h] = row[idx] ?? '' })
    if (obj['姓名']) records.push(obj)
  }
  return { rowCount: records.length, importTime: new Date().toLocaleString('zh-CN'), records, detail: sheets['考勤统计表'] ? parseSheetToRecords(sheets['考勤统计表']) : [] }
}

/* ---- 劳保穿戴 解析 ---- */
export function parseSafetyData(data) {
  const items = Array.isArray(data) ? data : data?.records ?? data?.data ?? []
  if (!items.length) return null
  return { rowCount: items.length, importTime: new Date().toLocaleString('zh-CN'), records: items }
}

/* ---- 作业组合 解析 ---- */
export function parseOperationsData(sheets) {
  const mopSheet = Object.values(sheets).find(s => s.length > 0) || []
  return { rowCount: mopSheet.length, importTime: new Date().toLocaleString('zh-CN'), records: parseSheetToRecords(mopSheet) }
}

function parseSheetToRecords(rows) {
  if (!rows || rows.length < 2) return []
  const headers = rows[0]
  const result = []
  for (let i = 1; i < rows.length; i++) {
    const obj = {}
    headers.forEach((h, idx) => { obj[h] = rows[i][idx] ?? '' })
    result.push(obj)
  }
  return result
}

/* ---- 工时统计 解析 ---- */
export function parseWorkhoursData(sheets) {
  const ws = sheets[Object.keys(sheets)[0]]
  const records = ws ? parseSheetToRecords(ws) : []
  return { rowCount: records.length, importTime: new Date().toLocaleString('zh-CN'), records }
}
