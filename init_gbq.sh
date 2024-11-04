bq mk --location=europe-west1 -d $GBQ_PROJECT_ID:$GBQ_DS

bq query --project_id=$GBQ_PROJECT_ID --dataset_id=$GBQ_DATASET --use_legacy_sql=false < ./sql/init_velib_gbq.sql
