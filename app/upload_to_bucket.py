import os
from google.cloud import storage

def upload_json_files():
    """Uploads all JSON files in the current directory to the specified bucket.

    Args:
        bucket_name: The name of the bucket to upload to.
    """

    storage_client = storage.Client(project=os.getenv('GCP_PROJECT'))
    bucket = storage_client.bucket(os.getenv('GS_BUCKET_VELIB_STATUS'))

    velib_status_path ='./data/velib_status'
    for filename in os.listdir(velib_status_path):
        if filename.endswith('.jsonl'):
            full_path = os.path.join(velib_status_path, filename)
            print(filename)
            print(full_path)
            blob = bucket.blob(filename)
            blob.upload_from_filename(full_path)
            print(f"File {full_path} uploaded to {os.getenv('GS_BUCKET')}.")



if __name__ == "__main__":
    upload_json_files()
