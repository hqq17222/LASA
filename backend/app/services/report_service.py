# 报告生成服务（HTML）
from datetime import datetime
from typing import List
from app.models import Project, IndicatorResult, Alarm

TEMPLATE = """
<!DOCTYPE html>
<html>
<head>
<meta charset="utf-8">
<title>{title}</title>
<style>
body {{ font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Helvetica Neue", Arial, sans-serif; margin: 40px; color: #333; }}
h1 {{ color: #2c5e2e; border-bottom: 2px solid #2c5e2e; padding-bottom: 10px; }}
.card {{ background: #f6f7f8; border-radius: 8px; padding: 20px; margin: 20px 0; }}
.table {{ width: 100%; border-collapse: collapse; margin: 10px 0; }}
.table th, .table td {{ border: 1px solid #ddd; padding: 8px; text-align: left; }}
.table th {{ background: #e9f0e9; }}
.badge {{ display: inline-block; padding: 2px 8px; border-radius: 4px; font-size: 12px; color: white; }}
.badge-yellow {{ background: #f0ad4e; }}
.badge-orange {{ background: #f07c32; }}
.badge-red {{ background: #d9534f; }}
</style>
</head>
<body>
<h1>{title}</h1>
<p>生成时间：{generated_at}</p>
<div class="card">
  <h3>项目信息</h3>
  <p><strong>名称：</strong>{project_name}</p>
  <p><strong>编码：</strong>{project_code}</p>
</div>
<div class="card">
  <h3>评估指标</h3>
  <table class="table">
    <tr><th>维度</th><th>指标</th><th>周期</th><th>数值</th><th>说明</th></tr>
    {indicator_rows}
  </table>
</div>
<div class="card">
  <h3>未关闭预警</h3>
  <table class="table">
    <tr><th>级别</th><th>类型</th><th>标题</th><th>状态</th><th>时间</th></tr>
    {alarm_rows}
  </table>
</div>
</body>
</html>
"""

def generate_html(project: Project, indicators: List[IndicatorResult], alarms: List[Alarm], period: str) -> str:
    def badge(level):
        cls = {"yellow": "badge-yellow", "orange": "badge-orange", "red": "badge-red"}.get(level, "badge-yellow")
        return f'<span class="badge {cls}">{level}</span>'
    ind_rows = "\n".join(
        f"<tr><td>{i.dimension}</td><td>{i.name}</td><td>{i.period}</td><td>{i.value if i.value is not None else '-'}</td><td>{i.value_text or ''}</td></tr>"
        for i in indicators
    ) or "<tr><td colspan='5'>暂无指标</td></tr>"
    alarm_rows = "\n".join(
        f"<tr><td>{badge(a.level)}</td><td>{a.alarm_type}</td><td>{a.title}</td><td>{a.status}</td><td>{a.created_at.strftime('%Y-%m-%d %H:%M') if a.created_at else ''}</td></tr>"
        for a in alarms
    ) or "<tr><td colspan='5'>暂无预警</td></tr>"
    return TEMPLATE.format(
        title=f"{project.name} - {period} 评估报告" if project else "评估报告",
        generated_at=datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        project_name=project.name if project else "",
        project_code=project.code if project else "",
        indicator_rows=ind_rows,
        alarm_rows=alarm_rows,
    )
