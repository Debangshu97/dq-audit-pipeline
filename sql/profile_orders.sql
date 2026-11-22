SELECT
  count(*)                                              AS total_rows,
  count(DISTINCT order_id)                              AS distinct_order_ids,
  count(*) FILTER (WHERE order_approved_at = '')        AS missing_approved,
  count(*) FILTER (WHERE order_delivered_customer_date = '') AS missing_delivered,
  min(order_purchase_timestamp)                         AS first_purchase,
  max(order_purchase_timestamp)                         AS last_purchase
FROM raw.orders;

SELECT order_status, count(*) AS n
FROM raw.orders
GROUP BY order_status
ORDER BY n DESC;

SELECT order_status,
       count(*) FILTER (WHERE order_delivered_customer_date = '') AS missing_delivered,
       count(*) FILTER (WHERE order_approved_at = '')             AS missing_approved
FROM raw.orders
GROUP BY order_status
ORDER BY order_status;