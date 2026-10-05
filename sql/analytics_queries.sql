-- Total demand per spare part
SELECT
    part_id,
    SUM(demand) AS total_demand
FROM fact_inventory
GROUP BY part_id
ORDER BY total_demand DESC;

-- Monthly demand trend
SELECT
    month,
    SUM(demand) AS monthly_demand
FROM fact_inventory
GROUP BY month
ORDER BY month;

-- Average inventory by part and location
SELECT
    part_id,
    location,
    ROUND(AVG(inventory), 2) AS average_inventory
FROM fact_inventory
GROUP BY part_id, location
ORDER BY average_inventory ASC;

-- Stockout frequency and rate
SELECT
    part_id,
    location,
    SUM(stockout) AS stockout_events,
    ROUND(AVG(stockout::NUMERIC) * 100, 2) AS stockout_rate_pct
FROM fact_inventory
GROUP BY part_id, location
ORDER BY stockout_events DESC, stockout_rate_pct DESC;

-- Demand by location
SELECT
    location,
    SUM(demand) AS total_demand,
    ROUND(AVG(demand), 2) AS average_demand
FROM fact_inventory
GROUP BY location
ORDER BY total_demand DESC;

-- Average supplier lead time
SELECT
    part_id,
    location,
    ROUND(AVG(lead_time), 2) AS average_lead_time_days,
    MAX(lead_time) AS max_lead_time_days
FROM fact_inventory
GROUP BY part_id, location
ORDER BY average_lead_time_days DESC;

-- Parts below reorder point using monthly demand and lead time
WITH metrics AS (
    SELECT
        part_id,
        location,
        AVG(demand) AS average_demand,
        AVG(lead_time) AS average_lead_time,
        GREATEST(MAX(lead_time) - AVG(lead_time), 1) AS safety_lead_time,
        (ARRAY_AGG(inventory ORDER BY date DESC))[1] AS current_stock
    FROM fact_inventory
    GROUP BY part_id, location
),
reorder AS (
    SELECT
        part_id,
        location,
        current_stock,
        CEIL(average_demand * safety_lead_time / 30.0) AS safety_stock,
        CEIL((average_demand * average_lead_time / 30.0) + (average_demand * safety_lead_time / 30.0)) AS reorder_point
    FROM metrics
)
SELECT
    part_id,
    location,
    current_stock,
    safety_stock,
    reorder_point,
    CASE
        WHEN current_stock <= 0 THEN 'STOCKOUT'
        WHEN current_stock <= safety_stock THEN 'CRITICAL'
        WHEN current_stock <= reorder_point THEN 'REORDER'
        ELSE 'SAFE'
    END AS inventory_status
FROM reorder
WHERE current_stock <= reorder_point
ORDER BY reorder_point DESC;
