import os
import sys
import time
import requests
import psycopg2
from dotenv import load_dotenv

load_dotenv()

API_URL = "https://data.medicaid.gov/api/1/datastore/query/61729e5a-7aa8-448c-8903-ba3e0cd0ea3c/0"
PAGE_SIZE = 5000
MAX_RETRIES = 5
RESUME = "--resume" in sys.argv

conn = psycopg2.connect(
    host=os.getenv("DB_HOST"),
    port=os.getenv("DB_PORT"),
    dbname=os.getenv("DB_NAME"),
    user=os.getenv("DB_USER"),
    password=os.getenv("DB_PASSWORD"),
)
cur = conn.cursor()

if RESUME:
    # Every page is committed whole, so the row count is a safe restart point
    cur.execute("SELECT count(*) FROM raw.sdud_2024;")
    offset = cur.fetchone()[0]
    total_loaded = offset
    print(f"Resuming from row {offset}.")
else:
    cur.execute("TRUNCATE TABLE raw.sdud_2024;")
    conn.commit()
    offset = 0
    total_loaded = 0
    print("Table truncated. Starting fresh.")

COLUMNS = [
    "utilization_type", "state", "ndc", "labeler_code", "product_code",
    "package_size", "year", "quarter", "suppression_used", "product_name",
    "units_reimbursed", "number_of_prescriptions", "total_amount_reimbursed",
    "medicaid_amount_reimbursed", "non_medicaid_amount_reimbursed",
]
insert_sql = f"INSERT INTO raw.sdud_2024 ({', '.join(COLUMNS)}) VALUES ({', '.join(['%s'] * 15)})"


def fetch_page(page_offset):
    for attempt in range(1, MAX_RETRIES + 1):
        try:
            response = requests.get(
                API_URL,
                params={"limit": PAGE_SIZE, "offset": page_offset},
                timeout=60,
            )
            response.raise_for_status()
            return response.json()
        except (requests.RequestException, ValueError) as e:
            wait = 5 * attempt
            print(f"Offset {page_offset} failed (attempt {attempt}/{MAX_RETRIES}): {e}. Retrying in {wait}s...")
            time.sleep(wait)
    raise RuntimeError(f"Gave up at offset {page_offset}. Re-run with --resume.")


while True:
    data = fetch_page(offset)
    rows = data["results"]
    total_available = data["count"]

    if not rows:
        break

    values = [tuple(row[col] for col in COLUMNS) for row in rows]
    cur.executemany(insert_sql, values)
    conn.commit()

    total_loaded += len(rows)
    offset += PAGE_SIZE
    print(f"Loaded {total_loaded} / {total_available} rows")

    if total_loaded >= total_available:
        break

cur.close()
conn.close()
print("Done. Total rows loaded:", total_loaded)