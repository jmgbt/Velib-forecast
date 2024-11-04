import os
from google.cloud import storage

def upload_json_files(bucket_name):
    """Uploads all JSON files in the current directory to the specified bucket.

    Args:
        bucket_name: The name of the bucket to upload to.
    """

    storage_client = storage.Client.from_service_account_json('/home/jmgobet/.gcp_keys/velib-key.json')
    bucket = storage_client.bucket(bucket_name)

    filename = "./data/station_info_2024-11-03_09-51-54.json"
    blob = bucket.blob(filename)
    blob.upload_from_filename(filename)

    print(f"File {filename} uploaded to {bucket_name}.")

if __name__ == "__main__":

    upload_json_files("json_velib")
