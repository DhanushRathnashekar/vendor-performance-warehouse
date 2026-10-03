-- ============================================================
-- Vendor Performance Warehouse — Schema
-- 3 dimension tables + 5 fact tables, star-schema style
-- ============================================================

-- ---------- DIMENSIONS ----------

CREATE TABLE dim_product (
    brand           INTEGER PRIMARY KEY,   -- the key: repeats everywhere a product is sold/bought
    description     TEXT,
    size            TEXT,
    volume          TEXT,
    classification  INTEGER
);

CREATE TABLE dim_vendor (
    vendor_number   INTEGER PRIMARY KEY,   -- the key
    vendor_name     TEXT
);

CREATE TABLE dim_store (
    store           INTEGER PRIMARY KEY,   -- the key
    city            TEXT
);

-- ---------- FACTS ----------
-- Each fact table: a surrogate id (its own row identifier),
-- foreign keys pointing back to the dimensions above,
-- then the actual measures/dates for that event.

CREATE TABLE fact_invoice_purchases (
    invoice_purchase_id INTEGER PRIMARY KEY AUTOINCREMENT,
    vendor_number   INTEGER REFERENCES dim_vendor(vendor_number),
    po_number       INTEGER,
    po_date         TEXT,
    invoice_date    TEXT,
    pay_date        TEXT,
    quantity        INTEGER,
    dollars         REAL,
    freight         REAL,
    approval        TEXT
);

CREATE TABLE fact_purchases (
    purchase_id     INTEGER PRIMARY KEY AUTOINCREMENT,
    store           INTEGER REFERENCES dim_store(store),
    brand           INTEGER REFERENCES dim_product(brand),
    vendor_number   INTEGER REFERENCES dim_vendor(vendor_number),
    po_number       INTEGER,
    po_date         TEXT,
    receiving_date  TEXT,
    invoice_date    TEXT,
    pay_date        TEXT,
    purchase_price  REAL,
    quantity        INTEGER,
    dollars         REAL
);

CREATE TABLE fact_sales (
    sale_id         INTEGER PRIMARY KEY AUTOINCREMENT,
    store           INTEGER REFERENCES dim_store(store),
    brand           INTEGER REFERENCES dim_product(brand),
    vendor_number   INTEGER REFERENCES dim_vendor(vendor_number),  -- fixes the raw file's "VendorNo" naming
    sales_date      TEXT,
    sales_quantity  INTEGER,
    sales_dollars   REAL,
    sales_price     REAL,
    excise_tax      REAL
);

CREATE TABLE fact_beginning_inventory (
    beg_inv_id      INTEGER PRIMARY KEY AUTOINCREMENT,
    store           INTEGER REFERENCES dim_store(store),
    brand           INTEGER REFERENCES dim_product(brand),
    start_date      TEXT,
    on_hand         INTEGER,
    price           REAL
);

CREATE TABLE fact_ending_inventory (
    end_inv_id      INTEGER PRIMARY KEY AUTOINCREMENT,
    store           INTEGER REFERENCES dim_store(store),
    brand           INTEGER REFERENCES dim_product(brand),
    end_date        TEXT,
    on_hand         INTEGER,
    price           REAL
);
