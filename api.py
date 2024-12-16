# https://api.market/store/aedbx/aerodatabox
import requests
from dotenv import load_dotenv
from opensky_api import OpenSkyApi
from utils import gen_date_range
from datetime import datetime
import os

load_dotenv()

CUTOFF_DATE = datetime(2024, 10, 1).timestamp()

AIRPORT_API_KEY= "e3b202405eafc13e73d2d4f8eee15fdbf0ee36610d136bdb1df5c17edadd32df535d6c7b6b3eedf130bd05cf46b4aaa5"

def airport_data(icao_code):
    url = f"https://airportdb.io/api/v1/airport/{icao_code}?apiToken={AIRPORT_API_KEY}"
    params = {
        "limit": 1
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
        latitude = data.get("latitude_deg", 0.0)
        longitude = data.get("longitude_deg", 0.0)

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
    url = "https://api.magicapi.dev/api/v1/aedbx/aerodatabox/aircrafts/search/term"
    params = {
        "q": tail_number,
        "limit": 1
    }
    headers = {
        "Authorization": f"Bearer {flight_api_key}"
    } 
                           
    response = requests.get(url, headers=headers, params=params)

    if response.status_code == 200:
        data = response.json()
        items = data.get("items", [])[0]
        hex_icao = hex_icao = items.get("hexIcao", "")
        first_flight_date = items.get("firstFlightDate", "")
        try:
            # convert to unix timestamp
            first_flight_date = datetime.strptime(first_flight_date, "%Y-%m-%d").timestamp()
            # make first flight date 2024 March 1st if before
            if first_flight_date < CUTOFF_DATE:
                first_flight_date = CUTOFF_DATE
        except: 
            first_flight_date = CUTOFF_DATE
        return {
            "tail_number": tail_number,
            "icao": hex_icao,
            "first_flight_date": first_flight_date
        }
    else:
        print(f"Error: {response.status_code}, {response.text}")

def get_list_of_src_dst_coords(list_of_flights):
    src_dst_coords = []
    print(f"Fetching data for {len(list_of_flights)} flights")
    for src, dst in list_of_flights:
        if not src or not dst:
            continue
        src_data = airport_data(src)
        dst_data = airport_data(dst)
        src_coords = (src_data["latitude"], src_data["longitude"])
        dst_coords = (dst_data["latitude"], dst_data["longitude"])
        src_dst_coords.append((src_coords, dst_coords))
        print(f"Added {src} to {dst} to list")
    return src_dst_coords


def fetch_flight_data(plane_icao, initial_date, halfway=False):
    # phony auth somehow works
    if halfway:
        # api = OpenSkyApi(username="tropicalsimr", password="OPENSKY2024")
        # api = OpenSkyApi(username="troptropsimr", password="OPENSKY2024")
        api = OpenSkyApi(username="Lev2", password="Football96!")
    else:
        # Lev Football96!
        # api = OpenSkyApi(username="troptropical", password="OPENSKY2024")
        api = OpenSkyApi(username="Lev3", password="Football96!")
    start_date = initial_date
    # lowercase the icao code
    plane_icao = plane_icao.lower()

    # list of tuples with src airport icao and dst airport icao
    list_of_flights = []
    count = 0
    while True:
        count += 1
        if count > 24:
            break
        start_date, end_date, done = gen_date_range(start_date)
        print(f"Fetching data from {start_date} to {end_date}")
        try:
            data = api.get_flights_by_aircraft(icao24=plane_icao, begin=start_date, end=end_date)
        except Exception as e:
            print(f"Error: {e}")
            data = []
        if data:
            for flight in data:
                list_of_flights.append(
                    (
                        flight.estDepartureAirport, 
                        flight.estArrivalAirport
                    )
                )
        if done:
            break
        start_date = end_date
        # prevents greater than 25 flights being logged
        if len(list_of_flights) > 24:
            break
    if len(list_of_flights) > 24:
        list_of_flights = list_of_flights[:24]
    return get_list_of_src_dst_coords(list_of_flights)

# def fuel_consumption():
#     pass
#     url = 



