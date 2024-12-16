"""Main file"""

import sqlite3 
from database import init_db
from webscraper import finish_web_scrape
from api import (
    fetch_plane_metadata, 
    fetch_flight_data,
)
from utils import calc_flight_distance, process_data_and_calc
import matplotlib.pyplot as plt
import numpy as np
import sys
import json

def get_celeb_and_tail(run_count):
    conn = sqlite3.connect('celebrity_airplane.db')
    cursor = conn.cursor()
    cursor.execute(
        """
            SELECT Celebrity.id, tail_number
            FROM Airplane
            JOIN Celebrity ON Airplane.id = Celebrity.plane_id
            LIMIT 1
            OFFSET ?
        """, (run_count,)
    )
    celeb_id, tail_number = cursor.fetchone()
    conn.close()
    return celeb_id, tail_number

def build_up_db(run_count, halfway):
    celeb_id, tail_number = get_celeb_and_tail(run_count)
    # get icao for plane from api
    print(f"Fetching data for {tail_number}")
    plane_data = fetch_plane_metadata(tail_number)
    icao_code = plane_data["icao"]
    first_flight_date = plane_data["first_flight_date"]

    # get flight data in form of list of src coord, dst coord tuples
    list_of_flights = fetch_flight_data(icao_code, first_flight_date, halfway)
    list_of_flight_distances = calc_flight_distance(list_of_flights)

    conn = sqlite3.connect('celebrity_airplane.db')
    cursor = conn.cursor()
    for flight_distance in list_of_flight_distances:
        print(f"Inserting flight distance {flight_distance} for {tail_number}")
        cursor.execute(
            """
                INSERT INTO Flights (distance, celeb_id)
                VALUES (?, ?)
            """, (flight_distance, celeb_id)
        )
    conn.commit()


def main(new_flag, run_count, halfway):
    """Main function"""

    if new_flag == "new":
        print("Starting up")
        # all these things only need to be done once upon starting up
        init_db()
        # will get all data and add it to our db
        finish_web_scrape()

    # collect all data to add to db
    if halfway == "halfway":
        halfway = True
    else:
        halfway = False
    build_up_db(run_count, halfway)

    if new_flag == "done":
        process_data_and_calc()


if __name__ == "__main__":
    # Check if a parameter was provided
    if len(sys.argv) > 1:
        new_flag = sys.argv[1]  
        run_count = sys.argv[2]
        halfway = sys.argv[3]
        main(new_flag, run_count, halfway)
    else:
        print("Please provide two parameters!")