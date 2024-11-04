CREATE TABLE IF NOT EXISTS velib.stations (
  station_id INT64 NOT NULL,
  station_code INT64 NOT NULL,
  station_name STRING NOT NULL,
  station_latitude FLOAT64 NOT NULL,
  station_longitude FLOAT64 NOT NULL,
  station_capacity INT64 NOT NULL,
  PRIMARY KEY(station_id) NOT ENFORCED
);

CREATE TABLE IF NOT EXISTS velib.
station_status (
  station_id INT64 NOT NULL,
  last_reported TIMESTAMP NOT NULL,
  num_bikes_available INT64 NOT NULL,
  num_docks_available INT64 NOT NULL,
  num_bikes_available_mechanical INT64 NOT NULL,
  num_bikes_available_ebike INT64 NOT NULL,
  is_installed BOOLEAN NOT NULL,
  is_renting BOOLEAN NOT NULL,
  is_returning BOOLEAN NOT NULL,
  PRIMARY KEY(station_id, last_reported) NOT ENFORCED
);
