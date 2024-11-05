import requests
latitude= 48.8566
longitude = 2.3522
altitude = requests.get(f'https://api.open-elevation.com/api/v1/lookup?locations={latitude},{longitude}')
altitude = altitude.json()['results'][0]['elevation']
print(str(altitude))
