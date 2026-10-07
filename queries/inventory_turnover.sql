-- Business question: which products have the fastest-moving inventory (units sold
-- through from beginning to ending stock)?
-- Finding: Maurice's Mentholated Mint moved the most units (7,806) over the year,
-- followed by Pearl Cucumber Vodka (5,839) and Smirnoff 80 Proof (5,821). These are
-- the SKUs most at risk of stockout if under-ordered — and the ones that should carry
-- the EOQ model's real demand instead of the flat 500/yr assumption it currently uses.

SELECT p.description AS product, SUM(b.on_hand - e.on_hand) AS units_moved
FROM fact_beginning_inventory b
JOIN fact_ending_inventory e ON b.store = e.store AND b.brand = e.brand
JOIN dim_product p ON b.brand = p.brand
GROUP BY p.description
ORDER BY units_moved DESC
LIMIT 10;