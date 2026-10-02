import math
from typing import List, Dict, Tuple, Optional
from ortools.constraint_solver import pywrapcp, routing_enums_pb2


# Controlled AgroFlow MVP Locations & Coordinates (Maharashtra region)
AGROFLOW_LOCATIONS: Dict[str, Dict[str, float | str]] = {
    "Ratnagiri": {
        "city": "Ratnagiri",
        "latitude": 16.9902,
        "longitude": 73.3120,
        "description": "Ratnagiri Orchard & Cold Storage Hub"
    },
    "Pune": {
        "city": "Pune",
        "latitude": 18.5204,
        "longitude": 73.8567,
        "description": "Pune Regional Hub & Organic Processing Facility"
    },
    "Mumbai": {
        "city": "Mumbai",
        "latitude": 19.0760,
        "longitude": 72.8777,
        "description": "Mumbai Central Cold Storage & Retail Hub"
    },
    "Navi Mumbai": {
        "city": "Navi Mumbai",
        "latitude": 19.0330,
        "longitude": 73.0297,
        "description": "Navi Mumbai APMC Wholesale Distribution Depot"
    },
    "Thane": {
        "city": "Thane",
        "latitude": 19.2183,
        "longitude": 72.9781,
        "description": "Thane Logistics & Distribution Hub"
    },
    "Nashik": {
        "city": "Nashik",
        "latitude": 20.0059,
        "longitude": 73.7898,
        "description": "Nashik Grape & Produce Cold Storage Depot"
    },
    "Nagpur": {
        "city": "Nagpur",
        "latitude": 21.1458,
        "longitude": 79.0882,
        "description": "Nagpur Citrus & Regional Collection Hub"
    },
    "Satara": {
        "city": "Satara",
        "latitude": 17.6805,
        "longitude": 74.0183,
        "description": "Satara Produce Collection & Packing Station"
    },
    "Kolhapur": {
        "city": "Kolhapur",
        "latitude": 16.7050,
        "longitude": 74.2433,
        "description": "Kolhapur Agro Processing & Cold Fleet Depot"
    }
}

# Alias mapping for fuzzy matching common facility text strings to known cities
LOCATION_ALIASES: Dict[str, str] = {
    "ratnagiri": "Ratnagiri",
    "pune": "Pune",
    "mumbai": "Mumbai",
    "navi mumbai": "Navi Mumbai",
    "vashi": "Navi Mumbai",
    "thane": "Thane",
    "nashik": "Nashik",
    "nagpur": "Nagpur",
    "satara": "Satara",
    "kolhapur": "Kolhapur",
    "freshmart": "Mumbai",
    "organic foods": "Navi Mumbai",
}


def resolve_location(name: str, latitude: Optional[float] = None, longitude: Optional[float] = None) -> Dict[str, float | str]:
    """
    Resolves a stop input into validated name, city, latitude, and longitude.
    If explicit latitude & longitude are supplied, uses those coordinates.
    Otherwise matches the string against AgroFlow controlled locations dictionary.
    """
    if latitude is not None and longitude is not None:
        return {
            "name": name,
            "city": name.split()[0] if name else "Custom Location",
            "latitude": float(latitude),
            "longitude": float(longitude)
        }

    clean_name = name.strip().lower()

    # Direct exact match
    for loc_key, loc_data in AGROFLOW_LOCATIONS.items():
        if loc_key.lower() == clean_name:
            return {
                "name": name,
                "city": loc_data["city"],
                "latitude": loc_data["latitude"],
                "longitude": loc_data["longitude"]
            }

    # Alias / substring search
    for alias, loc_key in LOCATION_ALIASES.items():
        if alias in clean_name:
            loc_data = AGROFLOW_LOCATIONS[loc_key]
            return {
                "name": name,
                "city": loc_data["city"],
                "latitude": loc_data["latitude"],
                "longitude": loc_data["longitude"]
            }

    # Keyword search across keys
    for loc_key, loc_data in AGROFLOW_LOCATIONS.items():
        if loc_key.lower() in clean_name:
            return {
                "name": name,
                "city": loc_data["city"],
                "latitude": loc_data["latitude"],
                "longitude": loc_data["longitude"]
            }

    raise ValueError(f"Location '{name}' could not be resolved to valid geographic coordinates.")


def haversine_distance_km(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    """
    Calculates great-circle distance between two geographic coordinates in kilometers.
    """
    R = 6371.0  # Earth's mean radius in kilometers
    dlat = math.radians(lat2 - lat1)
    dlon = math.radians(lon2 - lon1)
    a = (
        math.sin(dlat / 2) ** 2
        + math.cos(math.radians(lat1))
        * math.cos(math.radians(lat2))
        * math.sin(dlon / 2) ** 2
    )
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
    return R * c


def solve_route_optimization(
    resolved_stops: List[Dict[str, float | str]],
    start_index: int = 0,
    average_speed_kmh: float = 50.0
) -> Dict:
    """
    Uses Google OR-Tools Routing Solver to determine the optimal visit sequence (TSP)
    for a list of resolved delivery stops.
    """
    num_stops = len(resolved_stops)
    if num_stops < 2:
        raise ValueError("At least 2 stops are required for route optimization.")

    if start_index < 0 or start_index >= num_stops:
        start_index = 0

    # Build integer distance matrix in meters for OR-Tools
    distance_matrix: List[List[int]] = []
    for i in range(num_stops):
        row = []
        for j in range(num_stops):
            if i == j:
                row.append(0)
            else:
                dist_km = haversine_distance_km(
                    resolved_stops[i]["latitude"],
                    resolved_stops[i]["longitude"],
                    resolved_stops[j]["latitude"],
                    resolved_stops[j]["longitude"]
                )
                row.append(int(dist_km * 1000))  # Convert to meters
        distance_matrix.append(row)

    # Initialize OR-Tools Routing Model
    manager = pywrapcp.RoutingIndexManager(num_stops, 1, start_index)
    routing = pywrapcp.RoutingModel(manager)

    def distance_callback(from_index: int, to_index: int) -> int:
        from_node = manager.IndexToNode(from_index)
        to_node = manager.IndexToNode(to_index)
        return distance_matrix[from_node][to_node]

    transit_callback_index = routing.RegisterTransitCallback(distance_callback)
    routing.SetArcCostEvaluatorOfAllVehicles(transit_callback_index)

    # Search parameters
    search_parameters = pywrapcp.DefaultRoutingSearchParameters()
    search_parameters.first_solution_strategy = (
        routing_enums_pb2.FirstSolutionStrategy.PATH_CHEAPEST_ARC
    )

    # Solve
    solution = routing.SolveWithParameters(search_parameters)

    ordered_indices: List[int] = []
    if solution:
        index = routing.Start(0)
        while not routing.IsEnd(index):
            node = manager.IndexToNode(index)
            ordered_indices.append(node)
            index = solution.Value(routing.NextVar(index))
        # Add the end node if not already present
        end_node = manager.IndexToNode(index)
        if end_node not in ordered_indices and end_node < num_stops:
            ordered_indices.append(end_node)
    else:
        # Fallback to original order if solver fails
        ordered_indices = list(range(num_stops))

    # Construct optimized route details & legs
    optimized_route = []
    legs = []
    total_distance_km = 0.0
    total_duration_minutes = 0

    for idx, stop_idx in enumerate(ordered_indices):
        stop_data = resolved_stops[stop_idx]
        optimized_route.append({
            "sequence_index": idx,
            "name": stop_data["name"],
            "city": stop_data["city"],
            "latitude": stop_data["latitude"],
            "longitude": stop_data["longitude"],
            "is_start": (idx == 0)
        })

    for idx in range(len(optimized_route) - 1):
        curr_stop = optimized_route[idx]
        next_stop = optimized_route[idx + 1]

        leg_dist_km = haversine_distance_km(
            curr_stop["latitude"],
            curr_stop["longitude"],
            next_stop["latitude"],
            next_stop["longitude"]
        )
        leg_dist_km = round(leg_dist_km, 2)
        leg_duration_min = int(round((leg_dist_km / average_speed_kmh) * 60))

        total_distance_km += leg_dist_km
        total_duration_minutes += leg_duration_min

        legs.append({
            "leg_number": idx + 1,
            "from_stop": curr_stop["name"],
            "to_stop": next_stop["name"],
            "distance_km": leg_dist_km,
            "estimated_duration_minutes": leg_duration_min
        })

    total_distance_km = round(total_distance_km, 2)

    hours = total_duration_minutes // 60
    mins = total_duration_minutes % 60
    duration_str = f"{hours} hrs {mins} mins" if hours > 0 else f"{mins} mins"

    return {
        "optimized_route": optimized_route,
        "total_distance_km": total_distance_km,
        "estimated_duration_minutes": total_duration_minutes,
        "estimated_duration_formatted": duration_str,
        "average_speed_kmh": average_speed_kmh,
        "legs": legs,
        "algorithm": "Google OR-Tools TSP Solver (Path Cheapest Arc)",
        "disclaimer": "Distance and travel duration estimates are calculated using geographic Haversine distance at an assumed average vehicle speed of 50 km/h. No live GPS or real-time traffic data is used."
    }
