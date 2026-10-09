-- =============================================================================
-- SCRIPT: 01_staging_schema.sql
-- PURPOSE: Staging Layer Schema for Lab 3 Vulnerability Data Warehouse
-- ARCHITECTURE: Stores raw, unmodified data extracted from JSONL and CSV sources
-- =============================================================================

CREATE SCHEMA IF NOT EXISTS staging;

-- 1. Raw JSONL Staging Table (Java Vulnerability Samples from paper datasets)
DROP TABLE IF EXISTS staging.stg_vulnerability_raw_jsonl CASCADE;

CREATE TABLE staging.stg_vulnerability_raw_jsonl (
    stg_id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    source_folder TEXT NOT NULL,         -- 'without_p3' or 'with_p3'
    split_file TEXT NOT NULL,            -- 'train.jsonl', 'valid.jsonl', 'test.jsonl'
    raw_idx INT,
    raw_cwe TEXT,
    raw_status TEXT,
    raw_target INT,
    raw_commit TEXT,
    raw_function_name TEXT,
    raw_body_hash TEXT,
    raw_code TEXT,
    raw_token_count INT,
    loaded_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

-- 2. Raw CSV Staging Table (CWE Definitions and Severity Taxonomy)
DROP TABLE IF EXISTS staging.stg_cwe_metadata_csv CASCADE;

CREATE TABLE staging.stg_cwe_metadata_csv (
    stg_cwe_id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    cwe_code TEXT NOT NULL,
    cwe_name TEXT,
    severity_level TEXT,
    description TEXT,
    loaded_at TIMESTAMPTZ NOT NULL DEFAULT now()
);
