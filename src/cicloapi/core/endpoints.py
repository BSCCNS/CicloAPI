# endpoints.py

from fastapi import HTTPException, APIRouter
from cicloapi.schemas import schemas
import asyncio
import logging
from fastapi.responses import FileResponse
import datetime
import uuid
import os


## model imports

import sys
from pathlib import Path

# Add the 'backend' directory to the module search path
sys.path.append(str(Path(__file__).resolve().parents[1]))


from cicloapi.backend.models.scripts import (
    path,
    prepare_networks,
    prepare_pois,
    cluster_pois,
    poi_based_generation,
    analyze_results,
    real_city_metrics,
)
from cicloapi.backend.models.parameters.parameters import snapthreshold
from cicloapi.database.db_methods import create_connection, Database

current_working_directory = os.getcwd()

logger = logging.getLogger("uvicorn.error")
tasks = {}

def after_task_done(task, task_id):
        tasks[task_id].status = 'Completed'

router = APIRouter()
###########
# ENDPOINTS
###########

# Endpoint to setup the city (downloads OSM data)
@router.post(
    "/city_setup",
    summary="Setup the app for a given city.",
)
async def city_setup(input: schemas.InputCity):
    """
    Starts the execution of a task setting up the model for a given city, downloading all neccessary files.
    """

    task_id = str(uuid.uuid4())  # Generate a unique ID for the task
    logger.info(f"Starting run with task ID: {task_id}")

    PATH = path.PATH
    for subfolder in [
        "data",
        "plots",
        "plots_networks",
        "results",
        "exports",
        "exports_json",
        "videos",
    ]:
        for key in input.city.keys():
            placepath = PATH[subfolder] / key
            placepath.mkdir(parents=True, exist_ok=True)
            #print(f"Successfully created folder {placepath}")

    async def setup_task(task_id):
        try:
            # Extract parameters
            PATH = path.PATH

            connection = create_connection()
            database = Database(connection)
            # Execute workflow
            
            # Create table if not exists
            database.create_task_poi_table()

            logger.info("Running - Preparing networks")
            await asyncio.to_thread(prepare_networks.main, PATH, input.city)  # Runs first

            logger.info("Running - Preparing POIs")
            await asyncio.to_thread(prepare_pois.main, PATH, task_id, input.city)

            logger.info(f"Run with task ID: {task_id} finished")
        except asyncio.CancelledError:
            logger.info(f"Run with task ID: {task_id} cancelled")
            raise  # Propagate the cancellation exception

    time = str(datetime.datetime.now())
    
    
    task = asyncio.create_task(setup_task(task_id))
    task_ob = schemas.ModelTask(task=task, 
                                start_time=time, 
                                type = 'City_setup',
                                city = input.city
                                )
    tasks[task_id] = task_ob
    task.add_done_callback(lambda t: after_task_done(t, task_id))
    return {"task_id": task_id}


#######################
#######################


# Endpoint to run the task
@router.post("/run", summary="Compute an extension of the bicycle network.")
async def run_model(input: schemas.InputData):
    """
    Starts execution of a model task.
    """

    task_id = str(uuid.uuid4())  # Generate a unique ID for the task
    logger.info(f"Starting run with task ID: {task_id}")

    async def model_task(task_id):
        try:
            # Extract parameters
            PATH = path.PATH
            sliders = input.sliders

            logger.info("Running - Clustering POIs")
            await asyncio.to_thread(cluster_pois.main,
                PATH,
                task_id,
                input.city,
                input.h3_zoom,
                snapthreshold,
                sliders["sanidad"],
                sliders["educacion"],
                sliders["administracion"],
                sliders["aprovisionamiento"],
                sliders["cultura"],
                sliders["deporte"],
                sliders["transporte"],
            )

            await asyncio.to_thread(poi_based_generation.main, PATH, task_id, input.city, input.prune_measure)

            logger.info(f"Run with task ID: {task_id} finished")
            tasks[task_id].status = 'Completed'
        except asyncio.CancelledError:
            logger.info(f"Run with task ID: {task_id} cancelled")
            raise  # Propagate the cancellation exception

    time = str(datetime.datetime.now())
    task = asyncio.create_task(model_task(task_id))
    task_ob = schemas.PruneTask(task=task, 
                                start_time=time,
                                type = 'Model_task',
                                city = input.city,
                                prune_measure = input.prune_measure
                                )
    tasks[task_id] = task_ob
    task.add_done_callback(lambda t: after_task_done(t, task_id))
    return {"task_id": task_id}


#####################
#####################


@router.post(
    "/city_metrics",
    summary="Compute the metrics for the current city network.",
)
async def run_analysis(input: schemas.InputResults):
    """
    Starts a task computing the metrics for given run and city at a stage specified by the input.
    """

    task_id = str(uuid.uuid4())  # Generate a unique ID for the task
    logger.info(f"Starting run with task ID: {task_id}")

    logger.info(f"Starting analysis with task ID: {task_id}")

    async def analysis_task(task_id):
        try:
            # Extract parameters
            PATH = path.PATH
            cities = input.city

            logger.info("Running - Analyzing Metrics")
            await asyncio.to_thread(real_city_metrics.main, PATH, input.task_id, cities)

            logger.info(f"Analysis with task ID: {task_id} finished")
           

        except asyncio.CancelledError:
            logger.info(f"Analysis with task ID: {task_id} cancelled")
            raise  # Propagate the cancellation exception

    

    time = str(datetime.datetime.now())
    task = asyncio.create_task(analysis_task(task_id))
    task.add_done_callback(lambda t: after_task_done(t, task_id))
    task_ob = schemas.ModelTask(task=task, 
                                start_time=time,
                                type = 'Metrics_task',
                                city = input.city
                                )
    tasks[task_id] = task_ob
    task.add_done_callback(lambda t: after_task_done(t, task_id))
    return {"task_id": task_id}


#######################
#######################


@router.post("/run_analysis", summary="?????")
async def run_analysis(input: schemas.InputResults):
    """
    Starts execution of an analysis task. (Roger, check this, please)
    Parameters:
        input (InputResults): Input parameters for the analysis.
    Return:
        (JSON): ID of the task.
    """

    task_id = str(uuid.uuid4())  # Generate a unique ID for the task
    logger.info(f"Starting run with task ID: {task_id}")

    logger.info(f"Starting analysis with task ID: {task_id}")

    async def analysis_task(task_id):
        try:
            # Extract parameters
            PATH = path.PATH
            cities = input.city

            logger.info("Running - Analyzing Metrics")
            await asyncio.to_thread(analyze_results.main, PATH, input.task_id, cities, prune_index=input.phase)


            logger.info(f"Analysis with task ID: {task_id} finished")
            tasks[task_id].status = 'Completed'

        except asyncio.CancelledError:
            logger.info(f"Analysis with task ID: {task_id} cancelled")
            raise  # Propagate the cancellation exception

    time = str(datetime.datetime.now())
    task = asyncio.create_task(analysis_task(task_id))
    task_ob = schemas.ModelTask(task=task, 
                                start_time=time,
                                type = 'Analysis_task',
                                city = input.city
                                )
    tasks[task_id] = task_ob
    task.add_done_callback(lambda t: after_task_done(t, task_id))
    return {"task_id": task_id}


#######################
#######################

# Endpoint to download the map


@router.get("/map/{task_id}", summary="Download the geographic data of the network.")
async def download_map(task_id: str):
    """
    Streams the download of the map stored in disk for the task with ID equal to task_id.
    """
    PATH = path.PATH

    task_ob = tasks.get(task_id)
    if task_ob is None:
        raise HTTPException(status_code=404, detail="No task with ID " + task_id)

    suffix = ".geojson"
    city_key = list(task_ob.city.keys())[0]
    filename = f"{city_key}_{task_ob.prune_measure}{suffix}"

    # Use pathlib to construct the file path
    result_path = Path(PATH["task_output"]) / task_id / filename
    return FileResponse(result_path)


#######################
#######################


# Endpoint to check tasks running
@router.get("/list", summary="Query running and completed tasks.")
async def check_tasks():
    """
    Checks which tasks are being executed or finished in the backend.
    """

    return tasks


#####################
#####################


# Endpoint to stop the task
@router.delete("/stop/{task_id}", summary="Stop a running task.")
async def stop_model(task_id: str):
    """
    Stops a running task, provided its ID.
    """

    try:
        task_ob = tasks.get(task_id)
    except:
        raise HTTPException(status_code=404, detail="Task not found")

    task = task_ob.task

    if not task:
        raise HTTPException(status_code=404, detail="Task not found")

    if task.done():
        raise HTTPException(status_code=400, detail="Task already completed")

    task.cancel()  # Cancel the running task

    try:
        await task  # Wait for the task to handle the cancellation
    except asyncio.CancelledError:
        logger.info(f"Task {task_id} successfully cancelled")
    finally:
        tasks.pop(task_id, None)  # Clean up the task from the dictionary

    return {"status": "Task cancelled", "task_id": task_id}
