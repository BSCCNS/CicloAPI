# config
from pathlib import Path

debug = False

# system
import logging

# Local
from cicloapi.backend.models.scripts.functions import (
    csv_to_ig,
    write_result,
    mst_routing,
    greedy_triangulation_routing,
    ig_to_geojson
)
from cicloapi.backend.models.parameters.parameters import poi_source, prune_quantiles
from cicloapi.database.db_methods import Database
from cicloapi.database.database_models import SessionLocal

from pathlib import Path
from typing import Dict, Union
import igraph as ig
from shapely.geometry import shape, mapping

from shapely.geometry import LineString

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
    prune_measure: str = "betweenness",
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
    session = SessionLocal()
    database = Database(session)

    for placeid, placeinfo in cities.items():
        logger.info(f"{placeid}: Generating networks")

        # Load transportation network
        G_carall = csv_to_ig(PATH["data"] / placeid, placeid, "carall")

        # Load network nodes
        nnids_path = (
            Path(PATH["task_output"]) / task_id / f"{placeid}_nnids_sliders.csv"
        )
        with nnids_path.open() as f:
            nnids = [int(line.rstrip()) for line in f]

        # Generate routing results
        logger.info(f"{placeid}: Running greedy triangulation routing")
        GTs, GT_abstracts = greedy_triangulation_routing(
            G_carall, G_carall, nnids, prune_quantiles, prune_measure
        )

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
            "MST_abstract": MST_abstract,
        }

        path_output = PATH["task_output"]
        logger.info(f"{placeid}: Writing results to geojson and pickle")
        write_result(
            path_output, task_id, results, "pickle", placeid, prune_measure, ".pickle"
        )
        write_result(
            path_output, task_id, results, "geojson", placeid, prune_measure, ".geojson"
        )
        
        print("Starting conversion of results to geojson format...")
        geojson_data = {}
        for key, val in results.items():
            print(f"Processing key: {key}")
            if isinstance(val, list) and all(isinstance(item, ig.Graph) for item in val):
                new_geoms = []
                previous_geom = None
                for idx, (q, item) in enumerate(zip(results["prune_quantiles"], val)):
                    print(f"  Processing list item at index {idx} with quantile {q}")
                    current_geom_shapely = shape(ig_to_geojson(item))
                    if previous_geom is not None:
                        diff_geom = current_geom_shapely.difference(previous_geom)
                        print("    Performed difference with previous geometry")
                    else:
                        diff_geom = current_geom_shapely
                        print("    No previous geometry to subtract")
                    previous_geom = current_geom_shapely
                    
                    # Create segments with segment_id and linestring
                    if diff_geom.geom_type == "MultiLineString":
                        segments = []
                        for seg_id, seg in enumerate(diff_geom.geoms):
                            segments.append({
                                "segment_id": seg_id,
                                "linestring": mapping(seg),
                            })
                        new_geoms.append({
                            "prune_index": idx,
                            "quantile": q,
                            "segments": segments,
                        })
                    elif diff_geom.geom_type == "LineString":
                        new_geoms.append({
                            "prune_index": idx,
                            "quantile": q,
                            "segment_id": 0,
                            "linestring": mapping(diff_geom),
                        })
                    else:
                        # Fallback: store the whole geometry
                        new_geoms.append({
                            "prune_index": idx,
                            "quantile": q,
                            "geometry": mapping(diff_geom),
                        })
                geojson_data[key] = new_geoms
            elif isinstance(val, ig.Graph):
                print(f"  Converting igraph object for key: {key}")
                geojson_data[key] = {"geometry": ig_to_geojson(val)}
            else:
                print(f"  Assigning value for key: {key} without conversion")
                geojson_data[key] = val
        print("Completed geojson conversion:")


        segments_data = []
        for key, geoms in geojson_data.items():
            print(f"Processing key: {key}")
            if isinstance(geoms, list) and key in ["GTs"]:
                for item in geoms:
                    if "segments" in item:
                        for seg in item["segments"]:
                            wkt_geom = shape(seg["linestring"]).wkt
                            segments_data.append({
                                "task_id": task_id,
                                "city_id": placeid,
                                "prune_index": item["prune_index"],
                                "quantile": item["quantile"],
                                "geometry": wkt_geom,
                            })
                    elif "linestring" in item:
                        wkt_geom = shape(item["linestring"]).wkt
                        segments_data.append({
                            "task_id": task_id,
                            "city_id": placeid,
                            "prune_index": item["prune_index"],
                            "quantile": item["quantile"],
                            "geometry": wkt_geom,
                        })
                    elif "geometry" in item:
                        wkt_geom = shape(item["geometry"]).wkt
                        segments_data.append({
                            "task_id": task_id,
                            "city_id": placeid,
                            "prune_index": item["prune_index"],
                            "quantile": item["quantile"],
                            "geometry": wkt_geom,
                        })
                    else:
                        logger.error("No geometry found in item")
        print(segments_data)
        # Now insert segments_data into the database
        Database.insert_simulation_segments(database,segments_data)
            

if __name__ == "__main__":
    main()
