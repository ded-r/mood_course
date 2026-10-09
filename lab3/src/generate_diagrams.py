import os
import matplotlib.pyplot as plt
import matplotlib.patches as patches
from config import OUTPUT_DIR

def create_architecture_diagram():
    """Generates a polished Source-to-Target Data Flow Architecture Diagram."""
    fig, ax = plt.subplots(figsize=(12, 7), dpi=300)
    ax.set_xlim(0, 12)
    ax.set_ylim(0, 7)
    ax.axis("off")

    # Title
    ax.text(6, 6.6, "End-to-End Vulnerability Data Warehouse Architecture", 
            ha="center", va="center", fontsize=15, fontweight="bold", color="#1E293B")
    ax.text(6, 6.25, "Source Ingestion  →  Staging Layer  →  ETL / Integration  →  Star Schema  →  ML / Analytics", 
            ha="center", va="center", fontsize=10, color="#64748B", style="italic")

    # Layer 1: Sources (x: 0.5 to 2.5)
    box_sources = patches.FancyBboxPatch((0.5, 1.2), 2.2, 4.5, boxstyle="round,pad=0.2", 
                                        ec="#3B82F6", fc="#EFF6FF", lw=1.5)
    ax.add_patch(box_sources)
    ax.text(1.6, 5.3, "OPERATIONAL\nSOURCES", ha="center", va="center", fontsize=11, fontweight="bold", color="#1E40AF")
    
    # Source sub-boxes
    s1 = patches.FancyBboxPatch((0.7, 3.8), 1.8, 1.1, boxstyle="round,pad=0.1", ec="#93C5FD", fc="#FFFFFF", lw=1)
    ax.add_patch(s1)
    ax.text(1.6, 4.35, "Raw JSONL Files\n(without_p3 / with_p3)\n24,288 samples", ha="center", va="center", fontsize=8.5, color="#1E3A8A")

    s2 = patches.FancyBboxPatch((0.7, 1.7), 1.8, 1.1, boxstyle="round,pad=0.1", ec="#93C5FD", fc="#FFFFFF", lw=1)
    ax.add_patch(s2)
    ax.text(1.6, 2.25, "Raw CSV File\n(cwe_definitions.csv)\nCWE Taxonomy", ha="center", va="center", fontsize=8.5, color="#1E3A8A")

    # Arrow 1 -> 2
    ax.annotate("", xy=(3.3, 3.5), xytext=(2.8, 3.5),
                arrowprops=dict(arrowstyle="->", lw=2, color="#3B82F6"))

    # Layer 2: Staging (x: 3.4 to 5.2)
    box_staging = patches.FancyBboxPatch((3.4, 1.2), 2.0, 4.5, boxstyle="round,pad=0.2", 
                                         ec="#8B5CF6", fc="#F5F3FF", lw=1.5)
    ax.add_patch(box_staging)
    ax.text(4.4, 5.3, "POSTGRESQL\nSTAGING", ha="center", va="center", fontsize=11, fontweight="bold", color="#5B21B6")
    
    stg1 = patches.FancyBboxPatch((3.55, 3.5), 1.7, 1.3, boxstyle="round,pad=0.1", ec="#C4B5FD", fc="#FFFFFF", lw=1)
    ax.add_patch(stg1)
    ax.text(4.4, 4.15, "staging.\nstg_vulnerability_\nraw_jsonl\n(24,288 rows)", ha="center", va="center", fontsize=8, color="#4C1D95")

    stg2 = patches.FancyBboxPatch((3.55, 1.7), 1.7, 1.1, boxstyle="round,pad=0.1", ec="#C4B5FD", fc="#FFFFFF", lw=1)
    ax.add_patch(stg2)
    ax.text(4.4, 2.25, "staging.\nstg_cwe_metadata_csv\n(25 rows)", ha="center", va="center", fontsize=8, color="#4C1D95")

    # Arrow 2 -> 3
    ax.annotate("", xy=(6.0, 3.5), xytext=(5.5, 3.5),
                arrowprops=dict(arrowstyle="->", lw=2, color="#8B5CF6"))

    # Layer 3: ETL Pipeline (x: 6.1 to 8.2)
    box_etl = patches.FancyBboxPatch((6.1, 1.2), 2.2, 4.5, boxstyle="round,pad=0.2", 
                                     ec="#10B981", fc="#ECFDF5", lw=1.5)
    ax.add_patch(box_etl)
    ax.text(7.2, 5.3, "PYTHON ETL\nENGINE", ha="center", va="center", fontsize=11, fontweight="bold", color="#065F46")
    
    etl_text = (
        "• Schema Harmonization\n"
        "• Boolean Target Normalization\n"
        "• P1 / P2 / P3 Partitioning\n"
        "• CWE Cleaning & Taxonomy\n"
        "• Duplicate Body Flagging\n"
        "• Code Metrics (Length/Lines)\n"
        "• Surrogate Key Generation\n"
        "• Automated Quality Checks"
    )
    e1 = patches.FancyBboxPatch((6.25, 1.5), 1.9, 3.3, boxstyle="round,pad=0.1", ec="#A7F3D0", fc="#FFFFFF", lw=1)
    ax.add_patch(e1)
    ax.text(7.2, 3.15, etl_text, ha="center", va="center", fontsize=8, color="#064E3B", linespacing=1.3)

    # Arrow 3 -> 4
    ax.annotate("", xy=(8.9, 3.5), xytext=(8.4, 3.5),
                arrowprops=dict(arrowstyle="->", lw=2, color="#10B981"))

    # Layer 4: Star Schema DWH (x: 9.0 to 11.4)
    box_dwh = patches.FancyBboxPatch((9.0, 1.2), 2.4, 4.5, boxstyle="round,pad=0.2", 
                                     ec="#F59E0B", fc="#FFFBEB", lw=1.5)
    ax.add_patch(box_dwh)
    ax.text(10.2, 5.3, "STAR SCHEMA\nWAREHOUSE", ha="center", va="center", fontsize=11, fontweight="bold", color="#92400E")

    dwh_text = (
        "FACT TABLE:\n"
        "• fact_vulnerability_sample\n"
        "  (24,288 Records)\n\n"
        "DIMENSION TABLES:\n"
        "• dim_partition (P1, P2, P3)\n"
        "• dim_split (train/valid/test)\n"
        "• dim_source (with/without_p3)\n"
        "• dim_cwe (90 CWE Types)\n"
        "• dim_project (Java Repos)"
    )
    d1 = patches.FancyBboxPatch((9.15, 1.5), 2.1, 3.3, boxstyle="round,pad=0.1", ec="#FDE68A", fc="#FFFFFF", lw=1)
    ax.add_patch(d1)
    ax.text(10.2, 3.15, dwh_text, ha="center", va="center", fontsize=8, color="#78350F", linespacing=1.2)

    # Consumer Annotation at bottom
    box_consumer = patches.FancyBboxPatch((1.0, 0.2), 10.0, 0.7, boxstyle="round,pad=0.1", 
                                          ec="#CBD5E1", fc="#F8FAFC", lw=1)
    ax.add_patch(box_consumer)
    ax.text(6.0, 0.55, "ANALYTICAL & ML CONSUMER: SQL Aggregations  |  Balanced (P1+P2) Export  |  Imbalanced (P1+P2+P3) Export  |  LLM Fine-tuning", 
            ha="center", va="center", fontsize=8.5, fontweight="bold", color="#334155")

    plt.tight_layout()
    out_file = os.path.join(OUTPUT_DIR, "architecture_diagram.png")
    plt.savefig(out_file, bbox_inches="tight")
    plt.close()
    print(f"[DIAGRAM] Saved architecture diagram to {out_file}")

def create_star_schema_diagram():
    """Generates a high-quality Star Schema Entity-Relationship Diagram."""
    fig, ax = plt.subplots(figsize=(13, 8), dpi=300)
    ax.set_xlim(0, 13)
    ax.set_ylim(0, 8)
    ax.axis("off")

    ax.text(6.5, 7.6, "Vulnerability Detection Star Schema (dwh schema)", 
            ha="center", va="center", fontsize=15, fontweight="bold", color="#0F172A")
    ax.text(6.5, 7.25, "Dimensional Design: Central Fact Table Surrounded by 5 Independent Dimensions", 
            ha="center", va="center", fontsize=10, color="#64748B", style="italic")

    # Central Fact Table (x: 4.8 to 8.2, y: 1.8 to 5.6)
    fact_box = patches.FancyBboxPatch((4.7, 1.8), 3.6, 4.4, boxstyle="round,pad=0.15", 
                                      ec="#B91C1C", fc="#FEF2F2", lw=2)
    ax.add_patch(fact_box)
    
    fact_title = patches.Rectangle((4.7, 5.7), 3.6, 0.5, fc="#DC2626", ec="#B91C1C", lw=1)
    ax.add_patch(fact_title)
    ax.text(6.5, 5.95, "fact_vulnerability_sample", ha="center", va="center", fontsize=11, fontweight="bold", color="#FFFFFF")

    fact_content = (
        "PK: sample_key (BIGINT IDENTITY)\n"
        "UK: sample_id (TEXT, Natural Key)\n"
        "───────────────────────────────\n"
        "FK: partition_key (BIGINT) ────► dim_partition\n"
        "FK: split_key (BIGINT) ────────► dim_split\n"
        "FK: source_key (BIGINT) ───────► dim_source\n"
        "FK: cwe_key (BIGINT) ──────────► dim_cwe\n"
        "FK: project_key (BIGINT) ──────► dim_project\n"
        "───────────────────────────────\n"
        "is_vulnerable (BOOLEAN NOT NULL)\n"
        "raw_status (TEXT)\n"
        "function_name (TEXT)\n"
        "commit_hash (TEXT)\n"
        "body_hash (TEXT)\n"
        "code_length (INT, Characters)\n"
        "token_count (INT, Tokens)\n"
        "line_count (INT, Lines)\n"
        "has_duplicate_body (BOOLEAN)\n"
        "created_at (TIMESTAMPTZ)"
    )
    ax.text(6.5, 3.7, fact_content, ha="center", va="center", fontsize=7.5, color="#7F1D1D", linespacing=1.25)

    # Dimension 1: dim_partition (Top Left)
    d1 = patches.FancyBboxPatch((0.5, 5.0), 3.2, 2.0, boxstyle="round,pad=0.1", ec="#2563EB", fc="#EFF6FF", lw=1.5)
    ax.add_patch(d1)
    ax.text(2.1, 6.75, "dim_partition", ha="center", va="center", fontsize=10, fontweight="bold", color="#1D4ED8")
    d1_content = (
        "PK: partition_key (BIGINT)\n"
        "UK: partition_code (P1, P2, P3)\n"
        "partition_name (TEXT)\n"
        "classification_role (Positive/Negative)\n"
        "description (TEXT)"
    )
    ax.text(2.1, 5.85, d1_content, ha="center", va="center", fontsize=7.5, color="#1E3A8A")

    # Dimension 2: dim_split (Bottom Left)
    d2 = patches.FancyBboxPatch((0.5, 1.8), 3.2, 1.9, boxstyle="round,pad=0.1", ec="#059669", fc="#ECFDF5", lw=1.5)
    ax.add_patch(d2)
    ax.text(2.1, 3.45, "dim_split", ha="center", va="center", fontsize=10, fontweight="bold", color="#047857")
    d2_content = (
        "PK: split_key (BIGINT)\n"
        "UK: split_name (train, valid, test)\n"
        "split_description (TEXT)"
    )
    ax.text(2.1, 2.65, d2_content, ha="center", va="center", fontsize=7.5, color="#064E3B")

    # Dimension 3: dim_source (Top Right)
    d3 = patches.FancyBboxPatch((9.3, 5.0), 3.2, 2.0, boxstyle="round,pad=0.1", ec="#7C3AED", fc="#F5F3FF", lw=1.5)
    ax.add_patch(d3)
    ax.text(10.9, 6.75, "dim_source", ha="center", va="center", fontsize=10, fontweight="bold", color="#6D28D9")
    d3_content = (
        "PK: source_key (BIGINT)\n"
        "UK: source_name (with_p3, without_p3)\n"
        "dataset_role (Balanced / Imbalanced)\n"
        "source_format (JSONL)"
    )
    ax.text(10.9, 5.85, d3_content, ha="center", va="center", fontsize=7.5, color="#4C1D95")

    # Dimension 4: dim_cwe (Bottom Right)
    d4 = patches.FancyBboxPatch((9.3, 1.8), 3.2, 2.1, boxstyle="round,pad=0.1", ec="#D97706", fc="#FFFBEB", lw=1.5)
    ax.add_patch(d4)
    ax.text(10.9, 3.65, "dim_cwe", ha="center", va="center", fontsize=10, fontweight="bold", color="#B45309")
    d4_content = (
        "PK: cwe_key (BIGINT)\n"
        "UK: cwe_code (CWE-20, CWE-79...)\n"
        "cwe_name (Improper Input Validation...)\n"
        "severity_level (High, Medium, Low)\n"
        "description (Taxonomy definition)"
    )
    ax.text(10.9, 2.65, d4_content, ha="center", va="center", fontsize=7.5, color="#78350F")

    # Dimension 5: dim_project (Bottom Center)
    d5 = patches.FancyBboxPatch((4.9, 0.2), 3.2, 1.2, boxstyle="round,pad=0.1", ec="#475569", fc="#F8FAFC", lw=1.5)
    ax.add_patch(d5)
    ax.text(6.5, 1.15, "dim_project", ha="center", va="center", fontsize=9.5, fontweight="bold", color="#334155")
    d5_content = (
        "PK: project_key (BIGINT)\n"
        "UK: project_name (open-source-java-cvefixes)\n"
        "primary_language (Java)"
    )
    ax.text(6.5, 0.65, d5_content, ha="center", va="center", fontsize=7.5, color="#1E293B")

    # Connecting Arrows (Dimensions to Fact - 1 to N relationships)
    # dim_partition -> Fact
    ax.annotate("", xy=(4.7, 4.8), xytext=(3.7, 5.6),
                arrowprops=dict(arrowstyle="->", lw=1.8, color="#2563EB"))
    ax.text(4.1, 5.4, "1 : N", fontsize=8, fontweight="bold", color="#2563EB")

    # dim_split -> Fact
    ax.annotate("", xy=(4.7, 3.2), xytext=(3.7, 2.8),
                arrowprops=dict(arrowstyle="->", lw=1.8, color="#059669"))
    ax.text(4.1, 3.1, "1 : N", fontsize=8, fontweight="bold", color="#059669")

    # dim_source -> Fact
    ax.annotate("", xy=(8.3, 4.8), xytext=(9.3, 5.6),
                arrowprops=dict(arrowstyle="->", lw=1.8, color="#7C3AED"))
    ax.text(8.8, 5.4, "1 : N", fontsize=8, fontweight="bold", color="#7C3AED")

    # dim_cwe -> Fact
    ax.annotate("", xy=(8.3, 3.2), xytext=(9.3, 2.8),
                arrowprops=dict(arrowstyle="->", lw=1.8, color="#D97706"))
    ax.text(8.8, 3.1, "1 : N", fontsize=8, fontweight="bold", color="#D97706")

    # dim_project -> Fact
    ax.annotate("", xy=(6.5, 1.8), xytext=(6.5, 1.4),
                arrowprops=dict(arrowstyle="->", lw=1.8, color="#475569"))
    ax.text(6.65, 1.55, "1 : N", fontsize=8, fontweight="bold", color="#475569")

    plt.tight_layout()
    out_file = os.path.join(OUTPUT_DIR, "star_schema_diagram.png")
    plt.savefig(out_file, bbox_inches="tight")
    plt.close()
    print(f"[DIAGRAM] Saved star schema diagram to {out_file}")

if __name__ == "__main__":
    create_architecture_diagram()
    create_star_schema_diagram()
