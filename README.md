# tsp_optimizer.py: Offline Route Optimizer

## Overview
This is a simple tool for planning travel routes between cities in the United States. It uses a popular method called the **Nearest Neighbor heuristic** to estimate the shortest round-trip route.

## What it Does
- Calculates travel distance between cities using the **Haversine formula**, which measures distances on Earth using latitude and longitude.
- Lets you choose between:
  1. **Interactive mode** – You enter city names yourself.
  2. **Fixed list mode** – Uses a built-in list of 20 major U.S. cities.

## How to Use
1. Run the program in a Python environment.
2. Choose a mode:
   - Press `1` for interactive mode (add cities manually).
   - Press `2` to use all 20 preloaded cities automatically.
3. Choose which city to start from.
4. The tool will print:
   - An ordered list of travel steps.
   - Distance between each step.
   - Total distance of the full loop (in miles).

## Disclaimer
- This program does **not** use maps or the internet (except for geocoding if you use interactive mode).
- It does **not** find the perfect route—just a good one based on proximity.
- This tool uses the **Nearest Neighbor heuristic**, which does **not** guarantee the optimal route.
- Geocoding (in Interactive mode) depends on an online service and may occasionally return innacurate
- This is meant for **educational or rough planning purposes**, not for real world navigation or logistics.



**
## Requirements
- Python 3.13
- Packages: `pandas`, `geopy`

Run it by typing:
```bash
python tsp_optimizer.py
```

Enjoy planning smarter road trips!
