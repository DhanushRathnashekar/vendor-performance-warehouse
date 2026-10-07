-- Business question: how many days does each vendor's invoice take from invoice date to payment?
-- Uses fact_invoice_purchases (one row per PO invoice) rather than fact_purchases, which
-- repeats the same invoice/pay dates on every line item and would weight vendors by line count.

SELECT d.vendor_name,
       ROUND(AVG(julianday(f.pay_date) - julianday(f.invoice_date)), 2) AS avg_days_to_pay,
       COUNT(*) AS invoices
FROM fact_invoice_purchases f
JOIN dim_vendor d ON f.vendor_number = d.vendor_number
GROUP BY d.vendor_name
HAVING COUNT(*) >= 10
ORDER BY avg_days_to_pay DESC;
