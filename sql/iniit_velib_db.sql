CREATE TABLE IF NOT EXISTS stations (
  station_id BIGINT PRIMARY KEY,
  station_code INT NOT NULL,
  station_name VARCHAR(255) NOT NULL,
  station_latitude FLOAT NOT NULL,
  station_longitude FLOAT NOT NULL,
  station_capacity INT NOT NULL,
  rental_methods VARCHAR(255) NOT NULL
);

CREATE TABLE IF NOT EXISTS station_status (
  station_id BIGINT NOT NULL,
  last_reported TIMESTAMP NOT NULL,
  num_bikes_available INT NOT NULL,
  num_docks_available INT NOT NULL,
  num_bikes_available_mechanical INT NOT NULL,
  num_bikes_available_ebike INT NOT NULL,
  is_installed BOOLEAN NOT NULL,
  is_renting BOOLEAN NOT NULL,
  is_returning BOOLEAN NOT NULL,
  PRIMARY KEY (station_id, last_reported),
  FOREIGN KEY (station_id) REFERENCES stations(station_id)
);
