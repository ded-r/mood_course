import os
import psycopg2.extras
import pandas as pd
from config import get_db_connection, SQL_DIR
from transform import fetch_staging_data, transform_data

def run_ddl_script(conn, filename):
    """Executes a SQL script file."""
    filepath = os.path.join(SQL_DIR, filename)
    with open(filepath, "r", encoding="utf-8") as f:
        sql = f.read()
    with conn.cursor() as cur:
        cur.execute(sql)
    conn.commit()
    print(f"[DDL] Executed {filename} successfully.")

def load_dimensions(conn, transformed_data):
    """
    Loads all 5 dimension tables first to preserve referential integrity.
    Returns mapping dictionaries from natural codes to surrogate keys.
    """
    print("[LOAD] Loading Dimensions into dwh schema...")
    with conn.cursor() as cur:
        # 1. Load dim_partition
        p_df = transformed_data["dim_partition_df"]
        for _, row in p_df.iterrows():
            cur.execute("""
                INSERT INTO dwh.dim_partition (partition_code, partition_name, classification_role, description)
                VALUES (%s, %s, %s, %s)
                ON CONFLICT (partition_code) DO UPDATE 
                SET partition_name = EXCLUDED.partition_name,
                    classification_role = EXCLUDED.classification_role,
                    description = EXCLUDED.description;
            """, (row["partition_code"], row["partition_name"], row["classification_role"], row["description"]))

        # 2. Load dim_split
        s_df = transformed_data["dim_split_df"]
        for _, row in s_df.iterrows():
            cur.execute("""
                INSERT INTO dwh.dim_split (split_name, split_description)
                VALUES (%s, %s)
                ON CONFLICT (split_name) DO UPDATE 
                SET split_description = EXCLUDED.split_description;
            """, (row["split_name"], row["split_description"]))

        # 3. Load dim_source
        src_df = transformed_data["dim_source_df"]
        for _, row in src_df.iterrows():
            cur.execute("""
                INSERT INTO dwh.dim_source (source_name, dataset_role, source_format)
                VALUES (%s, %s, %s)
                ON CONFLICT (source_name) DO UPDATE 
                SET dataset_role = EXCLUDED.dataset_role,
                    source_format = EXCLUDED.source_format;
            """, (row["source_name"], row["dataset_role"], row["source_format"]))

        # 4. Load dim_project
        prj_df = transformed_data["dim_project_df"]
        for _, row in prj_df.iterrows():
            cur.execute("""
                INSERT INTO dwh.dim_project (project_name, primary_language)
                VALUES (%s, %s)
                ON CONFLICT (project_name) DO UPDATE 
                SET primary_language = EXCLUDED.primary_language;
            """, (row["project_name"], row["primary_language"]))

        # 5. Load dim_cwe
        cwe_df = transformed_data["dim_cwe_df"]
        cwe_records = [
            (row["cwe_code"], row["cwe_name"], row["severity_level"], row.get("description", ""))
            for _, row in cwe_df.iterrows()
        ]
        psycopg2.extras.execute_batch(cur, """
            INSERT INTO dwh.dim_cwe (cwe_code, cwe_name, severity_level, description)
            VALUES (%s, %s, %s, %s)
            ON CONFLICT (cwe_code) DO UPDATE 
            SET cwe_name = EXCLUDED.cwe_name,
                severity_level = EXCLUDED.severity_level,
                description = EXCLUDED.description;
        """, cwe_records)

    conn.commit()

    # Query back all surrogate key lookup maps
    lookups = {}
    with conn.cursor() as cur:
        cur.execute("SELECT partition_code, partition_key FROM dwh.dim_partition;")
        lookups["partition"] = dict(cur.fetchall())

        cur.execute("SELECT split_name, split_key FROM dwh.dim_split;")
        lookups["split"] = dict(cur.fetchall())

        cur.execute("SELECT source_name, source_key FROM dwh.dim_source;")
        lookups["source"] = dict(cur.fetchall())

        cur.execute("SELECT project_name, project_key FROM dwh.dim_project;")
        lookups["project"] = dict(cur.fetchall())

        cur.execute("SELECT cwe_code, cwe_key FROM dwh.dim_cwe;")
        lookups["cwe"] = dict(cur.fetchall())

    print(f"[LOAD] Dimensions successfully loaded and surrogate key maps cached.")
    return lookups

def load_fact_table(conn, fact_df, lookups, mode="full", batch_size=2000):
    """
    Loads fact_vulnerability_sample referencing surrogate keys.
    Supports mode='full' (replace) or mode='incremental' (insert non-existing).
    """
    print(f"[LOAD] Loading Fact Table (mode='{mode}')...")

    # Map surrogate keys
    fact_df["partition_key"] = fact_df["partition_code"].map(lookups["partition"])
    fact_df["split_key"] = fact_df["split_name"].map(lookups["split"])
    fact_df["source_key"] = fact_df["source_folder"].map(lookups["source"])
    fact_df["project_key"] = fact_df["project_name"].map(lookups["project"])

    unknown_cwe_key = lookups["cwe"].get("CWE-UNKNOWN", 1)
    fact_df["cwe_key"] = fact_df["cwe_code"].map(lookups["cwe"]).fillna(unknown_cwe_key).astype(int)

    records = []
    for _, row in fact_df.iterrows():
        records.append((
            row["sample_id"],
            int(row["partition_key"]),
            int(row["split_key"]),
            int(row["source_key"]),
            int(row["cwe_key"]),
            int(row["project_key"]),
            bool(row["is_vulnerable"]),
            str(row["raw_status"]),
            str(row["function_name"]),
            str(row["commit_hash"]),
            str(row["body_hash"]),
            int(row["code_length"]),
            int(row["token_count"]),
            int(row["line_count"]),
            bool(row["has_duplicate_body"])
        ))

    insert_sql = """
        INSERT INTO dwh.fact_vulnerability_sample (
            sample_id, partition_key, split_key, source_key, cwe_key, project_key,
            is_vulnerable, raw_status, function_name, commit_hash, body_hash,
            code_length, token_count, line_count, has_duplicate_body
        ) VALUES (
            %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s
        )
        ON CONFLICT (sample_id) DO NOTHING;
    """

    with conn.cursor() as cur:
        if mode == "full":
            cur.execute("TRUNCATE TABLE dwh.fact_vulnerability_sample CASCADE;")
            conn.commit()

        total = len(records)
        for i in range(0, total, batch_size):
            chunk = records[i:i + batch_size]
            psycopg2.extras.execute_batch(cur, insert_sql, chunk)
            print(f"[LOAD] Inserted batch {i + len(chunk)}/{total} into fact_vulnerability_sample")

    conn.commit()
    print(f"[LOAD] Fact table load complete. Total processed: {total}")

def run_loading(mode="full"):
    """Orchestrates Dimension and Fact loading."""
    print(f"=== STARTING TASK 5: LOADING WAREHOUSE (mode={mode}) ===")
    conn = get_db_connection()
    try:
        if mode == "full":
            run_ddl_script(conn, "02_dwh_star_schema.sql")

        jsonl_df, cwe_csv_df = fetch_staging_data()
        transformed_data = transform_data(jsonl_df, cwe_csv_df)
        
        # 1. Load dimensions first
        lookups = load_dimensions(conn, transformed_data)

        # 2. Load fact table
        load_fact_table(conn, transformed_data["fact_df"], lookups, mode=mode)
        print("=== TASK 5 COMPLETED SUCCESSFULLY ===")
    finally:
        conn.close()

if __name__ == "__main__":
    run_loading(mode="full")
