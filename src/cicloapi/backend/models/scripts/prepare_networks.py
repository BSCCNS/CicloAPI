
#config
from backend.models.scripts.path import PATH
debug = False

# System
import csv
import os
import logging
from tqdm import tqdm

# Math/Data
import numpy as np

# Network
import networkx as nx

# Plotting
import matplotlib.pyplot as plt
from matplotlib import cm

# Geo
import osmnx as ox
ox.settings.log_file = True
ox.settings.requests_timeout = 300
ox.settings.logs_folder = PATH["logs"]
import fiona
import shapely

# Local
from backend.models.scripts.functions import fill_holes, extract_relevant_polygon, ox_to_csv, compress_file
from backend.models.parameters.parameters import  networktypes, osmnxparameters

# Configuración del logger
logging.basicConfig(
    format="%(asctime)s - %(levelname)s - %(message)s",
    level=logging.INFO  # Puedes cambiar a DEBUG para más detalles
)
logger = logging.getLogger("uvicorn.error")


def main(PATH, cities):
    logger.info("Starting network processing...")

    for placeid, placeinfo in tqdm(cities.items(), desc="Cities"):
        logger.info(f"Processing city: {placeid}")

        if placeinfo["nominatimstring"]:
            try:
                location = ox.geocoder.geocode_to_gdf(placeinfo["nominatimstring"])
                location = fill_holes(extract_relevant_polygon(placeid, shapely.geometry.shape(location['geometry'][0])))
            except Exception as e:
                logger.error(f"Error processing geocode for {placeid}: {e}")
                continue

            if debug:  # Draw location polygons and their holes
                try:
                    color = cm.rainbow(np.linspace(0, 1, len(location)))
                    for poly, c in zip(location, color):
                        plt.plot(*poly.exterior.xy, c=c)
                        for intr in poly.interiors:
                            plt.plot(*intr.xy, c="red")
                except Exception as e:
                    logger.warning(f"Error drawing location polygons for {placeid}: {e}")
                    plt.plot(*location.exterior.xy)
                plt.show()
        else:
            try:
                shp_path = os.path.join(PATH["data"], placeid, f"{placeid}.shp")
                shp = fiona.open(shp_path)
                first = next(iter(shp))
                location = shapely.geometry.shape(first['geometry'])
            except Exception as e:
                logger.error(f"Error loading shapefile for {placeid}: {e}")
                continue

        Gs = {}
        for parameterid, parameterinfo in tqdm(osmnxparameters.items(), desc="Networks", leave=False):
            logger.info(f"Processing network {parameterid} for {placeid}")

            for i in range(10):  # retry loop
                try:
                    Gs[parameterid] = ox.graph_from_polygon(
                        location,
                        network_type=parameterinfo['network_type'],
                        custom_filter=parameterinfo['custom_filter'],
                        retain_all=parameterinfo['retain_all'],
                        simplify=False
                    )
                    break  # Success, exit retry loop
                except ValueError:
                    Gs[parameterid] = nx.empty_graph(create_using=nx.MultiDiGraph)
                    logger.warning(f"{placeid}: No OSM data for graph {parameterid}. Created empty graph.")
                    break
                except (ConnectionError, UnboundLocalError):
                    logger.warning(f"Connection error or UnboundLocalError for {placeid}, retrying ({i+1}/10)...")
                    continue
                except Exception as e:
                    logger.error(f"Unexpected error in network {parameterid} for {placeid}: {e}, retrying ({i+1}/10)...")
                    continue

            if parameterinfo['export']:
                ox_to_csv(Gs[parameterid], PATH["data"] / placeid, placeid, parameterid)

        # Composing special cases
        try:
            Gs['biketrack'] = nx.compose_all([
                Gs['bike_cyclewaylefttrack'], Gs['bike_cyclewaytrack'],
                Gs['bike_highwaycycleway'], Gs['bike_bicycleroad'],
                Gs['bike_cyclewayrighttrack'], Gs['bike_designatedpath'],
                Gs['bike_cyclestreet']
            ])
            ox_to_csv(Gs['biketrack'], PATH["data"] / placeid, placeid, 'biketrack')

            Gs['bikeable'] = nx.compose_all([Gs['biketrack'], Gs['car30'], Gs['bike_livingstreet']])
            ox_to_csv(Gs['bikeable'], PATH["data"] / placeid, placeid, 'bikeable')

            Gs['biketrackcarall'] = nx.compose(Gs['biketrack'], Gs['carall'])
            ox_to_csv(Gs['biketrackcarall'], PATH["data"] / placeid, placeid, 'biketrackcarall')
        except KeyError as e:
            logger.error(f"Missing key during network composition for {placeid}: {e}")
        except Exception as e:
            logger.error(f"Unexpected error in network composition for {placeid}: {e}")

        # Simplify and save graphs
        for parameterid in networktypes[:-2]:
            try:
                ox_to_csv(ox.simplify_graph(Gs[parameterid]), PATH["data"] / placeid, placeid, parameterid, "_simplified")
            except Exception as e:
                logger.error(f"Error simplifying {parameterid} for {placeid}: {e}")

    # Compress all data files
    for folder, _, files in os.walk(PATH["data"]):
        for file in files:
            if file.endswith('es.csv'):
                try:
                    compress_file(folder, file.split(".")[0])
                except Exception as e:
                    logger.error(f"Error compressing {file} in {folder}: {e}")

    logger.info("Processing completed!")


if __name__ == "__main__":
    main()
