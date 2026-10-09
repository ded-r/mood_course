import pandas as pd
from config import get_engine

def fetch_staging_data():
    """Fetches raw data from staging tables for transformation using SQLAlchemy engine."""
    engine = get_engine()
    with engine.connect() as conn:
        jsonl_df = pd.read_sql_query("""
            SELECT 
                stg_id,
                source_folder,
                split_file,
                raw_idx,
                raw_cwe,
                raw_status,
                raw_target,
                raw_commit,
                raw_function_name,
                raw_body_hash,
                raw_code,
                raw_token_count
            FROM staging.stg_vulnerability_raw_jsonl
        """, conn)

        cwe_csv_df = pd.read_sql_query("""
            SELECT 
                cwe_code,
                cwe_name,
                severity_level,
                description
            FROM staging.stg_cwe_metadata_csv
        """, conn)

    return jsonl_df, cwe_csv_df

def transform_data(jsonl_df, cwe_csv_df):
    """
    Executes Task 4 Transformation and Integration:
    - Standardizes column names
    - Converts status and target into unified Boolean (is_vulnerable)
    - Maps P1, P2, P3 partitions
    - Cleans project/function strings
    - Computes code_length and line_count
    - Flags duplicates for data leakage tracking
    - Resolves missing CWE values
    """
    print("[TRANSFORM] Starting data transformation and integration...")

    df = jsonl_df.copy()

    # 1. Normalize split name: 'train.jsonl' -> 'train'
    df["split_name"] = df["split_file"].apply(lambda x: x.replace(".jsonl", "").strip().lower())

    # 2. Map dataset partition: P1 (VULNERABLE), P2 (FIXED), P3 (NOT_VULNERABLE)
    def determine_partition(status_val):
        status = str(status_val).upper().strip()
        if status == "VULNERABLE":
            return "P1"
        elif status == "FIXED":
            return "P2"
        elif status == "NOT_VULNERABLE":
            return "P3"
        return "P3"

    df["partition_code"] = df["raw_status"].apply(determine_partition)

    # 3. Standardize boolean label (is_vulnerable)
    def determine_is_vulnerable(row):
        target = row["raw_target"]
        status = str(row["raw_status"]).upper().strip()
        if target == 1 or status == "VULNERABLE":
            return True
        return False

    df["is_vulnerable"] = df.apply(determine_is_vulnerable, axis=1)

    # 4. Normalize function name and commit hash
    df["function_name"] = df["raw_function_name"].fillna("anonymous_function").apply(lambda s: str(s).strip() or "anonymous_function")
    df["commit_hash"] = df["raw_commit"].fillna("unknown_commit").apply(lambda s: str(s).strip() or "unknown_commit")
    df["body_hash"] = df["raw_body_hash"].fillna("").apply(lambda s: str(s).strip())

    # 5. Normalize CWE code
    def clean_cwe(val):
        if not val or pd.isna(val):
            return "CWE-UNKNOWN"
        val = str(val).strip().upper()
        if "NOINFO" in val or "OTHER" in val or "UNKNOWN" in val:
            return "CWE-UNKNOWN"
        if not val.startswith("CWE-"):
            val = f"CWE-{val}"
        return val

    df["cwe_code"] = df["raw_cwe"].apply(clean_cwe)

    # 6. Normalize Project dimension
    df["project_name"] = "open-source-java-cvefixes"

    # 7. Compute code metrics: code_length, line_count, token_count
    df["raw_code"] = df["raw_code"].fillna("")
    df["code_length"] = df["raw_code"].apply(lambda code: max(1, len(code)))
    df["line_count"] = df["raw_code"].apply(lambda code: max(1, len(code.splitlines())))
    df["token_count"] = df["raw_token_count"].fillna(0).astype(int)

    # 8. Duplicate detection across code bodies (Data Leakage flag)
    body_counts = df["body_hash"].value_counts()
    duplicate_hashes = set(body_counts[body_counts > 1].index)
    duplicate_hashes.discard("")
    df["has_duplicate_body"] = df["body_hash"].apply(lambda h: h in duplicate_hashes)

    # 9. Generate Natural Business Key (sample_id) for auditability and idempotency
    df["sample_id"] = (
        df["source_folder"] + "_" + 
        df["split_name"] + "_" + 
        df["partition_code"] + "_" + 
        df["body_hash"].str.slice(0, 16) + "_" + 
        df["raw_idx"].fillna(0).astype(str)
    )

    duplicate_sample_ids = set(df[df.duplicated(subset=["sample_id"], keep=False)]["sample_id"])
    if duplicate_sample_ids:
        df["sample_id"] = df.apply(
            lambda r: f"{r['sample_id']}_{r['stg_id']}" if r["sample_id"] in duplicate_sample_ids else r["sample_id"],
            axis=1
        )

    # 10. Prepare Dimension DataFrames
    dim_partition_df = pd.DataFrame([
        {"partition_code": "P1", "partition_name": "Vulnerable Function (Pre-change)", "classification_role": "Positive Class", "description": "Pre-fix version of function fixing commit"},
        {"partition_code": "P2", "partition_name": "Fixed Function (Post-change)", "classification_role": "Hard Negative", "description": "Post-fix version of patched function (near-identical negative)"},
        {"partition_code": "P3", "partition_name": "Neutral Function (Unchanged)", "classification_role": "Easy Negative", "description": "Unchanged functions from patched files with no vulnerabilities"}
    ])

    dim_split_df = pd.DataFrame([
        {"split_name": "train", "split_description": "Training split used for parameter optimization"},
        {"split_name": "valid", "split_description": "Validation split used for hyperparameter tuning and threshold selection"},
        {"split_name": "test", "split_description": "Holdout test split for final generalizability evaluation"}
    ])

    dim_source_df = pd.DataFrame([
        {"source_name": "without_p3", "dataset_role": "Balanced Dataset (1:1 ablation)", "source_format": "JSONL"},
        {"source_name": "with_p3", "dataset_role": "Imbalanced Dataset (1:34 realistic)", "source_format": "JSONL"}
    ])

    dim_project_df = pd.DataFrame([
        {"project_name": "open-source-java-cvefixes", "primary_language": "Java"}
    ])

    # Combine CSV CWEs + dataset CWEs, ensuring CWE-UNKNOWN is always included
    cwe_dict = {}
    for _, row in cwe_csv_df.iterrows():
        cwe_dict[row["cwe_code"]] = {
            "cwe_code": row["cwe_code"],
            "cwe_name": row["cwe_name"],
            "severity_level": row["severity_level"],
            "description": row.get("description", "")
        }

    if "CWE-UNKNOWN" not in cwe_dict:
        cwe_dict["CWE-UNKNOWN"] = {
            "cwe_code": "CWE-UNKNOWN",
            "cwe_name": "Unknown or Unmapped Weakness",
            "severity_level": "Low",
            "description": "Weakness type not categorized or missing in upstream commit."
        }

    for cwe in df["cwe_code"].unique():
        if cwe not in cwe_dict:
            cwe_dict[cwe] = {
                "cwe_code": cwe,
                "cwe_name": f"Weakness Classification {cwe}",
                "severity_level": "Medium",
                "description": f"Automated entry for weakness {cwe}"
            }

    dim_cwe_df = pd.DataFrame(list(cwe_dict.values()))

    print(f"[TRANSFORM] Transformed {len(df)} samples.")
    print(f"[TRANSFORM] Registered {len(dim_cwe_df)} total CWE dimension entities.")
    print(f"[TRANSFORM] Flagged {df['has_duplicate_body'].sum()} rows with duplicate code bodies.")

    return {
        "fact_df": df,
        "dim_partition_df": dim_partition_df,
        "dim_split_df": dim_split_df,
        "dim_source_df": dim_source_df,
        "dim_cwe_df": dim_cwe_df,
        "dim_project_df": dim_project_df
    }
