import csv
import sqlite3
from pathlib import Path

HERE = Path(__file__).parent
DB = HERE / "vendor_performance.db"
OUT = HERE.parent / "vendor-performance-dashboard" / "data"
OUT.mkdir(parents=True, exist_ok=True)

QUERIES = {
    "dim_vendor": """
        SELECT vendor_number, vendor_name
        FROM dim_vendor
        ORDER BY vendor_number
    """,
    "purchases_monthly": """
        SELECT vendor_number,
               strftime('%Y-%m-01', po_date) AS po_month,
               COUNT(*) AS purchase_lines,
               SUM(quantity) AS units,
               ROUND(SUM(dollars), 2) AS spend,
               ROUND(SUM(julianday(receiving_date) - julianday(po_date)), 0) AS total_lead_days
        FROM fact_purchases
        GROUP BY vendor_number, strftime('%Y-%m-01', po_date)
        ORDER BY vendor_number, po_month
    """,
    "invoices_monthly": """
        SELECT vendor_number,
               strftime('%Y-%m-01', invoice_date) AS invoice_month,
               COUNT(*) AS invoices,
               ROUND(SUM(dollars), 2) AS invoice_dollars,
               ROUND(SUM(freight), 2) AS freight,
               ROUND(SUM(julianday(pay_date) - julianday(invoice_date)), 0) AS total_pay_days
        FROM fact_invoice_purchases
        GROUP BY vendor_number, strftime('%Y-%m-01', invoice_date)
        ORDER BY vendor_number, invoice_month
    """,
}

conn = sqlite3.connect(DB)
for name, sql in QUERIES.items():
    cur = conn.execute(sql)
    rows = cur.fetchall()
    with open(OUT / f"{name}.csv", "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow([c[0] for c in cur.description])
        w.writerows(rows)
    print(f"{name}.csv: {len(rows)} rows")
conn.close()
print("Saved to:", OUT)