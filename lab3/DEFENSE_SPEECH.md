# Laboratory Work 3 Defense Speech & Presentation Guide

## 🎙️ Spoken Defense Script (approx. 3–5 minutes)
*Tip for delivery: Speak at a calm, natural pace. Pause briefly between sections. Stand or sit straight, make eye contact.*

---

### 1. Introduction (30 seconds)
> "Good morning / afternoon, Professor.
>
> Today, I am defending my project for Laboratory Work 3: **Building an ETL Pipeline for a Vulnerability-Detection Data Warehouse**.
>
> The motivation behind this lab comes from a 2025 research paper by Shestov and colleagues, where researchers train AI models to spot security flaws in Java source code. 
>
> However, raw security data is usually very messy, scattered in huge text files, and full of duplicates. My goal in this lab was to take that messy raw data, build an automated, professional data pipeline, and organize everything into an analytical **Data Warehouse** running in Docker."

---

### 2. Core Concepts in Simple Words (1 minute)
> "Before showing what I built, let me briefly explain the core concepts:
>
> 1. **What is a Data Warehouse?**
>    Think of a regular database like a store's cash register—it is built to quickly save one transaction at a time. A Data Warehouse is like the headquarters' analytics center. It brings data from different places together, organizes it historically, and is optimized for heavy analytical questions, like: *'Which vulnerability types are most common across 20,000 files?'*
>
> 2. **What is ETL?**
>    ETL stands for **Extract, Transform, Load**. It is the bridge between raw data and the warehouse:
>    - **Extract:** We pick up raw data from files or APIs without altering it.
>    - **Transform:** We clean it—we fix messy labels, remove duplicates, calculate line lengths, and format everything cleanly.
>    - **Load:** We insert the clean data into structured tables ready for queries.
>
> 3. **What is a Star Schema?**
>    In our warehouse, we don't dump everything into one giant spreadsheet. We use a **Star Schema**:
>    - In the center sits our **Fact Table** (`fact_vulnerability_sample`). It holds the actual events and numbers: the code length, line count, and whether it's vulnerable.
>    - Surrounding it are **Dimension Tables**: they provide context—*Which project did this code come from? Which CWE vulnerability category does it belong to? Is it part of the training or testing split?*
>    - Because the dimension tables point to the center fact table, the diagram looks like a star. This structure makes SQL queries simple, lightning-fast, and easy to read."

---

### 3. Architecture & What I Built (1.5 minutes)
> "Here is how I implemented the entire system:
>
> - **Containerized Database:** I ran a PostgreSQL 15 database inside a lightweight Docker container, completely isolated and reproducible with `docker-compose`.
>
> - **Staging Area:** First, my Python extraction script loaded over **24,288 raw vulnerability records** from JSONL files and CWE security taxonomy definitions into raw staging tables.
>
> - **Transformation Logic:** During the transformation step:
>   - I calculated code metrics like character length and line count.
>   - I detected **data leakage**—finding records where the exact same code snippet appeared multiple times.
>   - I cleaned noisy labels, such as turning non-standard NVD placeholders into clean identifiers.
>
> - **Automated Data Quality:** Before trusting any data, I wrote automated quality checks:
>   - We check that foreign keys actually exist.
>   - We check that vulnerability flags are strictly 0 or 1.
>   - We check that no mandatory fields are null.
>   - All **7 out of 7 automated quality tests passed with 100% compliance**!
>
> - **Incremental vs Full Loading:** I also implemented logic so that if new data arrives tomorrow, we don't have to re-import all 24,000 records from scratch. The pipeline uses natural keys (`func_hash`) to safely insert only newly arriving records without creating duplicates."

---

### 4. Key Analytical Findings (1 minute)
> "Finally, I ran analytical SQL queries on the data warehouse to see what the data actually tells us:
>
> 1. **Massive Class Imbalance:** The benchmark `without_p3` is balanced 50/50, but the realistic benchmark `with_p3` has **34 safe code samples for every 1 vulnerable sample**. This proves why real-world vulnerability detection is so hard for AI.
> 2. **Code Leakage:** Around **10.98% of code snippets were duplicates**. If the same snippet is in both the training set and testing set, the model might just memorize it rather than learn real vulnerabilities.
> 3. **Top Vulnerabilities:** The most frequent issues are input validation and memory/web flaws—specifically CWE-79 (Cross-Site Scripting) and CWE-89 (SQL Injection).
> 4. **Code Length:** Vulnerable functions tended to be longer on average than non-vulnerable functions, showing that complexity often breeds bugs."

---

### 5. Conclusion (30 seconds)
> "To conclude: 
> This lab taught me how modern data engineering supports modern AI research. Without a solid ETL pipeline and a well-modeled Data Warehouse, researchers spend 80% of their time cleaning messy files instead of training models. 
>
> All code, Docker configurations, SQL scripts, automated tests, and reports are fully tested, reproducible, and tracked in Git.
>
> Thank you, and I am ready for your questions!"

---

## 💡 Quick Metaphors (Cheat Sheet for Interruptions)

| Technical Concept | Simple Metaphor (Explain Like I'm 5) |
|---|---|
| **Data Warehouse** | *A supermarket or library where items are sorted by aisle and category for easy browsing, rather than a cluttered delivery truck.* |
| **ETL Pipeline** | *Harvesting vegetables from a farm (Extract), washing, peeling, and cutting them in a kitchen (Transform), and plating them nicely for dinner (Load).* |
| **Fact Table** | *The receipt showing the purchase (amounts, price, timestamp)—the core event.* |
| **Dimension Table** | *The customer profile, store directory, or product catalog that gives meaning to the receipt numbers.* |
| **Star Schema** | *A sun in the middle (Fact table) with planets orbiting around it (Dimensions). No complicated spiderwebs, just direct connections.* |
| **Staging Table** | *The cutting board or loading dock where raw boxes are unloaded before you clean and store them.* |

---

## 🎯 Top Professor Questions & Model Answers

### Q1: "Why did you need a Data Warehouse? Couldn't we just use pandas in a Jupyter Notebook?"
> **Answer:** 
> "Pandas loads everything into RAM in a single computer. For small files that's fine, but in production, datasets reach tens of millions of records. A Data Warehouse stores historical data securely, allows multiple data scientists and dashboards to query it concurrently using standard SQL, enforces data integrity with foreign keys, and persists across reboots in Docker."

### Q2: "Why did you use a Star Schema instead of a 3NF (Third Normal Form) database?"
> **Answer:** 
> "3NF is great for operational systems (OLTP) to prevent write anomalies by splitting data across many small tables. But querying 3NF requires joining 10 or 15 tables together, which is slow for analytics. A Star Schema intentionally de-normalizes dimensions. Queries only require 1 join from the fact to any dimension, making read queries much faster and very easy to write."

### Q3: "What happens if a corrupt row arrives with empty or invalid data?"
> **Answer:** 
> "Our extraction loads raw data into staging first without throwing it away. During transformation, we clean it—for instance, mapping missing or noisy CWE values to a standardized `CWE-UNKNOWN` record. Then, our automated quality check suite verifies null constraints, allowed value ranges, and foreign key validity before reports are generated."

### Q4: "How does incremental loading work in your project?"
> **Answer:** 
> "Instead of doing a `TRUNCATE` and reloading all 24,288 records, incremental mode queries the database using `ON CONFLICT (func_hash) DO NOTHING` or checks `WHERE NOT EXISTS`. It matches each incoming record against its SHA-256 function hash, inserting only genuinely new code samples and saving significant compute time."

### Q5: "What is data leakage and why was it important in your findings?"
> **Answer:** 
> "Data leakage happens when information from outside the training dataset sneaks into the model. We discovered that nearly 11% of the code samples had identical function bodies across different commits and splits. If a model sees the exact same code snippet in both training and test sets, its evaluation score will look artificially high because it just memorized the code."
