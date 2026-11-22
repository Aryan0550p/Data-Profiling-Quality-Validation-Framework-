"""
Rule Registry and Validation Constants.
Maps quality dimensions, severities, and KPI evaluation thresholds.
"""

from enum import Enum
from typing import Dict, Any


class QualityDimension(str, Enum):
    COMPLETENESS = "completeness"
    CONSISTENCY = "consistency"
    ACCURACY = "accuracy"
    DISTRIBUTION = "distribution"


class RuleSeverity(str, Enum):
    CRITICAL = "CRITICAL"
    HIGH = "HIGH"
    MEDIUM = "MEDIUM"
    LOW = "LOW"


SEVERITY_WEIGHTS = {
    RuleSeverity.CRITICAL: 1.00,
    RuleSeverity.HIGH: 0.75,
    RuleSeverity.MEDIUM: 0.50,
    RuleSeverity.LOW: 0.25
}

DIMENSION_WEIGHTS = {
    QualityDimension.COMPLETENESS: 0.30,
    QualityDimension.CONSISTENCY: 0.25,
    QualityDimension.ACCURACY: 0.25,
    QualityDimension.DISTRIBUTION: 0.20
}
