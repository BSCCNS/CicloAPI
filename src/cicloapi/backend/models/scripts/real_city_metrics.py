#config
from pathlib import Path
from cicloapi.backend.models.scripts.path import PATH
debug = True

# System
import os
import pickle
import warnings
from tqdm import tqdm
import logging
import copy
from typing import Dict, Union

# Network
import igraph as ig
from shapely.geometry import Polygon

# Local
from cicloapi.backend.models.scripts.functions import csv_to_ig, calculate_metrics_parallel, delete_overlaps, intersect_igraphs, calculate_metrics_additively, write_result
from cicloapi.backend.models.parameters.parameters import  prune_measure, networktypes, buffer_walk, numnodepairs

# Configure logging
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)
console_handler = logging.StreamHandler()
console_handler.setLevel(logging.INFO)
formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
console_handler.setFormatter(formatter)
logger.addHandler(console_handler)

logger = logging.getLogger("uvicorn.error")

def main(
    PATH: str,
    task_id: str,
    cities: Dict[str, Dict[str, Union[str, None]]]
    )-> None:
    """
    Main function to analyze existing infrastructure and calculate metrics for given cities.

    Args:
    PATH (dict): Dictionary containing paths for data and output.
    task_id (str): Task identifier.
    cities (dict): Dictionary containing city information.

    Returns:
    None
    """
    warnings.filterwarnings('ignore')
    rerun_existing = True
    path_output = Path(PATH["task_output"])

    for placeid, placeinfo in cities.items():
        logger.info(f"{placeid}: Analyzing existing infrastructure.")
    
        # Filename check
        filename = f"{placeid}_{prune_measure}.pickle"
        rerun_check = rerun_existing or not os.path.isfile(PATH["results"] + placeid + "/" + filename)

        if rerun_check:
            empty_metrics = {
            "length": 0,
            "length_lcc": 0,
            "coverage": 0,
            "directness": 0,
            "directness_lcc": 0,
            "poi_coverage": 0,
            "components": 0,
            "efficiency_global": 0,
            "efficiency_local": 0,
            "efficiency_global_routed": 0,
            "efficiency_local_routed": 0,
            "directness_lcc_linkwise": 0,
            "directness_all_linkwise": 0
            }
            output_place = {networktype: copy.deepcopy(empty_metrics) for networktype in networktypes}

            # Analyze all networks
            Gs = {}
            for networktype in networktypes:
                logger.info(f"{placeid}: Processing network type: {networktype}")
                if networktype not in ["biketrack_onstreet", "bikeable_offstreet"]:
                    Gs[networktype] = csv_to_ig(PATH["data"] / placeid, placeid, networktype)
                    Gs[networktype + "_simplified"] = csv_to_ig(PATH["data"] / placeid, placeid, networktype + "_simplified")
                elif networktype == "biketrack_onstreet":
                    Gs[networktype] = intersect_igraphs(Gs["biketrack"], Gs["carall"])
                    Gs[networktype + "_simplified"] = intersect_igraphs(Gs["biketrack_simplified"], Gs["carall_simplified"])
                elif networktype == "bikeable_offstreet":
                    G_temp = copy.deepcopy(Gs["bikeable"])
                    delete_overlaps(G_temp, Gs["carall"])
                    Gs[networktype] = G_temp
                    G_temp = copy.deepcopy(Gs["bikeable_simplified"])
                    delete_overlaps(G_temp, Gs["carall_simplified"])
                    Gs[networktype + "_simplified"] = G_temp

            # Load POIs
            logger.info(f"{placeid}: Loading POIs")

            with open(Path(path_output) / task_id / f"{placeid}_nnids_sliders.csv") as f:
                nnids = [int(line.rstrip()) for line in f]

            # Metrics calculation
            covs = {}
            for networktype in tqdm(networktypes, desc="Networks", leave=False):
                logger.info(f"{placeid}: Analyzing results: {networktype}")
                metrics, cov = calculate_metrics_parallel(Gs[networktype], Gs[networktype + "_simplified"], Gs['carall'], nnids, empty_metrics, buffer_walk, numnodepairs, debug)
                for key, val in metrics.items():
                    output_place[networktype][key] = val
                covs[networktype] = cov

            # Save covers
            logger.info(f"{placeid}: Saving covers")
            print(covs)
            write_result(path_output, task_id, covs, "pickle", placeid, "", "existing_covers.pickle")

            # Write to CSV
            logger.info(f"{placeid}: Writing results to CSV")
            print(output_place)
            write_result(path_output, task_id, output_place, "dictnested", placeid, "", "existing.csv", empty_metrics)

if __name__ == "__main__":
    main()