import requests
import json
import time

def fetch_and_save_velib_data():
    url = "https://velib-metropole-opendata.smovengo.cloud/opendata/Velib_Metropole/station_status.json"

    response = requests.get(url)

    if response.status_code == 200:
        data = response.json()

        # Create a timestamp for the filename
        timestamp = time.strftime("%Y-%m-%d_%H-%M-%S")
        filename = f"velib_station_status_{timestamp}.json"

        # Save the JSON data to a file
        with open(filename, 'w') as f:
            json.dump(data, f, indent=4)

        print(f"Station status data fetched and saved to {filename}")
    else:
        print(f"Error fetching data: {response.status_code}")

# Set the interval for data fetching (in seconds)
interval = 600  # 10 minutes

while True:
    fetch_and_save_velib_data()
    time.sleep(interval)
