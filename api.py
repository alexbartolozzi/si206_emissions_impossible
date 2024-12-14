# https://api.market/store/aedbx/aerodatabox
import requests
from dotenv import load_dotenv
from opensky_api import OpenSkyApi
from utils import gen_date_range
from datetime import datetime
import os

load_dotenv()

AIRPORT_API_KEY= "e3b202405eafc13e73d2d4f8eee15fdbf0ee36610d136bdb1df5c17edadd32df535d6c7b6b3eedf130bd05cf46b4aaa5"

def airport_data(icao_code):
    print(AIRPORT_API_KEY)
    url = f"https://airportdb.io/api/v1/airport/{icao_code}?apiToken={AIRPORT_API_KEY}"
    params = {
        "limit": 10
    }
    headers = {
        "Authorization": f"Bearer {AIRPORT_API_KEY}"
    }

response = requests.get(url)

    if response.status_code == 200:
        data = response.json()

        airport_name = data.get("name", "")
        city = data.get("municipality", "")
        country = data.get("iso_country", "")
        latitude = data.get("latitude", 0.0)
        longitude = data.get("longitude", 0.0)

        return {
            "icao_code": icao_code,
            "airport_name": airport_name,
            "city": city,
            "country": country,
            "latitude": latitude,
            "longitude": longitude
        }
    else:
        print(f"Error: {response.status_code}, {response.text}")
        return None



flight_api_key = os.getenv("FLIGHT_API_KEY")

def fetch_plane_metadata(tail_number):
    print(flight_api_key)
    url = "https://api.magicapi.dev/api/v1/aedbx/aerodatabox/aircrafts/search/term"
    tail_number = "N898TS"
    params = {
        "q": tail_number,
        "limit": 10
    }
    headers = {
        "Authorization": f"Bearer {flight_api_key}"
    } 
                           
    response = requests.get(url, headers=headers, params=params)

    if response.status_code == 200:
        data = response.json().get("data", [])
        hex_icao = hex_icao = data[0].get("hexIcao", "")
        plane_name = data[0].get("typeName", "")
        first_flight_date = data[0].get("firstFlightDate", "")
        try:
            # convert to unix timestamp
            first_flight_date = datetime.strptime(first_flight_date, "%Y-%m-%d").timestamp()
            # if first flight date is before 2015, set it to 2015
            if first_flight_date < 1420070400:
                first_flight_date = 1420070400
        except: 
            first_flight_date = 1420070400

        return {
            "tail_number": tail_number,
            "icao": hex_icao,
            "plane_name": plane_name,
            "first_flight_date": first_flight_date
        }
    else:
        print(f"Error: {response.status_code}, {response.text}")


def fetch_flight_data(icao, initial_date):
    api = OpenSkyApi()
    s = api.get_states()
    print(s)
    start_date = initial_date
    # lowercase the icao code
    icao = icao.lower()
    print(icao)

    data = api.get_flights_by_aircraft("3c675a", 1517184000, 1517270400)
    for flight in data:
        print(flight)
    while True:
        start_date, end_date, done = gen_date_range(start_date)
        print(f"Fetching data from {start_date} to {end_date}")
        data = api.get_flights_by_aircraft(icao24=icao, begin=start_date, end=end_date)
        print(data)
        if done:
            break
        start_date = end_date

fetch_flight_data("3c675a", 1420070400)


# def fuel_consumption():
#     pass
#     url = 


## Fuel Burn = (Fuel Consumption Rate) x (Flight Time or Distance)
## Flight time = Distance (miles) / Cruise Speed (MPH)

## Jet fuel emits approximately 9.57 kg of CO2 per gallon (or 3.16 kg of CO2 per liter) when burned.

## CO2 Emissions (kg) = (Fuel Burn in liters) x (Emission Factor: 3.16 kg CO2/liter)