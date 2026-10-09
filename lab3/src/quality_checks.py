import os
from tabulate import tabulate
from config import get_db_connection, SQL_DIR, OUTPUT_DIR

def run_quality_checks():
    """
    Executes Task 6 Data Quality Validation Suite against the warehouse.
    Verifies assertions and outputs a formatted compliance report.
    """
    print("=== STARTING TASK 6: DATA QUALITY VERIFICATION ===")
    conn = get_db_connection()
    try:
        sql_file = os.path.join(SQL_DIR, "03_quality_checks.sql")
        with open(sql_file, "r", encoding="utf-8") as f:
            full_sql = f.read()

        raw_statements = [s.strip() for s in full_sql.split(";") if s.strip()]
        valid_queries = []
        for s in raw_statements:
            lines = [l for l in s.splitlines() if not l.strip().startswith("--")]
            stmt = "\n".join(lines).strip()
            if stmt:
                valid_queries.append(stmt)

        results = []
        all_passed = True

        with conn.cursor() as cur:
            for q in valid_queries:
                cur.execute(q)
                rows = cur.fetchall()
                for row in rows:
                    check_name, failed_count, status = row[0], row[1], row[2]
                    is_passed = (status == "PASSED")
                    if not is_passed:
                        all_passed = False
                    results.append([check_name, failed_count, status])

        headers = ["Data Quality Check Rule", "Failed Records", "Compliance Status"]
        table_output = tabulate(results, headers=headers, tablefmt="github")
        print("\n" + table_output + "\n")

        output_path = os.path.join(OUTPUT_DIR, "data_quality_report.txt")
        with open(output_path, "w", encoding="utf-8") as f:
            f.write("TASK 6: DATA QUALITY VALIDATION SUITE REPORT\n")
            f.write("=" * 60 + "\n\n")
            f.write(table_output + "\n\n")
            f.write(f"OVERALL STATUS: {'ALL CHECKS PASSED (100%)' if all_passed else 'SOME CHECKS FAILED'}\n")

        print(f"[QUALITY] Report saved to {output_path}")
        if not all_passed:
            raise AssertionError("Some data quality checks failed! Review report above.")
        print("=== TASK 6 COMPLETED: ALL QUALITY CHECKS PASSED ===")
        return results
    finally:
        conn.close()

if __name__ == "__main__":
    run_quality_checks()
