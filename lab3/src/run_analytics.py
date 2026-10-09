import os
import pandas as pd
from tabulate import tabulate
from config import get_db_connection, SQL_DIR, OUTPUT_DIR

QUERIES = [
    {
        "id": "QUERY 1",
        "title": "Overall Vulnerable vs Non-Vulnerable Sample Distribution",
        "sql": """
            SELECT 
                CASE WHEN f.is_vulnerable THEN 'Vulnerable (Class 1)' ELSE 'Non-Vulnerable (Class 0)' END AS vulnerability_status,
                COUNT(*) AS total_samples,
                ROUND(100.0 * COUNT(*) / SUM(COUNT(*)) OVER (), 2) AS percentage_share
            FROM dwh.fact_vulnerability_sample f
            GROUP BY f.is_vulnerable
            ORDER BY f.is_vulnerable DESC;
        """
    },
    {
        "id": "QUERY 2",
        "title": "Class Ratio by Dataset Partition (P1, P2, P3)",
        "sql": """
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
        """
    },
    {
        "id": "QUERY 3",
        "title": "Sample Counts by Source Dataset Configuration",
        "sql": """
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
        """
    },
    {
        "id": "QUERY 4",
        "title": "Top 10 CWE Vulnerability Categories",
        "sql": """
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
        """
    },
    {
        "id": "QUERY 5",
        "title": "Train / Validation / Test Split Distributions Across Classes",
        "sql": """
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
        """
    },
    {
        "id": "QUERY 6",
        "title": "Audit of Missing, Unknown, or Flagged Records",
        "sql": """
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
        """
    }
]

def run_analytics():
    """Executes all 6 analytical queries and exports Markdown and formatted logs."""
    print("=== STARTING TASK 7: ANALYTICAL SQL QUERIES ===")
    conn = get_db_connection()
    md_output = ["# Task 7: Analytical SQL Results\n"]

    try:
        with conn.cursor() as cur:
            for item in QUERIES:
                print(f"\n--- {item['id']}: {item['title']} ---")
                cur.execute(item["sql"])
                col_names = [desc[0] for desc in cur.description]
                rows = cur.fetchall()

                table_str = tabulate(rows, headers=col_names, tablefmt="github")
                print(table_str)

                md_output.append(f"### {item['id']}: {item['title']}\n")
                md_output.append("```sql\n" + item["sql"].strip() + "\n```\n")
                md_output.append(table_str + "\n")

        # Save to output file
        report_path = os.path.join(OUTPUT_DIR, "analytical_queries_output.md")
        with open(report_path, "w", encoding="utf-8") as f:
            f.write("\n".join(md_output))
        print(f"\n[ANALYTICS] Results saved to {report_path}")
        print("=== TASK 7 COMPLETED SUCCESSFULLY ===")
    finally:
        conn.close()

if __name__ == "__main__":
    run_analytics()
