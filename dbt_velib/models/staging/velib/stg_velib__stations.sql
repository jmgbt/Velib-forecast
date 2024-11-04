-- stg_velib__stations.sql

with

source as (

    select * from {{ source('velib','stations') }}

),

renamed as (

    select
      *
    from source

)

select * from renamed
