import os
from datetime import datetime, timedelta
import pendulum
from airflow import DAG
from airflow.operators.python import PythonOperator
from pathlib import Path
from app.fetch_data import fetch_and_save_velib_data
from app.fetch_station_information import fetch_and_save_station_information
from app.trigger_airbyte import trigger_airbyte

AIRFLOW_HOME = os.getenv("AIRFLOW_HOME")


with DAG(
    "velib_workflow",
    default_args={"depends_on_past": False},
    description="DAG to process velib workflow for DataEng project",
    schedule_interval='*/10 * * * *', # every 10 minutes
    catchup = False,
    #depends_on_past=False,
    start_date=pendulum.today("UTC")

) as dag:

    fetch_spot_data = PythonOperator(
    task_id='fetch_spot_data',
    python_callable=fetch_and_save_velib_data,
    dag=dag)

    # fetch_station_info = PythonOperator(
    # task_id='fetch_station_info',
    # python_callable=fetch_station_info,
    # dag=dag)

    upload_to_bucket = PythonOperator(
    task_id='upload_to_bucket',
    python_callable=upload_json_files,
    dag=dag)

    trigger_airbyte = PythonOperator(
    task_id='trigger_airbyte',
    python_callable=trigger_airbyte,
    dag=dag)


    fetch_spot_data >> upload_to_bucket >> trigger_airbyte
    # fetch_station_info >> upload_to_bucket
