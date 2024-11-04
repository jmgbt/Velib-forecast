import os
from google.cloud import storage

def upload_json_files(bucket_name_info, bucket_name_status):
    """Uploads all JSON files in the current directory to the specified bucket.

    Args:
        bucket_name: The name of the bucket to upload to.
    """

    storage_client = storage.Client.from_service_account_json('/home/jmgobet/.gcp_keys/velib-key.json')

    bucket_i = storage_client.bucket(bucket_name_info)
    local_filename="data/station_info.jsonl"
    bucket_filename="station_info.jsonl"
    blob = bucket_i.blob(bucket_filename)
    blob.upload_from_filename(local_filename)
    print(f"File {local_filename} uploaded to {bucket_name_info}.")

    #bucket_s = storage_client.bucket(bucket_name_status)
    #for filename in os.listdir('.'):
    #    if filename.endswith('.jsonl'):
    #        blob = bucket_s.blob(filename)
    #        blob.upload_from_filename(filename)
    #        print(f"File {filename} uploaded to {bucket_name_status}.")


if __name__ == "__main__":
    upload_json_files("velib_info", "velib_status")
