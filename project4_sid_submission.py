import math
import itertools

# --- Fixed city list ---
cities = {
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
    "Washington, DC": (38.9072, -77.0369)
}
city_names = list(cities.keys())

# --- Display numbered list ---
print("Select 3–10 cities by entering numbers separated by spaces. Type DONE to finish.\n")
for idx, name in enumerate(city_names):
    print(f"{idx + 1}. {name}")

# --- Get user input ---
selected = []
while True:
    raw = input("\nEnter city numbers (e.g. 1 4 9) or DONE: ").strip()
    if raw.lower() == "done":
        break
    try:
        nums = [int(n) - 1 for n in raw.split()]
        for i in nums:
            if 0 <= i < len(city_names):
                city = city_names[i]
                if city not in selected:
                    selected.append(city)
    except ValueError:
        print("Invalid input. Please enter numbers or 'DONE'.")

# --- Validate city count ---
if len(selected) < 3 or len(selected) > 10:
    print("\n⚠ You must select between 3 and 10 cities.")
    exit()

# --- Haversine formula ---
def haversine(coord1, coord2):
    R = 6371.0
    lat1, lon1 = coord1
    lat2, lon2 = coord2
    phi1, phi2 = math.radians(lat1), math.radians(lat2)
    dphi = math.radians(lat2 - lat1)
    dlambda = math.radians(lon2 - lon1)
    a = math.sin(dphi / 2)**2 + math.cos(phi1) * math.cos(phi2) * math.sin(dlambda / 2)**2
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
    return R * c

# --- Brute-force TSP ---
min_distance = float("inf")
best_path = None

for perm in itertools.permutations(selected):
    total = 0
    for i in range(len(perm) - 1):
        total += haversine(cities[perm[i]], cities[perm[i + 1]])
    total += haversine(cities[perm[-1]], cities[perm[0]])  # round trip
    if total < min_distance:
        min_distance = total
        best_path = perm

# --- Output results ---
print("\n Optimal route:")
for city in best_path:
    print(f"→ {city}")
print(f"→ {best_path[0]} (return to start)")
print(f"\n📏 Total distance: {min_distance:.2f} km")
