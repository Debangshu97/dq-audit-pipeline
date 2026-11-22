# Profiling notes: Olist raw data

## Load
- All 9 CSVs were loaded into the `raw` schema as text, with `_source_file` and `_loaded_at` lineage columns.
- Row counts: orders 99,441; order_items 112,650; order_payments 103,886; order_reviews 99,224; customers 99,441; geolocation 1,000,163; products 32,951; sellers 3,095; category translation 71.
- Missing values come through as empty strings (''), not NULL, because the loader uses `keep_default_na=False`.

## raw.orders
- `order_id` is unique: 99,441 rows and 99,441 distinct IDs.
- Purchase dates run from 2016-09-04 to 2018-10-17, so freshness will be tested by replaying the data as daily batches, not by comparing with today's date.
- `order_status` has 8 values: delivered 96,478, shipped 1,107, canceled 625, unavailable 609, invoiced 314, processing 301, created 5, approved 2.

## Defects found
- 8 delivered orders have no delivery date (conditional completeness).
- 14 delivered orders have no approval date (missing process step).
- 6 canceled orders have a delivery date (status inconsistency, warning).
- A missing delivery date on undelivered orders (2,957 rows) is expected, not a defect.

## Reconciliation: payments vs items (price + freight)
- 99,441 orders compared with a FULL OUTER JOIN.
- 775 orders are paid but have no items (830 payment rows): mostly unavailable (643), canceled (179) and created (5), which is expected. 2 invoiced and 1 shipped order have no items, which is a defect.
- 1 order has items but no payment (orphan, failure).
- 303 orders have a payment total that differs from items plus freight by more than 0.01: 264 overpaid, 39 underpaid, average gap R$10.79, largest R$182.81. This is likely installment interest, so it's a warning within tolerance and a failure beyond it.