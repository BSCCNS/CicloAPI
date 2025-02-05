#config
from pathlib import Path
debug = False

#system
import logging

# Local
from cicloapi.backend.models.scripts.functions import csv_to_ig, write_result, mst_routing, greedy_triangulation_routing
from cicloapi.backend.models.parameters.parameters import poi_source, prune_quantiles

from pathlib import Path
from typing import Dict, Union


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
    cities: Dict[str, Dict[str, Union[str, None]]],
    prune_measure: str = "betweenness"
) -> None:
    """
    Generate bikelane networks for multiple cities and perform routing analysis.

    Args:
        PATH (Dict[str, Path]): Dictionary containing paths to data and output directories.
        task_id (str): Identifier for the current task.
        cities (Dict[str, Dict[str, str]]): Dictionary where keys are place IDs and values contain city metadata.

    Returns:
        None

    Workflow:
        1. Load transportation network for each city.
        2. Read node IDs used for routing.
        3. Generate routing results using greedy triangulation and MST methods.
        4. Store the results in pickle format.
    """
    
    for placeid, placeinfo in cities.items():
        logger.info(f"{placeid}: Generating networks")

        # Load transportation network
        G_carall = csv_to_ig(PATH["data"] / placeid, placeid, 'carall')
        
        # Load network nodes
        nnids_path = Path(PATH["task_output"]) / task_id / f"{placeid}_nnids_sliders.csv"
        with nnids_path.open() as f:
            nnids = [int(line.rstrip()) for line in f]
        
        # Generate routing results
        logger.info(f"{placeid}: Running greedy triangulation routing")
        GTs, GT_abstracts = greedy_triangulation_routing(G_carall, G_carall, nnids, prune_quantiles, prune_measure)
        
        logger.info(f"{placeid}: Running MST routing")
        MST, MST_abstract = mst_routing(G_carall, G_carall, nnids)

        # Store results
        results = {
            "placeid": placeid,
            "prune_measure": prune_measure,
            "poi_source": poi_source,
            "prune_quantiles": prune_quantiles,
            "GTs": GTs,
            "GT_abstracts": GT_abstracts,
            "MST": MST,
            "MST_abstract": MST_abstract
        }

        path_output = PATH["task_output"]
        logger.info(f"{placeid}: Writing results to geojson and pickle")
        write_result(path_output, task_id, results, "pickle", placeid, prune_measure, ".pickle")
        write_result(path_output, task_id, results, "geojson", placeid, prune_measure, ".geojson")

if __name__ == "__main__":
    main()