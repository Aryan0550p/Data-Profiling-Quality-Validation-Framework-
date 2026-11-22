# Power BI Data Quality Dashboard Specification

This document details the multi-page Power BI dashboard design, visual layout, interactive drill-through paths, and KPI tracking implementation for the **Data Quality & Profiling Framework**.

---

## 1. Executive Summary & Dashboard Architecture

The dashboard provides continuous observability into the data health of the enterprise data warehouse across **8 core datasets** and **73 columns**, measuring **6 quality KPIs** and flagging **23 specific data anomalies**.

```
+---------------------------------------------------------------------------------------------------+
| PAGE 1: EXECUTIVE DQ SCORECARD                                                                    |
|  - 6 KPI Scorecard Cards (DQ Index, Completeness, Consistency, Accuracy, Distribution, Freshness)  |
|  - Quality Dimension Radar / Gauge Breakdown                                                     |
|  - 30-Day DQ Index Trend Line Chart                                                               |
|  - Issue Impact by Downstream Analytics Team (Donut Chart)                                        |
+---------------------------------------------------------------------------------------------------+
| PAGE 2: DIAGNOSTICS & ROOT-CAUSE EXPLORER                                                         |
|  - Slicers: Quality Dimension, Severity (Critical/High/Med/Low), Downstream Team, Dataset         |
|  - Detailed Issue Audit Grid with Root-Cause Analysis & Remediation Recommendations                |
|  - Violating Records Volume by Dataset (Horizontal Stacked Bar)                                   |
+---------------------------------------------------------------------------------------------------+
| PAGE 3: DATASET PROFILER & COLUMN INSPECTOR                                                       |
|  - Table Health Matrix (Rows, Columns, Memory, Nulls %, Duplicate Rows)                          |
|  - Column Level Profiler (Dtype, Cardinality, Min/Max/Mean/Std, Null %)                           |
|  - Distribution Anomaly Viewer (Outlier counts & frequency spikes)                                |
+---------------------------------------------------------------------------------------------------+
```

---

## 2. Page-by-Page Visual Specification

### Page 1: Executive DQ Scorecard
- **Header**: Enterprise Data Quality Health Center | Last Automated Run: `CURRENT_DATE()` | Refresh SLA: `PASS`.
- **Top Row (6 KPI Cards)**:
  1. `Overall_DQ_Index`: Goal: 95.0% | Dynamic Color formatting (#10B981, #F59E0B, #EF4444).
  2. `Completeness_Pct`: Goal: 98.0%.
  3. `Consistency_Pct`: Goal: 99.0%.
  4. `Accuracy_Pct`: Goal: 98.5%.
  5. `Distribution_Health_Pct`: Goal: 96.0%.
  6. `Freshness_SLA_Pct`: Goal: 99.5%.
- **Left Chart (Gauge / Bullet Chart)**:
  - 4 Quality Dimensions health comparison against SLAs.
- **Center Chart (Area / Line Chart)**:
  - 30-Day historical trend of `Overall_DQ_Index` vs Target SLA line.
- **Right Chart (Donut Chart)**:
  - Issues distribution by Downstream Analytics Team (Marketing vs Supply Chain vs Finance).

### Page 2: Issue Diagnostics & Root Cause Explorer
- **Top Slicers**:
  - `dim_dq_issues[severity]` (Multi-select pills: Critical, High, Medium, Low).
  - `dim_dq_issues[dimension]` (Completeness, Consistency, Accuracy, Distribution).
  - `dim_dq_issues[impacted_team]` (Marketing, Supply Chain, Finance).
  - `dim_dq_issues[dataset_name]` (Dropdown).
- **Primary Grid (Matrix / Table Visual)**:
  - Columns: `Issue ID`, `Dataset`, `Column`, `Severity` (Conditional Badge), `Dimension`, `Violations Count`, `Violation %`, `Root Cause Summary`, `Actionable Remediation`.
- **Detail Flyout / Drill-through**:
  - Right-click issue -> Drill-through to column distribution and raw affected sample queries.

### Page 3: Dataset Profiler & Column Inspector
- **Dataset Summary Table**:
  - Lists the 8 datasets with primary key, row count, column count, memory footprint, completeness %.
- **Column Deep-Dive Table**:
  - Column name, data type, non-null count, distinct count, cardinality tag (`UNIQUE_KEY`, `HIGH`, `LOW`, `CONSTANT`).
- **Distribution Anomaly Indicators**:
  - Flags zero-variance columns (`fct_inventory.warehouse_id`).
  - Flags extreme outlier fields (`fct_orders.total_amount`, `dim_products.weight_kg`, `fct_customer_interactions.resolution_time_mins`).
  - Flags bimodal clustering (`fct_orders.discount_amount` $0.01 spike).

---

## 3. Power BI Ingestion Guide (Step-by-Step)

1. Open **Power BI Desktop**.
2. Select **Get Data -> Folder / Text/CSV**.
3. Point to directory `data/powerbi/`.
4. Import the 6 CSV files:
   - `dim_dq_datasets.csv`
   - `dim_dq_columns.csv`
   - `dim_dq_rules.csv`
   - `dim_dq_issues.csv`
   - `fact_dq_validation_results.csv`
   - `fact_dq_kpis.csv`
5. Verify relationships in the **Model View** matching `powerbi/Data_Model_Diagram.md`.
6. Open **DAX Measures** tab and copy measures from `powerbi/DAX_Measures.dax`.
7. Configure conditional formatting rules on KPI cards and severity badges.
