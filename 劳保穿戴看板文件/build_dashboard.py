import json
import datetime
import os

script_dir = os.path.dirname(os.path.abspath(__file__))

# Load data
with open(os.path.join(script_dir, 'dashboard_data.json'), 'r', encoding='utf-8') as f:
    data = json.load(f)

data_json = json.dumps(data, ensure_ascii=False)

# Read HTML template
with open(os.path.join(script_dir, 'dashboard_template.html'), 'r', encoding='utf-8') as f:
    html = f.read()

# Replace placeholders
html = html.replace('__DATA__', data_json)
html = html.replace('__DATE_START__', data['summary']['date_range']['start'])
html = html.replace('__DATE_END__', data['summary']['date_range']['end'])
html = html.replace('__TOTAL__', str(data['summary']['total']))
html = html.replace('__GENERATED_TIME__', datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'))

out_path = os.path.join(script_dir, '劳保穿戴违规事件分析报表.html')
with open(out_path, 'w', encoding='utf-8') as f:
    f.write(html)

print('Dashboard saved to:', out_path)
print('File size:', round(len(html) / 1024, 1), 'KB')
