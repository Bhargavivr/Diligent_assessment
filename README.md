# Synthetic E-Commerce Assessment Kit

This repository now includes both the Cursor prompts **and** fully generated assets (CSV data, ingestion script, SQL analytics) tailored for Diligent’s campus recruitment exercise. You can reuse the prompts to regenerate everything inside Cursor, or run the ready-made assets locally to showcase an end-to-end solution within 30 minutes.

## Repository Map
- `prompts/` — the three curated prompts (data generation, SQLite ETL, analytical SQL) that satisfy the “write prompts” portion of the exercise.
- `data/` — five CSV files plus a README produced via `scripts/generate_data.py` (~750 customers, 180 products, 1,150 orders, etc.).
- `scripts/generate_data.py` — deterministic generator that produces the dataset the prompts describe.
- `scripts/load_ecommerce_data.py` — CLI ETL that loads the CSVs into `ecommerce.db`, enforces constraints, and materializes `customer_kpis`.
- `sql/customer_ltv_report.sql` — reporting query with LTV leaderboard, channel mix, category and inventory summaries.
- `ecommerce.db` — SQLite database produced by running the loader (safe to regenerate).

## Quick Start
```bash
# 1. Regenerate data (optional)
python scripts/generate_data.py

# 2. Load into SQLite (creates ecommerce.db)
python scripts/load_ecommerce_data.py --data-dir data --database ecommerce.db --drop-tables --vacuum

# 3. Run analytics (e.g., via sqlite3 CLI or Datasette)
sqlite3 ecommerce.db < sql/customer_ltv_report.sql
```

## Cursor Workflow (per exercise instructions)
1. In Cursor, open each file under `prompts/` and use “Run Prompt” to generate the artifacts if you need a clean regeneration.
2. Save the generated CSVs/scripts/SQL back into this repo (the structure above is a ready-made reference).
3. Record screenshots or Loom clips of each step to document compliance with the “completed using Cursor IDE” requirement.

## Differentiation Tips
- Use the dataset README in `data/` plus loader stats/logs as evidence of validation rigor.
- Snapshot the `customer_kpis` table or results from `customer_ltv_report.sql` to highlight insights.
- Extend `sql/customer_ltv_report.sql` with filters specific to the assessment brief (e.g., date range arguments) if allowed.

## GitHub Notes
This repo is already initialized and pushed to [`Bhargavivr/Diligent_assessment`](https://github.com/Bhargavivr/Diligent_assessment). If you clone or modify elsewhere:
1. `git add .`
2. `git commit -m "Your update message"`
3. `git push origin main`

Ensure you are authenticated with GitHub (PAT or SSH) before pushing.
