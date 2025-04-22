#!/usr/bin/env python3
"""
tsp_optimizer.py: Offline Route Optimizer
Provides two modes:
 1) Nearest-neighbor heuristic on an arbitrary city list (interactive).
 2) Nearest-neighbor heuristic on a fixed list of 20 major U.S. cities.
"""
import os
import time
import json
from typing import List, Dict, Tuple

import pandas as pd
from geopy.geocoders import Nominatim
from math import radians, sin, cos, sqrt, atan2

# ----- Configuration -----
CACHE_FILE = "geocode_cache.json"
GEOCODE_DELAY = 1.0  # seconds between geocode requests

# ----- Fixed list of 20 major U.S. cities -----
FIXED_CITIES: Dict[str, Tuple[float, float]] = {
    "New York, NY": (40.7128, -74.0060),
    "Los Angeles, CA": (34.0522, -118.2437),
    "Chicago, IL": (41.8781, -87.6298),
    "Houston, TX": (29.7604, -95.3698),
    "Phoenix, AZ": (33.4484, -112.0740),
    "Philadelphia, PA": (39.9526, -75.1652),
    "San Antonio, TX": (29.4241, -98.4936),
    "San Diego, CA": (32.7157, -117.1611),
    "Dallas, TX": (32.7767, -96.7970),
    "San Jose, CA": (37.3382, -121.8863),
    "Austin, TX": (30.2672, -97.7431),
    "Jacksonville, FL": (30.3322, -81.6557),
    "Fort Worth, TX": (32.7555, -97.3308),
    "Columbus, OH": (39.9612, -82.9988),
    "Charlotte, NC": (35.2271, -80.8431),
    "Indianapolis, IN": (39.7684, -86.1581),
    "San Francisco, CA": (37.7749, -122.4194),
    "Seattle, WA": (47.6062, -122.3321),
    "Denver, CO": (39.7392, -104.9903),
    "Washington, DC": (38.9072, -77.0369),
}

# ----- Geocoding cache -----
def load_cache() -> Dict[str, Tuple[float, float]]:
    if os.path.exists(CACHE_FILE):
        with open(CACHE_FILE, "r") as f:
            return json.load(f)
    return {}


def save_cache(cache: Dict[str, Tuple[float, float]]) -> None:
    with open(CACHE_FILE, "w") as f:
        json.dump(cache, f)


def geocode_city(name: str,
                 geolocator: Nominatim,
                 cache: Dict[str, Tuple[float, float]]) -> Tuple[float, float]:
    if name in cache:
        return cache[name]
    location = geolocator.geocode(name)
    if not location:
        raise ValueError(f"Could not geocode '{name}'")
    coords = (location.latitude, location.longitude)
    cache[name] = coords
    save_cache(cache)
    time.sleep(GEOCODE_DELAY)
    return coords

# ----- Distance calculation (Haversine) -----
def haversine(lat1: float, lon1: float,
              lat2: float, lon2: float) -> float:
    """
    Calculate great-circle distance between two points on Earth in miles.
    """
    R = 3958.8  # Earth's radius in miles
    dlat = radians(lat2 - lat1)
    dlon = radians(lon2 - lon1)
    a = sin(dlat/2)**2 + cos(radians(lat1)) * cos(radians(lat2)) * sin(dlon/2)**2
    c = 2 * atan2(sqrt(a), sqrt(1 - a))
    return R * c

# ----- Interactive arbitrary list mode -----
def get_city_list() -> List[Dict[str, object]]:
    geolocator = Nominatim(user_agent="offline_tsp")
    cache = load_cache()
    cities: List[Dict[str, object]] = []

    if os.path.exists("city_list.csv"):
        choice = input("1. New List\n2. Load Saved List\nChoose: ").strip()
    else:
        choice = "1"
    if choice == '2':
        df = pd.read_csv("city_list.csv")
        cities = df.to_dict('records')
        print("Loaded saved city list.")

    while True:
        print("\nCurrent City List:")
        for idx, city in enumerate(cities):
            print(f"{idx+1}. {city['name']}")
        action = input("1. Add City\n2. Remove City\n3. Continue\nChoose: ").strip()

        if action == '1':
            name = input("Enter city (City, State): ").strip()
            try:
                lat, lon = geocode_city(name, geolocator, cache)
                cities.append({'name': name, 'lat': lat, 'lon': lon})
                print(f"Added {name} → ({lat:.6f}, {lon:.6f})")
            except ValueError as e:
                print(e)

        elif action == '2':
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

        elif action == '3':
            save = input("Save this list to city_list.csv? (y/n): ").strip().lower()
            if save == 'y':
                pd.DataFrame(cities).to_csv("city_list.csv", index=False)
                print("City list saved.")
            break

        else:
            print("Invalid choice.")

    return cities

# ----- Fixed list mode uses all 20 cities -----
def get_preselected_list() -> List[Dict[str, object]]:
    # Automatically return all fixed cities without prompting
    return [
        {'name': name, 'lat': coords[0], 'lon': coords[1]}
        for name, coords in FIXED_CITIES.items()
    ]

# ----- Heuristic TSP solver -----
def solve_tsp(cities: List[Dict[str, object]], start_idx: int = 0) -> Tuple[List[int], float]:
    n = len(cities)
    visited = [False] * n
    route = [start_idx]
    visited[start_idx] = True
    total = 0.0
    while len(route) < n:
        last = route[-1]
        nearest, mind = None, float('inf')
        for i in range(n):
            if not visited[i]:
                d = haversine(cities[last]['lat'], cities[last]['lon'],
                              cities[i]['lat'], cities[i]['lon'])
                if d < mind:
                    mind, nearest = d, i
        if nearest is None:
            break
        visited[nearest] = True
        route.append(nearest)
        total += mind
    # return to start
    total += haversine(cities[route[-1]]['lat'], cities[route[-1]]['lon'],
                       cities[route[0]]['lat'], cities[route[0]]['lon'])
    route.append(route[0])
    return route, total

# ----- Print route -----
def print_route(cities: List[Dict[str, object]], route: List[int]) -> None:
    print("\nRoute (Heuristic):")
    print(f"{'City A':25} | {'City B':25} | Distance (mi)")
    print('-'*65)
    for i in range(len(route)-1):
        a, b = cities[route[i]], cities[route[i+1]]
        d = haversine(a['lat'], a['lon'], b['lat'], b['lon'])
        print(f"{a['name'][:25]:25} | {b['name'][:25]:25} | {d:10.1f}")

# ----- Main -----
def main():
    print("Welcome to the Offline Route Optimizer!")
    print("1. Heuristic mode (interactive)")
    print("2. Fixed list mode (20 cities)")
    mode = input("Choose mode: ").strip()
    if mode == '1':
        cities = get_city_list()
    elif mode == '2':
        cities = get_preselected_list()
    else:
        print("Invalid mode.")
        return

    for i, c in enumerate(cities):
        print(f"{i+1}. {c['name']}")
    start = input("Start from city number: ").strip()
    start_idx = int(start) - 1 if start.isdigit() and 0 <= int(start)-1 < len(cities) else 0
    route, total = solve_tsp(cities, start_idx)
    print_route(cities, route)
    print(f"\nTotal distance: {total:.1f} mi")

if __name__ == '__main__':
    main()
