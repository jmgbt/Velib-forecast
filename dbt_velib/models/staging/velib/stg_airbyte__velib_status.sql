-- stg_airbyte__station_status.sql

select
 station_id, last_reported, num_bikes_available, num_docks_available

  ,CAST(JSON_EXTRACT_SCALAR(
    JSON_EXTRACT_ARRAY(num_bikes_available_types)[OFFSET(0)],
    '$.mechanical'
  ) AS INT) as mechanical_bikes_available,

  CAST(JSON_EXTRACT_SCALAR(
    JSON_EXTRACT_ARRAY(num_bikes_available_types)[OFFSET(1)],
    '$.ebike'
  ) AS INT) as ebikes_available
 , is_installed,
  is_renting, is_returning
 from {{ source('Airbyte','velib_status') }}
