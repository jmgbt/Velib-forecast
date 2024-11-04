CREATE OR REPLACE EXTERNAL TABLE velib.stations_external
OPTIONS (
  format = 'JSON',
  uris = ['gs://json_velib/info/station_info.jsonl']
);

INSERT INTO velib.stations
SELECT
  station_id,
  CAST(stationCode as INT64) as station_code,
  name as station_name,
  lat as station_latitude,
  lon as station_longitude,
  capacity as station_capacity
FROM velib.stations_external;

DROP TABLE velib.stations_external;
