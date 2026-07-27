# -*- coding: utf-8 -*-
"""考勤月度下钻分析 v2：月份范围 + 趋势拆双图 + 人员按部门分组"""
import pandas as pd
import numpy as np
import json, re, sys
sys.stdout.reconfigure(encoding='utf-8')

SRC2 = 'F:/OneDrive/工作-400/项目文档-410/短期紧急任务/搭建人员场景数据分析系统/01源数据/考勤统计表.xlsx'
OUT = 'C:/Users/LENOVO/WorkBuddy/2026-07-18-15-09-50/考勤月度下钻分析.html'

dt = pd.read_excel(SRC2, sheet_name='考勤统计表', header=0)
dt['考勤日期'] = pd.to_datetime(dt['考勤日期'], errors='coerce')
dt = dt.dropna(subset=['考勤日期']).copy()
dt['月份'] = dt['考勤日期'].dt.strftime('%Y-%m')

def category(at):
    if pd.isna(at): return '管理人员'
    return '自由排班人员' if str(at)=='自由排班' else '管理人员'
dt['人员类别'] = dt['考勤类型'].apply(category)
dt['状态列表'] = dt['考勤状态'].fillna('').astype(str).apply(lambda x: [p.strip() for p in x.split(';') if p.strip()])
dt['是否正常'] = dt['状态列表'].apply(lambda x: len(x)==1 and x[0]=='正常')
dt['是否迟到'] = dt['状态列表'].apply(lambda x: any('迟到' in s for s in x))
dt['是否早退'] = dt['状态列表'].apply(lambda x: any('早退' in s for s in x))
dt['是否旷工'] = dt['状态列表'].apply(lambda x: any('旷工' in s for s in x))
dt['是否缺卡'] = dt['状态列表'].apply(lambda x: any('缺卡' in s for s in x))
dt['部门'] = dt['部门'].fillna('未填写'); dt['姓名'] = dt['姓名'].fillna('未知'); dt['卡号'] = dt['卡号'].fillna('').astype(str)

months = sorted(dt['月份'].unique())

trend_rows=[]; dept_rows=[]; person_rows=[]
for (m,cat),g in dt.groupby(['月份','人员类别']):
    t=int(len(g)); n=int(g['是否正常'].sum())
    trend_rows.append({'month':m,'cat':cat,'total':t,'normal':n,'rate':round(n/t*100,1) if t else 0,
        'late':int(g['是否迟到'].sum()),'early':int(g['是否早退'].sum()),'absent':int(g['是否旷工'].sum()),'miss':int(g['是否缺卡'].sum())})
for (m,cat,dept),g in dt.groupby(['月份','人员类别','部门']):
    t=int(len(g)); n=int(g['是否正常'].sum())
    dept_rows.append({'month':m,'cat':cat,'dept':dept,'total':t,'normal':n,'rate':round(n/t*100,1) if t else 0,
        'late':int(g['是否迟到'].sum()),'early':int(g['是否早退'].sum()),'absent':int(g['是否旷工'].sum()),'miss':int(g['是否缺卡'].sum())})
for (m,cat,dept,card,name),g in dt.groupby(['月份','人员类别','部门','卡号','姓名']):
    t=int(len(g)); n=int(g['是否正常'].sum())
    person_rows.append({'month':m,'cat':cat,'dept':dept,'name':name,'total':t,'normal':n,'rate':round(n/t*100,1) if t else 0,
        'late':int(g['是否迟到'].sum()),'early':int(g['是否早退'].sum()),'absent':int(g['是否旷工'].sum()),'miss':int(g['是否缺卡'].sum())})

DATA = {'months':months,'cats':['管理人员','自由排班人员'],'trend':trend_rows,'depts':dept_rows,'persons':person_rows,
    'meta':{'records':len(dt),'months_n':len(months),'date_min':dt['考勤日期'].min().strftime('%Y-%m-%d'),
    'date_max':dt['考勤日期'].max().strftime('%Y-%m-%d'),'mgr_total':int((dt['人员类别']=='管理人员').sum()),
    'free_total':int((dt['人员类别']=='自由排班人员').sum())}}
data_json = json.dumps(DATA, ensure_ascii=False)

HTML = r'''<!DOCTYPE html>
<html lang="zh-CN"><head><meta charset="UTF-8"><meta name="viewport" content="width=device-width,initial-scale=1.0">
<title>考勤月度下钻分析 v2 · 月份范围</title>
<script src="https://cdn.jsdelivr.net/npm/chart.js@4.4.1/dist/chart.umd.min.js"></script>
<style>
:root{--primary:#2563eb;--danger:#dc2626;--warning:#f59e0b;--success:#16a34a;--purple:#7c3aed;--bg:#eef2f7;--card:#fff;--text:#1e293b;--text2:#64748b;--border:#e2e8f0;--soft:#f8fafc}
*{margin:0;padding:0;box-sizing:border-box}
body{font-family:'Microsoft YaHei',sans-serif;background:var(--bg);color:var(--text);line-height:1.6}
.wrap{max-width:1520px;margin:0 auto;padding:22px}
.header{background:linear-gradient(135deg,#1e3a8a,#2563eb);color:#fff;border-radius:14px;padding:24px 30px;margin-bottom:18px}
.header h1{font-size:23px;font-weight:700}.header .sub{margin-top:7px;font-size:13px;opacity:.92;display:flex;gap:18px;flex-wrap:wrap}
.header .tip{margin-top:10px;font-size:12px;background:rgba(255,255,255,.15);padding:6px 12px;border-radius:6px;display:inline-block}
.ctl{background:var(--card);border-radius:12px;padding:16px 20px;margin-bottom:18px;border:1px solid var(--border);display:flex;align-items:center;gap:18px;flex-wrap:wrap}
.ctl .grp{display:flex;align-items:center;gap:8px}.ctl label{font-size:13px;font-weight:600;color:var(--text2)}
.ctl select{padding:6px 12px;border:1px solid var(--border);border-radius:6px;font-size:13px;background:#fff;color:var(--text);cursor:pointer;min-width:110px}
.ctl .arrow{color:var(--text2);font-weight:700}
.tabs{display:flex;gap:4px;background:var(--soft);padding:4px;border-radius:8px;border:1px solid var(--border)}
.tabs button{padding:6px 16px;border:none;background:transparent;border-radius:6px;font-size:13px;cursor:pointer;color:var(--text2);font-weight:600;transition:.15s}
.tabs button.active{background:var(--primary);color:#fff}
.breadcrumb{font-size:13px;color:var(--text2);display:flex;align-items:center;gap:6px;flex-wrap:wrap}
.breadcrumb b{color:var(--primary)}.breadcrumb .sep{color:#cbd5e1}.breadcrumb .clear{color:var(--danger);cursor:pointer;text-decoration:underline;margin-left:8px}
.kpi-grid{display:grid;grid-template-columns:repeat(5,1fr);gap:12px;margin-bottom:18px}
.kpi{background:var(--card);border-radius:10px;padding:14px 16px;border:1px solid var(--border);border-left:4px solid var(--primary)}
.kpi.danger{border-left-color:var(--danger)}.kpi.warning{border-left-color:var(--warning)}.kpi.success{border-left-color:var(--success)}.kpi.purple{border-left-color:var(--purple)}
.kpi .l{font-size:12px;color:var(--text2)}.kpi .v{font-size:24px;font-weight:700;margin-top:3px}.kpi .v small{font-size:12px;color:var(--text2);font-weight:500;margin-left:3px}
.section{background:var(--card);border-radius:12px;padding:20px;margin-bottom:18px;border:1px solid var(--border)}
.section-title{font-size:16px;font-weight:700;display:flex;align-items:center;gap:8px;margin-bottom:4px}
.section-title .bar{width:4px;height:16px;background:var(--primary);border-radius:2px}
.section-desc{font-size:12px;color:var(--text2);margin-bottom:14px}
.chart-box{background:var(--soft);border-radius:10px;padding:14px;border:1px solid var(--border)}
.chart-box h4{font-size:14px;font-weight:600;margin-bottom:2px}.chart-box .ctip{font-size:12px;color:var(--text2);margin-bottom:8px}
.cg-2{display:grid;grid-template-columns:1fr 1fr;gap:16px}
canvas{max-height:300px}
.tbl-wrap{overflow:auto;max-height:600px;border:1px solid var(--border);border-radius:8px;background:#fff}
table{width:100%;border-collapse:collapse;font-size:13px}
thead{position:sticky;top:0;background:#f1f5f9;z-index:3}
th{padding:9px 12px;text-align:left;font-weight:600;color:var(--text2);border-bottom:2px solid var(--border);white-space:nowrap;cursor:pointer;user-select:none}
th:hover{background:#e2e8f0}th .arrow{font-size:10px;margin-left:3px;color:var(--primary)}
td{padding:7px 12px;border-bottom:1px solid var(--border);white-space:nowrap}
tr:hover{background:#eff6ff}
.tag{display:inline-block;padding:2px 8px;border-radius:4px;font-size:12px;font-weight:600}
.tag.ok{background:#dcfce7;color:#16a34a}.tag.warn{background:#fef3c7;color:#d97706}.tag.bad{background:#fee2e2;color:#dc2626}
.rate-bar{display:inline-block;width:50px;height:8px;background:#e2e8f0;border-radius:4px;vertical-align:middle;margin-right:6px;overflow:hidden}
.rate-bar i{display:block;height:100%;background:var(--success)}
.dept-cell{cursor:pointer;color:var(--primary);text-decoration:underline}.dept-cell:hover{color:#1d4ed8}
.empty{text-align:center;padding:30px;color:var(--text2);font-size:14px}
.hint{font-size:12px;color:var(--text2);margin-top:8px;margin-bottom:10px;background:#fffbeb;border:1px solid #fde68a;border-radius:6px;padding:8px 12px}
.hint b{color:#92400e}
.grp-head{position:sticky;top:0;background:#dbeafe;z-index:2;font-weight:700;color:#1e40af;padding:8px 12px;border-bottom:2px solid #93c5fd;display:flex;justify-content:space-between;align-items:center;font-size:13px}
.grp-head .gstat{font-size:12px;color:#1e40af;font-weight:600}
.tool-row{display:flex;gap:8px;align-items:center;margin-bottom:10px;flex-wrap:wrap}
.tool-row input{padding:6px 12px;border:1px solid var(--border);border-radius:6px;font-size:13px;width:220px}
.btn{padding:6px 12px;border:1px solid var(--border);border-radius:6px;font-size:12px;cursor:pointer;background:#fff;color:var(--text2);font-weight:600}
.btn:hover{background:var(--soft)}.btn.primary{background:var(--primary);color:#fff;border-color:var(--primary)}
.footer{text-align:center;color:var(--text2);font-size:12px;padding:14px}
details{border:1px solid var(--border);border-radius:8px;margin-bottom:6px;overflow:hidden;background:#fff}
details summary{padding:9px 14px;background:#f1f5f9;cursor:pointer;font-weight:600;font-size:13px;color:var(--text);display:flex;justify-content:space-between;align-items:center;list-style:none}
details summary::-webkit-details-marker{display:none}
details summary .gleft{display:flex;align-items:center;gap:8px}
details summary .gname{color:#1e40af}
details summary .gstat{font-size:12px;color:var(--text2);font-weight:600}
details[open] summary{border-bottom:1px solid var(--border)}
details .gbody{padding:0}
@media(max-width:1000px){.kpi-grid{grid-template-columns:repeat(2,1fr)}.cg-2{grid-template-columns:1fr}}
</style></head><body>
<div class="wrap">
  <div class="header">
    <h1>考勤月度下钻分析 · 正常打卡率（月份范围版）</h1>
    <div class="sub">
      <span>数据周期：<b id="d-range"></b></span><span>覆盖月份：<b id="d-months"></b> 个</span>
      <span>打卡明细：<b id="d-records"></b> 条</span><span>管理人员记录：<b id="d-mgr"></b></span><span>自由排班记录：<b id="d-free"></b></span>
    </div>
    <div class="tip">分类依据：管理人员 = 固定班制/非固定班制考勤类型（职能/管理岗）；自由排班人员 = 自由排班考勤类型（一线倒班岗）</div>
  </div>

  <div class="ctl">
    <div class="grp"><label>开始月份：</label><select id="sel-ms"></select></div>
    <span class="arrow">→</span>
    <div class="grp"><label>结束月份：</label><select id="sel-me"></select></div>
    <div class="grp"><label>人员类别：</label>
      <div class="tabs" id="tab-cat"><button data-cat="全部" class="active">全部</button><button data-cat="管理人员">管理人员</button><button data-cat="自由排班人员">自由排班人员</button></div>
    </div>
    <div class="breadcrumb" id="bc"></div>
  </div>

  <div class="kpi-grid" id="kpi-grid"></div>

  <div class="section">
    <div class="section-title"><span class="bar"></span>一、月度正常打卡率趋势（管理人员 / 自由排班人员 分图）</div>
    <div class="section-desc">两类人员各自独立成图，受上方"开始-结束月份"范围控制。绿带为95%达标线。</div>
    <div class="cg-2">
      <div class="chart-box"><h4>管理人员 · 月度正常打卡率</h4><div class="ctip">紫色折线，悬停查看各月明细</div><canvas id="c-trend-mgr"></canvas></div>
      <div class="chart-box"><h4>自由排班人员 · 月度正常打卡率</h4><div class="ctip">蓝色折线，悬停查看各月明细</div><canvas id="c-trend-free"></canvas></div>
    </div>
  </div>

  <div class="section">
    <div class="section-title"><span class="bar"></span>二、部门/班组正常打卡率（月份范围聚合 · 点击柱子下钻）</div>
    <div class="section-desc">所选月份范围内各部门数据汇总累加。点击柱状图任一部门，下方明细切换为该部门人员。</div>
    <div class="cg-2">
      <div class="chart-box"><h4>各部门正常打卡率（范围内汇总）</h4><div class="ctip">绿≥95% / 橙90-95% / 红&lt;90%，点击下钻</div><canvas id="c-dept"></canvas></div>
      <div class="chart-box"><h4>各部门异常次数（范围内汇总）</h4><div class="ctip">迟到/早退/缺卡/旷工 堆叠</div><canvas id="c-dept-abn"></canvas></div>
    </div>
  </div>

  <div class="section">
    <div class="section-title"><span class="bar"></span>三、人员明细（按部门/班组分组 · 月份范围聚合）</div>
    <div class="section-desc">所选月份范围内人员数据汇总，按部门/班组分组展示。点击分组标题展开/收起；点击部门柱可单独筛选某部门。</div>
    <div class="hint"><b>下钻路径：</b>选择开始-结束月份 → 选择人员类别 → 点击部门柱（可选）→ 展开部门分组查看人员。当前层级：<span id="cur-level">全部部门分组</span></div>
    <div class="tool-row">
      <input id="search" placeholder="搜索姓名/部门...">
      <button class="btn" id="btn-expand">全部展开</button>
      <button class="btn" id="btn-collapse">全部收起</button>
      <span style="font-size:12px;color:var(--text2)" id="tbl-count"></span>
    </div>
    <div id="grp-container"></div>
  </div>
  <div class="footer">数据来源：考勤统计表（91,520条明细）· 月份范围聚合 · 按部门分组下钻 · 表头可排序</div>
</div>

<script>
const D = __DATA__;
document.getElementById('d-range').textContent = D.meta.date_min+' 至 '+D.meta.date_max;
document.getElementById('d-months').textContent = D.meta.months_n;
document.getElementById('d-records').textContent = D.meta.records.toLocaleString();
document.getElementById('d-mgr').textContent = D.meta.mgr_total.toLocaleString();
document.getElementById('d-free').textContent = D.meta.free_total.toLocaleString();

const selMS=document.getElementById('sel-ms'), selME=document.getElementById('sel-me');
D.months.forEach(m=>{const a=document.createElement('option');a.value=m;a.textContent=m;selMS.appendChild(a);
  const b=document.createElement('option');b.value=m;b.textContent=m;selME.appendChild(b)});
selMS.value=D.months[0]; selME.value=D.months[D.months.length-1];

let state={ms:selMS.value, me:selME.value, cat:'全部', dept:null, sortKey:'rate', sortDir:1, search:''};
let cTM=null,cTF=null,cD=null,cDA=null;

document.querySelectorAll('#tab-cat button').forEach(b=>b.onclick=()=>{document.querySelectorAll('#tab-cat button').forEach(x=>x.classList.remove('active'));b.classList.add('active');state.cat=b.dataset.cat;state.dept=null;renderAll()});
selMS.onchange=()=>{if(selMS.value>selME.value)selME.value=selMS.value;state.ms=selMS.value;state.dept=null;renderAll()};
selME.onchange=()=>{if(selME.value<selMS.value)selMS.value=selME.value;state.me=selME.value;state.dept=null;renderAll()};
document.getElementById('search').oninput=(e)=>{state.search=e.target.value.trim().toLowerCase();renderGroups()};
document.getElementById('btn-expand').onclick=()=>{document.querySelectorAll('#grp-container details').forEach(d=>d.open=true)};
document.getElementById('btn-collapse').onclick=()=>{document.querySelectorAll('#grp-container details').forEach(d=>d.open=false)};

function inRange(m){return m>=state.ms && m<=state.me}
function catMatch(r){return state.cat==='全部'||r.cat===state.cat}
function rateColor(v){return v>=95?'#16a34a':(v>=90?'#f59e0b':'#dc2626')}
function rateTag(v){const c=v>=95?'ok':(v>=90?'warn':'bad');return `<span class="rate-bar"><i style="width:${v}%;background:${rateColor(v)}"></i></span><span class="tag ${c}">${v}%</span>`}

function rangeMonths(){return D.months.filter(inRange)}

// 趋势：两个图
function renderTrend(){
  const ms=rangeMonths();
  const mk=(c)=>ms.map(m=>{const r=D.trend.find(x=>x.month===m&&x.cat===c);return r?r.rate:null});
  const mkt=(c)=>ms.map(m=>{const r=D.trend.find(x=>x.month===m&&x.cat===c);return r?r.total:0});
  const mkn=(c)=>ms.map(m=>{const r=D.trend.find(x=>x.month===m&&x.cat===c);return r?r.normal:0});
  const opt=(color,fill)=>({responsive:true,maintainAspectRatio:false,plugins:{legend:{display:false},
    tooltip:{callbacks:{label:(c)=>'正常率 '+c.parsed.y+'%',afterLabel:(c)=>'正常 '+mkn(c.dataset.label_)[c.dataIndex].toLocaleString()+' / '+mkt(c.dataset.label_)[c.dataIndex].toLocaleString()+' 条'}}},
    scales:{x:{title:{display:true,text:'月份'}},y:{title:{display:true,text:'正常打卡率(%)'},min:0,max:100,
      grid:{color:(ctx)=>ctx.tick.value>=95?'rgba(22,163,106,.22)':'rgba(226,232,240,.6)'}}}});
  if(cTM)cTM.destroy(); if(cTF)cTF.destroy();
  cTM=new Chart(document.getElementById('c-trend-mgr'),{type:'line',data:{labels:ms,datasets:[
    {label:'管理人员',label_:'管理人员',data:mk('管理人员'),borderColor:'#7c3aed',backgroundColor:'rgba(124,58,237,.12)',borderWidth:2.5,tension:.3,pointRadius:4,pointBackgroundColor:'#7c3aed',fill:true}]},options:opt('#7c3aed',true)});
  cTF=new Chart(document.getElementById('c-trend-free'),{type:'line',data:{labels:ms,datasets:[
    {label:'自由排班人员',label_:'自由排班人员',data:mk('自由排班人员'),borderColor:'#2563eb',backgroundColor:'rgba(37,99,235,.12)',borderWidth:2.5,tension:.3,pointRadius:4,pointBackgroundColor:'#2563eb',fill:true}]},options:opt('#2563eb',true)});
}

function renderKPI(){
  const rows=D.trend.filter(r=>inRange(r.month)&&catMatch(r));
  const total=rows.reduce((s,r)=>s+r.total,0), normal=rows.reduce((s,r)=>s+r.normal,0);
  const late=rows.reduce((s,r)=>s+r.late,0), early=rows.reduce((s,r)=>s+r.early,0), miss=rows.reduce((s,r)=>s+r.miss,0);
  const rate=total>0?(normal/total*100):0;
  const kpis=[
    {l:'正常打卡率',v:rate.toFixed(1),u:'%',c:rate>=95?'success':(rate>=90?'warning':'danger'),n:state.ms+'~'+state.me},
    {l:'打卡记录数',v:total.toLocaleString(),u:'',c:'',n:'正常'+normal.toLocaleString()+'条'},
    {l:'迟到',v:late,u:'次',c:'danger',n:''},{l:'早退',v:early,u:'次',c:'warning',n:''},{l:'缺卡',v:miss,u:'次',c:'purple',n:''}];
  const kg=document.getElementById('kpi-grid');kg.innerHTML='';
  kpis.forEach(k=>{const e=document.createElement('div');e.className='kpi '+k.c;e.innerHTML=`<div class="l">${k.l}</div><div class="v">${k.v}<small>${k.u}</small></div><div style="font-size:11px;color:var(--text2)">${k.n}</div>`;kg.appendChild(e)});
}

// 部门聚合（月份范围）
function getDeptAgg(){
  let rows=D.depts.filter(r=>inRange(r.month)&&catMatch(r));
  const map={};
  rows.forEach(r=>{if(!map[r.dept])map[r.dept]={dept:r.dept,total:0,normal:0,late:0,early:0,absent:0,miss:0};
    const m=map[r.dept];m.total+=r.total;m.normal+=r.normal;m.late+=r.late;m.early+=r.early;m.absent+=r.absent;m.miss+=r.miss});
  let arr=Object.values(map).filter(m=>m.total>=30);
  arr.forEach(m=>m.rate=m.total>0?Math.round(m.normal/m.total*1000)/10:0);
  return arr;
}

function renderDept(){
  let arr=getDeptAgg().sort((a,b)=>a.rate-b.rate);
  const labels=arr.map(r=>r.dept);
  if(cD)cD.destroy(); if(cDA)cDA.destroy();
  cD=new Chart(document.getElementById('c-dept'),{type:'bar',data:{labels:labels,datasets:[
    {label:'正常打卡率(%)',data:arr.map(r=>r.rate),backgroundColor:arr.map(r=>rateColor(r.rate)),borderWidth:0}]},
    options:{indexAxis:'y',responsive:true,maintainAspectRatio:false,
      onClick:(e,el)=>{if(el.length){state.dept=labels[el[0].index];renderAll()}},
      onHover:(e,el)=>{e.native.target.style.cursor=el.length?'pointer':'default'},
      plugins:{legend:{display:false},tooltip:{callbacks:{label:(c)=>'正常率 '+c.parsed.x+'%',
        afterLabel:(c)=>{const r=arr[c.dataIndex];return '正常'+r.normal+'/'+r.total+' | 迟到'+r.late+' 早退'+r.early+' 缺卡'+r.miss+' 旷工'+r.absent}}}},
      scales:{x:{title:{display:true,text:'正常打卡率(%)'},min:0,max:100}}}});
  cDA=new Chart(document.getElementById('c-dept-abn'),{type:'bar',data:{labels:labels,datasets:[
    {label:'迟到',data:arr.map(r=>r.late),backgroundColor:'#ea580c'},
    {label:'早退',data:arr.map(r=>r.early),backgroundColor:'#dc2626'},
    {label:'缺卡',data:arr.map(r=>r.miss),backgroundColor:'#f59e0b'},
    {label:'旷工',data:arr.map(r=>r.absent),backgroundColor:'#7c3aed'}]},
    options:{indexAxis:'y',responsive:true,maintainAspectRatio:false,
      onClick:(e,el)=>{if(el.length){state.dept=labels[el[0].index];renderAll()}},
      onHover:(e,el)=>{e.native.target.style.cursor=el.length?'pointer':'default'},
      plugins:{legend:{position:'top'}},scales:{x:{stacked:true,title:{display:true,text:'次数'}},y:{stacked:true}}}});
}

function renderBC(){
  const bc=document.getElementById('bc');
  let html='<span>当前：</span><b>'+state.ms+' ~ '+state.me+'</b><span class="sep">/</span><b>'+state.cat+'</b>';
  if(state.dept){html+='<span class="sep">/</span><b>'+state.dept+'</b><span class="clear" onclick="clearDept()">✕ 清除部门</span>'}
  bc.innerHTML=html;
  document.getElementById('cur-level').textContent=state.dept?('【'+state.dept+'】人员明细'):'全部部门分组';
}
window.clearDept=()=>{state.dept=null;renderAll()};

// 人员聚合（月份范围 + 按部门分组）
function getPersonAgg(){
  let rows=D.persons.filter(r=>inRange(r.month)&&catMatch(r));
  if(state.dept)rows=rows.filter(r=>r.dept===state.dept);
  const map={};
  rows.forEach(r=>{const k=r.name+'||'+r.dept;
    if(!map[k])map[k]={name:r.name,dept:r.dept,total:0,normal:0,late:0,early:0,absent:0,miss:0};
    const m=map[k];m.total+=r.total;m.normal+=r.normal;m.late+=r.late;m.early+=r.early;m.absent+=r.absent;m.miss+=r.miss});
  let arr=Object.values(map);
  arr.forEach(m=>m.rate=m.total>0?Math.round(m.normal/m.total*1000)/10:0);
  if(state.search)arr=arr.filter(r=>r.name.toLowerCase().includes(state.search)||r.dept.toLowerCase().includes(state.search));
  // 全局排序
  const k=state.sortKey;
  arr.sort((a,b)=>{if(k==='name'||k==='dept')return state.sortDir*a[k].localeCompare(b[k]);return state.sortDir*(a[k]-b[k])});
  // 分组 by dept
  const groups={};
  arr.forEach(r=>{if(!groups[r.dept])groups[r.dept]=[];groups[r.dept].push(r)});
  // 部门顺序：按平均正常率升序（差的在前）
  const garr=Object.keys(groups).map(dn=>{const ps=groups[dn];const t=ps.reduce((s,p)=>s+p.total,0),n=ps.reduce((s,p)=>s+p.normal,0);
    return{dept:dn,persons:ps,avg:t>0?Math.round(n/t*1000)/10:0,total:t}});
  garr.sort((a,b)=>a.avg-b.avg);
  return garr;
}

const COLS=[['name','姓名'],['dept','部门/班组'],['total','打卡天数'],['normal','正常天数'],['rate','正常率'],['late','迟到'],['early','早退'],['miss','缺卡'],['absent','旷工']];

function renderGroups(){
  const garr=getPersonAgg();
  const totalPeople=garr.reduce((s,g)=>s+g.persons.length,0);
  document.getElementById('tbl-count').textContent='共 '+garr.length+' 个部门 / '+totalPeople+' 人';
  const cont=document.getElementById('grp-container');
  if(!garr.length){cont.innerHTML='<div class="empty">暂无数据</div>';return}
  const thHtml=COLS.map(c=>{const a=state.sortKey===c[0]?'<span class="arrow">'+(state.sortDir>0?'▲':'▼')+'</span>':'';return `<th onclick="sortTbl('${c[0]}')">${c[1]}${a}</th>`}).join('');
  cont.innerHTML=garr.map(g=>{
    const isOpen = state.dept? true : g.persons.length<=25; // 人数少的默认展开
    const rows=g.persons.slice(0,200).map(r=>`<tr><td>${r.name}</td><td>${r.dept}</td><td>${r.total}</td><td>${r.normal}</td><td>${rateTag(r.rate)}</td><td>${r.late||''}</td><td>${r.early||''}</td><td>${r.miss||''}</td><td>${r.absent||''}</td></tr>`).join('');
    const more=g.persons.length>200?`<tr><td colspan="9" class="empty">仅显示前200人，共${g.persons.length}人</td></tr>`:'';
    return `<details ${isOpen?'open':''}><summary><span class="gleft"><span>▸</span><span class="gname">${g.dept}</span></span><span class="gstat">${g.persons.length}人 · 平均正常率 ${g.avg}% · ${g.total}条记录</span></summary><div class="gbody"><table><thead><tr>${thHtml}</tr></thead><tbody>${rows}${more}</tbody></table></div></details>`;
  }).join('');
}
window.sortTbl=(k)=>{if(state.sortKey===k)state.sortDir=-state.sortDir;else{state.sortKey=k;state.sortDir=1}renderGroups()};

function renderAll(){renderKPI();renderDept();renderBC();renderGroups()}
renderTrend();renderAll();
</script></body></html>'''
html = HTML.replace('__DATA__', data_json)
with open(OUT,'w',encoding='utf-8') as f: f.write(html)
print('已生成:',OUT)
print(f'月份:{len(months)} | 趋势:{len(trend_rows)} | 部门:{len(dept_rows)} | 人员:{len(person_rows)} | JSON:{len(data_json.encode())/1024:.0f}KB')
