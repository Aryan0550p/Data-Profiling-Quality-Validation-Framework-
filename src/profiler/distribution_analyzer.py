"""
Distribution and statistical anomaly analyzer.
Performs outlier detection (IQR & Z-score), skewness profiling,
zero-variance checks, and multimodal frequency spike detection.
"""

import logging
from typing import Any, Dict, List
import numpy as np
import pandas as pd
from scipy import stats

logger = logging.getLogger(__name__)


class DistributionAnalyzer:
    """Analyzes statistical distributions and detects anomalies."""

    @staticmethod
    def analyze_numeric_column(series: pd.Series, col_name: str) -> Dict[str, Any]:
        """Compute deep distribution properties and detect outliers for a numeric series."""
        clean_series = pd.to_numeric(series.dropna(), errors='coerce').dropna()
        n = len(clean_series)
        if n == 0:
            return {
                "column": col_name,
                "count": 0,
                "is_zero_variance": False,
                "outliers_iqr_extreme_count": 0,
                "outliers_zscore_count": 0,
                "distribution_health": "EMPTY"
            }

        # Basic descriptive statistics
        mean_val = float(clean_series.mean())
        std_val = float(clean_series.std()) if n > 1 else 0.0
        median_val = float(clean_series.median())
        q25 = float(clean_series.quantile(0.25))
        q75 = float(clean_series.quantile(0.75))
        iqr = q75 - q25
        min_val = float(clean_series.min())
        max_val = float(clean_series.max())

        # Zero-variance check
        is_zero_var = bool(std_val == 0.0 or min_val == max_val)

        # Skewness & Kurtosis
        try:
            skew_val = float(stats.skew(clean_series, bias=False)) if n > 2 and std_val > 0 else 0.0
            kurt_val = float(stats.kurtosis(clean_series, bias=False)) if n > 3 and std_val > 0 else 0.0
        except Exception:
            skew_val, kurt_val = 0.0, 0.0

        # Outlier Detection: IQR method (1.5 IQR mild, 3.0 IQR extreme)
        lower_bound_extreme = q25 - 3.0 * iqr
        upper_bound_extreme = q75 + 3.0 * iqr
        extreme_iqr_mask = (clean_series < lower_bound_extreme) | (clean_series > upper_bound_extreme)
        extreme_iqr_outliers = clean_series[extreme_iqr_mask]
        iqr_outlier_count = int(len(extreme_iqr_outliers))

        # Outlier Detection: Z-Score (|z| > 3.5)
        if std_val > 0:
            z_scores = (clean_series - mean_val) / std_val
            z_outliers = clean_series[np.abs(z_scores) > 3.5]
            z_outlier_count = int(len(z_outliers))
        else:
            z_outlier_count = 0

        # Frequency spike / clustering check (e.g. $0.01 micro-discount spike)
        value_counts = clean_series.value_counts(normalize=True)
        top_val = float(value_counts.index[0]) if len(value_counts) > 0 else None
        top_freq = float(value_counts.iloc[0]) if len(value_counts) > 0 else 0.0
        has_frequency_spike = bool(top_freq > 0.08 and top_val not in (0.0, 0))

        # Overall distribution health evaluation
        anomalies_detected = []
        if is_zero_var:
            anomalies_detected.append("ZERO_VARIANCE_DEGENERATE")
        if iqr_outlier_count > 0:
            anomalies_detected.append(f"EXTREME_OUTLIERS_COUNT_{iqr_outlier_count}")
        if abs(skew_val) > 4.0:
            anomalies_detected.append(f"HIGH_SKEWNESS_{round(skew_val, 2)}")
        if has_frequency_spike:
            anomalies_detected.append(f"ANOMALOUS_VALUE_SPIKE_{top_val}_AT_{round(top_freq*100, 1)}%")

        health_status = "HEALTHY" if len(anomalies_detected) == 0 else "ANOMALY_FLAGGED"

        return {
            "column": col_name,
            "count": n,
            "min": round(min_val, 4),
            "max": round(max_val, 4),
            "mean": round(mean_val, 4),
            "std": round(std_val, 4),
            "median": round(median_val, 4),
            "q25": round(q25, 4),
            "q75": round(q75, 4),
            "iqr": round(iqr, 4),
            "skewness": round(skew_val, 4),
            "kurtosis": round(kurt_val, 4),
            "is_zero_variance": is_zero_var,
            "outliers_iqr_extreme_count": iqr_outlier_count,
            "outliers_zscore_count": z_outlier_count,
            "has_frequency_spike": has_frequency_spike,
            "top_frequent_value": top_val,
            "top_frequency_ratio": round(top_freq, 4),
            "anomalies_detected": anomalies_detected,
            "health_status": health_status
        }
