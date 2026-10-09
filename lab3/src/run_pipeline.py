import argparse
import sys
import time
from extract import run_extraction
from load import run_loading
from quality_checks import run_quality_checks
from run_analytics import run_analytics

def main():
    parser = argparse.ArgumentParser(description="End-to-End Vulnerability Data Warehouse ETL Pipeline")
    parser.add_argument("--mode", choices=["full", "incremental"], default="full", 
                        help="Warehouse load mode: 'full' (recreate tables) or 'incremental' (append non-existing)")
    args = parser.parse_args()

    start_time = time.time()
    print("=" * 80)
    print("   VULNERABILITY DATA WAREHOUSE (LAB 3) ETL PIPELINE EXECUTION")
    print(f"   Target Engine: PostgreSQL | Mode: {args.mode.upper()}")
    print("=" * 80)

    try:
        # Phase 1: Task 3 - Extract to Staging
        run_extraction()

        # Phase 2: Task 4 & Task 5 - Transform & Load into Star Schema
        run_loading(mode=args.mode)

        # Phase 3: Task 6 - Data Quality Checks
        run_quality_checks()

        # Phase 4: Task 7 - Analytical SQL Queries
        run_analytics()

        elapsed = time.time() - start_time
        print("\n" + "=" * 80)
        print(f"   ETL PIPELINE COMPLETED SUCCESSFULLY IN {elapsed:.2f} SECONDS")
        print("=" * 80)

    except Exception as e:
        print(f"\n[ERROR] Pipeline failed with error: {e}", file=sys.stderr)
        sys.exit(1)

if __name__ == "__main__":
    main()
