-- Business question: which vendors do we spend the most with in total purchase dollars?
-- Finding: DIAGEO NORTH AMERICA INC is the top vendor by a wide margin ($50.96M),
-- nearly double #2 (MARTIGNETTI COMPANIES, $27.86M) — real vendor concentration:
-- strong leverage for negotiation, but meaningful single-vendor risk exposure.

SELECT d.vendor_name, SUM(f.dollars) AS total_amount
FROM fact_purchases f
JOIN dim_vendor d ON f.vendor_number = d.vendor_number
GROUP BY d.vendor_name
ORDER BY total_amount DESC
LIMIT 10;
