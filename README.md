# Vendor Performance Data Warehouse

A SQL data warehouse built from a real distributor dataset (purchases, sales, inventory and invoices for a multi-store alcohol distributor), used to answer everyday supply chain questions about vendors, inventory and payments.

## What this project shows

- Designing a **star schema**: 3 dimension tables and 5 fact tables, with keys and foreign keys
- Loading about 3.8 million rows into SQLite
- Writing SQL (JOIN, GROUP BY, HAVING, date math) to answer real procurement, logistics and inventory questions
- Reading the results the way a supply chain team would, including spotting misleading averages

## The warehouse

| Type | Table | Describes |
|------|-------|-----------|
| Dimension | dim_product | Brands, descriptions, size, classification |
| Dimension | dim_vendor | Vendor number and name |
| Dimension | dim_store | Store number and city |
| Fact | fact_purchases | Every purchase line received |
| Fact | fact_invoice_purchases | Vendor invoices, freight and payment dates |
| Fact | fact_sales | Sales transactions |
| Fact | fact_beginning_inventory | Inventory snapshot at start of period |
| Fact | fact_ending_inventory | Inventory snapshot at end of period |

The full table definitions are in `schema.sql`.

## Questions answered and what I found

| Query | Business question | Finding |
|-------|-------------------|---------|
| top_vendors_by_spend | Which vendors do we spend the most with? | Diageo is first at about $51M (roughly 16% of all spend), followed by Martignetti, Jim Beam, Pernod Ricard and Bacardi. This is a vendor concentration and negotiating leverage question for procurement. |
| inventory_turnover | Which products move fastest? | The fastest movers sell down thousands of units per store group in the period. These are the items to protect from stockouts and the right demand inputs for EOQ planning. |
| freight_by_vendor | Which vendors cost the most in freight? | Freight is about 0.5% of invoice dollars for every vendor, so there is no freight outlier. It is likely allocated in proportion to invoice value. |
| vendor_lead_time | How long from PO to receipt? | Average 7.6 days (range 3 to 14). Vendors with only a few orders looked slow only because of tiny samples, so I used HAVING COUNT(*) to filter them out. |
| vendor_payment_timing | How long do we take to pay after invoice? | Average 35.5 days (range 23 to 48). Martignetti is paid slowest among major vendors at about 37 days. |
| supplier_risk | Which big-spend vendors are also slow? | 8 vendors, about 34% of spend. Ultra Beverage is the clearest case at 8.4 days on $13.2M. The rest are close to average, so this is a watch list, not an alarm. |

Each query file in `queries/` starts with its business question and finding.

## Data notes

- Source: Kaggle "Vendor Performance Analysis" dataset (six CSV files).
- The sales file covers only January and February 2016, so sales-based conclusions describe two months, not a full year.
- The SQLite database (about 270 MB) is not in this repository because of GitHub's file size limit. It is rebuilt from the CSVs using `build_warehouse.py` and `schema.sql`.

## Tools

SQLite, SQL, Python, VS Code, Git

## Next steps

- Export query results and build a Power BI dashboard
- Add demand forecasting and an inventory optimization model
- Build a supplier scorecard combining cost, lead time and payment terms