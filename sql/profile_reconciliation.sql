WITH items AS (
  SELECT order_id, sum(price::numeric + freight_value::numeric) AS items_total
  FROM raw.order_items GROUP BY order_id
), pays AS (
  SELECT order_id, sum(payment_value::numeric) AS paid_total
  FROM raw.order_payments GROUP BY order_id
)
SELECT
  count(*)                                                        AS orders_compared,
  count(*) FILTER (WHERE i.order_id IS NULL)                      AS paid_but_no_items,
  count(*) FILTER (WHERE p.order_id IS NULL)                      AS items_but_no_payment,
  count(*) FILTER (WHERE abs(i.items_total - p.paid_total) > 0.01) AS amount_mismatch
FROM items i
FULL OUTER JOIN pays p ON p.order_id = i.order_id;




-- 1) Status of orders that were paid but have no items
SELECT o.order_status, count(*)
FROM raw.order_payments p
JOIN raw.orders o USING (order_id)
WHERE NOT EXISTS (SELECT 1 FROM raw.order_items i WHERE i.order_id = p.order_id)
GROUP BY 1 ORDER BY 2 DESC;

-- 2) How big the 303 mismatches are
WITH items AS (
  SELECT order_id, sum(price::numeric + freight_value::numeric) AS items_total
  FROM raw.order_items GROUP BY order_id
), pays AS (
  SELECT order_id, sum(payment_value::numeric) AS paid_total
  FROM raw.order_payments GROUP BY order_id
)
SELECT
  count(*) FILTER (WHERE p.paid_total > i.items_total) AS overpaid,
  count(*) FILTER (WHERE p.paid_total < i.items_total) AS underpaid,
  round(avg(abs(p.paid_total - i.items_total)), 2)     AS avg_gap,
  max(abs(p.paid_total - i.items_total))               AS max_gap
FROM items i JOIN pays p USING (order_id)
WHERE abs(i.items_total - p.paid_total) > 0.01;