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

from cicloapi.database.db_methods import create_connection, Database


def main(PATH, task_id, cities):
    """
    Main function to prepare Points of Interest (POIs) for given cities.

    Args:
        PATH (dict): Dictionary containing paths to data directories.
        cities (dict): Dictionary containing city information with place IDs as keys and place details as values.

    The function performs the following steps:
    1. Establishes a database connection.
    2. Loads carall graphs for each city in OSMNX format.
    3. Iterates through the cities to load location polygons and carall graphs.
    4. Geocodes the location geometry or reads shapefiles if available.
    5. Loads and assigns carall graphs for each city.
    6. Processes each POI parameter and extracts relevant geometries.
    7. Snaps points to the nearest nodes in the network.
    8. Saves nearest node IDs for POIs in a CSV file.
    9. Converts the GeoDataFrame to string type and saves locally.
    10. Prepares POI data for database insertion.
    11. Inserts POIs into the database.
    12. Closes the database connection.

    Raises:
        Exception: If any error occurs during the processing of POIs.
    """
    connection = create_connection()
    database = Database(connection)
    pois = []

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

                # Prepare POI data for database insertion
                created_at = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                for _, row in gdf.iterrows():
                    pois.append((
                        task_id,
                        placeid,
                        row.get("name", None),
                        poitag,
                        row.to_json(),
                        row["geometry"].wkt,
                        row.get("addr:postcode", None),
                        row.get("addr:street", None),
                        row.get("amenity", None),
                        row.get("network", None),
                        row.get("outdoor", None),
                        row.get("shelter_type", None),
                        row.get("addr:housenumber", None),
                        row.get("indoor", None),
                        created_at
                    ))

            except Exception as e:
                print(f"No {poiid} in {placeinfo}. No POIs created. Error: {e}")

            except Exception as e:
                print(f"No {poiid} in {placeinfo}. No POIs created. Error: {e}")

    # Insert POIs into the database
    database.insert_pois(pois)

    connection.close()

if __name__ == "__main__":
    main()
