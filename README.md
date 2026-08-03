# 💊 Diabetes Drug Spend & Utilization Pipeline

An end-to-end ELT data pipeline analyzing Medicaid spending and utilization across the four largest diabetes drug classes, with an automated FDA recall-monitoring layer.

![Python](https://img.shields.io/badge/Python-3.14-blue)
![PostgreSQL](https://img.shields.io/badge/PostgreSQL-18-336791)
![dbt](https://img.shields.io/badge/dbt-1.12-FF694B)
![Power BI](https://img.shields.io/badge/Power_BI-Dashboard-F2C811)
![n8n](https://img.shields.io/badge/n8n-Automation-EA4B71)

## 📊 Key Finding

Across the four largest diabetes drug classes in Medicaid (2024), **GLP-1 agonists consumed ~80% of total spending (~$8.7B) despite metformin being the most-prescribed class** (9.8M prescriptions). Cost per prescription ranged from **$12.90 (metformin)** to **$1,063 (GLP-1)** — an ~82x gap between the cheapest and most expensive classes.

| Drug Class | Prescriptions | Total Spend | Cost / Rx |
|------------|--------------:|------------:|----------:|
| GLP-1      | 8.2M          | $8.69B      | $1,063    |
| Insulin    | 6.8M          | $1.15B      | $170      |
| DPP-4      | 1.3M          | $0.95B      | $754      |
| Metformin  | 9.8M          | $0.13B      | $12.90    |

## 🏗️ Architecture

Medicaid SDUD API → Python extractor → PostgreSQL (raw) → dbt (staging + marts) → Power BI dashboard → n8n + Groq AI automation

- **Extract:** Python script pulls ~5.3M rows from the Medicaid SDUD API with pagination and idempotent (truncate-reload) loading.
- **Load:** Raw data landed in PostgreSQL, untouched, all columns as text (ELT — transform in-warehouse).
- **Transform:** dbt models — a staging view (type casting, suppressed-null handling), a curated drug-class seed, and star-schema fact/summary marts.
- **Visualize:** Power BI dashboard — cost-per-drug ranking, spend-vs-volume divergence by class, and a state-level choropleth.
- **Automate:** n8n workflow cross-references live openFDA drug recalls against the spend analysis and emails a styled briefing via Groq — with all figures computed in code so the LLM never fabricates numbers.

## 🔍 Data Engineering Highlights

- **NDC/name normalization:** Product names are dosage-fragmented (e.g. `OZEMPIC 1M`, `OZEMPIC 2M`); a keyword-based `LIKE` join collapses variants back to their parent drug.
- **Caught a 2x inflation bug:** The SDUD `XX` code represents national totals that duplicate state-level rows. Verification via row counts caught the double-count before it reached the dashboard; filtered at the staging layer.
- **LLM fabrication guardrail:** All numbers are pre-computed in code and passed to the LLM as finished facts. The model writes prose only — it never performs arithmetic or generates figures.

## 🛠️ Tech Stack

Python · PostgreSQL · dbt · Power BI · n8n · Groq (Llama 3.3) · openFDA API · Medicaid SDUD

## 📁 Repo Structure

- `extract_sdud.py` — API extractor
- `diabetes_dbt/` — dbt project (models, seeds)
- `automation/` — n8n workflow export
- `requirements.txt` — Python dependencies

## 📈 Dashboard

![Dashboard](dashboard-screenshot.png)

## 📝 Data Source

[Medicaid State Drug Utilization Data (SDUD)](https://data.medicaid.gov/) · [openFDA Drug Enforcement API](https://open.fda.gov/)

---
*Built by Angel Mbenoun♡ · Aug 2026*
