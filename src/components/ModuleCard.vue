<template>
  <a :href="module.link" target="_blank" class="module-card" :style="delayStyle">
    <div class="icon" :style="{ background: module.iconBg, color: module.iconColor }" v-html="module.icon"></div>
    <h3>{{ module.title }}</h3>
    <p class="desc">{{ module.desc }}</p>
    <span class="enter-btn" :style="{ background: module.btnBg, color: module.btnColor }">
      进入模块 →
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
.icon{
  width:52px;height:52px;
  border-radius:12px;
  display:flex;align-items:center;justify-content:center;
  margin-bottom:16px;
}
.icon :deep(svg){width:26px;height:26px}
h3{font-size:20px;font-weight:700;margin-bottom:6px}
.desc{font-size:14px;color:#64748b;line-height:1.7;margin-bottom:16px}
.enter-btn{
  display:inline-flex;align-items:center;gap:6px;
  padding:8px 20px;border-radius:8px;
  font-size:14px;font-weight:600;
}
</style>
