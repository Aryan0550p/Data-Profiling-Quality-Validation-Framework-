"""
HTML Report Generator for Data Profiling & Quality Validation.
Produces a standalone executive visual HTML report with interactive KPI cards,
dimension progress bars, and the full catalog of flagged data quality issues.
"""

from datetime import datetime
from pathlib import Path
from typing import Any, Dict
from src.config import REPORTS_DIR


class HTMLReportGenerator:
    def __init__(self, output_dir: Path = REPORTS_DIR):
        self.output_dir = output_dir
        self.output_dir.mkdir(parents=True, exist_ok=True)

    def generate(self, profiling_summary: Dict[str, Any], validation_results: Dict[str, Any]) -> Path:
        """Generates comprehensive HTML report."""
        kpis = validation_results["kpis"]
        dim_scores = validation_results["dimension_scores"]
        issues = validation_results["flagged_issues_detected"]
        table_summaries = profiling_summary["table_summaries"]
        run_ts = validation_results.get("run_timestamp", datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S UTC"))

        # Build KPI Cards HTML
        kpi_cards_html = ""
        for key, kpi in kpis.items():
            val = kpi["value"]
            sla = kpi["target_sla"]
            status = kpi["status"]
            status_color = "#10b981" if status == "PASS" else ("#f59e0b" if status == "WARNING" else "#ef4444")
            bg_color = "rgba(16, 185, 129, 0.08)" if status == "PASS" else ("rgba(245, 158, 11, 0.08)" if status == "WARNING" else "rgba(239, 68, 68, 0.08)")
            kpi_cards_html += f"""
            <div class="kpi-card" style="border-top: 4px solid {status_color}; background: {bg_color};">
                <div class="kpi-header">
                    <span class="kpi-title">{kpi['name']}</span>
                    <span class="badge" style="background:{status_color}22; color:{status_color}; border: 1px solid {status_color}55;">{status}</span>
                </div>
                <div class="kpi-value" style="color: {status_color};">{val}{kpi['unit']}</div>
                <div class="kpi-target">Target SLA: <strong>{sla}{kpi['unit']}</strong></div>
            </div>
            """

        # Build Issues Table HTML
        issues_rows_html = ""
        for issue in issues:
            sev = issue["severity"]
            sev_color = "#ef4444" if sev == "CRITICAL" else ("#f97316" if sev == "HIGH" else ("#3b82f6" if sev == "MEDIUM" else "#64748b"))
            dim = issue["dimension"].capitalize()
            issues_rows_html += f"""
            <tr>
                <td><code class="issue-id">{issue['issue_id']}</code></td>
                <td><strong>{issue['dataset']}</strong></td>
                <td><code>{issue['column']}</code></td>
                <td><span class="dim-pill dim-{issue['dimension']}">{dim}</span></td>
                <td><span class="badge" style="background:{sev_color}22; color:{sev_color}; border: 1px solid {sev_color}66;">{sev}</span></td>
                <td><strong>{issue['unexpected_count']:,}</strong> <span class="text-muted">({issue['unexpected_percent']}%)</span></td>
                <td>{issue['description']}</td>
                <td><span class="team-tag">{issue['impacted_team']}</span></td>
                <td class="remediation-cell">{issue['remediation']}</td>
            </tr>
            """

        # Build Datasets Table HTML
        datasets_rows_html = ""
        for name, summ in table_summaries.items():
            comp = summ["completeness_rate_pct"]
            comp_color = "#10b981" if comp >= 99.0 else ("#f59e0b" if comp >= 95.0 else "#ef4444")
            datasets_rows_html += f"""
            <tr>
                <td><strong>{name}</strong></td>
                <td><code>{summ['primary_key']}</code></td>
                <td>{summ['row_count']:,}</td>
                <td>{summ['column_count']}</td>
                <td>{summ['memory_usage_mb']} MB</td>
                <td>{summ['null_cells']:,}</td>
                <td>
                    <div class="progress-bar-container">
                        <div class="progress-bar" style="width: {comp}%; background: {comp_color};"></div>
                    </div>
                    <span style="font-weight: 600; color: {comp_color};">{comp}%</span>
                </td>
            </tr>
            """

        html_content = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Enterprise Data Profiling, Quality & Validation Report</title>
    <style>
        :root {{
            --bg-primary: #0f172a;
            --bg-card: #1e293b;
            --bg-card-hover: #334155;
            --text-primary: #f8fafc;
            --text-secondary: #94a3b8;
            --border-color: #334155;
            --primary: #38bdf8;
            --success: #10b981;
            --warning: #f59e0b;
            --danger: #ef4444;
        }}
        * {{ box-sizing: border-box; margin: 0; padding: 0; }}
        body {{
            font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif;
            background-color: var(--bg-primary);
            color: var(--text-primary);
            line-height: 1.5;
            padding: 2rem;
        }}
        .header {{
            display: flex;
            justify-content: space-between;
            align-items: center;
            padding-bottom: 1.5rem;
            border-bottom: 1px solid var(--border-color);
            margin-bottom: 2rem;
        }}
        .header h1 {{ font-size: 1.875rem; font-weight: 700; color: var(--text-primary); }}
        .header p {{ color: var(--text-secondary); font-size: 0.875rem; margin-top: 0.25rem; }}
        .section-title {{
            font-size: 1.25rem;
            font-weight: 600;
            margin-bottom: 1rem;
            color: var(--primary);
            display: flex;
            align-items: center;
            gap: 0.5rem;
        }}
        .kpi-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(220px, 1fr));
            gap: 1.25rem;
            margin-bottom: 2.5rem;
        }}
        .kpi-card {{
            background: var(--bg-card);
            border-radius: 0.75rem;
            padding: 1.25rem;
            border: 1px solid var(--border-color);
            box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.2);
        }}
        .kpi-header {{ display: flex; justify-content: space-between; align-items: flex-start; margin-bottom: 0.5rem; }}
        .kpi-title {{ font-size: 0.825rem; color: var(--text-secondary); font-weight: 600; text-transform: uppercase; }}
        .kpi-value {{ font-size: 2rem; font-weight: 800; line-height: 1.2; margin: 0.25rem 0; }}
        .kpi-target {{ font-size: 0.75rem; color: var(--text-secondary); }}
        .badge {{
            padding: 0.25rem 0.6rem;
            border-radius: 9999px;
            font-size: 0.75rem;
            font-weight: 700;
            text-transform: uppercase;
        }}
        .dim-pill {{
            padding: 0.2rem 0.5rem;
            border-radius: 0.375rem;
            font-size: 0.75rem;
            font-weight: 600;
        }}
        .dim-completeness {{ background: #0284c722; color: #38bdf8; border: 1px solid #38bdf855; }}
        .dim-consistency {{ background: #8b5cf622; color: #a78bfa; border: 1px solid #a78bfa55; }}
        .dim-accuracy {{ background: #f59e0b22; color: #fbbf24; border: 1px solid #fbbf2455; }}
        .dim-distribution {{ background: #ec489922; color: #f472b6; border: 1px solid #f472b655; }}
        .team-tag {{
            background: #334155;
            color: #cbd5e1;
            padding: 0.2rem 0.5rem;
            border-radius: 0.25rem;
            font-size: 0.75rem;
            font-weight: 500;
            display: inline-block;
        }}
        .dimension-grid {{
            display: grid;
            grid-template-columns: repeat(4, 1fr);
            gap: 1rem;
            margin-bottom: 2.5rem;
        }}
        .dim-box {{
            background: var(--bg-card);
            border: 1px solid var(--border-color);
            border-radius: 0.5rem;
            padding: 1rem;
        }}
        .dim-box h4 {{ font-size: 0.875rem; color: var(--text-secondary); text-transform: uppercase; margin-bottom: 0.5rem; }}
        .dim-box .score {{ font-size: 1.5rem; font-weight: 700; color: var(--text-primary); }}
        .table-container {{
            background: var(--bg-card);
            border: 1px solid var(--border-color);
            border-radius: 0.75rem;
            overflow: hidden;
            margin-bottom: 2.5rem;
        }}
        table {{
            width: 100%;
            border-collapse: collapse;
            text-align: left;
            font-size: 0.85rem;
        }}
        th {{
            background: #1e293b;
            color: var(--text-secondary);
            font-weight: 600;
            padding: 0.875rem 1rem;
            border-bottom: 1px solid var(--border-color);
            text-transform: uppercase;
            font-size: 0.75rem;
            letter-spacing: 0.05em;
        }}
        td {{
            padding: 0.875rem 1rem;
            border-bottom: 1px solid var(--border-color);
            color: var(--text-primary);
            vertical-align: middle;
        }}
        tr:hover td {{ background: var(--bg-card-hover); }}
        code {{
            background: #0f172a;
            padding: 0.15rem 0.4rem;
            border-radius: 0.25rem;
            font-family: ui-monospace, SFMono-Regular, Menlo, Monaco, Consolas, monospace;
            font-size: 0.8rem;
            color: #38bdf8;
        }}
        .issue-id {{
            font-weight: 700;
            color: #f43f5e;
            background: #f43f5e15;
            border: 1px solid #f43f5e33;
        }}
        .progress-bar-container {{
            width: 100px;
            height: 8px;
            background: #334155;
            border-radius: 9999px;
            overflow: hidden;
            display: inline-block;
            vertical-align: middle;
            margin-right: 0.5rem;
        }}
        .progress-bar {{ height: 100%; border-radius: 9999px; }}
        .text-muted {{ color: var(--text-secondary); font-size: 0.75rem; }}
        .remediation-cell {{ font-size: 0.8rem; color: #cbd5e1; max-width: 320px; }}
    </style>
</head>
<body>

    <div class="header">
        <div>
            <h1>Data Profiling, Quality & Validation Framework</h1>
            <p>Automated Great Expectations + pandas Validation Pipeline | 8 Enterprise Datasets | 73 Profiled Columns</p>
        </div>
        <div style="text-align: right;">
            <span class="badge" style="background: #38bdf822; color: #38bdf8; border: 1px solid #38bdf855;">Execution: {run_ts}</span>
        </div>
    </div>

    <!-- 6 CORE QUALITY KPIS -->
    <div class="section-title">6 Core Data Quality KPIs</div>
    <div class="kpi-grid">
        {kpi_cards_html}
    </div>

    <!-- 4 QUALITY DIMENSIONS HEALTH -->
    <div class="section-title">Quality Dimension Health Breakdown</div>
    <div class="dimension-grid">
        <div class="dim-box">
            <h4>Completeness</h4>
            <div class="score" style="color: #38bdf8;">{dim_scores['completeness']['score']}%</div>
            <div class="text-muted">{dim_scores['completeness']['passed']}/{dim_scores['completeness']['total']} Rules Passing</div>
        </div>
        <div class="dim-box">
            <h4>Consistency</h4>
            <div class="score" style="color: #a78bfa;">{dim_scores['consistency']['score']}%</div>
            <div class="text-muted">{dim_scores['consistency']['passed']}/{dim_scores['consistency']['total']} Rules Passing</div>
        </div>
        <div class="dim-box">
            <h4>Accuracy</h4>
            <div class="score" style="color: #fbbf24;">{dim_scores['accuracy']['score']}%</div>
            <div class="text-muted">{dim_scores['accuracy']['passed']}/{dim_scores['accuracy']['total']} Rules Passing</div>
        </div>
        <div class="dim-box">
            <h4>Distribution</h4>
            <div class="score" style="color: #f472b6;">{dim_scores['distribution']['score']}%</div>
            <div class="text-muted">{dim_scores['distribution']['passed']}/{dim_scores['distribution']['total']} Rules Passing</div>
        </div>
    </div>

    <!-- 23 FLAGGED DATA QUALITY ISSUES -->
    <div class="section-title">Flagged Data Quality Issues & Root Causes ({len(issues)} Issues)</div>
    <div class="table-container">
        <table>
            <thead>
                <tr>
                    <th>Issue ID</th>
                    <th>Dataset</th>
                    <th>Column</th>
                    <th>Dimension</th>
                    <th>Severity</th>
                    <th>Violations</th>
                    <th>Description</th>
                    <th>Downstream Team</th>
                    <th>Remediation Playbook</th>
                </tr>
            </thead>
            <tbody>
                {issues_rows_html}
            </tbody>
        </table>
    </div>

    <!-- 8 PROFILED DATASETS METRICS -->
    <div class="section-title">Catalog of 8 Profiled Datasets</div>
    <div class="table-container">
        <table>
            <thead>
                <tr>
                    <th>Dataset Name</th>
                    <th>Primary Key</th>
                    <th>Row Count</th>
                    <th>Columns</th>
                    <th>Memory</th>
                    <th>Null Cells</th>
                    <th>Completeness %</th>
                </tr>
            </thead>
            <tbody>
                {datasets_rows_html}
            </tbody>
        </table>
    </div>

</body>
</html>
"""
        report_file = self.output_dir / "data_profiling_and_quality_report.html"
        with open(report_file, "w", encoding="utf-8") as f:
            f.write(html_content)
        return report_file
