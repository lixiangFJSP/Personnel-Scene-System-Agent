# -*- coding: utf-8 -*-
"""
作业组合周期对比甘特图分析（以叶片流水号为索引）
数据源: MOP工时周期明细.xlsx (工序级) / ST工时周期明细.xlsx (工步级)
"""
import pandas as pd
import plotly.graph_objects as go
import plotly.io as pio
import re
import json, os

script_dir = os.path.dirname(os.path.abspath(__file__))
data_dir = os.path.join(script_dir, '..', '01源数据')
SRC_MOP = os.path.join(data_dir, 'MOP工时周期明细.xlsx')
SRC_ST = os.path.join(data_dir, 'ST工时周期明细.xlsx')
OUT_HTML = os.path.join(script_dir, '作业组合周期对比甘特图.html')

# ---------- 读取与预处理 ----------
mop = pd.read_excel(SRC_MOP)
st = pd.read_excel(SRC_ST)
mop['开始'] = pd.to_datetime(mop['开始时间']); mop['结束'] = pd.to_datetime(mop['结束时间'])
st['开始'] = pd.to_datetime(st['开始时间']); st['结束'] = pd.to_datetime(st['结束时间'])

# 提取叶片流水号: 任务编码 GW108AB-07A-F260226CE -> F260226
def sn(t):
    m = re.search(r'(F\d+)', str(t))
    return m.group(1) if m else str(t)
mop['叶片流水号'] = mop['任务编码'].map(sn)
st['叶片流水号'] = st['任务编码'].map(sn)

PROC_ORDER = ['MOP230', 'MOP240', 'JP003', 'MOP270', 'MOP280', 'MOP290']
PROC_LABEL = {
    'MOP230': '①壳体模具准备', 'MOP240': '②A部分玻纤布铺设', 'JP003': '③预制件安放',
    'MOP270': '④B部分玻纤布铺设', 'MOP280': '⑤壳体流道布置', 'MOP290': '⑥壳体真空系统制作',
}
COL_MOP = '#E8743B'   # 橙 - MOP工序级
COL_ST = '#2E86DE'    # 蓝 - ST工步级
FONT = dict(family='Microsoft YaHei, SimHei, sans-serif')

common = sorted(set(mop['叶片流水号']) & set(st['叶片流水号']))

# 每叶片每工序 MOP/ST 周期
def proc_agg(df, src):
    g = df[df['叶片流水号'].isin(common)].groupby(['叶片流水号', '工序编码'], as_index=False)['周期(分钟)'].sum()
    g['src'] = src
    return g
mp = proc_agg(mop, 'MOP').rename(columns={'周期(分钟)': 'MOP周期'})
sp = proc_agg(st, 'ST').rename(columns={'周期(分钟)': 'ST周期'})
cell = mp.merge(sp, on=['叶片流水号', '工序编码'], how='inner')
cell['差异'] = cell['ST周期'] - cell['MOP周期']
cell['差异%'] = cell.apply(lambda r: round(r['差异'] / r['MOP周期'] * 100, 1) if r['MOP周期'] else 0, axis=1)

# 分面聚合: 叶片 × 工序 × 叶面(PS/SS) —— 工序级分面统计
FACES = ['PS', 'SS']
mpf = mop[mop['叶片流水号'].isin(common)].groupby(['叶片流水号', '工序编码', '叶面'], as_index=False)['周期(分钟)'].sum().rename(columns={'周期(分钟)': 'MOP周期'})
spf = st[st['叶片流水号'].isin(common)].groupby(['叶片流水号', '工序编码', '叶面'], as_index=False)['周期(分钟)'].sum().rename(columns={'周期(分钟)': 'ST周期'})
cell_f = mpf.merge(spf, on=['叶片流水号', '工序编码', '叶面'], how='inner')
cell_f['差异'] = cell_f['ST周期'] - cell_f['MOP周期']
cell_f['差异%'] = cell_f.apply(lambda r: round(r['差异'] / r['MOP周期'] * 100, 1) if r['MOP周期'] else 0, axis=1)

# 每叶片总周期
tot = cell.groupby('叶片流水号').agg(MOP总=('MOP周期', 'sum'), ST总=('ST周期', 'sum')).reset_index()
tot['差异'] = tot['ST总'] - tot['MOP总']
tot['差异%'] = (tot['差异'] / tot['MOP总'] * 100).round(1)
tot = tot.sort_values('叶片流水号').reset_index(drop=True)

avg_mop_tot = round(tot['MOP总'].mean(), 1)
avg_st_tot = round(tot['ST总'].mean(), 1)
avg_diff = round((avg_st_tot / avg_mop_tot - 1) * 100, 1)
max_row = tot.loc[tot['差异%'].idxmax()]
min_row = tot.loc[tot['差异%'].idxmin()]

# ---------- 图1: 以叶片流水号为索引 — MOP vs ST 总周期对比甘特 ----------
blades = tot['叶片流水号'].tolist()[::-1]   # 反转使小编号在顶
mop_tot = tot['MOP总'].tolist()[::-1]
st_tot = tot['ST总'].tolist()[::-1]
diff_lbl = [f'{d:+.0f}%' for d in tot['差异%'].tolist()[::-1]]

fig1 = go.Figure()
# ST 条 (底层, 半透明, 较长)
fig1.add_trace(go.Bar(
    y=blades, x=st_tot, orientation='h', name='ST 工步级总周期',
    marker_color=COL_ST, opacity=0.55,
    text=[f'{v:.0f}' for v in st_tot], textposition='outside',
    hovertemplate='叶片: %{y}<br>ST总周期: %{x:.1f} 分钟<extra></extra>',
))
# MOP 条 (上层, 实色, 较短)
fig1.add_trace(go.Bar(
    y=blades, x=mop_tot, orientation='h', name='MOP 工序级总周期',
    marker_color=COL_MOP, opacity=0.95,
    text=[f'{v:.0f}' for v in mop_tot], textposition='inside',
    hovertemplate='叶片: %{y}<br>MOP总周期: %{x:.1f} 分钟<extra></extra>',
))
# 差异标注 (右侧)
xmax = max(st_tot) * 1.18
fig1.add_trace(go.Bar(
    y=blades, x=[xmax - v for v in st_tot], base=st_tot, orientation='h',
    marker_color='rgba(0,0,0,0)', showlegend=False,
    text=diff_lbl, textposition='inside', textfont=dict(color='#c0392b', size=12, family='Microsoft YaHei'),
    hoverinfo='skip',
))
fig1.update_layout(
    barmode='overlay',
    title=dict(text='<b>图1 · 以叶片流水号为索引 — 作业组合总周期对比甘特图</b><br><span style="font-size:13px;color:#666">每叶片6道工序周期之和；蓝条=ST工步级，橙条=MOP工序级；右侧红字为差异%</span>', x=0.01, font=dict(size=17)),
    xaxis=dict(title='周期 (分钟)', gridcolor='#eee', zeroline=False, range=[0, xmax]),
    yaxis=dict(title='叶片流水号', automargin=True, gridcolor='#f5f5f5'),
    legend=dict(orientation='h', x=0.01, y=1.04, bgcolor='rgba(0,0,0,0)'),
    height=620, margin=dict(l=110, r=60, t=110, b=50),
    font=FONT, plot_bgcolor='white',
)

# ---------- 图2: 叶片 × (工序-面) 差异% 热力图 (PS/SS分开) ----------
heat2 = cell_f.pivot_table(index='叶片流水号', columns=['工序编码', '叶面'], values='差异%', aggfunc='first')
cols2 = [(p, f) for p in PROC_ORDER for f in FACES]
heat2 = heat2.reindex(index=tot['叶片流水号'], columns=cols2)
x2 = [f'{PROC_LABEL[p]}·{f}面' for p in PROC_ORDER for f in FACES]
fig2 = go.Figure(data=go.Heatmap(
    z=heat2.values, x=x2, y=heat2.index,
    colorscale=[[0, '#27AE60'], [0.5, '#FFFFFF'], [1, '#C0392B']],
    zmid=0, zmin=-40, zmax=220,
    text=heat2.values, texttemplate='%{text:.0f}%', textfont=dict(size=10, family='Microsoft YaHei'),
    hovertemplate='叶片: %{y}<br>工序·面: %{x}<br>差异: %{z:.1f}%<extra></extra>',
    colorbar=dict(title='差异%', ticksuffix='%'),
))
fig2.update_layout(
    title=dict(text='<b>图2 · 叶片流水号 × 工序(PS面/SS面分开) — 周期差异热力图</b><br><span style="font-size:13px;color:#666">每道工序拆分PS/SS两面分别统计；红=ST高于MOP，绿=ST低于MOP</span>', x=0.01, font=dict(size=17)),
    xaxis=dict(title='工序 · 叶面', automargin=True, gridcolor='#f5f5f5', tickangle=-40),
    yaxis=dict(title='叶片流水号', automargin=True, gridcolor='#f5f5f5', autorange='reversed'),
    height=600, margin=dict(l=100, r=60, t=100, b=120),
    font=FONT, plot_bgcolor='white',
)

# ---------- 图3: 全部14片叶片 工艺时间轴甘特 (按叶片流水号纵向排列) ----------
PROC_COLOR = {'MOP230': '#4A90D9', 'MOP240': '#50C878', 'JP003': '#9B59B6',
              'MOP270': '#F39C12', 'MOP280': '#1ABC9C', 'MOP290': '#E74C3C'}
g3 = mop[mop['叶片流水号'].isin(common)].copy().sort_values(['叶片流水号', '开始'])
blade_order = sorted(common, reverse=True)   # categoryarray: 末位在顶部 -> 小编号在顶
fig3 = go.Figure()
seen_proc = set()
for _, r in g3.iterrows():
    p = r['工序编码']
    start_ms = int(r['开始'].timestamp() * 1000)
    dur_ms = (r['结束'] - r['开始']).total_seconds() * 1000
    show = p not in seen_proc
    seen_proc.add(p)
    fig3.add_trace(go.Bar(
        y=[r['叶片流水号']], x=[dur_ms], base=[start_ms], orientation='h',
        marker_color=PROC_COLOR.get(p, '#888'), opacity=0.92,
        showlegend=show, legendgroup=p, name=PROC_LABEL.get(p, p),
        hovertemplate=(f"叶片: <b>{r['叶片流水号']}</b><br>"
                       f"工序: {PROC_LABEL.get(p, p)} [{r['叶面']}面]<br>"
                       f"开始: {r['开始'].strftime('%m-%d %H:%M')}<br>"
                       f"结束: {r['结束'].strftime('%m-%d %H:%M')}<br>"
                       f"周期: {r['周期(分钟)']:.0f}分 / 工时: {r['工时(分钟)']:.0f}分<extra></extra>"),
    ))
fig3.update_layout(
    barmode='overlay',
    title=dict(text='<b>图3 · 全部叶片工艺时间轴甘特图（按叶片流水号排列，14片）</b><br><span style="font-size:13px;color:#666">真实开始/结束时间；颜色=工序；MOP与ST时间轴一致，差异在周期口径；可见约1~2天生产1片的排产节奏</span>', x=0.01, font=dict(size=17)),
    xaxis=dict(title='时间', type='date', gridcolor='#eee'),
    yaxis=dict(title='叶片流水号', categoryorder='array', categoryarray=blade_order,
               automargin=True, gridcolor='#f5f5f5'),
    legend=dict(orientation='h', x=0.01, y=1.05, bgcolor='rgba(0,0,0,0)', font=dict(size=12)),
    height=640, margin=dict(l=110, r=40, t=120, b=50),
    font=FONT, plot_bgcolor='white',
)

# ---------- 下钻明细表数据 (工序×叶面分开) ----------
drill = []
for _, brow in tot.iterrows():
    blade = brow['叶片流水号']
    b = {'叶片': blade, 'MOP总': round(float(brow['MOP总']), 1), 'ST总': round(float(brow['ST总']), 1),
         '差异': round(float(brow['差异']), 1), '差异%': round(float(brow['差异%']), 1), 'faces': []}
    sub = cell_f[cell_f['叶片流水号'] == blade]
    for p in PROC_ORDER:
        for f in FACES:
            r = sub[(sub['工序编码'] == p) & (sub['叶面'] == f)]
            if r.empty:
                continue
            r = r.iloc[0]
            face = {'工序': p, '工序名': PROC_LABEL[p], '叶面': f,
                    'MOP周期': round(float(r['MOP周期']), 1), 'ST周期': round(float(r['ST周期']), 1),
                    '差异': round(float(r['差异']), 1), '差异%': round(float(r['差异%']), 1),
                    'mop_rows': [], 'st_rows': []}
            mr = mop[(mop['叶片流水号'] == blade) & (mop['工序编码'] == p) & (mop['叶面'] == f)].sort_values('开始')
            for _, m in mr.iterrows():
                face['mop_rows'].append({
                    '开始': m['开始'].strftime('%Y-%m-%d %H:%M:%S'),
                    '结束': m['结束'].strftime('%Y-%m-%d %H:%M:%S'),
                    '周期': round(float(m['周期(分钟)']), 1), '工时': round(float(m['工时(分钟)']), 1),
                    '得分': int(m['得分'])})
            sr = st[(st['叶片流水号'] == blade) & (st['工序编码'] == p) & (st['叶面'] == f)].sort_values('开始')
            for _, s in sr.iterrows():
                face['st_rows'].append({
                    '工步': str(s['工步编码']), '描述': str(s['工步描述']),
                    '开始': s['开始'].strftime('%Y-%m-%d %H:%M:%S'), '结束': s['结束'].strftime('%Y-%m-%d %H:%M:%S'),
                    '周期': round(float(s['周期(分钟)']), 1), '工时': round(float(s['工时(分钟)']), 1),
                    '得分': int(s['得分'])})
            b['faces'].append(face)
    drill.append(b)
drill_json = json.dumps(drill, ensure_ascii=False)

DRILL_HTML = '''
<style>
  .dt-wrap{background:white;border-radius:10px;padding:16px;margin-bottom:22px;box-shadow:0 1px 4px rgba(0,0,0,.06);}
  .dt-title{font-size:17px;font-weight:700;color:#222;margin:0 0 4px;}
  .dt-hint{font-size:13px;color:#666;margin-bottom:10px;}
  .dt-toolbar{margin-bottom:8px;}
  .dt-toolbar button{font-family:inherit;font-size:12px;border:1px solid #2E86DE;background:white;color:#2E86DE;border-radius:5px;padding:4px 10px;cursor:pointer;margin-right:6px;}
  .dt-toolbar button:hover{background:#2E86DE;color:white;}
  table.dt{width:100%;border-collapse:collapse;font-size:13px;}
  table.dt th{background:#f0f5ff;padding:8px;text-align:center;border:1px solid #e5e5e5;font-weight:600;position:sticky;top:0;}
  table.dt td{padding:6px 8px;border:1px solid #eef0f3;text-align:center;}
  table.dt td.obj{text-align:left;}
  table.dt tr.lv1{background:#eaf2ff;cursor:pointer;}
  table.dt tr.lv1:hover{background:#dceaff;}
  table.dt tr.lv2{background:#f7f9fc;cursor:pointer;}
  table.dt tr.lv2:hover{background:#eef3fb;}
  table.dt tr.lv3h{background:#fafbfd;}
  table.dt tr.mop-row{background:#fff7f0;}
  table.dt tr.st-row{background:#f0f6ff;}
  .ind2{padding-left:30px;}
  .ind3{padding-left:54px;}
  .ind4{padding-left:74px;}
  .btn{display:inline-block;width:14px;color:#2E86DE;font-weight:700;cursor:pointer;}
  td.mop,th.mop{color:#E8743B;}
  td.st,th.st{color:#2E86DE;}
  td.diff{color:#c0392b;}
  .muted{color:#aaa;}
  .tag{display:inline-block;font-size:11px;padding:1px 7px;border-radius:9px;background:#e0e0e0;color:#555;margin-left:4px;}
  .tag.proc{background:#ede7f6;color:#5e35b1;}
  .tag.mop{background:#fdebe0;color:#c0560b;}
  .tag.st{background:#e3f0ff;color:#1e5fb0;}
</style>
<div class="dt-wrap">
  <div class="dt-title">图4 · 叶片流水号下钻明细表</div>
  <div class="dt-hint">点击行逐层展开：第一层 叶片汇总（14片） → 第二层 工序×叶面(PS/SS)分开对比 → 第三层 该面 MOP记录 / ST工步明细</div>
  <div class="dt-toolbar">
    <button onclick="expandAll(1)">全部展开·叶片</button>
    <button onclick="expandAll(2)">全部展开·工序</button>
    <button onclick="collapseAll()">全部折叠</button>
  </div>
  <table class="dt" id="drill">
    <thead><tr><th class="obj" style="text-align:left">对象</th><th>开始时间</th><th>结束时间</th><th class="mop">MOP周期(分)</th><th class="st">ST周期(分)</th><th>差异</th><th>得分</th></tr></thead>
    <tbody id="drill-body"></tbody>
  </table>
</div>
<script>
const DRILL = ''' + drill_json + ''';
const tbody = document.getElementById('drill-body');
function renderL1(){
  tbody.innerHTML='';
  DRILL.forEach((b,i)=>{
    const tr=document.createElement('tr'); tr.className='lv1'; tr.dataset.gid='g'+i; tr.dataset.expanded='0';
    tr.innerHTML='<td class="obj"><span class="btn">&#9654;</span> <b>'+b.叶片+'</b> <span class="tag">叶片</span></td>'
      +'<td class="muted">6工序汇总</td><td class="muted">—</td>'
      +'<td class="mop"><b>'+b.MOP总.toFixed(1)+'</b></td>'
      +'<td class="st"><b>'+b.ST总.toFixed(1)+'</b></td>'
      +'<td class="diff">'+b.差异.toFixed(1)+' / <b>'+b['差异%'].toFixed(1)+'%</b></td><td class="muted">—</td>';
    tr.onclick=()=>toggleL1(tr,b,'g'+i);
    tbody.appendChild(tr);
  });
}
function toggleL1(tr,b,gid){
  if(tr.dataset.expanded==='1'){
    document.querySelectorAll('#drill tr.sub[data-owner="'+gid+'"]').forEach(r=>r.remove());
    tr.dataset.expanded='0'; tr.querySelector('.btn').innerHTML='&#9654;';
    return;
  }
  tr.dataset.expanded='1'; tr.querySelector('.btn').innerHTML='&#9660;';
  let ref=tr;
  b.faces.forEach((p,j)=>{
    const oid=gid+'-'+j;
    const tr2=document.createElement('tr'); tr2.className='lv2 sub'; tr2.dataset.owner=gid; tr2.dataset.oid=oid; tr2.dataset.expanded='0';
    tr2.innerHTML='<td class="obj ind2"><span class="btn">&#9654;</span> '+p.工序名+' · <b>'+p.叶面+'面</b> <span class="tag proc">'+p.工序+'</span></td>'
      +'<td class="muted">工序·面汇总</td><td class="muted">—</td>'
      +'<td class="mop">'+p.MOP周期.toFixed(1)+'</td>'
      +'<td class="st">'+p.ST周期.toFixed(1)+'</td>'
      +'<td class="diff">'+p.差异.toFixed(1)+' / <b>'+p['差异%'].toFixed(1)+'%</b></td><td class="muted">—</td>';
    tr2.onclick=(e)=>{e.stopPropagation();toggleL2(tr2,p,oid);};
    ref.after(tr2); ref=tr2;
  });
}
function toggleL2(tr2,p,oid){
  if(tr2.dataset.expanded==='1'){
    document.querySelectorAll('#drill tr.sub[data-owner="'+oid+'"]').forEach(r=>r.remove());
    tr2.dataset.expanded='0'; tr2.querySelector('.btn').innerHTML='&#9654;';
    return;
  }
  tr2.dataset.expanded='1'; tr2.querySelector('.btn').innerHTML='&#9660;';
  let ref=tr2;
  if(p.mop_rows.length){
    const h=document.createElement('tr'); h.className='lv3h sub'; h.dataset.owner=oid;
    h.innerHTML='<td class="obj ind3" colspan="7"><span class="tag mop">MOP 工序级明细</span> '+p.mop_rows.length+' 条 · '+p.叶面+'面';
    ref.after(h); ref=h;
    p.mop_rows.forEach(m=>{
      const r=document.createElement('tr'); r.className='lv3 sub mop-row'; r.dataset.owner=oid;
      r.innerHTML='<td class="obj ind4">工序记录</td><td>'+m.开始+'</td><td>'+m.结束+'</td>'
        +'<td class="mop">'+m.周期.toFixed(1)+'</td><td class="muted">—</td><td class="muted">工时 '+m.工时.toFixed(0)+'</td><td>'+m.得分+'</td>';
      ref.after(r); ref=r;
    });
  }
  if(p.st_rows.length){
    const h=document.createElement('tr'); h.className='lv3h sub'; h.dataset.owner=oid;
    h.innerHTML='<td class="obj ind3" colspan="7"><span class="tag st">ST 工步级明细</span> '+p.st_rows.length+' 条 · '+p.叶面+'面';
    ref.after(h); ref=h;
    p.st_rows.forEach(s=>{
      const r=document.createElement('tr'); r.className='lv3 sub st-row'; r.dataset.owner=oid;
      r.innerHTML='<td class="obj ind4">'+s.工步+' '+s.描述+'</td><td>'+s.开始+'</td><td>'+s.结束+'</td>'
        +'<td class="muted">—</td><td class="st">'+s.周期.toFixed(1)+'</td><td class="muted">工时 '+s.工时.toFixed(0)+'</td><td>'+s.得分+'</td>';
      ref.after(r); ref=r;
    });
  }
}
function expandAll(level){
  collapseAll();
  document.querySelectorAll('#drill tr.lv1').forEach((tr,i)=>{
    if(tr.dataset.expanded!=='1'){ tr.click(); }
    if(level>=2){
      setTimeout(()=>{
        document.querySelectorAll('#drill tr.lv2').forEach(t2=>{ if(t2.dataset.expanded!=='1') t2.click(); });
      },50);
    }
  });
}
function collapseAll(){
  document.querySelectorAll('#drill tr.sub').forEach(r=>r.remove());
  document.querySelectorAll('#drill tr.lv1').forEach(tr=>{tr.dataset.expanded='0'; tr.querySelector('.btn').innerHTML='&#9654;';});
  document.querySelectorAll('#drill tr.lv2').forEach(tr=>{tr.dataset.expanded='0'; tr.querySelector('.btn').innerHTML='&#9654;';});
}
renderL1();
</script>
'''

# ---------- 组合 HTML ----------
html = f"""<!DOCTYPE html>
<html lang="zh-CN"><head><meta charset="utf-8">
<title>作业组合周期对比甘特图分析（叶片流水号索引）</title>
<style>
  body {{ font-family: 'Microsoft YaHei', SimHei, sans-serif; background:#f7f8fa; margin:0; padding:0; color:#222; }}
  .wrap {{ max-width:1280px; margin:0 auto; padding:24px; }}
  h1 {{ font-size:24px; border-left:5px solid #2E86DE; padding-left:12px; margin:0 0 6px; }}
  .sub {{ color:#666; font-size:14px; margin-bottom:18px; }}
  .summary {{ background:white; border-radius:10px; padding:18px 22px; margin-bottom:20px; box-shadow:0 1px 4px rgba(0,0,0,.06); }}
  .summary h2 {{ font-size:17px; margin:0 0 10px; color:#2E86DE; }}
  .summary ul {{ margin:0; padding-left:20px; line-height:1.9; font-size:14px; }}
  .kpi-row {{ display:flex; gap:14px; flex-wrap:wrap; margin:12px 0; }}
  .kpi {{ flex:1; min-width:150px; background:#f0f5ff; border-radius:8px; padding:12px 14px; }}
  .kpi .v {{ font-size:22px; font-weight:700; color:#E8743B; }}
  .kpi .l {{ font-size:12px; color:#666; }}
  .chart {{ background:white; border-radius:10px; padding:14px; margin-bottom:22px; box-shadow:0 1px 4px rgba(0,0,0,.06); }}
  .foot {{ color:#999; font-size:12px; text-align:center; padding:14px; }}
  table {{ border-collapse:collapse; width:100%; font-size:13px; margin-top:8px; }}
  th,td {{ border:1px solid #e5e5e5; padding:5px 8px; text-align:center; }}
  th {{ background:#f0f5ff; }}
  td.b {{ text-align:left; }}
</style></head>
<body><div class="wrap">
<h1>作业组合周期对比甘特图分析（以叶片流水号为索引）</h1>
<div class="sub">数据源：MOP工时周期明细（工序级，160条）/ ST工时周期明细（工步级，1672条）｜共同叶片：14片（{common[0]}~{common[-1]}）｜作业组合：6道工序构成完整壳体制造工艺路线</div>

<div class="summary">
  <h2>核心洞察（以叶片流水号为索引）</h2>
  <div class="kpi-row">
    <div class="kpi"><div class="v">{max_row['差异%']:+.0f}%</div><div class="l">{max_row['叶片流水号']} 差异最大</div></div>
    <div class="kpi"><div class="v">{avg_diff:+.0f}%</div><div class="l">14叶片平均差异</div></div>
    <div class="kpi"><div class="v">{min_row['差异%']:+.0f}%</div><div class="l">{min_row['叶片流水号']} 差异最小</div></div>
    <div class="kpi"><div class="v">14/14</div><div class="l">叶片ST全部高于MOP</div></div>
  </div>
  <ul>
    <li><b>全部14片叶片的 ST 总周期均高于 MOP</b>，差异区间 +{min_row['差异%']:.0f}% ~ +{max_row['差异%']:.0f}%，平均 +{avg_diff:.0f}%，说明工步级明细周期系统性地大于工序级汇总周期。</li>
    <li><b>差异最大的叶片是 {max_row['叶片流水号']}（+{max_row['差异%']:.0f}%）</b>：MOP总周期 {max_row['MOP总']:.0f}分 vs ST总周期 {max_row['ST总']:.0f}分，差距 {max_row['差异']:.0f}分钟；其次为 F260226（+93%）。</li>
    <li><b>差异按工序归因</b>（见热力图）：JP003预制件安放、MOP240/MOP270玻纤布铺设是差异主来源；MOP280流道/MOP290真空系统差异极小。</li>
    <li><b>差异本质在周期口径</b>：同一叶片同一工序，MOP与ST的真实开始/结束时间完全一致，"周期(分钟)"统计口径不同——MOP为工序级净作业时间，ST为工步级明细周期之和（含辅助/准备工步）。</li>
  </ul>
  <table>
    <tr><th>叶片流水号</th><th>MOP总周期</th><th>ST总周期</th><th>差异(分)</th><th>差异%</th></tr>
    {''.join(f"<tr><td class='b'>{r['叶片流水号']}</td><td>{r['MOP总']:.1f}</td><td>{r['ST总']:.1f}</td><td>{r['差异']:+.1f}</td><td style='color:#c0392b;font-weight:700'>{r['差异%']:+.1f}%</td></tr>" for _,r in tot.iterrows())}
    <tr style="background:#fff7e6;font-weight:700"><td class='b'>平均</td><td>{avg_mop_tot:.1f}</td><td>{avg_st_tot:.1f}</td><td>{avg_st_tot-avg_mop_tot:+.1f}</td><td style='color:#c0392b'>{avg_diff:+.1f}%</td></tr>
  </table>
</div>

<div class="chart">{pio.to_html(fig1, full_html=False, include_plotlyjs='cdn')}</div>
<div class="chart">{pio.to_html(fig2, full_html=False, include_plotlyjs=False)}</div>
<div class="chart">{pio.to_html(fig3, full_html=False, include_plotlyjs=False)}</div>

{DRILL_HTML}

<div class="foot">作业组合周期对比甘特图分析 · 索引维度=叶片流水号 · 共同叶片14片 · 含下钻明细表 · 生成于 2026-07-20</div>
</div></body></html>"""

with open(OUT_HTML, 'w', encoding='utf-8') as f:
    f.write(html)
print('OK ->', OUT_HTML)
print(f'共同叶片:{len(common)} 平均差异:{avg_diff}% 最大:{max_row["叶片流水号"]}({max_row["差异%"]}%) 最小:{min_row["叶片流水号"]}({min_row["差异%"]}%)')
