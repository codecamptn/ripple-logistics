# engine.py

# ===============================
# VEHICLES
# ===============================

VEHICLES = {
    "V1": {
        "capacity": 100,
        "broken": False
    },
    "V2": {
        "capacity": 100,
        "broken": False
    },
    "V3": {
        "capacity": 100,
        "broken": False
    },
    "V4": {
        "capacity": 60,
        "broken": False
    }
}


# ===============================
# DELIVERIES
# ===============================

DELIVERIES = [
    {
        "id": "D1",
        "name": "Hospital A",
        "vehicle": "V1",
        "priority": "P3",
        "load": 20,
        "eta": "09:10",
        "lat": 13.0105,
        "lng": 80.2209
    },
    {
        "id": "D2",
        "name": "Pharmacy A",
        "vehicle": "V1",
        "priority": "P2",
        "load": 15,
        "eta": "09:35",
        "lat": 13.0250,
        "lng": 80.2150
    },
    {
        "id": "D3",
        "name": "Retail A",
        "vehicle": "V1",
        "priority": "P1",
        "load": 20,
        "eta": "10:00",
        "lat": 13.0400,
        "lng": 80.2100
    },

    {
        "id": "D4",
        "name": "Hospital B",
        "vehicle": "V2",
        "priority": "P3",
        "load": 25,
        "eta": "09:20",
        "lat": 13.0550,
        "lng": 80.2250
    },
    {
        "id": "D5",
        "name": "Pharmacy B",
        "vehicle": "V2",
        "priority": "P2",
        "load": 20,
        "eta": "09:50",
        "lat": 13.0700,
        "lng": 80.2350
    },
    {
        "id": "D6",
        "name": "Retail B",
        "vehicle": "V2",
        "priority": "P1",
        "load": 15,
        "eta": "10:20",
        "lat": 13.0850,
        "lng": 80.2450
    },

    {
        "id": "D7",
        "name": "Hospital C",
        "vehicle": "V3",
        "priority": "P3",
        "load": 20,
        "eta": "09:15",
        "lat": 13.0200,
        "lng": 80.2500
    },
    {
        "id": "D8",
        "name": "Retail C",
        "vehicle": "V3",
        "priority": "P1",
        "load": 15,
        "eta": "09:45",
        "lat": 13.0350,
        "lng": 80.2600
    },
    {
        "id": "D9",
        "name": "Pharmacy C",
        "vehicle": "V3",
        "priority": "P2",
        "load": 20,
        "eta": "10:10",
        "lat": 13.0600,
        "lng": 80.2000
    },
    {
        "id": "D10",
        "name": "Retail D",
        "vehicle": "V3",
        "priority": "P1",
        "load": 15,
        "eta": "10:35",
        "lat": 13.0750,
        "lng": 80.1900
    },

    {
        "id": "D11",
        "name": "Hospital D",
        "vehicle": "V4",
        "priority": "P3",
        "load": 15,
        "eta": "09:25",
        "lat": 13.0450,
        "lng": 80.1750
    },
    {
        "id": "D12",
        "name": "Pharmacy D",
        "vehicle": "V4",
        "priority": "P2",
        "load": 15,
        "eta": "09:55",
        "lat": 13.0600,
        "lng": 80.1700
    },
    {
        "id": "D13",
        "name": "Retail E",
        "vehicle": "V4",
        "priority": "P1",
        "load": 10,
        "eta": "10:25",
        "lat": 13.0750,
        "lng": 80.1650
    }
]

# ===============================
# ROUTE ORDER
# ===============================

ROUTES = {
    "V1": ["D1", "D2", "D3"],
    "V2": ["D4", "D5", "D6"],
    "V3": ["D7", "D8", "D9", "D10"],
    "V4": ["D11", "D12", "D13"]
}


# ===============================
# DEPOT
# ===============================

DEPOT = {
    "id": "DEPOT",
    "name": "Guindy Depot",
    "lat": 13.0067,
    "lng": 80.2206
}


def get_baseline_plan():
    """
    Returns the original plan without any disruption.
    """

    return {
        "vehicles": VEHICLES,
        "deliveries": DELIVERIES,
        "routes": ROUTES,
        "depot": DEPOT
    }

import networkx as nx
import math


# ===============================
# DISRUPTION CONFIGURATION
# ===============================

ADYAR_BRIDGE = {
    "lat": 13.0067,
    "lng": 80.2572,
    "radius_km": 1.5
}


def distance_km(lat1, lng1, lat2, lng2):
    """
    Calculate approximate distance between two coordinates.
    """

    earth_radius_km = 6371.0

    lat1_rad = math.radians(lat1)
    lat2_rad = math.radians(lat2)

    delta_lat = math.radians(lat2 - lat1)
    delta_lng = math.radians(lng2 - lng1)

    a = (
        math.sin(delta_lat / 2) ** 2
        + math.cos(lat1_rad)
        * math.cos(lat2_rad)
        * math.sin(delta_lng / 2) ** 2
    )

    c = 2 * math.atan2(
        math.sqrt(a),
        math.sqrt(1 - a)
    )

    return earth_radius_km * c


def leg_touches_closure(stop_a, stop_b, closure):
    """
    Approximate whether a route leg passes through
    the disruption radius.

    We sample points between the two stops.
    """

    samples = 20

    for i in range(samples + 1):

        ratio = i / samples

        lat = (
            stop_a["lat"]
            + ratio * (stop_b["lat"] - stop_a["lat"])
        )

        lng = (
            stop_a["lng"]
            + ratio * (stop_b["lng"] - stop_a["lng"])
        )

        distance = distance_km(
            lat,
            lng,
            closure["lat"],
            closure["lng"]
        )

        if distance <= closure["radius_km"]:
            return True

    return False


def find_affected_legs(routes, deliveries, closure):
    """
    Find route legs that intersect the closure radius.
    """

    delivery_map = {
        delivery["id"]: delivery
        for delivery in deliveries
    }

    affected_legs = []

    for vehicle, stops in routes.items():

        previous_stop = None

        for stop_id in stops:

            current_stop = delivery_map[stop_id]

            if previous_stop is not None:

                if leg_touches_closure(
                    previous_stop,
                    current_stop,
                    closure
                ):

                    affected_legs.append({
                        "vehicle": vehicle,
                        "from": previous_stop["id"],
                        "to": current_stop["id"]
                    })

            previous_stop = current_stop

    return affected_legs


def build_dependency_graph(routes):
    """
    Build a dependency graph for each vehicle route.

    Example:
    D1 -> D2 -> D3
    """

    graph = nx.DiGraph()

    for vehicle, stops in routes.items():

        for stop in stops:
            graph.add_node(
                stop,
                vehicle=vehicle
            )

        for i in range(len(stops) - 1):

            current_stop = stops[i]
            next_stop = stops[i + 1]

            graph.add_edge(
                current_stop,
                next_stop,
                vehicle=vehicle
            )

    return graph


def get_downstream_stops(graph, stop_id):
    """
    Return all stops downstream from the given stop.
    """

    if stop_id not in graph:
        return []

    return list(nx.descendants(graph, stop_id))

if __name__ == "__main__":

    plan = get_baseline_plan()

    print("RIPPLE engine is working")
    print()
    print("Vehicles:", len(plan["vehicles"]))
    print("Deliveries:", len(plan["deliveries"]))
    print("Routes:", len(plan["routes"]))
    print("Depot:", plan["depot"]["name"])

    graph = build_dependency_graph(ROUTES)

    print()
    print("Dependency Test")
    print("D2 downstream:", get_downstream_stops(graph, "D2"))
    print("D5 downstream:", get_downstream_stops(graph, "D5"))
    print("D7 downstream:", get_downstream_stops(graph, "D7"))

    affected_legs = find_affected_legs(
        ROUTES,
        DELIVERIES,
        ADYAR_BRIDGE
    )

    print()
    print("Adyar Bridge Closure Test")

    for leg in affected_legs:
        print(
            leg["vehicle"],
            ":",
            leg["from"],
            "->",
            leg["to"]
        )