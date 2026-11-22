"""
JSON Report Generator for Machine-Readable Validation Output.
"""

import json
from pathlib import Path
from typing import Any, Dict
from src.config import REPORTS_DIR


class JSONReportGenerator:
    def __init__(self, output_dir: Path = REPORTS_DIR):
        self.output_dir = output_dir
        self.output_dir.mkdir(parents=True, exist_ok=True)

    def generate(self, profiling_summary: Dict[str, Any], validation_results: Dict[str, Any]) -> Path:
        out_path = self.output_dir / "dq_validation_results.json"
        payload = {
            "metadata": {
                "generated_at": validation_results.get("run_timestamp"),
                "total_datasets": len(profiling_summary["table_summaries"]),
                "total_columns": profiling_summary["global_metrics"]["total_columns"],
                "total_rows": profiling_summary["global_metrics"]["total_rows"]
            },
            "kpis": validation_results["kpis"],
            "dimension_scores": validation_results["dimension_scores"],
            "flagged_issues": validation_results["flagged_issues_detected"],
            "table_summaries": profiling_summary["table_summaries"],
            "global_metrics": profiling_summary["global_metrics"]
        }
        with open(out_path, "w", encoding="utf-8") as f:
            json.dump(payload, f, indent=2, default=str)
        return out_path
