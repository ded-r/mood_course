# Task 7: Analytical SQL Results

### QUERY 1: Overall Vulnerable vs Non-Vulnerable Sample Distribution

```sql
SELECT 
                CASE WHEN f.is_vulnerable THEN 'Vulnerable (Class 1)' ELSE 'Non-Vulnerable (Class 0)' END AS vulnerability_status,
                COUNT(*) AS total_samples,
                ROUND(100.0 * COUNT(*) / SUM(COUNT(*)) OVER (), 2) AS percentage_share
            FROM dwh.fact_vulnerability_sample f
            GROUP BY f.is_vulnerable
            ORDER BY f.is_vulnerable DESC;
```

| vulnerability_status     |   total_samples |   percentage_share |
|--------------------------|-----------------|--------------------|
| Vulnerable (Class 1)     |            1311 |                5.4 |
| Non-Vulnerable (Class 0) |           22977 |               94.6 |

### QUERY 2: Class Ratio by Dataset Partition (P1, P2, P3)

```sql
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
```

| partition_code   | partition_name                   | classification_role   |   total_samples |   vulnerable_count |   non_vulnerable_count |   positive_to_negative_ratio |
|------------------|----------------------------------|-----------------------|-----------------|--------------------|------------------------|------------------------------|
| P1               | Vulnerable Function (Pre-change) | Positive Class        |            1311 |               1311 |                      0 |                              |
| P2               | Fixed Function (Post-change)     | Hard Negative         |            1316 |                  0 |                   1316 |                            0 |
| P3               | Neutral Function (Unchanged)     | Easy Negative         |           21661 |                  0 |                  21661 |                            0 |

### QUERY 3: Sample Counts by Source Dataset Configuration

```sql
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
```

| source_name   | dataset_role                        |   total_samples |   positive_samples |   negative_samples |   negative_to_positive_multiplier |
|---------------|-------------------------------------|-----------------|--------------------|--------------------|-----------------------------------|
| with_p3       | Imbalanced Dataset (1:34 realistic) |           22954 |                646 |              22308 |                             34.53 |
| without_p3    | Balanced Dataset (1:1 ablation)     |            1334 |                665 |                669 |                              1.01 |

### QUERY 4: Top 10 CWE Vulnerability Categories

```sql
SELECT 
                c.cwe_code,
                c.cwe_name,
                c.severity_level,
                COUNT(*) AS occurrence_count,
                COUNT(*) FILTER (WHERE f.is_vulnerable) AS vulnerable_functions,
                ROUND(100.0 * COUNT(*) / (SELECT COUNT(*) FROM dwh.fact_vulnerability_sample), 2) AS pct_of_all_samples
            FROM dwh.fact_vulnerability_sample f
            JOIN dwh.dim_cwe c ON f.cwe_key = c.cwe_key
            GROUP BY c.cwe_code, c.cwe_name, c.severity_level
            ORDER BY occurrence_count DESC
            LIMIT 10;
```

| cwe_code    | cwe_name                                     | severity_level   |   occurrence_count |   vulnerable_functions |   pct_of_all_samples |
|-------------|----------------------------------------------|------------------|--------------------|------------------------|----------------------|
| CWE-UNKNOWN | Unknown or Unmapped Weakness                 | Low              |               3375 |                    172 |                13.9  |
| CWE-20      | Improper Input Validation                    | High             |               2051 |                    100 |                 8.44 |
| CWE-200     | Information Exposure                         | Medium           |               1701 |                     51 |                 7    |
| CWE-79      | Cross-site Scripting (XSS)                   | High             |               1627 |                    106 |                 6.7  |
| CWE-264     | Permissions, Privileges, and Access Controls | High             |               1531 |                     66 |                 6.3  |
| CWE-611     | Weakness Classification CWE-611              | Medium           |               1158 |                     99 |                 4.77 |
| CWE-863     | Incorrect Authorization                      | High             |                998 |                     37 |                 4.11 |
| CWE-352     | Cross-Site Request Forgery (CSRF)            | Medium           |                925 |                     36 |                 3.81 |
| CWE-22      | Path Traversal                               | High             |                919 |                     74 |                 3.78 |
| CWE-862     | Missing Authorization                        | High             |                817 |                     16 |                 3.36 |

### QUERY 5: Train / Validation / Test Split Distributions Across Classes

```sql
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
```

| split_name   | source_name   |   total_split_samples |   vulnerable_samples |   non_vulnerable_samples |   positive_pct |
|--------------|---------------|-----------------------|----------------------|--------------------------|----------------|
| train        | without_p3    |                   810 |                  403 |                      407 |          49.75 |
| valid        | without_p3    |                   272 |                  139 |                      133 |          51.1  |
| test         | without_p3    |                   252 |                  123 |                      129 |          48.81 |
| train        | with_p3       |                 13247 |                  397 |                    12850 |           3    |
| valid        | with_p3       |                  5131 |                  130 |                     5001 |           2.53 |
| test         | with_p3       |                  4576 |                  119 |                     4457 |           2.6  |

### QUERY 6: Audit of Missing, Unknown, or Flagged Records

```sql
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
            WHERE f.commit_hash IS NULL OR f.commit_hash = '' OR f.commit_hash = 'unknown_commit';
```

| category                                             |   record_count |   pct_of_total |
|------------------------------------------------------|----------------|----------------|
| Samples with CWE-UNKNOWN                             |           3375 |          13.9  |
| Samples with Duplicate Code Body (Data Leakage Risk) |           2668 |          10.98 |
| Samples with Missing Commit Hash                     |              0 |           0    |
