<template>
  <div class="settings-page">
    <div class="page-header">
      <div class="header-row">
        <div class="header-text">
          <h2>AI 大模型配置</h2>
          <p>配置国内大模型接口，用于对导入的数据进行智能分析与改善建议生成</p>
        </div>
        <router-link to="/" class="btn-back-home">
          <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M3 9l9-7 9 7v11a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2z"/><polyline points="9 22 9 12 15 12 15 22"/></svg>
          返回主页
        </router-link>
      </div>
    </div>

    <div class="settings-card">
      <h3>提供商</h3>
      <div class="provider-grid">
        <button v-for="p in providers" :key="p.key"
          class="provider-btn" :class="{ active: form.provider === p.key }"
          @click="selectProvider(p.key)">
          <span class="provider-name">{{ p.label }}</span>
          <span class="provider-model">{{ p.model }}</span>
        </button>
      </div>
    </div>

    <div class="settings-card" v-if="form.provider === 'custom'">
      <h3>自定义接口</h3>
      <div class="form-grid">
        <div class="field">
          <label>API Base URL</label>
          <input v-model="form.base_url" placeholder="https://your-api.com/v1" />
        </div>
        <div class="field">
          <label>模型名称</label>
          <input v-model="form.model" placeholder="your-model-name" />
        </div>
      </div>
    </div>

    <div class="settings-card">
      <h3>API 密钥</h3>
      <div class="field">
        <label>API Key</label>
        <input v-model="form.api_key" type="password" placeholder="输入 API Key" />
      </div>
    </div>

    <div class="settings-card">
      <h3>高级参数</h3>
      <div class="form-grid">
        <div class="field">
          <label>Temperature (0 - 2)</label>
          <input v-model.number="form.temperature" type="range" min="0" max="2" step="0.1" />
          <span class="range-val">{{ form.temperature }}</span>
        </div>
        <div class="field">
          <label>Max Tokens</label>
          <input v-model.number="form.max_tokens" type="number" min="256" max="32768" step="256" />
        </div>
      </div>
    </div>

    <div class="actions">
      <button class="btn-save" @click="saveConfig" :disabled="saving">
        {{ saving ? '保存中...' : '保存配置' }}
      </button>
      <button class="btn-test" @click="testConnection" :disabled="testing">
        {{ testing ? '测试中...' : '测试连接' }}
      </button>
    </div>

    <div v-if="statusMsg" class="status" :class="{ error: statusError }">
      {{ statusMsg }}
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'

const providers = [
  { key: 'deepseek', label: 'DeepSeek', model: 'deepseek-chat' },
  { key: 'qwen', label: '通义千问 (Qwen)', model: 'qwen-turbo' },
  { key: 'zhipu', label: '智谱 GLM', model: 'glm-4-flash' },
  { key: 'custom', label: '自定义接口', model: '' },
]

const form = ref({
  provider: 'deepseek',
  api_key: '',
  base_url: '',
  model: '',
  temperature: 0.7,
  max_tokens: 4096,
})

const saving = ref(false)
const testing = ref(false)
const statusMsg = ref('')
const statusError = ref(false)

function selectProvider(key) {
  form.value.provider = key
}

onMounted(async () => {
  try {
    const resp = await fetch('/api/llm/config')
    if (resp.ok) {
      const cfg = await resp.json()
      Object.assign(form.value, cfg)
    }
  } catch (e) { /* use defaults */ }
})

async function saveConfig() {
  saving.value = true
  statusMsg.value = ''
  try {
    const resp = await fetch('/api/llm/config', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(form.value),
    })
    const data = await resp.json()
    if (data.success) {
      statusMsg.value = '配置已保存'
      statusError.value = false
    } else {
      statusMsg.value = '保存失败: ' + (data.error || '未知错误')
      statusError.value = true
    }
  } catch (e) {
    statusMsg.value = '保存失败: 无法连接后端服务'
    statusError.value = true
  }
  saving.value = false
}

async function testConnection() {
  testing.value = true
  statusMsg.value = '正在测试连接...'
  statusError.value = false
  try {
    const resp = await fetch('/api/llm/test', { method: 'POST' })
    const data = await resp.json()
    statusMsg.value = data.success
      ? ('连接成功: ' + (data.reply || 'OK'))
      : ('连接失败: ' + (data.error || '未知错误'))
    statusError.value = !data.success
  } catch (e) {
    statusMsg.value = '连接测试失败: 无法连接后端服务'
    statusError.value = true
  }
  testing.value = false
}
</script>

<style scoped>
.settings-page { max-width: 720px; margin: 0 auto; }
.page-header { margin-bottom: 24px; }
.header-row{display:flex;align-items:flex-start;justify-content:space-between;gap:16px}
.header-text{flex:1;min-width:0}
.page-header h2 { font-size: 20px; font-weight: 700; margin-bottom: 6px; }
.page-header p { font-size: 14px; color: #64748b; line-height: 1.6; }
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

.settings-card {
  background: #fff; border-radius: 12px; padding: 20px 24px;
  margin-bottom: 16px; border: 1px solid #e2e8f0;
}
.settings-card h3 { font-size: 15px; font-weight: 700; margin-bottom: 14px; }

.provider-grid { display: grid; grid-template-columns: 1fr 1fr; gap: 10px; }
.provider-btn {
  display: flex; flex-direction: column; align-items: flex-start; gap: 4px;
  padding: 14px 16px; border: 2px solid #e2e8f0; border-radius: 10px;
  background: #fff; cursor: pointer; transition: all .15s; text-align: left;
}
.provider-btn:hover { border-color: #93c5fd; }
.provider-btn.active { border-color: #2563eb; background: #eff6ff; }
.provider-name { font-size: 14px; font-weight: 600; }
.provider-model { font-size: 12px; color: #94a3b8; }

.form-grid { display: grid; grid-template-columns: 1fr 1fr; gap: 16px; }
.field { display: flex; flex-direction: column; gap: 6px; }
.field label { font-size: 13px; font-weight: 600; color: #475569; }
.field input { padding: 10px 12px; border: 1px solid #e2e8f0; border-radius: 8px; font-size: 14px; }
.field input:focus { outline: none; border-color: #2563eb; }
.field input[type="range"] { padding: 0; }
.range-val { font-size: 13px; color: #2563eb; font-weight: 600; }

.actions { display: flex; gap: 12px; margin-top: 8px; }
.btn-save, .btn-test {
  padding: 10px 28px; border: none; border-radius: 10px;
  font-size: 14px; font-weight: 600; cursor: pointer; transition: all .15s;
}
.btn-save { background: #2563eb; color: #fff; }
.btn-save:hover:not(:disabled) { background: #1d4ed8; }
.btn-test { background: #fff; color: #2563eb; border: 1px solid #2563eb; }
.btn-test:hover:not(:disabled) { background: #eff6ff; }
.btn-save:disabled, .btn-test:disabled { opacity: 0.6; cursor: not-allowed; }

.status {
  margin-top: 16px; padding: 12px 16px; border-radius: 8px;
  background: #f0fdf4; color: #16a34a; font-size: 14px;
}
.status.error { background: #fef2f2; color: #dc2626; }
@media (max-width: 720px) {
  .provider-grid, .form-grid { grid-template-columns: 1fr; }
}
</style>
