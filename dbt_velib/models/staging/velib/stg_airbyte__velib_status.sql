-- stg_airbyte__station_status.sql

SELECT *
FROM (
  SELECT
  station_id
  , TIMESTAMP_SECONDS(CAST(last_reported as INT64)) AS last_reported
  , TIMESTAMP_TRUNC(
      TIMESTAMP_SUB(
          TIMESTAMP_SECONDS(CAST(last_reported as INT64)),
          INTERVAL MOD(EXTRACT(MINUTE FROM TIMESTAMP_SECONDS(CAST(last_reported as INT64))), 10) MINUTE
      ),
      MINUTE
  ) AS last_reported_1O

  , num_docks_available

    ,CAST(JSON_EXTRACT_SCALAR(
      JSON_EXTRACT_ARRAY(num_bikes_available_types)[OFFSET(0)],
      '$.mechanical'
    ) AS INT) AS mechanical_bikes_available,

    CAST(JSON_EXTRACT_SCALAR(
      JSON_EXTRACT_ARRAY(num_bikes_available_types)[OFFSET(1)],
      '$.ebike'
    ) AS INT) AS ebikes_available
  , is_installed,
    is_renting, is_returning
  FROM {{ source('Airbyte','velib_status') }}
)
WHERE mechanical_bikes_available IS NOT NULL AND ebikes_available IS NOT NULL
