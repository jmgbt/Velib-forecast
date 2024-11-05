-- int_velib__stg_station__status.sql

-- 100% coded by ClaudeGPT since I did not have time

WITH distinct_values AS (
   SELECT
       station_ID,
       last_reported_1O,
       AVG(mechanical_bikes_available) as mechanical_bikes_available,
       AVG(ebikes_available) as ebikes_available
   FROM
       {{ ref('stg_airbyte__velib_status') }}
   GROUP BY station_ID, last_reported_1O
),
time_bounds AS (
   SELECT
       station_ID,
       MIN(last_reported_1O) as min_time,
       MAX(last_reported_1O) as max_time
   FROM distinct_values
   GROUP BY station_ID
),
time_intervals AS (
   SELECT station_ID, interval_time
   FROM time_bounds,
   UNNEST(GENERATE_TIMESTAMP_ARRAY(min_time, max_time, INTERVAL 10 MINUTE)) as interval_time
)
-- all_intervals AS (
   SELECT
       t.station_ID,
       t.interval_time as last_reported_1O,
       -- mechanical bikes calculations
       COALESCE(d.mechanical_bikes_available,
           LAST_VALUE(d.mechanical_bikes_available IGNORE NULLS) OVER (PARTITION BY t.station_ID ORDER BY t.interval_time
               ROWS BETWEEN UNBOUNDED PRECEDING AND 1 PRECEDING)) as mechanical_value_before,
       FIRST_VALUE(d.mechanical_bikes_available IGNORE NULLS) OVER (PARTITION BY t.station_ID ORDER BY t.interval_time
           ROWS BETWEEN 1 FOLLOWING AND UNBOUNDED FOLLOWING) as mechanical_value_after,
       -- ebikes calculations
       COALESCE(d.ebikes_available,
           LAST_VALUE(d.ebikes_available IGNORE NULLS) OVER (PARTITION BY t.station_ID ORDER BY t.interval_time
               ROWS BETWEEN UNBOUNDED PRECEDING AND 1 PRECEDING)) as ebikes_value_before,
       FIRST_VALUE(d.ebikes_available IGNORE NULLS) OVER (PARTITION BY t.station_ID ORDER BY t.interval_time
           ROWS BETWEEN 1 FOLLOWING AND UNBOUNDED FOLLOWING) as ebikes_value_after,
       -- common time calculations
       LAST_VALUE(t.interval_time IGNORE NULLS) OVER (PARTITION BY t.station_ID ORDER BY t.interval_time
           ROWS BETWEEN UNBOUNDED PRECEDING AND 1 PRECEDING) as time_before,
       FIRST_VALUE(t.interval_time IGNORE NULLS) OVER (PARTITION BY t.station_ID ORDER BY t.interval_time
           ROWS BETWEEN 1 FOLLOWING AND UNBOUNDED FOLLOWING) as time_after,
       d.mechanical_bikes_available as mechanical_actual_value,
       d.ebikes_available as ebikes_actual_value
   FROM time_intervals t
   LEFT JOIN distinct_values d
   ON t.interval_time = d.last_reported_1O
   AND t.station_ID = d.station_ID
