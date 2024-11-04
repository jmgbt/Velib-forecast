import requests
import json
import time

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
            # json.dump(data, f, indent=4)
            # json.dump(data['data']['stations'], f, indent=4)
            for station in data['data']['stations']:
                f.write(json.dumps(station) + '\n')

        print(f"Station info fetched and saved to {filename}")
    else:
        print(f"Error fetching data: {response.status_code}")

if __name__ == '__main__':
    fetch_station_info()
