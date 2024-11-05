--station_status__hourly_avg.sql

SELECT station_ID
 , name, lat, lon
 , EXTRACT (TIME FROM last_reported_1O) as last_reported_10
 , avg(mechanical_bikes_available_interpolee) AS mechanical_bikes_available_avg
 , avg(ebikes_available_interpolee) AS ebikes_bikes_available_avg
 , avg(docks_available_interpolee) AS docks_bikes_available_avg
FROM
 velib.station_status_10min
GROUP BY 1, 2, 3, 4, 5
ORDER BY 1, 5
