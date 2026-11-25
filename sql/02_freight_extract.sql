-- Main data pull (used in Step 3 of src/finalProject.py)
-- One row per delivered, single-item order with valid weight and dimensions.
-- Its saved output is data/olist_freight_extract.csv (86,825 rows).
SELECT
    o.order_id,
    oi.order_item_id,
    o.order_purchase_timestamp,
    oi.price::numeric             AS price,
    oi.freight_value::numeric     AS freight_value,
    p.product_weight_g::numeric   AS weight_g,
    p.product_length_cm::numeric  AS length_cm,
    p.product_height_cm::numeric  AS height_cm,
    p.product_width_cm::numeric   AS width_cm,
    c.customer_state
FROM olist.orders o
JOIN olist.order_items oi ON oi.order_id   = o.order_id
JOIN olist.products    p  ON p.product_id  = oi.product_id
JOIN olist.customers   c  ON c.customer_id = o.customer_id
WHERE o.order_status = 'delivered'
  AND o.order_id IN (SELECT order_id FROM olist.order_items
                     GROUP BY order_id HAVING COUNT(*) = 1)
  AND p.product_weight_g  > 0
  AND p.product_length_cm > 0
  AND p.product_height_cm > 0
  AND p.product_width_cm  > 0;
