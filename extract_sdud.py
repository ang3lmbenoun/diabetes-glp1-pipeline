import os
import requests
import psycopg2
from dotenv import load_dotenv

load_dotenv()

API_URL = "https://data.medicaid.gov/api/1/datastore/query/61729e5a-7aa8-448c-8903-ba3e0cd0ea3c/0"
PAGE_SIZE = 5000

# 1. Connect to Postgres
conn = psycopg2.connect(
    host=os.getenv("DB_HOST"),
    port=os.getenv("DB_PORT"),
    dbname=os.getenv("DB_NAME"),
    user=os.getenv("DB_USER"),
    password=os.getenv("DB_PASSWORD"),
)
cur = conn.cursor()

# 2. Idempotency: empty the table before we start, so re-running can't duplicate
cur.execute("TRUNCATE TABLE raw.sdud_2024;")
conn.commit()
print("Table truncated. Starting fresh.")

# 3. The 15 columns, in the exact order of the table
COLUMNS = [
    "utilization_type", "state", "ndc", "labeler_code", "product_code",
    "package_size", "year", "quarter", "suppression_used", "product_name",
    "units_reimbursed", "number_of_prescriptions", "total_amount_reimbursed",
    "medicaid_amount_reimbursed", "non_medicaid_amount_reimbursed",
]

insert_sql = f"INSERT INTO raw.sdud_2024 ({', '.join(COLUMNS)}) VALUES ({', '.join(['%s'] * 15)})"

# 4. The pagination loop
offset = 0
total_loaded = 0

while True:
    params = {"limit": PAGE_SIZE, "offset": offset}
    response = requests.get(API_URL, params=params)
    data = response.json()

    rows = data["results"]
    total_available = data["count"]

    # If a page comes back empty, we've passed the end — stop.
    if not rows:
        break

    # Turn each row-dictionary into a tuple of values in column order
    values = [tuple(row[col] for col in COLUMNS) for row in rows]

    # Write this page to Postgres, then it leaves memory
    cur.executemany(insert_sql, values)
    conn.commit()

    total_loaded += len(rows)
    offset += PAGE_SIZE
    print(f"Loaded {total_loaded} / {total_available} rows")

    # Stop once we've collected everything
    if total_loaded >= total_available:
        break

# 5. Clean up
cur.close()
conn.close()
print("Done. Total rows loaded:", total_loaded)