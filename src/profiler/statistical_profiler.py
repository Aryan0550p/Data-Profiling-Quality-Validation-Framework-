"""
Comprehensive Automated Statistical Profiler for Enterprise Datasets.
Analyzes Completeness, Consistency, Accuracy, and Distribution across
all 8 datasets and 73 columns.
"""

import json
import logging
from pathlib import Path
from typing import Any, Dict, List
import pandas as pd

from src.config import DATASETS_SCHEMA, RAW_DATA_DIR, REPORTS_DIR
from src.profiler.distribution_analyzer import DistributionAnalyzer

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)


class DatasetProfiler:
    """Automated statistical and structural profiling engine."""

    def __init__(self, raw_dir: Path = RAW_DATA_DIR, reports_dir: Path = REPORTS_DIR):
        self.raw_dir = raw_dir
        self.reports_dir = reports_dir
        self.reports_dir.mkdir(parents=True, exist_ok=True)
        self.distribution_analyzer = DistributionAnalyzer()

    def profile_all_datasets(self) -> Dict[str, Any]:
        """Profiles all 8 enterprise datasets across 73 columns."""
        logger.info("Initiating comprehensive automated data profiling...")
        overall_profile = {
            "metadata": {
                "dataset_count": len(DATASETS_SCHEMA),
                "target_tables": list(DATASETS_SCHEMA.keys()),
                "total_columns_cataloged": sum(len(d["columns"]) for d in DATASETS_SCHEMA.values())
            },
            "table_summaries": {},
            "column_profiles": {},
            "distribution_profiles": {},
            "global_metrics": {
                "total_rows": 0,
                "total_cells": 0,
                "total_null_cells": 0,
                "total_columns": 0,
                "overall_completeness_rate": 100.0,
                "zero_variance_columns": [],
                "extreme_outlier_columns": []
            }
        }

        total_rows_all = 0
        total_cells_all = 0
        total_nulls_all = 0
        total_cols_all = 0

        for dataset_name, schema in DATASETS_SCHEMA.items():
            csv_path = self.raw_dir / f"{dataset_name}.csv"
            if not csv_path.exists():
                logger.warning(f"File not found: {csv_path}")
                continue

            df = pd.read_csv(csv_path)
            table_summary = self._profile_table(dataset_name, df, schema)
            overall_profile["table_summaries"][dataset_name] = table_summary

            total_rows_all += len(df)
            total_cols_all += len(df.columns)
            total_cells_all += len(df) * len(df.columns)
            total_nulls_all += int(df.isnull().sum().sum())

            # Profile individual columns
            col_profiles = []
            dist_profiles = []
            for col in df.columns:
                col_prof = self._profile_column(df, col)
                col_profiles.append(col_prof)

                if col_prof["distinct_count"] <= 1:
                    overall_profile["global_metrics"]["zero_variance_columns"].append(f"{dataset_name}.{col}")

                # Distribution analysis for numeric non-boolean fields
                if pd.api.types.is_numeric_dtype(df[col]) and not pd.api.types.is_bool_dtype(df[col]):
                    dist_prof = self.distribution_analyzer.analyze_numeric_column(df[col], col)
                    dist_prof["dataset"] = dataset_name
                    dist_profiles.append(dist_prof)

                    if dist_prof["is_zero_variance"] and f"{dataset_name}.{col}" not in overall_profile["global_metrics"]["zero_variance_columns"]:
                        overall_profile["global_metrics"]["zero_variance_columns"].append(f"{dataset_name}.{col}")
                    if dist_prof["outliers_iqr_extreme_count"] > 0:
                        overall_profile["global_metrics"]["extreme_outlier_columns"].append({
                            "dataset": dataset_name,
                            "column": col,
                            "outlier_count": dist_prof["outliers_iqr_extreme_count"]
                        })

            overall_profile["column_profiles"][dataset_name] = col_profiles
            overall_profile["distribution_profiles"][dataset_name] = dist_profiles

        overall_profile["global_metrics"]["total_rows"] = total_rows_all
        overall_profile["global_metrics"]["total_columns"] = total_cols_all
        overall_profile["global_metrics"]["total_cells"] = total_cells_all
        overall_profile["global_metrics"]["total_null_cells"] = total_nulls_all
        if total_cells_all > 0:
            overall_profile["global_metrics"]["overall_completeness_rate"] = round(
                (1.0 - (total_nulls_all / total_cells_all)) * 100.0, 2
            )

        # Save JSON profile summary
        json_output = self.reports_dir / "data_profiling_summary.json"
        with open(json_output, "w") as f:
            json.dump(overall_profile, f, indent=2, default=str)
        logger.info(f"Data profiling complete. Saved summary to {json_output.name}")

        return overall_profile

    def _profile_table(self, name: str, df: pd.DataFrame, schema: Dict[str, Any]) -> Dict[str, Any]:
        """Compute table-level structural metrics."""
        row_count = len(df)
        col_count = len(df.columns)
        total_cells = row_count * col_count
        null_cells = int(df.isnull().sum().sum())
        completeness = round(((total_cells - null_cells) / total_cells) * 100.0, 2) if total_cells > 0 else 100.0
        memory_mb = round(df.memory_usage(deep=True).sum() / (1024 * 1024), 3)
        duplicate_rows = int(df.duplicated().sum())

        return {
            "dataset_name": name,
            "description": schema.get("description", ""),
            "primary_key": schema.get("primary_key", ""),
            "row_count": row_count,
            "column_count": col_count,
            "memory_usage_mb": memory_mb,
            "total_cells": total_cells,
            "null_cells": null_cells,
            "completeness_rate_pct": completeness,
            "duplicate_rows": duplicate_rows
        }

    def _profile_column(self, df: pd.DataFrame, col: str) -> Dict[str, Any]:
        """Compute column-level statistical and structural metrics."""
        series = df[col]
        total_count = len(series)
        null_count = int(series.isnull().sum())
        null_pct = round((null_count / total_count) * 100.0, 2) if total_count > 0 else 0.0
        non_null_count = total_count - null_count
        distinct_count = int(series.nunique(dropna=True))
        distinct_pct = round((distinct_count / non_null_count) * 100.0, 2) if non_null_count > 0 else 0.0
        is_unique = bool(distinct_count == non_null_count and null_count == 0)

        # Cardinality categorization
        if distinct_count == 1:
            cardinality = "CONSTANT / ZERO_VARIANCE"
        elif is_unique:
            cardinality = "UNIQUE_KEY"
        elif distinct_pct > 80.0:
            cardinality = "HIGH_CARDINALITY"
        elif distinct_pct > 15.0:
            cardinality = "MEDIUM_CARDINALITY"
        else:
            cardinality = "LOW_CARDINALITY"

        profile = {
            "column": col,
            "dtype": str(series.dtype),
            "total_count": total_count,
            "null_count": null_count,
            "null_percentage": null_pct,
            "non_null_count": non_null_count,
            "distinct_count": distinct_count,
            "distinct_percentage": distinct_pct,
            "is_unique": is_unique,
            "cardinality": cardinality
        }

        # Numeric column specifics
        if pd.api.types.is_numeric_dtype(series):
            clean = series.dropna()
            profile["numeric_stats"] = {
                "min": float(clean.min()) if len(clean) > 0 else None,
                "max": float(clean.max()) if len(clean) > 0 else None,
                "mean": round(float(clean.mean()), 4) if len(clean) > 0 else None,
                "std": round(float(clean.std()), 4) if len(clean) > 1 else 0.0,
                "median": float(clean.median()) if len(clean) > 0 else None,
                "zero_count": int((clean == 0).sum()),
                "negative_count": int((clean < 0).sum())
            }

        # Text/String column specifics
        elif pd.api.types.is_string_dtype(series) or pd.api.types.is_object_dtype(series):
            clean = series.dropna().astype(str)
            lengths = clean.str.len()
            top_vals = clean.value_counts().head(5).to_dict()
            profile["text_stats"] = {
                "min_length": int(lengths.min()) if len(lengths) > 0 else 0,
                "max_length": int(lengths.max()) if len(lengths) > 0 else 0,
                "avg_length": round(float(lengths.mean()), 2) if len(lengths) > 0 else 0.0,
                "top_5_frequent": {str(k): int(v) for k, v in top_vals.items()}
            }

        return profile


if __name__ == "__main__":
    profiler = DatasetProfiler()
    summary = profiler.profile_all_datasets()
    print("\n--- GLOBAL DATA PROFILING SUMMARY ---")
    print(f"Total Datasets Profiled : {summary['metadata']['dataset_count']}")
    print(f"Total Columns Profiled  : {summary['global_metrics']['total_columns']}")
    print(f"Total Records Ingested  : {summary['global_metrics']['total_rows']:,}")
    print(f"Overall Completeness    : {summary['global_metrics']['overall_completeness_rate']}%")
    print(f"Zero Variance Columns   : {summary['global_metrics']['zero_variance_columns']}")
    print(f"Extreme Outlier Columns : {len(summary['global_metrics']['extreme_outlier_columns'])} flagged columns")
