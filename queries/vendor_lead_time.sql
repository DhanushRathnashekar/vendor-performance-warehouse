-- Business question: which vendors take longest from PO date to receiving date?
-- Finding: Average lead time is 7.6 days (range 3-14). Vendors with very few orders
-- look slow only because of tiny samples, so HAVING COUNT(*) >= 10000 restricts to
-- vendors with enough history. Ultra Beverage is slowest at 8.41 days; the top-spend
-- vendors cluster tightly around 7.5-7.7 days.

SELECT d.vendor_name,
       ROUND(AVG(julianday(f.receiving_date) - julianday(f.po_date)), 2) AS avg_lead_days,
       COUNT(*) AS purchase_lines
FROM fact_purchases f
JOIN dim_vendor d ON f.vendor_number = d.vendor_number
GROUP BY d.vendor_name
HAVING COUNT(*) >= 10000
ORDER BY avg_lead_days DESC
LIMIT 10;