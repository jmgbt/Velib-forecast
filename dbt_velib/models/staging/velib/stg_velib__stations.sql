-- stg_velib__stations.sql

select * from {{ source('Airbyte','station_info') }}
