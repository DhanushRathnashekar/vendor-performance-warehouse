import sqlite3
import csv
import os

UPLOAD_DIR = "/mnt/user-data/uploads"
DB_PATH = "/mnt/user-data/outputs/vendor_performance.db"

FILES = {
    "prices":    "1790170654761_2017PurchasePricesDec.csv",
    "purchases": "1790170654760_PurchasesFINAL12312016.csv",
    "sales":     "1790170654762_SalesFINAL12312016.csv",
    "beg_inv":   "1790170654761_BegInvFINAL12312016.csv",
    "end_inv":   "1790170654762_EndInvFINAL12312016.csv",
    "invoices":  "1790170654762_InvoicePurchases12312016.csv",
}

def path(key):
    return os.path.join(UPLOAD_DIR, FILES[key])

def to_int(v):
    try:
        return int(float(v)) if v not in (None, "") else None
    except ValueError:
        return None

def to_float(v):
    try:
        return float(v) if v not in (None, "") else None
    except ValueError:
        return None

os.makedirs("/mnt/user-data/outputs", exist_ok=True)
if os.path.exists(DB_PATH):
    os.remove(DB_PATH)  # rebuild clean each run

conn = sqlite3.connect(DB_PATH)
conn.execute("PRAGMA foreign_keys = ON;")  # enforce the FK relationships, don't just declare them
cur = conn.cursor()

with open("/home/claude/warehouse/schema.sql") as f:
    cur.executescript(f.read())

# ---------- DIM_PRODUCT ----------
# Build from the price list first (canonical), then add any brands
# that only appear in the transaction files but never in the price list.
products = {}
with open(path("prices")) as f:
    for row in csv.DictReader(f):
        b = to_int(row["Brand"])
        if b is not None and b not in products:
            products[b] = (b, row["Description"], row["Size"], row["Volume"], to_int(row["Classification"]))

for key, cols in [("purchases", ("Brand", "Description", "Size", "Volume", "Classification")),
                   ("sales",     ("Brand", "Description", "Size", "Volume", "Classification"))]:
    with open(path(key)) as f:
        for row in csv.DictReader(f):
            b = to_int(row[cols[0]])
            if b is not None and b not in products:
                products[b] = (b, row[cols[1]], row[cols[2]], row[cols[3]], to_int(row[cols[4]]))

cur.executemany("INSERT INTO dim_product VALUES (?,?,?,?,?)", products.values())
print(f"dim_product: {len(products):,} rows")

# ---------- DIM_VENDOR ----------
vendors = {}
with open(path("prices")) as f:
    for row in csv.DictReader(f):
        vn = to_int(row["VendorNumber"])
        if vn is not None and vn not in vendors:
            vendors[vn] = (vn, row["VendorName"].strip())

with open(path("purchases")) as f:
    for row in csv.DictReader(f):
        vn = to_int(row["VendorNumber"])
        if vn is not None and vn not in vendors:
            vendors[vn] = (vn, row["VendorName"].strip())

with open(path("sales")) as f:
    for row in csv.DictReader(f):
        vn = to_int(row["VendorNo"])  # note the raw file's inconsistent column name
        if vn is not None and vn not in vendors:
            vendors[vn] = (vn, row["VendorName"].strip())

cur.executemany("INSERT INTO dim_vendor VALUES (?,?)", vendors.values())
print(f"dim_vendor: {len(vendors):,} rows")

# ---------- DIM_STORE ----------
stores = {}
for key in ("beg_inv", "end_inv"):
    with open(path(key)) as f:
        for row in csv.DictReader(f):
            s = to_int(row["Store"])
            if s is not None and s not in stores:
                stores[s] = (s, row["City"])

cur.executemany("INSERT INTO dim_store VALUES (?,?)", stores.values())
print(f"dim_store: {len(stores):,} rows")

conn.commit()

# ---------- FACT TABLES (batched inserts for the big ones) ----------
def load_fact(csv_key, insert_sql, row_fn, batch_size=20000):
    batch = []
    n = 0
    with open(path(csv_key)) as f:
        for row in csv.DictReader(f):
            batch.append(row_fn(row))
            if len(batch) >= batch_size:
                cur.executemany(insert_sql, batch)
                n += len(batch)
                batch = []
    if batch:
        cur.executemany(insert_sql, batch)
        n += len(batch)
    conn.commit()
    print(f"{insert_sql.split()[2]}: {n:,} rows")

load_fact("invoices",
    "INSERT INTO fact_invoice_purchases (vendor_number, po_number, po_date, invoice_date, pay_date, quantity, dollars, freight, approval) VALUES (?,?,?,?,?,?,?,?,?)",
    lambda r: (to_int(r["VendorNumber"]), to_int(r["PONumber"]), r["PODate"], r["InvoiceDate"], r["PayDate"],
               to_int(r["Quantity"]), to_float(r["Dollars"]), to_float(r["Freight"]), r["Approval"]))

load_fact("purchases",
    "INSERT INTO fact_purchases (store, brand, vendor_number, po_number, po_date, receiving_date, invoice_date, pay_date, purchase_price, quantity, dollars) VALUES (?,?,?,?,?,?,?,?,?,?,?)",
    lambda r: (to_int(r["Store"]), to_int(r["Brand"]), to_int(r["VendorNumber"]), to_int(r["PONumber"]),
               r["PODate"], r["ReceivingDate"], r["InvoiceDate"], r["PayDate"],
               to_float(r["PurchasePrice"]), to_int(r["Quantity"]), to_float(r["Dollars"])))

load_fact("sales",
    "INSERT INTO fact_sales (store, brand, vendor_number, sales_date, sales_quantity, sales_dollars, sales_price, excise_tax) VALUES (?,?,?,?,?,?,?,?)",
    lambda r: (to_int(r["Store"]), to_int(r["Brand"]), to_int(r["VendorNo"]), r["SalesDate"],
               to_int(r["SalesQuantity"]), to_float(r["SalesDollars"]), to_float(r["SalesPrice"]), to_float(r["ExciseTax"])))

load_fact("beg_inv",
    "INSERT INTO fact_beginning_inventory (store, brand, start_date, on_hand, price) VALUES (?,?,?,?,?)",
    lambda r: (to_int(r["Store"]), to_int(r["Brand"]), r["startDate"], to_int(r["onHand"]), to_float(r["Price"])))

load_fact("end_inv",
    "INSERT INTO fact_ending_inventory (store, brand, end_date, on_hand, price) VALUES (?,?,?,?,?)",
    lambda r: (to_int(r["Store"]), to_int(r["Brand"]), r["endDate"], to_int(r["onHand"]), to_float(r["Price"])))

conn.close()
print("\nDone. Warehouse built at", DB_PATH)
