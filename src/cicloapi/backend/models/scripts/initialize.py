# config
from pathlib import Path
from cicloapi.backend.models.scripts.path import PATH

debug = False

# System
import csv
import os
import pprint

pp = pprint.PrettyPrinter(indent=4)


print("PATH:", PATH)
# Geo
import osmnx as ox

ox.settings.log_file = True
ox.settings.requests_timeout = 300
ox.settings.logs_folder = PATH["logs"]

# dict of placeid:placeinfo
# If a city has a proper shapefile through nominatim
# In case no (False), manual download of shapefile is necessary, see below

cities = {}
current_dir = os.getcwd()

with open(PATH["parameters"] / "cities.csv", mode="r", encoding="utf-8") as f:
    csvreader = csv.DictReader(f, delimiter=";")
    for row in csvreader:
        cities[row["placeid"]] = {}
        for field in csvreader.fieldnames[1:]:
            cities[row["placeid"]][field] = row[field]
if debug:
    print("\n\n=== Cities ===")
    pp.pprint(cities)
    print("==============\n\n")

# Create city subfolders
for placeid, placeinfo in cities.items():
    for subfolder in [
        "data",
        "plots",
        "plots_networks",
        "results",
        "exports",
        "exports_json",
        "videos",
    ]:
        placepath = PATH[subfolder] / placeid
        if not placepath.exists():
            placepath.mkdir(parents=True, exist_ok=True)
            print(f"Successfully created folder {placepath}")


print("Initialization complete.\n")
