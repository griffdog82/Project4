#!/usr/bin/env python3
"""
tsp_optimizer.py: Offline Route Optimizer
"""
import os
import time
import json
from typing import List, Dict, Tuple, Optional

import pandas as pd
from geopy.geocoders import Nominatim
from math import radians, sin, cos, sqrt, atan2

# ----- Configuration -----
CACHE_FILE = "geocode_cache.json"
GEOCODE_DELAY = 1.0  # seconds between geocode requests

# ----- Geocoding Cache -----
def load_cache() -> Dict[str, Tuple[float, float]]:
    if os.path.exists(CACHE_FILE):
        with open(CACHE_FILE, "r") as f:
            return json.load(f)
    return {}


def save_cache(cache: Dict[str, Tuple[float, float]]) -> None:
    with open(CACHE_FILE, "w") as f:
        json.dump(cache, f)


def geocode_city(name: str, geolocator, cache: Dict[str, Tuple[float, float]]) -> Tuple[float, float]:
    if name in cache:
        return cache[name]
    location = geolocator.geocode(name)
    if location is None:
        raise ValueError(f"Could not geocode '{name}'")
    coords = (location.latitude, location.longitude)
    cache[name] = coords
    save_cache(cache)
    time.sleep(GEOCODE_DELAY)
    return coords

# ----- Distance Calculation -----
def haversine(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    """
    Great-circle distance between two points (miles).
    """
    R = 3958.8  # Earth radius in miles
    dlat = radians(lat2 - lat1)
    dlon = radians(lon2 - lon1)
    a = sin(dlat/2)**2 + cos(radians(lat1))*cos(radians(lat2))*sin(dlon/2)**2
    c = 2 * atan2(sqrt(a), sqrt(1 - a))
    return R * c

# ----- User Interaction -----
def get_city_list() -> List[Dict[str, object]]:
    geolocator = Nominatim(user_agent="offline_tsp")
    cache = load_cache()
    cities: List[Dict[str, object]] = []

    if os.path.exists("city_list.csv"):
        choice = input("1. New List\n2. Load Saved List\nChoose: ").strip()
    else:
        choice = "1"
    if choice == "2":
        df = pd.read_csv("city_list.csv")
        cities = df.to_dict("records")
        print("Loaded saved city list.")

    while True:
        print("\nCurrent City List:")
        for idx, city in enumerate(cities):
            print(f"{idx+1}. {city['name']}")
        action = input("1. Add City\n2. Remove City\n3. Continue\nChoose: ").strip()

        if action == "1":
            name = input("Enter city (City, State): ").strip()
            try:
                lat, lon = geocode_city(name, geolocator, cache)
                cities.append({"name": name, "lat": lat, "lon": lon})
                print(f"Added {name} → ({lat:.6f}, {lon:.6f})")
            except ValueError as e:
                print(e)

        elif action == "2":
            idx = input("Enter city number to remove: ").strip()
            if idx.isdigit():
                i = int(idx) - 1
                if 0 <= i < len(cities):
                    removed = cities.pop(i)
                    print(f"Removed {removed['name']}")
                else:
                    print("Invalid index.")
            else:
                print("Please enter a number.")

        elif action == "3":
            save = input("Save this list to city_list.csv? (y/n): ").strip().lower()
            if save == "y":
                pd.DataFrame(cities).to_csv("city_list.csv", index=False)
                print("City list saved.")
            break

        else:
            print("Invalid choice.")

    return cities

# ----- TSP Solver -----
def solve_tsp(
    cities: List[Dict[str, object]],
    start_idx: int = 0,
    return_to_start: bool = True,
) -> Tuple[List[int], float]:
    n = len(cities)
    if not (0 <= start_idx < n):
        raise IndexError("start_idx out of range")

    visited = [False] * n
    route = [start_idx]
    visited[start_idx] = True
    total_distance = 0.0

    while len(route) < n:
        last = route[-1]
        nearest = None
        min_dist = float('inf')

        for i in range(n):
            if not visited[i]:
                dist = haversine(
                    cities[last]['lat'], cities[last]['lon'],
                    cities[i]['lat'], cities[i]['lon'],
                )
                if dist < min_dist:
                    min_dist = dist
                    nearest = i

        if nearest is None:
            raise ValueError("No reachable unvisited cities remain")

        visited[nearest] = True
        route.append(nearest)
        total_distance += min_dist

    if return_to_start:
        back = haversine(
            cities[route[-1]]['lat'], cities[route[-1]]['lon'],
            cities[start_idx]['lat'], cities[start_idx]['lon'],
        )
        route.append(start_idx)
        total_distance += back

    return route, total_distance

# ----- Output -----
def print_route(cities: List[Dict[str, object]], route: List[int]) -> None:
    print("\nOptimal Route (Nearest Neighbor Approximation):")
    print(f"{'City A':25} | {'City B':25} | {'Distance (mi)':>14}")
    print("-" * 70)
    for i in range(len(route) - 1):
        a = cities[route[i]]
        b = cities[route[i+1]]
        dist = haversine(a['lat'], a['lon'], b['lat'], b['lon'])
        print(f"{a['name'][:25]:25} | {b['name'][:25]:25} | {dist:14.1f}")

# ----- Main Guard -----
def main():
    print("Welcome to the Offline Route Optimizer!")
    cities = get_city_list()
    if len(cities) < 2:
        print("You need at least 2 cities.")
        return

    print("\nSelect starting city:")
    for idx, c in enumerate(cities):
        print(f"{idx+1}. {c['name']}")
    while True:
        choice = input("Enter number: ").strip()
        if choice.isdigit() and 1 <= int(choice) <= len(cities):
            start_idx = int(choice) - 1
            break
        print("Invalid selection.")

    route, total = solve_tsp(cities, start_idx)
    print_route(cities, route)
    print(f"\nEstimated Total Distance: {total:.1f} mi")

    save = input("Save results to CSV? (y/n): ").strip().lower()
    if save == 'y':
        records = []
        for i in range(len(route) - 1):
            a = cities[route[i]]
            b = cities[route[i+1]]
            dist = haversine(a['lat'], a['lon'], b['lat'], b['lon'])
            records.append({
                "City A": a['name'],
                "City B": b['name'],
                "Distance (mi)": round(dist, 1)
            })
        pd.DataFrame(records).to_csv("route_output.csv", index=False)
        print("Saved as route_output.csv")

if __name__ == "__main__":
    main()
