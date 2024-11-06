import os
from datetime import datetime, timedelta
import pendulum
from airflow import DAG
from airflow.operators.python import PythonOperator
from airflow.operators.bash import BashOperator
from pathlib import Path
import requests
import json
import requests
import time


AIRFLOW_HOME = os.getenv("AIRFLOW_HOME")
DBT_DIR = os.getenv("DBT_DIR")


def fetch_and_save_velib_data():
    url = "https://velib-metropole-opendata.smovengo.cloud/opendata/Velib_Metropole/station_status.json"

    response = requests.get(url)

    if response.status_code == 200:
        data = response.json()

        # Create a timestamp for the filename
        timestamp = time.strftime("%Y-%m-%d_%H-%M-%S")
        filename = f"./data_fetch/velib_station_status_{timestamp}.jsonl"

        # Save the JSON data to a file
        with open(filename, 'w') as f:
            for station in data['data']['stations']:
                f.write(json.dumps(station) + '\n')

def fetch_station_info():
    url = "https://velib-metropole-opendata.smovengo.cloud/opendata/Velib_Metropole/station_information.json"

    response = requests.get(url)

    if response.status_code == 200:
        data = response.json()

        # Create a timestamp for the filename
        timestamp = time.strftime("%Y-%m-%d_%H-%M-%S")
        filename = f"./data/station_info.jsonl"

        # Save the JSON data to a file
        with open(filename, 'w') as f:
            for station in data['data']['stations']:
                #ignore the rental_methods field - we don't need it and it's a pain
                if "rental_methods" in station:
                    del station['rental_methods']
                f.write(json.dumps(station) + '\n')

def trigger_airbyte():
    #obtaining the token
    url = "https://api.airbyte.com/v1/applications/token"

    payload = {
        "client_id": "91161352-4f8f-4298-a529-9ea628b64c84", #à mettre en os.environ
        "client_secret": "Az0F0XDLIrNrCppWeYPZtyrRLbaEBDvL", #à mettre en os.environ
        "grant-type": "client_credentials"
    }
    headers = {
        "accept": "application/json",
        "content-type": "application/json"
    }
    response = requests.post(url, json=payload, headers=headers)
    token=response.json()['access_token']

    #triggering the job

    url = "https://api.airbyte.com/v1/jobs"

    payload = {
        "jobType": "sync",
        "connectionId": "e98c6545-08ae-4c9b-b933-558a8819afa5" #à mettre en os.environ
    }
    headers = {
        "accept": "application/json",
        "content-type": "application/json",
        "authorization": f"Bearer {token}"
    }
    response = requests.post(url, json=payload, headers=headers)
    print(response.text)


def upload_json_files():
    """Uploads all JSON files in the current directory to the specified bucket.

    Args:
        bucket_name: The name of the bucket to upload to.
    """

    storage_client = storage.Client(project="dataengvelibforecast")  #à mettre en os.environ
    bucket = storage_client.bucket("velib_status")  #à mettre en os.environ

    velib_status_path ='./data/velib_status'
    for filename in os.listdir(velib_status_path):
        if filename.endswith('.jsonl'):
            full_path = os.path.join(velib_status_path, filename)
            blob = bucket.blob(filename)
            blob.upload_from_filename(full_path)



with DAG(
    "velib_workflow",
    default_args={"depends_on_past": False},
    description="DAG to process velib workflow for DataEng project",
    schedule_interval=None, #'*/10 * * * *', # every 10 minutes
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


with DAG(
    "velib_workflow_dbt",
    # default_args={"depends_on_past": False},
    description="DAG to process velib workflow for DataEng project",
    schedule_interval=None, #'*/10 * * * *', # every 10 minutes
    catchup = False,
    #depends_on_past=False,
    start_date=pendulum.today("UTC")

) as dbt_dag:

    dbt_run = BashOperator(
        task_id="dbt_run",
        bash_command=f"dbt run --project-dir {DBT_DIR}",
    )

    dbt_run
