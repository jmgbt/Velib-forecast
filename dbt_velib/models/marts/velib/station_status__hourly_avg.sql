--station_status__hourly_avg.sql

with temp as (
  SELECT station_ID
    , name, lat, lon
    , EXTRACT (TIME FROM last_reported_1O) as last_reported_10
    , avg(mechanical_bikes_available_interpolee) AS mechanical_bikes_available_avg
    , avg(ebikes_available_interpolee) AS ebikes_bikes_available_avg
    , avg(docks_available_interpolee) AS docks_bikes_available_avg
  FROM
  {{ ref('station_status_10min') }} as status
  GROUP BY 1, 2, 3, 4, 5
  ORDER BY 1, 5
)


SELECT station_id, name, ebikes_bikes_available_avg, mechanical_bikes_available_avg, docks_bikes_available_avg, last_reported_10
, EXTRACT(HOUR FROM last_reported_10) AS hour
, PARSE_TIMESTAMP('%Y-%m-%d %H:%M:%S', CONCAT(CURRENT_DATE(), ' ', last_reported_10)) AS timestamp_value
, CONCAT(lat,',',lon) AS localization
FROM temp
ORDER BY last_reported_10 desc
