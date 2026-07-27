<template>
  <a :href="module.link" target="_blank" class="module-card">
    <div class="card-top">
      <div class="icon" :style="{ background: module.iconBg, color: module.iconColor }" v-html="module.icon"></div>
      <div class="title-row">
        <h3>{{ module.title }}</h3>
        <span class="badge">AI 分析</span>
      </div>
    </div>
    <p class="desc">{{ module.desc }}</p>
    <span class="enter-btn" :style="{ background: module.btnBg, color: module.btnColor }">
      进入模块 &rarr;
    </span>
  </a>
</template>

<script setup>
defineProps({
  module: { type: Object, required: true },
})
</script>

<style scoped>
.module-card{
  display:block;
  background:#fff;
  border-radius:12px;
  padding:28px 26px;
  border:1px solid #e2e8f0;
  text-decoration:none;
  color:inherit;
  transition:transform .2s,box-shadow .2s;
  position:relative;overflow:hidden;
}
.module-card:hover{
  transform:translateY(-4px);
  box-shadow:0 12px 28px rgba(0,0,0,.1);
}
.card-top{display:flex;align-items:flex-start;gap:16px;margin-bottom:12px}
.icon{
  width:52px;height:52px;
  border-radius:12px;
  display:flex;align-items:center;justify-content:center;
  flex-shrink:0;
}
.icon :deep(svg){width:26px;height:26px}
.title-row{flex:1;display:flex;align-items:center;justify-content:space-between;gap:8px}
h3{font-size:18px;font-weight:700}
.badge{
  display:inline-flex;align-items:center;
  background:linear-gradient(135deg,#7c3aed,#a855f7);
  color:#fff;font-size:11px;font-weight:700;
  padding:3px 12px;border-radius:12px;
  letter-spacing:.5px;white-space:nowrap;
}
.desc{font-size:13px;color:#64748b;line-height:1.7;margin-bottom:16px}
.enter-btn{
  display:inline-flex;align-items:center;gap:6px;
  padding:8px 20px;border-radius:8px;
  font-size:14px;font-weight:600;
}
</style>
