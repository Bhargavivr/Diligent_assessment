# Synthetic E-Commerce Prompt Pack

This repository contains upgraded prompt templates for generating and working with a feature-rich synthetic e-commerce dataset inside Cursor. The flow covers three stages: data generation, SQLite ingestion, and analytical querying, each tailored to showcase excellence during Diligent’s campus recruitment assessment.

## Contents
- `prompts/synthetic_data_prompt.txt` — directs Cursor/GPT to create five interlinked CSVs (customers, products, orders, order_items, inventory_events) with loyalty tiers, acquisition channels, and built-in validation summaries.
- `prompts/sqlite_ingest_prompt.txt` — instructs Cursor/GPT to build a CLI-driven Python ETL that loads the dataset into SQLite with constraints, derived `customer_kpis`, data-quality metrics, and optional dry-run validation.
- `prompts/multi_table_query_prompt.sql` — guides Cursor/GPT to author an insight-rich SQL script covering customer LTV, channel mix, and inventory health with well-documented CTEs.

## Suggested Usage in Cursor
1. Open each prompt file and paste the contents into a new Cursor chat (or use “Run Prompt”).
2. Provide any needed context (e.g., confirm data paths) and execute the generations.
3. Save the generated artifacts in logical folders (`data/`, `scripts/`, `sql/`, `docs/`), then iterate or extend as desired.

## Pushing to GitHub
1. Initialize Git if needed: git init.
2. Add all files: git add .
3. Commit: git commit -m "Add synthetic e-commerce prompt pack".
4. Create a GitHub repo and copy its remote URL.
5. Add the remote: git remote add origin <REMOTE_URL>.
6. Push the main branch: git push -u origin main.

Ensure you are authenticated with GitHub (via PAT or SSH) before pushing.

## Bonus Ideas for Differentiation
- Capture screenshots or Loom recordings of each Cursor run and place them in `docs/`.
- Generate a lightweight dashboard (e.g., DuckDB + Streamlit) using the same data and link it in the README.
- Write a short “judges guide” summarizing what makes this dataset unique (loyalty tiers, channel attribution, inventory rigor).
