"""Domain-specific structured prompts for each analysis module."""

def build_analysis_prompt(module: str, data_json: str) -> str:
    base_role = (
        "你是一个制造业数据分析专家，擅长从生产运营数据中发现问题、提出改善措施。"
        "请根据下面提供的数据进行深入分析，用中文回答。"
    )

    structure = """
请严格按照以下结构输出分析结果，用 Markdown 格式：

## 一、数据概况
- 关键指标概览

## 二、存在的问题
- 列出数据中暴露的 3-5 个核心问题

## 三、改善措施
- 针对每个问题给出具体可操作的改善措施

## 四、改善方法建议
- 详细的执行方案（包括责任人建议、时间节点、考核方式）"""

    modules = {
        "attendance": f"{base_role}\n你正在分析的是**无感考勤**数据（员工出勤、迟到、早退、旷工等记录）。\n{structure}",
        "safety": f"{base_role}\n你正在分析的是**劳保穿戴违规事件**数据（违规类型、部门分布、时间趋势等）。\n{structure}",
        "operations": f"{base_role}\n你正在分析的是**作业组合**数据（MOP工序级与ST工步级周期对比数据）。\n{structure}",
        "workhours": f"{base_role}\n你正在分析的是**工时统计**数据（各工步/批次工时、节拍趋势等）。\n{structure}",
    }

    prompt = modules.get(module, modules["attendance"])
    return f"{prompt}\n\n数据内容如下（JSON格式）：\n```json\n{data_json}\n```"
