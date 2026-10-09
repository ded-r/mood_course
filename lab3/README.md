# Vulnerability Data Warehouse & ETL Pipeline (Lab 3)

This directory contains the complete implementation of **Laboratory Work 3: Building an ETL Pipeline for a Vulnerability-Detection Data Warehouse** based on the research paper:
> Shestov et al. (2025), *"Finetuning Large Language Models for Vulnerability Detection"*, IEEE Access, 13.

---

## Architecture Overview

* **Engine:** PostgreSQL 15 (Docker Container `vuln-dw-postgres`)
* **Schemas:**
  * `staging`: Raw ingestion tables (`stg_vulnerability_raw_jsonl`, `stg_cwe_metadata_csv`)
  * `dwh`: Star Schema dimensional warehouse (`fact_vulnerability_sample` + 5 dimensions)
* **Pipeline:** Python ETL using `psycopg2-binary`, `pandas`, `sqlalchemy`, and `tabulate`.

---

## Directory Structure

```
lab3/
├── docker-compose.yml                      # PostgreSQL 15 Docker service definition
├── requirements.txt                        # Python dependencies
├── Report_Lab3_Data_Warehousing_ETL.md     # Full comprehensive laboratory report
├── data/
│   └── raw/
│       ├── without_p3/ (train/valid/test)  # JSONL source (balanced 1:1)
│       ├── with_p3/    (train/valid/test)  # JSONL source (imbalanced 1:34)
│       └── cwe_definitions.csv             # CSV metadata source (CWE taxonomy)
├── sql/
│   ├── 01_staging_schema.sql               # Staging layer DDL
│   ├── 02_dwh_star_schema.sql              # Star Schema DDL (dimensions + fact)
│   ├── 03_quality_checks.sql               # 7 automated data quality verification rules
│   └── 04_analytical_queries.sql           # Task 7 analytical SQL research queries
├── src/
│   ├── config.py                           # DB settings and filesystem paths
│   ├── extract.py                          # Task 3: JSONL + CSV extraction to staging
│   ├── transform.py                        # Task 4: Cleaning, harmonization & surrogate keys
│   ├── load.py                             # Task 5: Loading dimensions then fact table
│   ├── quality_checks.py                   # Task 6: Data quality validation test suite
│   ├── run_analytics.py                    # Task 7: Analytical SQL execution & export
│   └── run_pipeline.py                     # Master orchestrator script
└── output/
    ├── data_quality_report.txt             # Task 6 quality verification logs (100% passed)
    └── analytical_queries_output.md        # Task 7 analytical query outputs
```

---

## Quickstart Guide

### 1. Start the PostgreSQL Database Container
```bash
cd lab3
docker-compose up -d
```
*(If already running via `docker run`, port 5432 is mapped to `localhost:5432` with DB `vuln_dw`, user `postgres`, password `postgres`)*.

### 2. Run the End-to-End Pipeline
Run the master pipeline script in either **full** or **incremental** mode:
```bash
# Full Load (Re-creates schemas and loads all 24,288 samples)
python3 src/run_pipeline.py --mode full

# Incremental Load (Preserves existing data and appends)
python3 src/run_pipeline.py --mode incremental
```

### 3. Run Quality Checks Independently
```bash
python3 src/quality_checks.py
```

### 4. Run Analytical SQL Queries
```bash
python3 src/run_analytics.py
```
