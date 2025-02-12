# config
from pathlib import Path
from cicloapi.backend.models.scripts.path import PATH

debug = True

# System
import os
import pickle
import warnings
import logging
import copy
from typing import Dict, Union

# Network
import igraph as ig
from shapely.geometry import Polygon

# Local
from cicloapi.backend.models.scripts.functions import (
    csv_to_ig,
    calculate_metrics_parallel,
    delete_overlaps,
    intersect_igraphs,
    calculate_metrics_additively,
    write_result,
)
from cicloapi.backend.models.parameters.parameters import (
    prune_measure,
    networktypes,
    buffer_walk,
    numnodepairs,
)

# Configure logging
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)
console_handler = logging.StreamHandler()
console_handler.setLevel(logging.INFO)
formatter = logging.Formatter("%(asctime)s - %(levelname)s - %(message)s")
console_handler.setFormatter(formatter)
logger.addHandler(console_handler)

logger = logging.getLogger("uvicorn.error")


def main(
    PATH: str,
    task_id: str,
    cities: Dict[str, Dict[str, Union[str, None]]],
    prune_index: list[int],
) -> None:
    """
    Main function to analyze existing infrastructure and calculate metrics for given cities.

    Args:
    PATH (dict): Dictionary containing paths for data and output.
    task_id (str): Task identifier.
    cities (dict): Dictionary containing city information.

    Returns:
    None
    """
    warnings.filterwarnings("ignore")
    rerun_existing = True
    path_output = Path(PATH["task_output"])

    for placeid, placeinfo in cities.items():
        logger.info(f"{placeid}: Analyzing existing infrastructure.")

        # Filename check
        filename = f"{placeid}_{prune_measure}.pickle"
        rerun_check = rerun_existing or not os.path.isfile(
            PATH["results"] + placeid + "/" + filename
        )

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
                "directness_all_linkwise": 0,
            }
            output_place = {
                networktype: copy.deepcopy(empty_metrics)
                for networktype in networktypes
            }

            # Analyze all networks
            Gs = {}
            for networktype in networktypes:
                logger.info(f"{placeid}: Processing network type: {networktype}")
                if networktype not in ["biketrack_onstreet", "bikeable_offstreet"]:
                    Gs[networktype] = csv_to_ig(
                        PATH["data"] / placeid, placeid, networktype
                    )
                    Gs[networktype + "_simplified"] = csv_to_ig(
                        PATH["data"] / placeid, placeid, networktype + "_simplified"
                    )
                elif networktype == "biketrack_onstreet":
                    Gs[networktype] = intersect_igraphs(Gs["biketrack"], Gs["carall"])
                    Gs[networktype + "_simplified"] = intersect_igraphs(
                        Gs["biketrack_simplified"], Gs["carall_simplified"]
                    )
                elif networktype == "bikeable_offstreet":
                    G_temp = copy.deepcopy(Gs["bikeable"])
                    delete_overlaps(G_temp, Gs["carall"])
                    Gs[networktype] = G_temp
                    G_temp = copy.deepcopy(Gs["bikeable_simplified"])
                    delete_overlaps(G_temp, Gs["carall_simplified"])
                    Gs[networktype + "_simplified"] = G_temp

            # Load POIs
            logger.info(f"{placeid}: Loading POIs")

            with open(
                Path(path_output) / task_id / f"{placeid}_nnids_sliders.csv"
            ) as f:
                nnids = [int(line.rstrip()) for line in f]

    for placeid, placeinfo in cities.items():
        logger.info(f"{placeid}: Analyzing results")

        G_carall = csv_to_ig(PATH["data"] / placeid, placeid, "carall")
        Gexisting = {
            networktype: csv_to_ig(PATH["data"] / placeid, placeid, networktype)
            for networktype in ["biketrack", "bikeable"]
        }

        # Load POIs
        logger.info(f"{placeid}: Loading POIs for results analysis")
        file_path = path_output / task_id / f"{placeid}_nnids_sliders.csv"
        with open(file_path) as f:
            nnids = [int(line.rstrip()) for line in f]

        # Load results
        logger.info(f"{placeid}: Loading results from pickle file")
        filename = f"{placeid}_{prune_measure}.pickle"
        resultfile_path = path_output / task_id / filename

        with open(resultfile_path, "rb") as resultfile:
            res = pickle.load(resultfile)

        # Calculate metrics
        logger.info(f"{placeid}: Calculating metrics additively")

        output, covs = calculate_metrics_additively(
            res["GTs"],
            res["GT_abstracts"],
            res["prune_quantiles"],
            G_carall,
            nnids,
            buffer_walk,
            numnodepairs,
            debug,
            True,
            Gexisting,
            selected_quantiles=[res["prune_quantiles"][i] for i in prune_index]
        )

        logger.info(f"{placeid}: Calculating metrics in parallel for MST")
        output_MST, cov_MST = calculate_metrics_parallel(
            res["MST"],
            res["MST_abstract"],
            G_carall,
            nnids,
            output,
            buffer_walk,
            numnodepairs,
            debug,
            True,
            ig.Graph(),
            Polygon(),
            False,
            Gexisting,
        )

        # Save the covers
        logger.info(f"{placeid}: Saving covers and MST covers")
        write_result(
            path_output,
            task_id,
            covs,
            "pickle",
            placeid,
            prune_measure,
            "_covers.pickle",
        )
        write_result(
            path_output,
            task_id,
            cov_MST,
            "pickle",
            placeid,
            prune_measure,
            "_cover_mst.pickle",
        )

        logger.info(f"{placeid}: Writing results to CSV and GeoJSON")

        write_result(
            path_output, task_id, output, "dict", placeid, prune_measure, ".csv"
        )
        write_result(path_output, task_id, output_MST, "dict", placeid, "", "mst.csv")

        write_result(
            path_output, task_id, output, "geojson", placeid, prune_measure, ".geojson"
        )
        write_result(
            path_output, task_id, output_MST, "geojson", placeid, "", "mst.geojson"
        )


if __name__ == "__main__":
    main()
