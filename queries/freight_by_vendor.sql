-- Business question: which vendors cost us the most in freight?
-- Finding: DIAGEO NORTH AMERICA INC leads at $257K, about 16% of the $1.64M total
-- freight and well ahead of #2 (MARTIGNETTI COMPANIES, $145K). The top 10 is the same
-- 10 vendors in the same order as top_vendors_by_spend.sql, so freight appears to
-- grow with purchase volume rather than any one vendor being unusually costly to ship.

SELECT d.vendor_name, SUM(f.freight) AS total_freight
FROM fact_invoice_purchases f
JOIN dim_vendor d ON f.vendor_number = d.vendor_number
GROUP BY d.vendor_name
ORDER BY total_freight DESC
LIMIT 10;
