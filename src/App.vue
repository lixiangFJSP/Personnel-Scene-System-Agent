<template>
  <div id="app-root">
    <nav class="navbar">
      <div class="nav-inner">
        <router-link to="/" class="nav-brand">
          <svg width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"/><polyline points="14 2 14 8 20 8"/><line x1="16" y1="13" x2="8" y2="13"/><line x1="16" y1="17" x2="8" y2="17"/></svg>
          人员场景数据分析系统
        </router-link>
        <div class="nav-links">
          <router-link to="/" class="nav-link">首页</router-link>
          <router-link to="/import" class="nav-link">导入数据</router-link>
        </div>
      </div>
    </nav>
    <main class="main-content">
      <router-view />
    </main>
  </div>
</template>

<script setup>
</script>

<style>
*{margin:0;padding:0;box-sizing:border-box}
body{
  font-family: 'Microsoft YaHei', -apple-system, 'Segoe UI', sans-serif;
  background: #f0f2f5;
  color: #1e293b;
  min-height: 100vh;
}
.navbar{
  background: linear-gradient(135deg,#1e3a5f 0%,#2c5282 50%,#2563eb 100%);
  color:#fff;
  box-shadow:0 2px 12px rgba(37,99,235,.2);
  position:sticky;top:0;z-index:100;
}
.nav-inner{
  max-width:1100px;margin:0 auto;
  display:flex;align-items:center;justify-content:space-between;
  padding:0 24px;height:56px;
}
.nav-brand{
  display:flex;align-items:center;gap:8px;
  color:#fff;text-decoration:none;
  font-size:17px;font-weight:700;letter-spacing:.5px;
}
.nav-links{display:flex;gap:6px}
.nav-link{
  color:rgba(255,255,255,.8);text-decoration:none;
  padding:6px 14px;border-radius:8px;
  font-size:14px;transition:all .15s;
}
.nav-link:hover,.nav-link.router-link-active{
  color:#fff;background:rgba(255,255,255,.15);
}
.main-content{max-width:1100px;margin:0 auto;padding:28px 24px 40px}
@media(max-width:720px){
  .nav-inner{padding:0 16px}
  .nav-brand{font-size:15px}
  .main-content{padding:20px 16px 32px}
}
</style>
