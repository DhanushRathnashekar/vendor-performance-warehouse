-- Business question: which vendors combine high spend (>$5M) with above-average lead time (>7.6 days)?
-- Finding: 8 vendors, about 34% of total purchase spend. Ultra Beverage is the clearest case
-- (8.41 days on $13.2M); the rest are within a fraction of a day of the 7.6-day average,
-- so this is a watch list, not an alarm. Lead time comes from PO date to receiving date.

SELECT d.vendor_name,
       ROUND(SUM(f.dollars), 0) AS total_spend,
       ROUND(AVG(julianday(f.receiving_date) - julianday(f.po_date)), 2) AS avg_lead_days
FROM fact_purchases f
JOIN dim_vendor d ON f.vendor_number = d.vendor_number
GROUP BY d.vendor_name
HAVING SUM(f.dollars) > 5000000 AND AVG(julianday(f.receiving_date) - julianday(f.po_date)) > 7.6
ORDER BY total_spend DESC;