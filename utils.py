from datetime import datetime, timedelta
import math
import matplotlib.pyplot as plt
import json
import sqlite3

def gen_date_range(initial_date):
    """
    Returns a tuple of start and end timestamps 30 days apart.
    Adjusts the end timestamp if it exceeds the current time.
    """
    start_date = datetime.fromtimestamp(initial_date)
    
    end_date = start_date + timedelta(days=29)
    
    start_timestamp = initial_date
    end_timestamp = int(end_date.timestamp())
    
    done = False
    now_timestamp = int(datetime.now().timestamp())
    if end_timestamp > now_timestamp:
        done = True
        end_timestamp = now_timestamp
    
    return (start_timestamp, end_timestamp, done)

def calc_flight_distance(list_of_flight_src_dst_coords):
    """
    Calculate the flight distances between source and destination coordinates.

    Parameters:
    list_of_flight_src_dst_coords (list): A list of tuples, each containing:
        ((src_latitude, src_longitude), (dst_latitude, dst_longitude))

    Returns:
    list: A list of distances in meters between each source and destination.
    """
    def haversine(coord1, coord2):
        # Radius of Earth in meters
        R = 6371000
        # Convert latitude and longitude from degrees to radians
        lat1, lon1 = math.radians(coord1[0]), math.radians(coord1[1])
        lat2, lon2 = math.radians(coord2[0]), math.radians(coord2[1])
        
        # Haversine formula
        dlat = lat2 - lat1
        dlon = lon2 - lon1
        a = math.sin(dlat / 2)**2 + math.cos(lat1) * math.cos(lat2) * math.sin(dlon / 2)**2
        c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
        
        # Distance in meters
        distance = R * c
        return distance

    # Calculate distances for each pair of coordinates
    distances = []
    for src, dst in list_of_flight_src_dst_coords:
        distances.append(haversine(src, dst))
    
    return distances

def process_data_and_calc():
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