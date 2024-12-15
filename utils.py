from datetime import datetime, timedelta
import math

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