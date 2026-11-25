-- How many orders survive each filter (used in Step 2 of src/finalProject.py)
--   n_delivered   : orders with status 'delivered'
--   n_single_item : of those, orders with exactly one item
--   n_final       : of those, products with weight and all three dimensions > 0
WITH delivered AS (
    SELECT order_id FROM olist.orders WHERE order_status = 'delivered'
),
single_item AS (
    SELECT order_id FROM olist.order_items GROUP BY order_id HAVING COUNT(*) = 1
)
SELECT
    (SELECT COUNT(*) FROM delivered) AS n_delivered,
    (SELECT COUNT(*) FROM delivered d JOIN single_item s ON d.order_id = s.order_id)
        AS n_single_item,
    (SELECT COUNT(*)
       FROM delivered d
       JOIN single_item s        ON d.order_id = s.order_id
       JOIN olist.order_items oi ON d.order_id = oi.order_id
       JOIN olist.products p     ON oi.product_id = p.product_id
      WHERE p.product_weight_g > 0 AND p.product_length_cm > 0
        AND p.product_height_cm > 0 AND p.product_width_cm > 0) AS n_final;
