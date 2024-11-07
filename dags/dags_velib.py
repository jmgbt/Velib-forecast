from pathlib import Path
import os
from datetime import datetime, timedelta
import requests, json, time, pendulum
from airflow import DAG
from airflow.operators.python import PythonOperator
from airflow.operators.bash import BashOperator
from airflow.providers.google.cloud.hooks.gcs import GCSHook
import logging

AIRFLOW_HOME = os.getenv("AIRFLOW_HOME")
DBT_DIR = os.getenv("DBT_DIR")


def fetch_and_save_velib_data():
    url = "https://velib-metropole-opendata.smovengo.cloud/opendata/Velib_Metropole/station_status.json"

    response = requests.get(url)

    if response.status_code == 200:
        data = response.json()

        # Create a timestamp for the filename
        timestamp = time.strftime("%Y-%m-%d_%H-%M-%S")
        filename = f"./data/fetch/velib_station_status_{timestamp}.jsonl"

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


def upload_json_files(**kwargs):
    """Uploads all JSON files in the current directory to the specified bucket.

    Args:
        bucket_name: The name of the bucket to upload to.
    """

    gcs_hook = GCSHook(gcp_conn_id='my_gcs_conn_velib') #/!\ json gcp en dur dans le setting Airflow à transformer en secret

    velib_status_path ='./data/fetch'
    bucket = os.getenv("GS_BUCKET_VELIB_STATUS")

    for filename in os.listdir(velib_status_path):
        if filename.endswith('.jsonl'):
            full_path_origin = os.path.join(velib_status_path, filename)
            gcs_hook.upload(bucket_name="velib_status_new",
                    object_name=filename, # destination
                    filename=full_path_origin) # origine

# Coded by ClaudeGPT (time pressure)
def get_airbyte_token():
    """Get a fresh Airbyte API token"""
    url = "https://api.airbyte.com/v1/applications/token"
    payload = {
        "client_id": os.getenv("airbyte_client_id"),
        "client_secret": os.getenv("airbyte_client_secret"),
        "grant-type": "client_credentials"
    }
    headers = {
        "accept": "application/json",
        "content-type": "application/json"
    }
    response = requests.post(url, json=payload, headers=headers)
    return response.json()['access_token']

# Coded by ClaudeGPT (time pressure)
def trigger_airbyte(**context):
    """Triggers Airbyte sync and returns job ID"""
    logging.info("Starting trigger_airbyte function")
    try:
        # Get a fresh token
        token = get_airbyte_token()

        logging.info("Successfully obtained access token")

        # First, check for running jobs
        connection_id = os.getenv("airbyte_connection_id")
        running_jobs_url = f"https://api.airbyte.com/v1/jobs?connectionId={connection_id}&status=running"
        headers = {
            "accept": "application/json",
            "authorization": f"Bearer {token}"
        }
        jobs_response = requests.get(running_jobs_url, headers=headers)
        jobs_data = jobs_response.json()

        # If there's a running job, use its ID
        if 'data' in jobs_data and jobs_data['data']:
            running_job = jobs_data['data'][0]  # Get the first running job
            job_id = str(running_job.get('jobId'))
            logging.info(f"Found running job with ID: {job_id}")
            task_instance = context['task_instance']
            task_instance.xcom_push(key='job_id', value=job_id)
            return job_id

        # If no running job, trigger new one
        url = "https://api.airbyte.com/v1/jobs"
        payload = {
            "jobType": "sync",
            "connectionId": connection_id
        }
        headers = {
            "accept": "application/json",
            "content-type": "application/json",
            "authorization": f"Bearer {token}"
        }
        response = requests.post(url, json=payload, headers=headers)
        response_data = response.json()

        # Check if we got an error response
        if response.status_code == 409:
            # Extract connection ID from error message
            error_msg = response_data.get('data', {}).get('message', '')
            logging.info(f"Got 409 response with message: {error_msg}")

            # Wait a moment and check for running jobs again
            time.sleep(5)
            jobs_response = requests.get(running_jobs_url, headers=headers)
            jobs_data = jobs_response.json()

            if 'data' in jobs_data and jobs_data['data']:
                running_job = jobs_data['data'][0]
                job_id = str(running_job.get('jobId'))
                logging.info(f"Found running job after 409 error: {job_id}")
                task_instance = context['task_instance']
                task_instance.xcom_push(key='job_id', value=job_id)
                return job_id

        # If we got a successful response
        if 'jobId' in response_data:
            job_id = str(response_data['jobId'])
            logging.info(f"Successfully created new job with ID: {job_id}")
            task_instance = context['task_instance']
            task_instance.xcom_push(key='job_id', value=job_id)
            return job_id

        raise ValueError(f"Unable to get or create job. Response was: {response.text}")

    except Exception as e:
        logging.error(f"Error in trigger_airbyte: {str(e)}")
        raise

# Coded by ClaudeGPT (time pressure)
def check_job_status(**context):
    """Checks Airbyte job status until completion"""
    try:
        job_id = context['task_instance'].xcom_pull(task_ids='trigger_airbyte')
        logging.info(f"Checking status for job ID: {job_id}")

        # Keep checking until job is complete
        max_attempts = 60  # Maximum number of attempts (60 minutes total with 1-minute intervals)
        attempt = 0

        while attempt < max_attempts:
            # Get fresh token for each check
            token = get_airbyte_token()
            headers = {
                "accept": "application/json",
                "authorization": f"Bearer {token}"
            }

            status_url = f"https://api.airbyte.com/v1/jobs/{job_id}"
            status_response = requests.get(status_url, headers=headers)
            status_data = status_response.json()
            logging.info(f"Status API Response: {status_data}")

            # Handle 401 error explicitly
            if status_response.status_code == 401:
                logging.warning("Token expired, getting new token...")
                token = get_airbyte_token()
                headers["authorization"] = f"Bearer {token}"
                status_response = requests.get(status_url, headers=headers)
                status_data = status_response.json()

            # Extract status from response
            status = None
            if 'job' in status_data:
                status = status_data['job'].get('status')
            else:
                status = status_data.get('status')

            logging.info(f"Current job status: {status}")

            if status == 'succeeded' or status == 'completed' or status == 'success':
                logging.info(f"Job {job_id} completed successfully")
                # Add a small delay to ensure data is fully available
                time.sleep(30)
                return True

            elif status in ['failed', 'cancelled', 'error', 'failure']:
                raise Exception(f"Job {job_id} failed with status: {status}")

            elif status in ['running', 'pending', 'waiting']:
                logging.info(f"Job still running (attempt {attempt + 1}/{max_attempts}). Waiting 60 seconds...")
                attempt += 1
                time.sleep(60)  # Wait for 1 minute before checking again
                continue

            else:
                logging.warning(f"Unknown status: {status}")
                attempt += 1
                time.sleep(60)

        # If we've exceeded max attempts
        raise Exception(f"Timeout waiting for job completion after {max_attempts} minutes")

    except Exception as e:
        logging.error(f"Error in check_job_status: {str(e)}")
        raise

default_args = {
    'owner': 'airflow',
    'depends_on_past': False,
    'email_on_failure': False,
    'email_on_retry': False,
    'retries': 1,
    'retry_delay': timedelta(minutes=5),
    'execution_timeout': timedelta(hours=2)
}

with DAG(
    "velib_workflow",
    default_args=default_args,
    description="DAG to process velib workflow for DataEng project",
    schedule_interval=None,
    catchup=False,
    start_date=pendulum.today("UTC")
) as dag:

    fetch_spot_data = PythonOperator(
    task_id='fetch_spot_data',
    python_callable=fetch_and_save_velib_data,
    dag=dag)

    upload_to_bucket = PythonOperator(
    task_id='upload_to_bucket',
    python_callable=upload_json_files,
    dag=dag)

    # In your DAG:
    trigger_airbyte_task = PythonOperator(
        task_id='trigger_airbyte',
        python_callable=trigger_airbyte,
        provide_context=True,  # Add this
        dag=dag,
    )

    wait_for_completion_task = PythonOperator(
        task_id='wait_for_completion',
        python_callable=check_job_status,
        provide_context=True,
        dag=dag,
    )

    dbt_run = BashOperator(
        task_id="dbt_run",
        bash_command=f"dbt run --project-dir {DBT_DIR}",
    dag=dag)

    fetch_spot_data >> upload_to_bucket >> trigger_airbyte_task >> wait_for_completion_task >> dbt_run

with DAG(
    "velib_dbt_run",
    default_args=default_args,
    description="DAG to call dbt run independently",
    schedule_interval=None,
    catchup=False,
    start_date=pendulum.today("UTC")
) as dbt_dag:
    dbt_run = BashOperator(
        task_id="dbt_run",
        bash_command=f"dbt run --project-dir {DBT_DIR}",
    dag=dbt_dag)

    dbt_run
