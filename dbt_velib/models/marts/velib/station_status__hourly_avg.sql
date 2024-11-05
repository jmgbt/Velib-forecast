--station_status__hourly_avg.sql

SELECT station_ID
  , EXTRACT (TIME FROM last_reported_1O) as last_reported_10
  , avg(mechanical_bikes_available_interpolee) AS mechanical_bikes_available_avg
  , avg(ebikes_available_interpolee) AS ebikes_bikes_available_avg
FROM
  {{ ref('station_status_10min') }}
GROUP BY station_ID, last_reported_1O
ORDER BY station_ID, last_reported_1O
