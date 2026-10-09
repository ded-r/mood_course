-- =============================================================================
-- SCRIPT: 03_quality_checks.sql
-- PURPOSE: Task 6 Data Quality Validation Suite
-- DESCRIPTION: Automated integrity assertions to ensure clean, audit-ready data
-- =============================================================================

-- CHECK 1: Unique Sample / Record Identifier
-- Expectation: Zero duplicates for natural business key sample_id
SELECT 
    'CHECK 1: Unique Sample ID' AS check_name,
    COUNT(*) - COUNT(DISTINCT sample_id) AS failed_records,
    CASE WHEN COUNT(*) = COUNT(DISTINCT sample_id) THEN 'PASSED' ELSE 'FAILED' END AS status
FROM dwh.fact_vulnerability_sample;

-- CHECK 2: Non-Null Vulnerability Label
-- Expectation: Zero records with NULL in target classification flag
SELECT 
    'CHECK 2: Non-null Vulnerability Label' AS check_name,
    COUNT(*) AS failed_records,
    CASE WHEN COUNT(*) = 0 THEN 'PASSED' ELSE 'FAILED' END AS status
FROM dwh.fact_vulnerability_sample
WHERE is_vulnerable IS NULL;

-- CHECK 3: Valid Split Values
-- Expectation: All records must map to 'train', 'valid', or 'test'
SELECT 
    'CHECK 3: Valid Split Values' AS check_name,
    COUNT(*) AS failed_records,
    CASE WHEN COUNT(*) = 0 THEN 'PASSED' ELSE 'FAILED' END AS status
FROM dwh.fact_vulnerability_sample f
JOIN dwh.dim_split s ON f.split_key = s.split_key
WHERE s.split_name NOT IN ('train', 'valid', 'test');

-- CHECK 4: Valid Dataset Partition
-- Expectation: All records must map to 'P1', 'P2', or 'P3'
SELECT 
    'CHECK 4: Valid Dataset Partition' AS check_name,
    COUNT(*) AS failed_records,
    CASE WHEN COUNT(*) = 0 THEN 'PASSED' ELSE 'FAILED' END AS status
FROM dwh.fact_vulnerability_sample f
JOIN dwh.dim_partition p ON f.partition_key = p.partition_key
WHERE p.partition_code NOT IN ('P1', 'P2', 'P3');

-- CHECK 5: Code Measurement Sanity (code_length and line_count > 0)
-- Expectation: No empty or negative length code snippets
SELECT 
    'CHECK 5: Code Measurement Sanity' AS check_name,
    COUNT(*) AS failed_records,
    CASE WHEN COUNT(*) = 0 THEN 'PASSED' ELSE 'FAILED' END AS status
FROM dwh.fact_vulnerability_sample
WHERE code_length <= 0 OR line_count <= 0;

-- CHECK 6 (Additional): Referential Integrity Across Dimensions
-- Expectation: Zero orphaned fact rows
SELECT 
    'CHECK 6: Referential Integrity' AS check_name,
    COUNT(*) AS failed_records,
    CASE WHEN COUNT(*) = 0 THEN 'PASSED' ELSE 'FAILED' END AS status
FROM dwh.fact_vulnerability_sample f
LEFT JOIN dwh.dim_partition p ON f.partition_key = p.partition_key
LEFT JOIN dwh.dim_split s ON f.split_key = s.split_key
LEFT JOIN dwh.dim_source src ON f.source_key = src.source_key
LEFT JOIN dwh.dim_cwe c ON f.cwe_key = c.cwe_key
LEFT JOIN dwh.dim_project prj ON f.project_key = prj.project_key
WHERE p.partition_key IS NULL 
   OR s.split_key IS NULL 
   OR src.source_key IS NULL 
   OR c.cwe_key IS NULL 
   OR prj.project_key IS NULL;

-- CHECK 7 (Additional): CWE Taxonomy Formatting
-- Expectation: All CWE codes adhere to standard pattern
SELECT 
    'CHECK 7: CWE Code Format' AS check_name,
    COUNT(*) AS failed_records,
    CASE WHEN COUNT(*) = 0 THEN 'PASSED' ELSE 'FAILED' END AS status
FROM dwh.dim_cwe
WHERE cwe_code !~ '^CWE-[0-9]+$' AND cwe_code != 'CWE-UNKNOWN';
