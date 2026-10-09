-- =============================================================================
-- SCRIPT: 02_dwh_star_schema.sql
-- PURPOSE: Star Schema Data Warehouse Schema for Vulnerability Detection
-- ARCHITECTURE: 5 Dimensions (Partition, Split, Source, CWE, Project) + 1 Central Fact
-- =============================================================================

CREATE SCHEMA IF NOT EXISTS dwh;

-- Drop existing tables with CASCADE to allow clean redeployments
DROP TABLE IF EXISTS dwh.fact_vulnerability_sample CASCADE;
DROP TABLE IF EXISTS dwh.dim_partition CASCADE;
DROP TABLE IF EXISTS dwh.dim_split CASCADE;
DROP TABLE IF EXISTS dwh.dim_source CASCADE;
DROP TABLE IF EXISTS dwh.dim_cwe CASCADE;
DROP TABLE IF EXISTS dwh.dim_project CASCADE;

-- -----------------------------------------------------------------------------
-- 1. DIMENSION: dim_partition
-- Represents the paper's P1, P2, P3 data partitions and classification roles
-- -----------------------------------------------------------------------------
CREATE TABLE dwh.dim_partition (
    partition_key BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    partition_code TEXT NOT NULL UNIQUE,          -- 'P1', 'P2', 'P3'
    partition_name TEXT NOT NULL,                 -- 'Vulnerable Function (Pre-change)', 'Fixed Function (Post-change)', 'Neutral Function (Unchanged)'
    classification_role TEXT NOT NULL,            -- 'Positive Class', 'Hard Negative', 'Easy Negative'
    description TEXT
);

-- -----------------------------------------------------------------------------
-- 2. DIMENSION: dim_split
-- Represents the experimental dataset split (train, validation, test)
-- -----------------------------------------------------------------------------
CREATE TABLE dwh.dim_split (
    split_key BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    split_name TEXT NOT NULL UNIQUE,              -- 'train', 'valid', 'test'
    split_description TEXT
);

-- -----------------------------------------------------------------------------
-- 3. DIMENSION: dim_source
-- Represents the dataset variant / source configuration from the paper
-- -----------------------------------------------------------------------------
CREATE TABLE dwh.dim_source (
    source_key BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    source_name TEXT NOT NULL UNIQUE,              -- 'without_p3', 'with_p3'
    dataset_role TEXT NOT NULL,                   -- 'Balanced Dataset (1:1 ablation)', 'Imbalanced Dataset (1:34 realistic)'
    source_format TEXT NOT NULL DEFAULT 'JSONL'
);

-- -----------------------------------------------------------------------------
-- 4. DIMENSION: dim_cwe
-- Common Weakness Enumeration taxonomy enriched from the CSV source
-- -----------------------------------------------------------------------------
CREATE TABLE dwh.dim_cwe (
    cwe_key BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    cwe_code TEXT NOT NULL UNIQUE,                -- e.g. 'CWE-20', 'CWE-79', 'CWE-UNKNOWN'
    cwe_name TEXT NOT NULL,                       -- e.g. 'Improper Input Validation'
    severity_level TEXT NOT NULL,                 -- 'Critical', 'High', 'Medium', 'Low', 'Unknown'
    description TEXT
);

-- -----------------------------------------------------------------------------
-- 5. DIMENSION: dim_project
-- Software project / repository dimension for tracking provenance
-- -----------------------------------------------------------------------------
CREATE TABLE dwh.dim_project (
    project_key BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    project_name TEXT NOT NULL UNIQUE,            -- e.g. 'open-source-java-cvefixes'
    primary_language TEXT NOT NULL DEFAULT 'Java'
);

-- -----------------------------------------------------------------------------
-- 6. FACT TABLE: fact_vulnerability_sample
-- Central fact table storing measurable attributes of each code sample
-- -----------------------------------------------------------------------------
CREATE TABLE dwh.fact_vulnerability_sample (
    sample_key BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    sample_id TEXT NOT NULL UNIQUE,               -- Natural business key for traceability
    partition_key BIGINT NOT NULL REFERENCES dwh.dim_partition(partition_key),
    split_key BIGINT NOT NULL REFERENCES dwh.dim_split(split_key),
    source_key BIGINT NOT NULL REFERENCES dwh.dim_source(source_key),
    cwe_key BIGINT NOT NULL REFERENCES dwh.dim_cwe(cwe_key),
    project_key BIGINT NOT NULL REFERENCES dwh.dim_project(project_key),
    
    -- Analytical attributes and measures
    is_vulnerable BOOLEAN NOT NULL,               -- Unified Boolean representation: True = 1, False = 0
    raw_status TEXT NOT NULL,                     -- Original raw label: 'VULNERABLE', 'FIXED', 'NOT_VULNERABLE'
    function_name TEXT NOT NULL,                  -- Function / method name
    commit_hash TEXT,                             -- Git commit hash
    body_hash TEXT NOT NULL,                      -- Hash of code body for duplicate detection
    code_length INT NOT NULL CHECK (code_length > 0), -- Measured characters
    token_count INT NOT NULL CHECK (token_count >= 0),-- Measured tokens
    line_count INT NOT NULL CHECK (line_count > 0),   -- Measured lines of code
    has_duplicate_body BOOLEAN NOT NULL DEFAULT FALSE,-- Flag for data leakage detection
    created_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

-- Explicit indexes on all Foreign Keys (best practice in PostgreSQL)
CREATE INDEX idx_fact_partition ON dwh.fact_vulnerability_sample (partition_key);
CREATE INDEX idx_fact_split ON dwh.fact_vulnerability_sample (split_key);
CREATE INDEX idx_fact_source ON dwh.fact_vulnerability_sample (source_key);
CREATE INDEX idx_fact_cwe ON dwh.fact_vulnerability_sample (cwe_key);
CREATE INDEX idx_fact_project ON dwh.fact_vulnerability_sample (project_key);

-- Filter & Analytics indexes
CREATE INDEX idx_fact_is_vulnerable ON dwh.fact_vulnerability_sample (is_vulnerable);
CREATE INDEX idx_fact_body_hash ON dwh.fact_vulnerability_sample (body_hash);
CREATE INDEX idx_fact_composite_analysis ON dwh.fact_vulnerability_sample (source_key, split_key, is_vulnerable);
