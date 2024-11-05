import requests
import os
from dotenv import load_dotenv

def trigger_airbyte():
    #obtaining the token
    url = "https://api.airbyte.com/v1/applications/token"

    payload = {
        "client_id": os.getenv("airbyte_client_id"), #à mettre en os.environ
        "client_secret": os.getenv("airbyte_client_secret"), #à mettre en os.environ
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
        "connectionId": os.getenv("airbyte_connectionId") #à mettre en os.environ
    }
    headers = {
        "accept": "application/json",
        "content-type": "application/json",
        "authorization": f"Bearer {token}"
    }
    response = requests.post(url, json=payload, headers=headers)
    print(response.text)

if __name__ == '__main__':
    trigger_airbyte()
