const STORAGE_KEY = 'analytics_uploaded_data'

export function loadModuleData(moduleName) {
  try {
    const raw = localStorage.getItem(`${STORAGE_KEY}_${moduleName}`)
    return raw ? JSON.parse(raw) : null
  } catch { return null }
}

export function saveModuleData(moduleName, data) {
  try {
    localStorage.setItem(`${STORAGE_KEY}_${moduleName}`, JSON.stringify(data))
    return true
  } catch { return false }
}

export function clearModuleData(moduleName) {
  localStorage.removeItem(`${STORAGE_KEY}_${moduleName}`)
}

export function getAllModulesStatus() {
  const modules = ['attendance', 'safety', 'operations', 'workhours']
  const labels = { attendance: '无感考勤', safety: '劳保穿戴', operations: '作业组合', workhours: '工时统计' }
  return modules.map(k => {
    const data = loadModuleData(k)
    return { key: k, label: labels[k], hasData: !!data, rows: data?.rowCount ?? 0, time: data?.importTime ?? '' }
  })
}
