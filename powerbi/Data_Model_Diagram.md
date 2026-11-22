# Power BI Star Schema Data Model Architecture

This document describes the dimensional data model designed for the enterprise **Data Quality, Profiling & Validation Framework**.

---

## 1. Star Schema Entity-Relationship Diagram

```mermaid
erDiagram
    dim_dq_datasets ||--o{ fact_dq_validation_results : "filters by dataset"
    dim_dq_rules ||--o{ fact_dq_validation_results : "filters by rule"
    dim_dq_issues ||--o{ fact_dq_validation_results : "links to root cause"
    dim_dq_datasets ||--o{ dim_dq_columns : "has columns"
    dim_dq_datasets ||--o{ fact_dq_kpis : "tracks KPIs"

    dim_dq_datasets {
        int dataset_key PK
        string dataset_name UK
        string description
        string primary_key
        string domain
        string owner_team
        int row_count
        int column_count
        float memory_usage_mb
        float completeness_pct
    }

    dim_dq_columns {
        int column_key PK
        string dataset_name FK
        string column_name
        string data_type
        boolean is_primary_key
        boolean is_foreign_key
        boolean is_nullable
    }

    dim_dq_rules {
        int rule_key PK
        string rule_code
        string expectation_type
        string dataset_name
        string target_column
        string dimension
        string severity
        string description
        string associated_issue_id
    }

    dim_dq_issues {
        int issue_key PK
        string issue_id UK
        string dataset_name
        string column_name
        string dimension
        string severity
        string rule_name
        string description
        string root_cause
        string impacted_team
        string remediation_action
        string status
    }

    fact_dq_validation_results {
        int result_key PK
        string run_id
        timestamp execution_timestamp
        string dataset_name FK
        string target_column
        string expectation_type
        string dimension
        string severity
        boolean is_success
        string status
        int element_count
        int unexpected_count
        float unexpected_percent
        string observed_value
        string issue_id FK
        string impacted_team
    }

    fact_dq_kpis {
        int kpi_fact_key PK
        date snapshot_date
        string kpi_code
        string kpi_name
        float actual_value
        float target_sla
        string unit
        string status
        string run_id
    }
```

---

## 2. Table Relationships and Cardinality

| From Table (Dimension) | To Table (Fact) | Primary Join Key | Cardinality | Cross-filter Direction |
| :--- | :--- | :--- | :---: | :---: |
| `dim_dq_datasets` | `fact_dq_validation_results` | `dataset_name` | 1 : Many | Single (Dimension to Fact) |
| `dim_dq_issues` | `fact_dq_validation_results` | `issue_id` | 1 : Many | Single (Dimension to Fact) |
| `dim_dq_rules` | `fact_dq_validation_results` | `expectation_type` + `dataset_name` | 1 : Many | Both / Single |
| `dim_dq_datasets` | `dim_dq_columns` | `dataset_name` | 1 : Many | Single |
| `dim_dq_datasets` | `fact_dq_kpis` | `run_id` | 1 : Many | Single |

---

## 3. Storage & Refresh Recommendations
- **Storage Mode**: Import Mode (Recommended for fast in-memory DAX aggregations) or DirectQuery for live warehouse connections.
- **Refresh Frequency**: Automated daily refresh scheduled post-ETL validation pipeline execution.
