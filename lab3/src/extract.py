import os
import json
import csv
import psycopg2.extras
from config import get_db_connection, DATA_RAW_DIR, SQL_DIR

def run_ddl_script(conn, filename):
    """Executes a SQL script file."""
    filepath = os.path.join(SQL_DIR, filename)
    with open(filepath, "r", encoding="utf-8") as f:
        sql = f.read()
    with conn.cursor() as cur:
        cur.execute(sql)
    conn.commit()
    print(f"[DDL] Executed {filename} successfully.")

def extract_cwe_csv_to_staging(conn):
    """Extracts raw CWE definitions from CSV into staging."""
    csv_path = os.path.join(DATA_RAW_DIR, "cwe_definitions.csv")
    if not os.path.exists(csv_path):
        raise FileNotFoundError(f"CSV file not found at {csv_path}")

    records = []
    with open(csv_path, "r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            records.append((
                row["cwe_code"].strip(),
                row.get("cwe_name", "").strip(),
                row.get("severity_level", "Unknown").strip(),
                row.get("description", "").strip()
            ))

    insert_sql = """
        INSERT INTO staging.stg_cwe_metadata_csv 
        (cwe_code, cwe_name, severity_level, description)
        VALUES (%s, %s, %s, %s);
    """
    with conn.cursor() as cur:
        psycopg2.extras.execute_batch(cur, insert_sql, records)
    conn.commit()
    print(f"[EXTRACT] Ingested {len(records)} CWE metadata rows from CSV into staging.stg_cwe_metadata_csv.")

def extract_jsonl_to_staging(conn, batch_size=2000):
    """Extracts raw vulnerability JSONL datasets into staging."""
    folders = ["without_p3", "with_p3"]
    split_files = ["train.jsonl", "valid.jsonl", "test.jsonl"]

    insert_sql = """
        INSERT INTO staging.stg_vulnerability_raw_jsonl
        (source_folder, split_file, raw_idx, raw_cwe, raw_status, raw_target, 
         raw_commit, raw_function_name, raw_body_hash, raw_code, raw_token_count)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s);
    """

    total_inserted = 0
    with conn.cursor() as cur:
        for folder in folders:
            folder_path = os.path.join(DATA_RAW_DIR, folder)
            for split_file in split_files:
                file_path = os.path.join(folder_path, split_file)
                if not os.path.exists(file_path):
                    print(f"[WARN] Skipping missing file {file_path}")
                    continue

                batch = []
                with open(file_path, "r", encoding="utf-8") as f:
                    for line_idx, line in enumerate(f):
                        line = line.strip()
                        if not line:
                            continue
                        data = json.loads(line)
                        tokens = data.get("code_tokens", [])
                        token_count = len(tokens) if isinstance(tokens, list) else 0

                        batch.append((
                            folder,
                            split_file,
                            data.get("idx"),
                            data.get("cwe"),
                            data.get("status"),
                            data.get("target"),
                            data.get("commit"),
                            data.get("function_name"),
                            data.get("body_hash"),
                            data.get("code"),
                            token_count
                        ))

                        if len(batch) >= batch_size:
                            psycopg2.extras.execute_batch(cur, insert_sql, batch)
                            total_inserted += len(batch)
                            batch.clear()

                if batch:
                    psycopg2.extras.execute_batch(cur, insert_sql, batch)
                    total_inserted += len(batch)
                    batch.clear()

                print(f"[EXTRACT] Ingested {folder}/{split_file} into staging.")

    conn.commit()
    print(f"[EXTRACT] Total JSONL records ingested into staging: {total_inserted}")

def run_extraction():
    """Main extraction runner."""
    print("=== STARTING TASK 3: EXTRACTION TO STAGING ===")
    conn = get_db_connection()
    try:
        # 1. Initialize staging schema
        run_ddl_script(conn, "01_staging_schema.sql")
        # 2. Ingest CSV source
        extract_cwe_csv_to_staging(conn)
        # 3. Ingest JSONL sources
        extract_jsonl_to_staging(conn)
        print("=== TASK 3 COMPLETED SUCCESSFULLY ===")
    finally:
        conn.close()

if __name__ == "__main__":
    run_extraction()
