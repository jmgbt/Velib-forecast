-- stg_velib__stations.sql

select * from {{ source('velib','stations') }}
