# config
from pathlib import Path
from cicloapi.backend.models.scripts.path import PATH

debug = True


# System
import logging
from tqdm import tqdm
from typing import Dict, Union

# Math/Data
import math
import numpy as np
import pandas as pd
from sklearn.cluster import AffinityPropagation
from sklearn.preprocessing import StandardScaler

# Plotting
import matplotlib.pyplot as plt

# Geo
import osmnx as ox

ox.settings.log_file = True
ox.settings.requests_timeout = 300
ox.settings.logs_folder = PATH["logs"]
import fiona
import shapely
from haversine import haversine
import geopandas as gpd
import pyproj
from shapely.geometry import Polygon
from tobler.util import h3fy

# Local
from cicloapi.backend.models.scripts.functions import (
    fill_holes,
    extract_relevant_polygon,
    csv_to_ox,
    convert_to_h3,
)
from cicloapi.backend.models.parameters.parameters import (
    sanidad,
    educacion,
    administracion,
    aprovisionamiento,
    cultura,
    deporte,
    transporte,
)

from cicloapi.database.database_models import SessionLocal
from cicloapi.database.db_methods import Database

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)
console_handler = logging.StreamHandler()
console_handler.setLevel(logging.INFO)
formatter = logging.Formatter("%(asctime)s - %(levelname)s - %(message)s")
console_handler.setFormatter(formatter)
logger.addHandler(console_handler)

logger = logging.getLogger("uvicorn.error")

# Example categories definition as a dictionary
categories = {
    "sanidad": sanidad,  # 'sanidad' should be a dictionary of POI types
    "educacion": educacion,
    "administracion": administracion,
    "aprovisionamiento": aprovisionamiento,
    "cultura": cultura,
    "deporte": deporte,
    "transporte": transporte,
}


def main(
    PATH: str,
    task_id: str,
    cities: Dict[str, Dict[str, Union[str, None]]],
    h3_zoom: int,
    snapthreshold: int,
    sanidad_slider: float,
    educacion_slider: float,
    administracion_slider: float,
    aprovisionamiento_slider: float,
    cultura_slider: float,
    deporte_slider: float,
    transporte_slider: float,
) -> None:
    """
    Process city data to generate H3 hexagons, analyze points of interest (POIs),
    and apply clustering for urban analysis.

    Args:
        PATH (str): Path to the base directory containing city data.
        cities (Dict[str, Dict[str, Union[str, None]]]): A dictionary where keys
            are place IDs and values are dictionaries containing city-specific metadata
            (e.g., Nominatim strings or shapefile paths).
        h3_zoom (int): H3 resolution level for generating hexagons.
        snapthreshold (int): Distance threshold in meters for snapping centroids
            to the nearest network nodes.
        sanidad_slider (float): Weight for the "sanidad" category POIs.
        educacion_slider (float): Weight for the "educacion" category POIs.
        administracion_slider (float): Weight for the "administracion" category POIs.
        aprovisionamiento_slider (float): Weight for the "aprovisionamiento" category POIs.
        cultura_slider (float): Weight for the "cultura" category POIs.
        deporte_slider (float): Weight for the "deporte" category POIs.
        transporte_slider (float): Weight for the "transporte" category POIs.

    Returns:
        None

    Raises:
        ValueError: If a category does not have a dictionary of POI types.
        Exception: If there is an error processing a city's geometry.

    Workflow:
        1. Load and preprocess city geometries (from Nominatim or shapefiles).
        2. Generate H3 hexagons for the city's region.
        3. Intersect hexagons with points of interest (POIs) for each category, applying
           category-specific weights.
        4. Perform clustering using Affinity Propagation based on POI density and
           location centroids.
        5. Snap exemplar centroids to the nearest nodes in the city's transport network
           within a defined threshold.

    Example Usage:
        main(
            PATH="path/to/data",
            cities={
                "city1": {"nominatimstring": "City, Country"},
                "city2": {"nominatimstring": None}
            },
            h3_zoom=8,
            snapthreshold=50,
            sanidad_slider=1.0,
            educacion_slider=1.2,
            administracion_slider=0.8,
            aprovisionamiento_slider=1.1,
            cultura_slider=1.0,
            deporte_slider=1.0,
            transporte_slider=1.0
        )
    """
    session = SessionLocal()
    database = Database(session)


    # Your loop and logic with logger
    for placeid, placeinfo in tqdm(cities.items(), desc="Cities"):
        logger.info(f"Processing city: {placeid}")
        logger.debug(f"Path for city {placeid}: {PATH}")

        # Print place information
        logger.info(f"{placeid}: Loading location polygon and generating H3 hexagons")

        ## grab polygon from prepare_pois.py
        # Check if 'nominatimstring' exists
        if placeinfo.get("nominatimstring"):
            logger.debug(f"Geocoding location: {placeinfo['nominatimstring']}")
            try:
                # Geocode to get the location geometry and extract relevant polygon
                location = ox.geocoder.geocode_to_gdf(placeinfo["nominatimstring"])
                location = fill_holes(
                    extract_relevant_polygon(placeid, location.geometry.iloc[0])
                )
            except Exception as e:
                logger.error(f"Error during geocoding for {placeid}: {e}")
                continue  # Skip to the next city if there is an error
        else:
            # If shapefile is available, read and extract geometry
            try:
                with fiona.open(f"../data/{placeid}/{placeid}.shp") as shp:
                    first = next(iter(shp))
                    try:
                        location = Polygon(
                            shapely.geometry.shape(first["geometry"])
                        )  # Handle if LineString is present
                    except Exception as e:
                        logger.error(f"Error processing geometry for {placeid}: {e}")
                        continue  # Skip to the next city if there is an error
            except Exception as e:
                logger.error(
                    f"Shapefile not found or error reading shapefile for {placeid}: {e}"
                )
                continue  # Skip to the next city if there is an error

        gdf_hex = convert_to_h3(location, h3_zoom)
        print(gdf_hex)

        # Example categories definition as a dictionary
        categories = {
            "sanidad": sanidad,
            "educacion": educacion,
            "administracion": administracion,
            "aprovisionamiento": aprovisionamiento,
            "cultura": cultura,
            "deporte": deporte,
            "transporte": transporte,
        }

        slider_weights = {
            "sanidad": sanidad_slider,
            "educacion": educacion_slider,
            "administracion": administracion_slider,
            "aprovisionamiento": aprovisionamiento_slider,
            "cultura": cultura_slider,
            "deporte": deporte_slider,
            "transporte": transporte_slider,
        }

        geodataframes = []

        # Process POIs and perform spatial operations
        for category_name, pois in categories.items():
            if not isinstance(pois, dict):  # Validate that 'pois' is a dictionary
                logger.error(
                    f"Expected dictionary for category '{category_name}', got {type(pois)}"
                )
                raise ValueError(
                    f"Expected dictionary for category '{category_name}', got {type(pois)}"
                )

            for poi_type in pois.keys():  # Loop through each POI type in the category
                poi_file = (
                    Path(PATH["data"]) / placeid / f"{placeid}_poi_{poi_type}.gpkg"
                )

                if poi_file.exists():
                    logger.info(f"Processing POI: {poi_type} for city {placeid}")
                    geo = gpd.read_file(poi_file)
                    geo["poi_source"] = poi_type  # Assign POI type (e.g., 'hospital')
                    geo["category"] = (
                        category_name  # Assign category name (e.g., 'sanidad')
                    )
                    geo["weight"] = slider_weights.get(
                        category_name, 1
                    )  # Assign slider weight
                    geodataframes.append(geo)  # Add to the list of GeoDataFrames
                else:
                    logger.warning(
                        f"POI file {poi_file} not found for city {placeid} and category {category_name}"
                    )

        # Combine all GeoDataFrames and perform spatial join
        if geodataframes:
            logger.info(
                f"Combining {len(geodataframes)} GeoDataFrames for city {placeid}"
            )
            combined_geo = gpd.GeoDataFrame(pd.concat(geodataframes, ignore_index=True))
            combined_geo = combined_geo.to_crs(gdf_hex.crs)

            # Perform spatial join
            hexagon_with_counts = gpd.sjoin(
                gdf_hex, combined_geo, how="inner", predicate="intersects"
            )

            # Apply weights to the point count
            hexagon_with_counts["weighted_count"] = hexagon_with_counts["weight"]

            # Aggregate weighted counts by hexagon
            hexagon_counts = (
                hexagon_with_counts.groupby("hex_id")["weighted_count"]
                .sum()
                .reset_index(name="weighted_point_count")
            )

            # Merge the weighted counts back with the original hexagons
            gdf_hex = gdf_hex.merge(hexagon_counts, on="hex_id", how="left").fillna(0)

            # Extract centroids and point_count
            gdf_hex["centroid"] = gdf_hex.geometry.centroid
            centroids = np.array([(geom.x, geom.y) for geom in gdf_hex["centroid"]])
            point_counts = gdf_hex["weighted_point_count"].values.reshape(-1, 1)

            # Standardize centroids and point_count
            scaler = StandardScaler()
            features = scaler.fit_transform(np.hstack([centroids, point_counts]))

            # Apply Affinity Propagation
            ap = AffinityPropagation(random_state=42).fit(features)
            gdf_hex["cluster"] = ap.labels_  # Assign cluster labels to hexagons

            # Identify exemplars and create exemplar label
            exemplars_indices = ap.cluster_centers_indices_
            gdf_hex["is_exemplar"] = 0  # Initialize all hexagons as non-exemplars
            gdf_hex.loc[exemplars_indices, "is_exemplar"] = 1  # Mark exemplars

            # Create the final dataframe keeping centroids and exemplar labels
            gdf_hex = gdf_hex[
                [   "hex_id",
                    "geometry",
                    "centroid",
                    "weighted_point_count",
                    "cluster",
                    "is_exemplar",
                ]
            ]
        else:
            logger.warning(f"No POI files found for city {placeid}")

        # Network processing
        logger.info(f"Processing network for city {placeid}")
        try:
            # It may need to execute the first cell first
            # Define the snapping threshold (in meters)
            snapthreshold = 100  # Adjust this value as needed

            # Initialize a set to store snapped node IDs
            nnids = set()
            G_caralls = {}
            G_caralls_simplified = {}
            locations = {}

            # Load network data
            G_caralls[placeid] = csv_to_ox(PATH["data"] / placeid, placeid, "carall")
            G_caralls[placeid].graph[
                "crs"
            ] = "epsg:4326"  # Assign CRS for OSMNX compatibility
            G_caralls_simplified[placeid] = csv_to_ox(
                PATH["data"] / placeid, placeid, "carall_simplified"
            )
            G_caralls_simplified[placeid].graph["crs"] = "epsg:4326"

            gdf = gpd.GeoDataFrame(
                gdf_hex[gdf_hex["is_exemplar"] == 1],
                geometry="centroid",
                crs="EPSG:4326",
            )
            gdf["db_centroid"] = gdf["centroid"].apply(lambda geom: geom.wkt)
            # Create a list to store node data into database
            node_data = []
            for idx, row in gdf.iterrows():
                node_data.append({
                    "hex_id": row["hex_id"],
                    "task_id": task_id,
                    "city_id": placeid,
                    "weighted_point_count": row["weighted_point_count"],
                    "cluster": row["cluster"],
                    "geometry": row["db_centroid"],  # geometry column is the centroid as defined 
                })


             # assumes DBMethods sets up the session
            Database.insert_simulation_nodes(database,node_data)

            G_carall = G_caralls[placeid]

            # Snap points to the nearest nodes in the network
            nnids = set()
            for g in gdf["centroid"]:
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

            nnids_file = (
                Path(PATH["task_output"]) / task_id / f"{placeid}_nnids_sliders.csv"
            )
            nnids_file.parent.mkdir(parents=True, exist_ok=True)
            df = pd.DataFrame({"nnid": list(nnids)})
            df.to_csv(nnids_file, index=False, header=False)

            logger.info(f"Saved snapped node IDs for {placeid} to {nnids_file}")

        except Exception as e:
            logger.error(f"Error processing network for {placeid}: {e}")


if __name__ == "__main__":
    main()
