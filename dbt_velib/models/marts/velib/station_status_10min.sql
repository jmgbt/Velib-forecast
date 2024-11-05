--station_status_10min.sql

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
)
SELECT
   station_ID,
   last_reported_1O,
   COALESCE(
       mechanical_actual_value,
       mechanical_value_before +
       (TIMESTAMP_DIFF(last_reported_1O, time_before, SECOND) *
       (mechanical_value_after - mechanical_value_before) /
       NULLIF(TIMESTAMP_DIFF(time_after, time_before, SECOND), 0))
   ) AS mechanical_bikes_available_interpolee,
   COALESCE(
       ebikes_actual_value,
       ebikes_value_before +
       (TIMESTAMP_DIFF(last_reported_1O, time_before, SECOND) *
       (ebikes_value_after - ebikes_value_before) /
       NULLIF(TIMESTAMP_DIFF(time_after, time_before, SECOND), 0))
   ) AS ebikes_available_interpolee
FROM
   {{ ref('int_velib__stg_station__status') }} AS a
WHERE last_reported_1O <= (SELECT max_time FROM time_bounds b WHERE b.station_ID = a.station_ID)
ORDER BY
   station_ID,
   last_reported_1O
