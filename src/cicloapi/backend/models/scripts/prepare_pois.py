# config
from cicloapi.backend.models.scripts.path import PATH

debug = False

# System
from tqdm.notebook import tqdm
from tqdm import tqdm


# Geo
import osmnx as ox

ox.settings.log_file = True
ox.settings.requests_timeout = 300
ox.settings.logs_folder = PATH["logs"]
import fiona
import shapely
from haversine import haversine
from shapely.geometry import Polygon

# Local

from cicloapi.backend.models.scripts.functions import (
    fill_holes,
    extract_relevant_polygon,
    csv_to_ox,
)
from cicloapi.backend.models.parameters.parameters import poiparameters, snapthreshold


def main(PATH, cities):
    # Load all carall graphs in OSMNX format
    G_caralls = {}
    G_caralls_simplified = {}
    locations = {}

    # Iterate through cities to load polygons and graphs
    for placeid, placeinfo in tqdm(cities.items(), desc="Cities"):

        print(f"{placeid}: Loading location polygon and carall graph")

        # Check if 'nominatimstring' exists
        if placeinfo["nominatimstring"]:
            # Geocode to get the location geometry and extract relevant polygon
            location = ox.geocoder.geocode_to_gdf(placeinfo["nominatimstring"])
            location = fill_holes(
                extract_relevant_polygon(
                    placeid, shapely.geometry.shape(location["geometry"][0])
                )
            )
        else:
            # If shapefile is available, read and extract geometry
            with fiona.open(PATH["data"] / placeid / f"{placeid}.shp") as shp:
                first = next(iter(shp))
                try:
                    location = Polygon(
                        shapely.geometry.shape(first["geometry"])
                    )  # Handle if LineString is present
                except:
                    location = shapely.geometry.shape(
                        first["geometry"]
                    )  # Otherwise, it's likely a polygon
        locations[placeid] = location

        # Load and assign carall graphs for each city
        G_caralls[placeid] = csv_to_ox(PATH["data"] / placeid, placeid, "carall")
        G_caralls[placeid].graph[
            "crs"
        ] = "epsg:4326"  # Assign CRS for OSMNX compatibility
        G_caralls_simplified[placeid] = csv_to_ox(
            PATH["data"] / placeid, placeid, "carall_simplified"
        )
        G_caralls_simplified[placeid].graph["crs"] = "epsg:4326"

        # Retrieve location geometry and simplified carall graph
    location = locations[placeid]
    G_carall = G_caralls[placeid]
    # Loop through POI parameters and process each tag
    for poiid, poitag in poiparameters.items():

        try:
            # Extract relevant geometries (Points only) from the location polygon
            gdf = ox.features.features_from_polygon(location, poitag)
            gdf = gdf[
                gdf["geometry"].type == "Point"
            ]  # Only consider Points (exclude polygons)

            # Snap points to the nearest nodes in the network
            nnids = set()
            for g in gdf["geometry"]:
                n = ox.distance.nearest_nodes(G_carall, g.x, g.y)
                # Only snap if within the defined threshold
                if (
                    n not in nnids
                    and haversine(
                        (g.y, g.x),
                        (G_carall.nodes[n]["y"], G_carall.nodes[n]["x"]),
                        unit="m",
                    )
                    <= snapthreshold
                ):
                    nnids.add(n)

            # Save nearest node ids for POIs in a CSV file
            output_file_path = (
                PATH["data"] / placeid / f"{placeid}_poi_{poiid}_nnidscarall.csv"
            )
            with output_file_path.open("w", newline="", encoding="utf-8") as f:
                for item in nnids:
                    f.write(f"{item}\n")

            # Convert the gdf to string type for writing, and save locally (if feasible)
            gdf = gdf.apply(
                lambda c: c.astype(str) if c.name != "geometry" else c, axis=0
            )
            try:
                gdf.to_file(
                    PATH["data"] / placeid / f"{placeid}_poi_{poiid}.gpkg",
                    driver="GPKG",
                )
            except:
                print(f"Notice: Writing the gdf did not work for {placeid}")

            if debug:
                gdf.plot(color="red")

        except Exception as e:
            print(f"No {poiid} in {placeinfo}. No POIs created. Error: {e}")


if __name__ == "__main__":
    main()
