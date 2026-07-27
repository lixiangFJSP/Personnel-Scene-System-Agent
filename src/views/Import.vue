<template>
  <div class="import-page">
    <div class="page-header">
      <h2>数据导入</h2>
      <p>上传 Excel、CSV 或 JSON 数据文件，系统将解析并预览数据内容。导入的数据可应用于各分析模块。</p>
    </div>
    <FileImport />
  </div>
</template>

<script setup>
import FileImport from '@/components/FileImport.vue'
</script>

<style scoped>
.page-header{margin-bottom:24px}
.page-header h2{font-size:22px;font-weight:700;margin-bottom:6px}
.page-header p{font-size:14px;color:#64748b;line-height:1.6}
</style>
