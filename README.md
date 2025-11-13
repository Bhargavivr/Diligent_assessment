# Synthetic E-Commerce Prompt Pack

This repository contains prompt templates for generating and working with a synthetic e-commerce dataset inside Cursor. The flow covers three stages: data generation, SQLite ingestion, and analytical querying.

## Contents
- prompts/synthetic_data_prompt.txt &mdash; guide Cursor/GPT to create ~5 realistic CSV files plus a README for the dataset.
- prompts/sqlite_ingest_prompt.txt &mdash; instructs Cursor/GPT to build a Python ETL script that loads the CSVs into ecommerce.db.
- prompts/multi_table_query_prompt.sql &mdash; prompts Cursor/GPT to author a SQL report joining multiple tables for a customer LTV analysis.

## Suggested Usage in Cursor
1. Open each prompt file and paste the contents into a new Cursor chat.
2. Provide any context (e.g., confirm file paths) and run the generations.
3. Save the generated artifacts in the repository under appropriate folders (data/, scripts/, sql/).

## Pushing to GitHub
1. Initialize Git if needed: git init.
2. Add all files: git add ..
3. Commit: git commit -m "Add synthetic e-commerce prompt pack".
4. Create a GitHub repo and copy its remote URL.
5. Add the remote: git remote add origin <REMOTE_URL>.
6. Push the main branch: git push -u origin main.

Ensure you are authenticated with GitHub (via PAT or SSH) before pushing.
