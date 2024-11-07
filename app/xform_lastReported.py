import os
import json
from datetime import datetime, timedelta
from google.cloud import storage


if __name__ == "__main__":

    source_bucket_name = "historique_json_raw"
    dest_bucket_name = "velib_status_new"

    client = storage.Client(project=os.getenv("GCP_PROJECT_ID"))
    source_bucket = client.get_bucket(source_bucket_name)
    dst_bucket = client.get_bucket(dest_bucket_name)

    # List all blobs/objects in the bucket
    source_blobs = source_bucket.list_blobs()

    print(f"Objects in bucket '{source_bucket_name}':")

    for source_blob in source_blobs:
        print(f"{source_blob.name}")
        json_content = source_blob.download_as_string()
        data = json.loads(json_content)

      # Create a list to store all processed stations
        processed_stations = []

        # Process each station and add to the list
        for station in data['data']['stations']:
            station['last_reported'] = data['lastUpdatedOther']
            processed_stations.append(json.dumps(station))

        # Join all stations with newlines to create JSONL format
        jsonl_content = '\n'.join(processed_stations) + '\n'

        # Upload to destination bucket
        dest_blob = dst_bucket.blob(f"{source_blob.name}l")
        dest_blob.upload_from_string(
            jsonl_content,
            content_type='application/jsonl'
        )

        print(f"Wrote {len(processed_stations)} stations to {source_blob.name}l")
