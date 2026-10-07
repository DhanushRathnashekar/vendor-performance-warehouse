-- Business question: how many days does each vendor take from PO date to receiving date?
-- Finding: lead times are tightly clustered. The overall average is 7.6 days and every
-- purchase lands within 3-14 days. The slowest averages (e.g. FLAVOR ESSENCE INC, 13 days)
-- come from vendors with only 1-2 purchase lines. Among high-volume vendors,
-- ULTRA BEVERAGE COMPANY LLP is the slowest at 8.4 days over 84K lines, so lead time is
-- not a strong differentiator between the main suppliers.

SELECT d.vendor_name,
       ROUND(AVG(julianday(f.receiving_date) - julianday(f.po_date)), 2) AS avg_lead_days,
       COUNT(*) AS purchase_lines
FROM fact_purchases f
JOIN dim_vendor d ON f.vendor_number = d.vendor_number
GROUP BY d.vendor_name
ORDER BY avg_lead_days DESC;
