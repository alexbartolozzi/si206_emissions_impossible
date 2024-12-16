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
    conn = sqlite3.connect('celebrity_airplane.db')
    # vis 1: histogram of number of flights
    cursor = conn.cursor()
    cursor.execute(
        """
            SELECT name, COUNT(*)
            FROM Celebrity
            JOIN Flights ON Celebrity.id = Flights.celeb_id
            GROUP BY name
        """
    )
    celeb_flight_counts = cursor.fetchall()
    counts = []
    for celeb, count in celeb_flight_counts:
        counts.append(count)
    plt.hist(counts, bins='auto', edgecolor='black', color="green")
    plt.grid(axis='y', linestyle='--', linewidth=0.7, alpha=0.7)
    plt.title("Number of Flights per Celebrity")
    plt.xlabel("Number of Flights")
    plt.ylabel("Number of Celebrities")
    plt.savefig("flights_per_celeb.png")
    plt.show()

    # vis 2: bar chart top 5 celebs x axis, y axis emissions 
    cursor.execute(
        """
            SELECT name, SUM(distance)
            FROM Celebrity
            JOIN Flights ON Celebrity.id = Flights.celeb_id
            GROUP BY name
            ORDER BY SUM(distance) DESC
            LIMIT 5
        """
    )
    top_5_celeb_emissions = cursor.fetchall()
    # calculate emissions from distance
    # assume 0.002353 Liters per meter of flight
    # assume 2.52 kg of CO₂ per Liter of Jet Fuel
    emissions_list = []
    for celeb, distance in top_5_celeb_emissions:
        fuel_burn = distance * 0.002353
        co2_emissions = fuel_burn * 2.52
        emissions_list.append((celeb, co2_emissions))
    
    celebs, emissions = zip(*emissions_list)

    # Define a simple custom palette for 5 items

    plt.bar(celebs, emissions, edgecolor='black', color="green")
    plt.title("Top 5 Celebrities by Emissions")
    plt.xlabel("Celebrity")
    plt.ylabel("Emissions (kg CO2)")
    plt.grid(axis='y', linestyle='--', linewidth=0.7, alpha=0.7)
    plt.savefig("top_5_celebs_emissions.png")
    plt.show()

    # vis 3: histogram of flight distance
    cursor.execute(
        """
            SELECT distance
            FROM Flights
        """
    )
    flight_distances = cursor.fetchall()
    distances = []
    for d in flight_distances:
        distances.append(d[0])
    plt.hist(distances, bins='auto', edgecolor='black', color="green")

    plt.title("Distribution of Flight Distances")
    plt.xlabel("Distance (m)")
    plt.ylabel("Number of Flights")
    plt.grid(axis='y', linestyle='--', linewidth=0.7, alpha=0.7)
    plt.savefig("flight_distances.png")
    plt.show()

    # part 4 output all data to json file
    cursor.execute(
        """
            SELECT name, plane_id
            FROM Celebrity
            JOIN Airplane ON Celebrity.plane_id = Airplane.id
        """
    )
    list_of_celebs = cursor.fetchall()
    celeb_data = {}
    for celeb, plane_id in list_of_celebs:
        cursor.execute(
            """
                SELECT distance
                FROM Flights
                WHERE celeb_id = ?
            """, (plane_id,)
        )
        flight_distances = cursor.fetchall()
        num_flights = len(flight_distances)
        total_distance = sum(d[0] for d in flight_distances)
        avg_distance = total_distance / num_flights if num_flights > 0 else 0
        max_dist = max(d[0] for d in flight_distances) if num_flights > 0 else 0
        min_dist = min(d[0] for d in flight_distances) if num_flights > 0 else 0
        total_emissions = total_distance * 0.002353 * 2.52
        celeb_data[celeb] = {
            "jet_name": plane_id,
            "total_emissions": total_emissions,
            "num_flights": num_flights,
            "avg_distance": avg_distance,
            "max_dist": max_dist,
            "min_dist": min_dist
        }
    with open("celeb_data.json", "w") as f:
        json.dump(celeb_data, f)


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