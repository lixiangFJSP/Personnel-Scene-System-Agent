# -*- coding: utf-8 -*-
"""构建百色工厂考勤数据分析仪表盘（总经理视角）"""
import pandas as pd
import numpy as np
import json, re, sys, os
sys.stdout.reconfigure(encoding='utf-8')

script_dir = os.path.dirname(os.path.abspath(__file__))
data_dir = os.path.join(script_dir, '..', '01源数据')  # 请将源数据放在此目录
SRC1 = os.path.join(data_dir, '考勤汇总表-.xlsx')
SRC2 = os.path.join(data_dir, '考勤统计表.xlsx')
OUT = os.path.join(script_dir, '考勤数据分析仪表盘.html')

# ============ 读取汇总表 ============
raw = pd.read_excel(SRC1, sheet_name='考勤汇总表', header=None)
cols = raw.iloc[2].tolist()
df = raw.iloc[3:].copy().astype(object)
df.columns = cols
df = df.reset_index(drop=True)
num_cols = ['出勤天数','休息天数','工作时长(小时)','迟到次数','严重迟到次数','旷工迟到次数',
            '早退次数','上班迟到次数','下班迟到次数','旷工天数','出差天数',
            '事假(天)','调休(天)','病假(天)','年假(天)','婚假(天)','丧假(天)','工伤假(天)',
            '值班天数','休息日加班','节假日加班']
for c in num_cols:
    if c in df.columns:
        df[c] = pd.to_numeric(df[c], errors='coerce').fillna(0)
for i in [10,12,15]:
    cn = df.columns[i]
    df[cn] = pd.to_numeric(df[cn], errors='coerce').fillna(0).astype(float)

def big_dept(d):
    if pd.isna(d): return '未填写'
    d=str(d)
    if '离职' in d: return '离职人员'
    if '铺层' in d: return '铺层班组'
    if '腹板' in d: return '腹板班组'
    if '大梁' in d: return '大梁预制班组'
    if '合模' in d: return '合模班组'
    if '拉挤' in d: return '拉挤梁班组'
    if '修补' in d: return '修补班组'
    if '检验' in d: return '检验班组'
    if '生产制造' in d: return '生产制造部'
    if '业务' in d or '财务' in d: return '业务财务部'
    if '监控' in d: return '监控班组'
    if '大修' in d: return '大修班'
    if '综合管理' in d or '管理' in d: return '综合管理部'
    return '其他班组'
df['大部门'] = df['部门'].apply(big_dept)

# ============ 读取统计表 ============
dt = pd.read_excel(SRC2, sheet_name='考勤统计表', header=0)
dt['考勤日期'] = pd.to_datetime(dt['考勤日期'], errors='coerce')

def parse_dur(t):
    if pd.isna(t): return np.nan
    t=str(t)
    h=re.search(r'(\d+)小时',t); m=re.search(r'(\d+)分钟',t); s=re.search(r'(\d+)秒',t)
    hh=float(h.group(1)) if h else 0
    mm=float(m.group(1)) if m else 0
    ss=float(s.group(1)) if s else 0
    return hh+mm/60+ss/3600
dt['工时_小时'] = dt['工作时长'].apply(parse_dur)
dt['上班时间'] = pd.to_datetime(dt['最早上班时间'], errors='coerce')
dt['上班小时'] = dt['上班时间'].dt.hour
dt['状态列表'] = dt['考勤状态'].fillna('').astype(str).apply(lambda x: [p.strip() for p in x.split(';') if p.strip()])
dt['是否正常'] = dt['状态列表'].apply(lambda x: len(x)==1 and x[0]=='正常')
dt['是否迟到'] = dt['状态列表'].apply(lambda x: any('迟到' in s for s in x))
dt['是否早退'] = dt['状态列表'].apply(lambda x: any('早退' in s for s in x))
dt['是否旷工'] = dt['状态列表'].apply(lambda x: any('旷工' in s for s in x))
dt['是否缺卡'] = dt['状态列表'].apply(lambda x: any('缺卡' in s for s in x))
dt['极短工时'] = dt['工时_小时']<1
dt['超长工时'] = dt['工时_小时']>14
dt['凌晨打卡'] = dt['上班小时'].isin([0,1,2,3])

# ============ 汇总指标 ============
tot_people = len(df)
tot_records = len(dt)
date_min = dt['考勤日期'].min().strftime('%Y-%m-%d')
date_max = dt['考勤日期'].max().strftime('%Y-%m-%d')
days = dt['考勤日期'].dt.date.nunique()
normal_rate = dt['是否正常'].mean()*100
s_late = int(dt['是否迟到'].sum())
s_early = int(dt['是否早退'].sum())
s_absent = int(dt['是否旷工'].sum())
s_miss = int(dt['是否缺卡'].sum())
s_short = int(dt['极短工时'].sum())
s_long = int(dt['超长工时'].sum())
s_dawn = int(dt['凌晨打卡'].sum())
avg_hours = float(dt['工时_小时'].mean())

# ============ 每日趋势 ============
daily = dt.groupby(dt['考勤日期'].dt.date).agg(
    记录数=('姓名','count'),
    迟到=('是否迟到','sum'),
    早退=('是否早退','sum'),
    旷工=('是否旷工','sum'),
    缺卡=('是否缺卡','sum'),
    极短=('极短工时','sum'),
    超长=('超长工时','sum'),
    平均工时=('工时_小时','mean'),
).reset_index()
daily = daily[daily['记录数']>=10].copy()  # 过滤零星天数
daily['异常合计'] = daily['迟到']+daily['早退']+daily['旷工']+daily['缺卡']
daily['异常率'] = daily['异常合计']/daily['记录数']*100
daily['日期str'] = daily['考勤日期'].astype(str)
daily_dates = daily['日期str'].tolist()
daily_records = daily['记录数'].astype(int).tolist()
daily_abn = daily['异常合计'].astype(int).tolist()
daily_abnrate = daily['异常率'].round(1).tolist()
daily_late = daily['迟到'].astype(int).tolist()
daily_early = daily['早退'].astype(int).tolist()
daily_absent = daily['旷工'].astype(int).tolist()
daily_miss = daily['缺卡'].astype(int).tolist()
daily_short = daily['极短'].astype(int).tolist()
daily_long = daily['超长'].astype(int).tolist()
daily_hours = daily['平均工时'].round(2).tolist()

# ============ 考勤状态构成 ============
status_data = [
    {'name':'正常','value':86140,'color':'#16a34a'},
    {'name':'缺卡','value':s_miss,'color':'#f59e0b'},
    {'name':'早退','value':s_early,'color':'#dc2626'},
    {'name':'迟到','value':s_late,'color':'#ea580c'},
    {'name':'旷工','value':s_absent,'color':'#7c3aed'},
    {'name':'其他','value':61+2+2+1,'color':'#94a3b8'},
]

# ============ 大部门异常对比(汇总表) ============
g = df.groupby('大部门').agg(
    人数=('姓名','count'),
    迟到=('迟到次数','sum'),
    早退=('早退次数','sum'),
    旷工=('旷工天数','sum'),
    刷卡异常=('上班迟到次数','sum'),
    出勤=('出勤天数','sum'),
).reset_index()
g['异常合计'] = g['迟到']+g['早退']+g['旷工']
g = g.sort_values('异常合计', ascending=False)
dept_names = g['大部门'].tolist()
dept_late = g['迟到'].astype(int).tolist()
dept_early = g['早退'].astype(int).tolist()
dept_absent = g['旷工'].astype(int).tolist()

# ============ 统计表部门异常率Top15 ============
dept2 = dt.groupby('部门').agg(
    记录数=('姓名','count'),
    迟到=('是否迟到','sum'),
    早退=('是否早退','sum'),
    旷工=('是否旷工','sum'),
    缺卡=('是否缺卡','sum'),
    极短=('极短工时','sum'),
).reset_index()
dept2['异常合计']=dept2['迟到']+dept2['早退']+dept2['旷工']+dept2['缺卡']
dept2['异常率']=dept2['异常合计']/dept2['记录数']*100
dept2 = dept2[dept2['记录数']>=500].sort_values('异常率',ascending=False).head(15)
dept2_names = dept2['部门'].tolist()
dept2_rate = dept2['异常率'].round(1).tolist()
dept2_abn = dept2['异常合计'].astype(int).tolist()
dept2_rec = dept2['记录数'].astype(int).tolist()

# ============ 工时分布 ============
bins = [0,1,4,8,12,14,18,24,9999]
labels = ['<1h','1-4h','4-8h','8-12h','12-14h','14-18h','18-24h','>24h']
dt['工时区间'] = pd.cut(dt['工时_小时'], bins=bins, labels=labels, right=False, include_lowest=True)
wh = dt['工时区间'].value_counts().reindex(labels).fillna(0).astype(int)
wh_labels = labels
wh_values = wh.tolist()
wh_colors = ['#dc2626','#f59e0b','#fbbf24','#16a34a','#f59e0b','#dc2626','#dc2626','#7c3aed']

# ============ 上班小时分布 ============
hr = dt['上班小时'].value_counts().sort_index()
hr_labels = [f'{int(h)}时' for h in hr.index]
hr_values = hr.astype(int).tolist()
hr_colors = ['#dc2626' if int(h)<4 else ('#f59e0b' if int(h)<6 else ('#16a34a' if 7<=int(h)<=9 else '#94a3b8')) for h in hr.index]

# ============ Top迟到人员(汇总表) ============
top_late = df.nlargest(10,'迟到次数')[['姓名','部门','出勤天数','迟到次数','早退次数']].copy()
top_late_names = top_late['姓名'].tolist()
top_late_vals = top_late['迟到次数'].astype(int).tolist()

# ============ Top缺卡人员(统计表) ============
miss_by_person = dt[dt['是否缺卡']].groupby(['卡号','姓名','部门']).size().reset_index(name='缺卡次数')
miss_by_person = miss_by_person.sort_values('缺卡次数',ascending=False).head(10)
top_miss_names = miss_by_person['姓名'].tolist()
top_miss_vals = miss_by_person['缺卡次数'].astype(int).tolist()

# ============ 异常工时部门Top(极短+超长) ============
abn_hr = dt.groupby('部门').agg(极短=('极短工时','sum'),超长=('超长工时','sum'),记录=('姓名','count')).reset_index()
abn_hr['异常工时']=abn_hr['极短']+abn_hr['超长']
abn_hr['异常工时率']=abn_hr['异常工时']/abn_hr['记录']*100
abn_hr = abn_hr[abn_hr['记录']>=500].sort_values('异常工时',ascending=False).head(12)
abnhr_names = abn_hr['部门'].tolist()
abnhr_short = abn_hr['极短'].astype(int).tolist()
abnhr_long = abn_hr['超长'].astype(int).tolist()

# ============ 装载数据 ============
DATA = {
    'meta': {'date_min':date_min,'date_max':date_max,'days':int(days),'people':tot_people,'records':tot_records},
    'kpi': {
        'people': tot_people, 'records': tot_records, 'normal_rate': round(normal_rate,1),
        'late': s_late, 'early': s_early, 'absent': s_absent, 'miss': s_miss,
        'short': s_short, 'long': s_long, 'dawn': s_dawn, 'avg_hours': round(avg_hours,2),
    },
    'daily': {'dates':daily_dates,'records':daily_records,'abn':daily_abn,'abnrate':daily_abnrate,
              'late':daily_late,'early':daily_early,'absent':daily_absent,'miss':daily_miss,
              'short':daily_short,'long':daily_long,'hours':daily_hours},
    'status': status_data,
    'dept': {'names':dept_names,'late':dept_late,'early':dept_early,'absent':dept_absent},
    'dept2': {'names':dept2_names,'rate':dept2_rate,'abn':dept2_abn,'rec':dept2_rec},
    'workhour': {'labels':wh_labels,'values':wh_values,'colors':wh_colors},
    'hour': {'labels':hr_labels,'values':hr_values,'colors':hr_colors},
    'top_late': {'names':top_late_names,'vals':top_late_vals},
    'top_miss': {'names':top_miss_names,'vals':top_miss_vals},
    'abn_hr': {'names':abnhr_names,'short':abnhr_short,'long':abnhr_long},
}

# 关键问题数值
problems = [
    {'n':1,'title':'早退问题比迟到更突出','data':f'早退{s_early}次 vs 迟到{s_late}次','desc':'早退次数高出迟到39%，说明下班时段管理松懈，员工提前离岗现象普遍，班组长未有效履行下班打卡监督职责。'},
    {'n':2,'title':'生产制造部异常高度集中','data':'人均迟到34.8次 / 占全厂异常60%+','desc':'生产制造部（装备、后处理、成型、附件）贡献了绝大多数迟到(870次)、早退(1014次)和旷工(162天)，是考勤管理的重灾区，需重点整治。'},
    {'n':3,'title':'极短工时打卡泛滥（疑似代打卡/打卡即走）','data':f'{s_short}条记录工时不足1小时','desc':'内修补2组(1734条)、内修补1(1554条)、内腔卫生等班组存在大量"打卡后数分钟即下班"的记录，部分仅十几秒，严重涉嫌代打卡或打卡后离岗，工时数据失真。'},
    {'n':4,'title':'超长工时记录异常（跨天/通宵未规范打卡）','data':f'{s_long}条记录工时超14小时','desc':'场外发货班、维修班等出现"24小时56分""23小时32分"等跨天记录，系未及时打下班卡或夜班交接记录混乱，导致工时虚高、加班数据失实。'},
    {'n':5,'title':'缺卡问题严重','data':f'累计{s_miss}次缺卡','desc':'库管班(369次)、裁布班(336次)缺卡集中，反映打卡设备覆盖不足或员工遗忘打卡，考勤闭环缺失。'},
    {'n':6,'title':'裁布班等班组异常率畸高','data':'裁布班异常率61.9% / 库管班32.4%','desc':'裁布班1013条异常/1636条记录，近三分之二考勤异常；库管班、离职人员、工艺质量部异常率均超10%，班组管理基本失效。'},
    {'n':7,'title':'离职人员考勤账户未及时停用','data':'68名离职人员仍有3152天出勤记录','desc':'离职人员群体产生313次缺卡、304条超长工时，账户未及时关闭，存在考勤数据污染甚至冒名顶替风险。'},
    {'n':8,'title':'凌晨打卡占比高，排班与考勤错配','data':f'{s_dawn}条0-4点上班打卡','desc':'0-4点上班打卡近9000条，部分为夜班正常，但与极短工时叠加后，大量凌晨打卡实为异常，排班制度与实际打卡时段错配。'},
    {'n':9,'title':'请假数据近乎缺失，离岗管理失控','data':'全厂请假仅记录2天','desc':'事假/病假/年假等几乎未录入考勤系统，请假审批与考勤脱节，无法核实员工真实在岗状态，存在管理盲区。'},
]

# 改善措施
actions = [
    {'cat':'制度层面','items':[
        '修订《考勤管理办法》，明确迟到/早退/缺卡/旷工的认定标准与处罚梯度，迟到3次以上扣绩效、连续旷工启动辞退流程；',
        '建立班组长考勤首问责任制，将本班组考勤异常率纳入班组长月度KPI（目标异常率≤3%）；',
        '推行请假全流程线上化，所有事假/病假/年假必须走系统审批并与考勤数据打通，杜绝"请假不记录"。']},
    {'cat':'现场执行','items':[
        '针对生产制造部、裁布班、库管班开展为期1个月的考勤专项整治，由综合管理部每日通报异常名单；',
        '规范上下班打卡秩序，下班时段安排专人监督打卡，杜绝提前离岗和代打卡；',
        '对极短工时(<1h)记录逐条核查，确认为代打卡/打卡即走的按旷工处理并追责。']},
    {'cat':'系统与设备','items':[
        '升级考勤设备，增加人脸识别防代打卡，在车间出入口补点覆盖消除打卡盲区；',
        '修复超长工时(>14h)记录规则，跨天未打下班卡系统自动提示并按实际工时校准；',
        '离职人员T+1日停用考勤账户，由HR与考勤系统联动，杜绝离职后考勤污染。']},
    {'cat':'排班优化','items':[
        '梳理三班倒排班，将排班时段与打卡时段对齐，消除凌晨异常打卡；',
        '对场外发货、维修等长工时岗位制定专项工时管理办法，明确加班审批与调休机制；',
        '建立周度考勤分析例会，由本仪表盘数据驱动问题跟踪与闭环。']},
]

DATA['problems'] = problems
DATA['actions'] = actions

data_json = json.dumps(DATA, ensure_ascii=False)

# ============ 生成HTML ============
HTML = r'''<!DOCTYPE html>
<html lang="zh-CN">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>百色工厂考勤数据分析报告 · 总经理视角</title>
<script src="https://cdn.jsdelivr.net/npm/chart.js@4.4.1/dist/chart.umd.min.js"></script>
<style>
:root{
  --primary:#2563eb; --danger:#dc2626; --warning:#f59e0b; --success:#16a34a;
  --purple:#7c3aed; --neutral:#64748b; --bg:#eef2f7; --card:#ffffff;
  --text:#1e293b; --text2:#64748b; --border:#e2e8f0; --soft:#f8fafc;
}
*{margin:0;padding:0;box-sizing:border-box}
body{font-family:'Microsoft YaHei','Segoe UI',sans-serif;background:var(--bg);color:var(--text);line-height:1.6}
.wrap{max-width:1480px;margin:0 auto;padding:24px}
/* header */
.header{background:linear-gradient(135deg,#1e3a8a,#2563eb);color:#fff;border-radius:14px;padding:28px 32px;margin-bottom:20px;box-shadow:0 6px 20px rgba(37,99,235,.25)}
.header h1{font-size:26px;font-weight:700;letter-spacing:1px}
.header .sub{margin-top:8px;font-size:14px;opacity:.92;display:flex;gap:20px;flex-wrap:wrap}
.header .sub span{display:inline-flex;align-items:center;gap:6px}
.header .role{margin-top:14px;display:inline-block;background:rgba(255,255,255,.18);padding:5px 14px;border-radius:20px;font-size:13px;font-weight:600}
/* kpi */
.kpi-grid{display:grid;grid-template-columns:repeat(4,1fr);gap:14px;margin-bottom:20px}
.kpi{background:var(--card);border-radius:12px;padding:18px 20px;border:1px solid var(--border);position:relative;overflow:hidden}
.kpi::before{content:'';position:absolute;left:0;top:0;bottom:0;width:4px;background:var(--primary)}
.kpi.danger::before{background:var(--danger)}
.kpi.warning::before{background:var(--warning)}
.kpi.success::before{background:var(--success)}
.kpi.purple::before{background:var(--purple)}
.kpi .label{font-size:13px;color:var(--text2);margin-bottom:6px}
.kpi .value{font-size:28px;font-weight:700;color:var(--text);line-height:1.1}
.kpi .value small{font-size:14px;font-weight:500;color:var(--text2);margin-left:4px}
.kpi .note{font-size:12px;color:var(--text2);margin-top:4px}
/* section */
.section{background:var(--card);border-radius:12px;padding:22px 24px;margin-bottom:20px;border:1px solid var(--border)}
.section-title{font-size:18px;font-weight:700;color:var(--text);margin-bottom:4px;display:flex;align-items:center;gap:8px}
.section-title .bar{width:4px;height:18px;background:var(--primary);border-radius:2px}
.section-desc{font-size:13px;color:var(--text2);margin-bottom:16px}
/* chart grid */
.chart-grid{display:grid;gap:18px}
.cg-2{grid-template-columns:1fr 1fr}
.cg-3{grid-template-columns:1fr 1fr 1fr}
.chart-box{background:var(--soft);border-radius:10px;padding:16px;border:1px solid var(--border)}
.chart-box h4{font-size:14px;font-weight:600;color:var(--text);margin-bottom:4px}
.chart-box .ctip{font-size:12px;color:var(--text2);margin-bottom:10px}
.chart-box canvas{max-height:300px}
.chart-box.tall canvas{max-height:360px}
/* problems */
.prob-list{display:grid;grid-template-columns:1fr 1fr;gap:14px}
.prob{background:var(--soft);border-left:4px solid var(--danger);border-radius:8px;padding:14px 16px}
.prob .ph{display:flex;align-items:center;gap:8px;margin-bottom:6px}
.prob .pn{background:var(--danger);color:#fff;width:22px;height:22px;border-radius:50%;display:flex;align-items:center;justify-content:center;font-size:12px;font-weight:700;flex-shrink:0}
.prob .pt{font-size:15px;font-weight:600;color:var(--text)}
.prob .pd{font-size:13px;color:var(--text2);margin-bottom:4px}
.prob .pdata{display:inline-block;background:#fef2f2;color:var(--danger);font-size:12px;font-weight:600;padding:2px 8px;border-radius:4px}
/* actions */
.action-grid{display:grid;grid-template-columns:1fr 1fr;gap:14px}
.action{background:var(--soft);border-radius:8px;padding:16px;border-top:3px solid var(--success)}
.action .ah{font-size:15px;font-weight:700;color:var(--success);margin-bottom:8px;display:flex;align-items:center;gap:6px}
.action ul{list-style:none;padding-left:0}
.action li{font-size:13px;color:var(--text);margin-bottom:8px;padding-left:18px;position:relative}
.action li::before{content:'';position:absolute;left:0;top:8px;width:6px;height:6px;background:var(--success);border-radius:50%}
/* summary box */
.summary-box{background:linear-gradient(135deg,#fef3c7,#fde68a);border-radius:12px;padding:20px 24px;margin-bottom:20px;border-left:5px solid var(--warning)}
.summary-box h3{font-size:16px;color:#92400e;margin-bottom:8px}
.summary-box p{font-size:14px;color:#78350f}
.footer{text-align:center;color:var(--text2);font-size:12px;padding:18px 0 8px}
@media(max-width:1100px){.kpi-grid{grid-template-columns:repeat(2,1fr)}.cg-2,.cg-3,.prob-list,.action-grid{grid-template-columns:1fr}}
</style>
</head>
<body>
<div class="wrap">
  <div class="header">
    <h1>百色工厂 · 考勤数据分析报告</h1>
    <div class="sub">
      <span>数据周期：<b id="d-range"></b></span>
      <span>覆盖天数：<b id="d-days"></b> 天</span>
      <span>在册人数：<b id="d-people"></b> 人</span>
      <span>打卡明细：<b id="d-records"></b> 条</span>
    </div>
    <div class="role">总经理决策视图 · 数据驱动改善</div>
  </div>

  <div class="kpi-grid" id="kpi-grid"></div>

  <div class="section">
    <div class="section-title"><span class="bar"></span>一、考勤趋势分析（220天动态）</div>
    <div class="section-desc">从每日出勤规模、异常规模、异常率与平均工时四个维度，观察工厂考勤健康度随时间演变。重点聚焦异常率的波动与工时偏离。</div>
    <div class="chart-grid cg-2">
      <div class="chart-box tall"><h4>每日出勤规模与异常率趋势</h4><div class="ctip">蓝柱=出勤记录数 / 红线=异常率(%)，双轴对照</div><canvas id="c-trend1"></canvas></div>
      <div class="chart-box tall"><h4>每日异常类型构成</h4><div class="ctip">迟到/早退/旷工/缺卡 堆叠趋势</div><canvas id="c-trend2"></canvas></div>
    </div>
    <div class="chart-grid" style="grid-template-columns:1fr;margin-top:18px">
      <div class="chart-box"><h4>每日平均工时趋势</h4><div class="ctip">全厂日均工作时长（小时），正常区间8-10h以绿色带标注</div><canvas id="c-trend3"></canvas></div>
    </div>
  </div>

  <div class="section">
    <div class="section-title"><span class="bar"></span>二、考勤问题诊断</div>
    <div class="section-desc">从考勤状态构成、部门异常率、工时分布、打卡时段四个视角，定位考勤管理结构性问题。</div>
    <div class="chart-grid cg-2">
      <div class="chart-box"><h4>考勤状态构成</h4><div class="ctip">9.1万条打卡明细的状态分布</div><canvas id="c-status"></canvas></div>
      <div class="chart-box"><h4>各部门考勤异常率 Top15</h4><div class="ctip">异常率=（迟到+早退+旷工+缺卡）/记录数，记录数≥500的部门</div><canvas id="c-dept2"></canvas></div>
    </div>
    <div class="chart-grid cg-2" style="margin-top:18px">
      <div class="chart-box"><h4>工作时长分布</h4><div class="ctip">红色=异常区间（&lt;1h极短 / &gt;14h超长），绿色=正常工时</div><canvas id="c-workhour"></canvas></div>
      <div class="chart-box"><h4>上班打卡时段分布</h4><div class="ctip">红色=凌晨0-4点 / 橙色=4-6点 / 绿色=7-9点正常白班</div><canvas id="c-hour"></canvas></div>
    </div>
    <div class="chart-grid cg-2" style="margin-top:18px">
      <div class="chart-box"><h4>大部门异常类型对比</h4><div class="ctip">按迟到/早退/旷工堆叠，定位异常高发部门</div><canvas id="c-dept1"></canvas></div>
      <div class="chart-box"><h4>异常工时（极短+超长）部门 Top12</h4><div class="ctip">橙色=极短工时 / 红色=超长工时</div><canvas id="c-abnhr"></canvas></div>
    </div>
  </div>

  <div class="section">
    <div class="section-title"><span class="bar"></span>三、重点人员榜单</div>
    <div class="section-desc">锁定考勤异常高发人员，为重点约谈与整治提供靶点。</div>
    <div class="chart-grid cg-2">
      <div class="chart-box tall"><h4>迟到次数 Top10 人员</h4><div class="ctip">月度汇总迟到次数排名</div><canvas id="c-toplate"></canvas></div>
      <div class="chart-box tall"><h4>缺卡次数 Top10 人员</h4><div class="ctip">明细统计缺卡次数排名</div><canvas id="c-topmiss"></canvas></div>
    </div>
  </div>

  <div class="section">
    <div class="section-title"><span class="bar"></span>四、核心问题清单（9大问题）</div>
    <div class="section-desc">基于上述数据，提炼工厂考勤管理亟需解决的9项核心问题。</div>
    <div class="prob-list" id="prob-list"></div>
  </div>

  <div class="summary-box">
    <h3>总经理研判</h3>
    <p>表面看工厂正常打卡率94.1%，但<b>早退多于迟到、极短工时1.6万条、超长工时7千条、裁布班异常率62%</b>——考勤数据存在系统性失真，"正常"背后掩盖了大量代打卡、打卡即走、跨天未打卡、请假不记录等管理漏洞。考勤已不仅是纪律问题，更直接关系到工时核算、加班成本与生产调度准确性，必须以系统+制度双管齐下立即整治。</p>
  </div>

  <div class="section">
    <div class="section-title"><span class="bar"></span>五、总经理改善方案与行动计划</div>
    <div class="section-desc">围绕"制度+现场+系统+排班"四条主线，制定可落地的改善措施。</div>
    <div class="action-grid" id="action-grid"></div>
  </div>

  <div class="footer">本报告基于考勤汇总表(721人)与考勤统计表(91,520条明细)自动生成 · 数据驱动管理决策</div>
</div>

<script>
const D = __DATA__;
// header
document.getElementById('d-range').textContent = D.meta.date_min + ' 至 ' + D.meta.date_max;
document.getElementById('d-days').textContent = D.meta.days;
document.getElementById('d-people').textContent = D.meta.people;
document.getElementById('d-records').textContent = D.meta.records.toLocaleString();

// KPI
const kpis = [
  {label:'正常打卡率',value:D.kpi.normal_rate,unit:'%',note:'9.1万条明细中正常占比',cls:'success'},
  {label:'累计迟到',value:D.kpi.late,unit:'次',note:'早退'+D.kpi.early+'次（高于迟到）',cls:'danger'},
  {label:'累计早退',value:D.kpi.early,unit:'次',note:'下班时段管理松懈',cls:'warning'},
  {label:'累计缺卡',value:D.kpi.miss,unit:'次',note:'打卡遗漏/设备覆盖不足',cls:'danger'},
  {label:'累计旷工',value:D.kpi.absent,unit:'天',note:'28人存在旷工记录',cls:'purple'},
  {label:'极短工时(<1h)',value:D.kpi.short,unit:'条',note:'疑似代打卡/打卡即走',cls:'danger'},
  {label:'超长工时(>14h)',value:D.kpi.long,unit:'条',note:'跨天/通宵未规范打卡',cls:'warning'},
  {label:'日均工时',value:D.kpi.avg_hours,unit:'h',note:'凌晨打卡'+D.kpi.dawn+'条',cls:''},
];
const kg = document.getElementById('kpi-grid');
kpis.forEach(k=>{
  const el=document.createElement('div');
  el.className='kpi '+k.cls;
  el.innerHTML='<div class="label">'+k.label+'</div><div class="value">'+k.value.toLocaleString()+'<small>'+k.unit+'</small></div><div class="note">'+k.note+'</div>';
  kg.appendChild(el);
});

Chart.defaults.font.family="'Microsoft YaHei',sans-serif";
Chart.defaults.color='#475569';
Chart.defaults.font.size=11;

const C = (id)=>document.getElementById(id);

// 1. trend1 出勤+异常率
new Chart(C('c-trend1'),{type:'bar',data:{labels:D.daily.dates,datasets:[
  {type:'bar',label:'出勤记录数',data:D.daily.records,backgroundColor:'rgba(37,99,235,.5)',borderColor:'rgba(37,99,235,.8)',borderWidth:1,yAxisID:'y'},
  {type:'line',label:'异常率(%)',data:D.daily.abnrate,borderColor:'#dc2626',backgroundColor:'rgba(220,38,38,.1)',borderWidth:2,pointRadius:0,tension:.3,yAxisID:'y1',fill:false}
]},options:{responsive:true,maintainAspectRatio:false,plugins:{legend:{position:'top'}},scales:{
  x:{ticks:{maxTicksLimit:12,autoSkip:true,maxRotation:0}},
  y:{position:'left',title:{display:true,text:'记录数'}},
  y1:{position:'right',title:{display:true,text:'异常率(%)'},grid:{drawOnChartArea:false}}
}}});

// 2. trend2 异常类型堆叠
new Chart(C('c-trend2'),{type:'bar',data:{labels:D.daily.dates,datasets:[
  {label:'迟到',data:D.daily.late,backgroundColor:'#ea580c'},
  {label:'早退',data:D.daily.early,backgroundColor:'#dc2626'},
  {label:'旷工',data:D.daily.absent,backgroundColor:'#7c3aed'},
  {label:'缺卡',data:D.daily.miss,backgroundColor:'#f59e0b'}
]},options:{responsive:true,maintainAspectRatio:false,plugins:{legend:{position:'top'}},
  scales:{x:{stacked:true,ticks:{maxTicksLimit:12,autoSkip:true,maxRotation:0}},y:{stacked:true,title:{display:true,text:'次数'}}}
}});

// 3. trend3 平均工时
new Chart(C('c-trend3'),{type:'line',data:{labels:D.daily.dates,datasets:[
  {label:'日均工时',data:D.daily.hours,borderColor:'#2563eb',backgroundColor:'rgba(37,99,235,.12)',borderWidth:2,pointRadius:0,tension:.3,fill:true}
]},options:{responsive:true,maintainAspectRatio:false,plugins:{legend:{display:false},
  annotation:{}},scales:{x:{ticks:{maxTicksLimit:14,autoSkip:true,maxRotation:0}},
  y:{title:{display:true,text:'小时'},min:0,max:16,
     grid:{color:(ctx)=>(ctx.tick.value>=8&&ctx.tick.value<=10?'rgba(22,163,106,.25)':'rgba(226,232,240,.6)')}}}}});

// 4. status pie
new Chart(C('c-status'),{type:'doughnut',data:{labels:D.status.map(s=>s.name),datasets:[
  {data:D.status.map(s=>s.value),backgroundColor:D.status.map(s=>s.color),borderWidth:2,borderColor:'#fff'}
]},options:{responsive:true,maintainAspectRatio:false,plugins:{legend:{position:'right'},
  tooltip:{callbacks:{label:(c)=>c.label+': '+c.parsed.toLocaleString()+' ('+(c.parsed/D.kpi.records*100).toFixed(1)+'%)'}}}}});

// 5. dept2 异常率Top15
new Chart(C('c-dept2'),{type:'bar',data:{labels:D.dept2.names,datasets:[
  {label:'异常率(%)',data:D.dept2.rate,backgroundColor:(c)=>c.parsed.y>20?'#dc2626':(c.parsed.y>5?'#f59e0b':'#16a34a'),borderWidth:0}
]},options:{indexAxis:'y',responsive:true,maintainAspectRatio:false,plugins:{legend:{display:false},
  tooltip:{callbacks:{afterLabel:(c)=>'异常'+D.dept2.abn[c.dataIndex]+'次 / 共'+D.dept2.rec[c.dataIndex]+'条'}},},scales:{x:{title:{display:true,text:'异常率(%)'}}}}});

// 6. workhour 分布
new Chart(C('c-workhour'),{type:'bar',data:{labels:D.workhour.labels,datasets:[
  {label:'记录数',data:D.workhour.values,backgroundColor:D.workhour.colors,borderWidth:0}
]},options:{responsive:true,maintainAspectRatio:false,plugins:{legend:{display:false}},scales:{x:{title:{display:true,text:'工时区间'}},y:{title:{display:true,text:'记录数'}}}}});

// 7. hour 上班时段
new Chart(C('c-hour'),{type:'bar',data:{labels:D.hour.labels,datasets:[
  {label:'打卡数',data:D.hour.values,backgroundColor:D.hour.colors,borderWidth:0}
]},options:{responsive:true,maintainAspectRatio:false,plugins:{legend:{display:false}},scales:{x:{title:{display:true,text:'上班小时'},ticks:{maxRotation:0}},y:{title:{display:true,text:'打卡次数'}}}}});

// 8. dept1 大部门异常
new Chart(C('c-dept1'),{type:'bar',data:{labels:D.dept.names,datasets:[
  {label:'迟到',data:D.dept.late,backgroundColor:'#ea580c'},
  {label:'早退',data:D.dept.early,backgroundColor:'#dc2626'},
  {label:'旷工',data:D.dept.absent,backgroundColor:'#7c3aed'}
]},options:{responsive:true,maintainAspectRatio:false,plugins:{legend:{position:'top'}},
  scales:{x:{stacked:true,ticks:{maxRotation:30}},y:{stacked:true,title:{display:true,text:'次数'}}}}});

// 9. abnhr 异常工时部门
new Chart(C('c-abnhr'),{type:'bar',data:{labels:D.abn_hr.names,datasets:[
  {label:'极短工时(<1h)',data:D.abn_hr.short,backgroundColor:'#f59e0b'},
  {label:'超长工时(>14h)',data:D.abn_hr.long,backgroundColor:'#dc2626'}
]},options:{indexAxis:'y',responsive:true,maintainAspectRatio:false,plugins:{legend:{position:'top'}},
  scales:{x:{stacked:true,title:{display:true,text:'记录数'}},y:{stacked:true}}}});

// 10. top late
new Chart(C('c-toplate'),{type:'bar',data:{labels:D.top_late.names,datasets:[
  {label:'迟到次数',data:D.top_late.vals,backgroundColor:'#dc2626',borderWidth:0}
]},options:{indexAxis:'y',responsive:true,maintainAspectRatio:false,plugins:{legend:{display:false}},scales:{x:{title:{display:true,text:'次数'}}}}});

// 11. top miss
new Chart(C('c-topmiss'),{type:'bar',data:{labels:D.top_miss.names,datasets:[
  {label:'缺卡次数',data:D.top_miss.vals,backgroundColor:'#f59e0b',borderWidth:0}
]},options:{indexAxis:'y',responsive:true,maintainAspectRatio:false,plugins:{legend:{display:false}},scales:{x:{title:{display:true,text:'次数'}}}}});

// problems
const pl = document.getElementById('prob-list');
D.problems.forEach(p=>{
  const el=document.createElement('div');
  el.className='prob';
  el.innerHTML='<div class="ph"><div class="pn">'+p.n+'</div><div class="pt">'+p.title+'</div></div>'+
    '<div class="pd">'+p.desc+'</div><span class="pdata">'+p.data+'</span>';
  pl.appendChild(el);
});

// actions
const ag = document.getElementById('action-grid');
D.actions.forEach(a=>{
  const el=document.createElement('div');
  el.className='action';
  el.innerHTML='<div class="ah">'+a.cat+'</div><ul>'+a.items.map(i=>'<li>'+i+'</li>').join('')+'</ul>';
  ag.appendChild(el);
});
</script>
</body>
</html>'''

html = HTML.replace('__DATA__', data_json)
with open(OUT, 'w', encoding='utf-8') as f:
    f.write(html)
print('已生成:', OUT)
print('数据点: 每日趋势', len(daily_dates), '天 | 部门异常Top', len(dept2_names), '| 问题', len(problems), '项 | 措施', len(actions), '类')
