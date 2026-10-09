-- =============================================================================
-- SCRIPT: 04_analytical_queries.sql
-- PURPOSE: Task 7 Analytical SQL Queries for Vulnerability Research
-- =============================================================================

-- -----------------------------------------------------------------------------
-- QUERY 1: Count Vulnerable vs Non-Vulnerable Samples Overall
-- Demonstrates global binary class breakdown
-- -----------------------------------------------------------------------------
SELECT 
    CASE WHEN f.is_vulnerable THEN 'Vulnerable (Class 1)' ELSE 'Non-Vulnerable (Class 0)' END AS vulnerability_status,
    COUNT(*) AS total_samples,
    ROUND(100.0 * COUNT(*) / SUM(COUNT(*)) OVER (), 2) AS percentage_share
FROM dwh.fact_vulnerability_sample f
GROUP BY f.is_vulnerable
ORDER BY f.is_vulnerable DESC;

-- -----------------------------------------------------------------------------
-- QUERY 2: Class Ratio by Dataset Partition (P1, P2, P3)
-- Demonstrates role of hard negatives (P2) vs easy negatives (P3)
-- -----------------------------------------------------------------------------
SELECT 
    p.partition_code,
    p.partition_name,
    p.classification_role,
    COUNT(*) AS total_samples,
    COUNT(*) FILTER (WHERE f.is_vulnerable) AS vulnerable_count,
    COUNT(*) FILTER (WHERE NOT f.is_vulnerable) AS non_vulnerable_count,
    ROUND(
        COUNT(*) FILTER (WHERE f.is_vulnerable)::NUMERIC / 
        NULLIF(COUNT(*) FILTER (WHERE NOT f.is_vulnerable), 0), 4
    ) AS positive_to_negative_ratio
FROM dwh.fact_vulnerability_sample f
JOIN dwh.dim_partition p ON f.partition_key = p.partition_key
GROUP BY p.partition_code, p.partition_name, p.classification_role
ORDER BY p.partition_code;

-- -----------------------------------------------------------------------------
-- QUERY 3: Count Samples by Source Dataset Variant
-- Compares balanced (without_p3) vs realistic imbalanced (with_p3)
-- -----------------------------------------------------------------------------
SELECT 
    src.source_name,
    src.dataset_role,
    COUNT(*) AS total_samples,
    COUNT(*) FILTER (WHERE f.is_vulnerable) AS positive_samples,
    COUNT(*) FILTER (WHERE NOT f.is_vulnerable) AS negative_samples,
    ROUND(
        COUNT(*) FILTER (WHERE NOT f.is_vulnerable)::NUMERIC / 
        NULLIF(COUNT(*) FILTER (WHERE f.is_vulnerable), 0), 2
    ) AS negative_to_positive_multiplier
FROM dwh.fact_vulnerability_sample f
JOIN dwh.dim_source src ON f.source_key = src.source_key
GROUP BY src.source_name, src.dataset_role
ORDER BY total_samples DESC;

-- -----------------------------------------------------------------------------
-- QUERY 4: Top 10 CWE Vulnerability Weakness Categories
-- Shows most prevalent security flaw categories in Java code
-- -----------------------------------------------------------------------------
SELECT 
    c.cwe_code,
    c.cwe_name,
    c.severity_level,
    COUNT(*) AS occurrence_count,
    COUNT(*) FILTER (WHERE f.is_vulnerable) AS vulnerable_functions,
    ROUND(100.0 * COUNT(*) / SUM(COUNT(*)) OVER (), 2) AS pct_of_all_samples
FROM dwh.fact_vulnerability_sample f
JOIN dwh.dim_cwe c ON f.cwe_key = c.cwe_key
GROUP BY c.cwe_code, c.cwe_name, c.severity_level
ORDER BY occurrence_count DESC
LIMIT 10;

-- -----------------------------------------------------------------------------
-- QUERY 5: Train / Validation / Test Distributions Across Classes
-- Evaluates experimental split consistency for ML model training
-- -----------------------------------------------------------------------------
SELECT 
    s.split_name,
    src.source_name,
    COUNT(*) AS total_split_samples,
    COUNT(*) FILTER (WHERE f.is_vulnerable) AS vulnerable_samples,
    COUNT(*) FILTER (WHERE NOT f.is_vulnerable) AS non_vulnerable_samples,
    ROUND(100.0 * COUNT(*) FILTER (WHERE f.is_vulnerable) / COUNT(*), 2) AS positive_pct
FROM dwh.fact_vulnerability_sample f
JOIN dwh.dim_split s ON f.split_key = s.split_key
JOIN dwh.dim_source src ON f.source_key = src.source_key
GROUP BY s.split_name, src.source_name
ORDER BY src.source_name, 
    CASE s.split_name 
        WHEN 'train' THEN 1 
        WHEN 'valid' THEN 2 
        WHEN 'test' THEN 3 
    END;

-- -----------------------------------------------------------------------------
-- QUERY 6: Identify Missing, Unknown, or Flagged Records
-- Detects data quality anomalies (CWE-UNKNOWN, duplicate code bodies)
-- -----------------------------------------------------------------------------
SELECT 
    'Samples with CWE-UNKNOWN' AS category,
    COUNT(*) AS record_count,
    ROUND(100.0 * COUNT(*) / (SELECT COUNT(*) FROM dwh.fact_vulnerability_sample), 2) AS pct_of_total
FROM dwh.fact_vulnerability_sample f
JOIN dwh.dim_cwe c ON f.cwe_key = c.cwe_key
WHERE c.cwe_code = 'CWE-UNKNOWN'

UNION ALL

SELECT 
    'Samples with Duplicate Code Body (Data Leakage Risk)' AS category,
    COUNT(*) AS record_count,
    ROUND(100.0 * COUNT(*) / (SELECT COUNT(*) FROM dwh.fact_vulnerability_sample), 2) AS pct_of_total
FROM dwh.fact_vulnerability_sample f
WHERE f.has_duplicate_body = TRUE

UNION ALL

SELECT 
    'Samples with Missing Commit Hash' AS category,
    COUNT(*) AS record_count,
    ROUND(100.0 * COUNT(*) / (SELECT COUNT(*) FROM dwh.fact_vulnerability_sample), 2) AS pct_of_total
FROM dwh.fact_vulnerability_sample f
WHERE f.commit_hash IS NULL OR f.commit_hash = '';
