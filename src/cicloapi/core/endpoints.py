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


from cicloapi.backend.models.scripts import path, prepare_networks, prepare_pois, cluster_pois, poi_based_generation, analyze_results, real_city_metrics
from cicloapi.backend.models.parameters.parameters import snapthreshold

current_working_directory = os.getcwd()

logger = logging.getLogger('uvicorn.error')
tasks = {}

router = APIRouter()



###########
#ENDPOINTS
###########

# Endpoint to check tasks running
@router.get("/list")
async def check_tasks():
    '''
    Checks which tasks are being executed in the backend.
    Parameters:
        token (dict): Decoded authentication token.
    Return:
        list[dict]: Dictionary containing the tasks. Task IDs are used as keys and values indicate starting time.
    '''

    list_dict ={}

    for key in tasks.keys():
        task_ob = tasks[key]
        list_dict[key] = task_ob.start_time

    return list_dict

# Endpoint to setup the city (download OSM data) 
@router.post("/city_setup")
async def city_setup(input: schemas.InputCity):
    '''
    Starts execution of a model task.
    Parameters:
        input (JSON): Input parameters for the model (see InputData schema).
        token (dict): Decoded authenticaton token.
    Return:
        (JSON): ID of the task.
    '''

    task_id = str(uuid.uuid4())  # Generate a unique ID for the task
    logger.info(f'Starting run with task ID: {task_id}')
    
    PATH = path.PATH
    for subfolder in ["data", "plots", "plots_networks", "results", "exports", "exports_json", "videos"]:
        for key in input.city.keys():
            placepath = PATH[subfolder] / key  
            placepath.mkdir(parents=True, exist_ok=True)  
            print(f"Successfully created folder {placepath}")
    
    
    async def setup_task(task_id):
        try:
            # Extract parameters
            PATH = path.PATH

            # Execute workflow
            logger.info("Running - Preparing networks")
            prepare_networks.main(PATH, input.city)

            logger.info("Running - Preparing POIs")
            prepare_pois.main(PATH, input.city)

            logger.info(f'Run with task ID: {task_id} finished')
        except asyncio.CancelledError:
            logger.info(f'Run with task ID: {task_id} cancelled')
            raise  # Propagate the cancellation exception

    time = str(datetime.datetime.now())
    task = asyncio.create_task(setup_task(task_id))
    task_ob = schemas.ModelTask(task=task, start_time=time)
    tasks[task_id] = task_ob
    return {"task_id": task_id}

# Endpoint to run the task 
@router.post("/run")
async def run_model(input: schemas.InputData):
    '''
    Starts execution of a model task.
    Parameters:
        input (JSON): Input parameters for the model (see InputData schema).
        token (dict): Decoded authenticaton token.
    Return:
        (JSON): ID of the task.
    '''
    
   
    task_id = str(uuid.uuid4())  # Generate a unique ID for the task
    logger.info(f'Starting run with task ID: {task_id}')

    async def model_task(task_id):
        try:
            # Extract parameters
            PATH = path.PATH
            sliders = input.sliders

            logger.info("Running - Clustering POIs")
            cluster_pois.main(
                PATH, task_id, input.city, input.h3_zoom, snapthreshold,
                sliders["sanidad"], sliders["educacion"], sliders["administracion"], 
                sliders["aprovisionamiento"], sliders["cultura"], sliders["deporte"], 
                sliders["transporte"]
            )

            poi_based_generation.main(PATH, task_id, input.city, input.prune_measure)


            logger.info(f'Run with task ID: {task_id} finished')
        except asyncio.CancelledError:
            logger.info(f'Run with task ID: {task_id} cancelled')
            raise  # Propagate the cancellation exception

    time = str(datetime.datetime.now())
    task = asyncio.create_task(model_task(task_id))
    task_ob = schemas.ModelTask(task=task, start_time=time)
    tasks[task_id] = task_ob
    return {"task_id": task_id}


@router.post("/city_metrics")
async def run_analysis(input: schemas.InputResults):
    '''
    Get the metrics for the actual city
    Parameters:
        input (JSON): Input parameters for the analysis (see InputData schema).
        token (dict): Decoded authentication token.
    Return:
        (JSON): ID of the task.
    '''
    
    task_id = str(uuid.uuid4())  # Generate a unique ID for the task
    logger.info(f'Starting run with task ID: {task_id}')

    logger.info(f'Starting analysis with task ID: {task_id}')

    async def analysis_task(task_id):
        try:
            # Extract parameters
            PATH = path.PATH
            cities = input.city

            logger.info("Running - Analyzing Metrics")
            real_city_metrics.main(PATH, input.task_id, cities)

            logger.info(f'Analysis with task ID: {task_id} finished')
        except asyncio.CancelledError:
            logger.info(f'Analysis with task ID: {task_id} cancelled')
            raise  # Propagate the cancellation exception

    time = str(datetime.datetime.now())
    task = asyncio.create_task(analysis_task(task_id))
    task_ob = schemas.ModelTask(task=task, start_time=time)
    tasks[task_id] = task_ob
    return {"task_id": task_id}

@router.post("/run_analysis")
async def run_analysis(input: schemas.InputResults):
    '''
    Starts execution of an analysis task.
    Parameters:
        input (JSON): Input parameters for the analysis (see InputData schema).
        token (dict): Decoded authentication token.
    Return:
        (JSON): ID of the task.
    '''
  

    task_id = str(uuid.uuid4())  # Generate a unique ID for the task
    logger.info(f'Starting run with task ID: {task_id}')

    logger.info(f'Starting analysis with task ID: {task_id}')

    async def analysis_task(task_id):
        try:
            # Extract parameters
            PATH = path.PATH
            cities = input.city

            logger.info("Running - Analyzing Metrics")
            analyze_results.main(PATH, input.task_id, cities, prune_index=input.phase)

            logger.info(f'Analysis with task ID: {task_id} finished')
        except asyncio.CancelledError:
            logger.info(f'Analysis with task ID: {task_id} cancelled')
            raise  # Propagate the cancellation exception

    time = str(datetime.datetime.now())
    task = asyncio.create_task(analysis_task(task_id))
    task_ob = schemas.ModelTask(task=task, start_time=time)
    tasks[task_id] = task_ob
    return {"task_id": task_id}



# Endpoint to stop the task
@router.delete("/stop/{task_id}")
async def stop_model(task_id: str):
    '''
    Stops a running task.
    Parameters:
        task_id (str): ID of the task to stop.
        token (dict): Decoded authenticaton token.
    Return:
        (JSON): Confirmation of cancellation.
    '''
    
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
        logger.info(f'Task {task_id} successfully cancelled')
    finally:
        tasks.pop(task_id, None)  # Clean up the task from the dictionary

    return {"status": "task cancelled", "task_id": task_id}


# Endpoint to download the map

@router.get("/map/{task_id}")
async def download_map(task_id: str, input: schemas.InputData):
    '''
    Streams the download of the map stored in disk for the task with ID equal to task_id.
    Parameters:
        task_id (str): ID of the task to stop.
        token (dict): Decoded authenticaton token.
    Return:
        (FileResponse): Map file in jpeg format.
    '''
    PATH = path.PATH

    task_ob = tasks.get(task_id)
    
    if task_ob is None:
        raise HTTPException(status_code=404, detail="No task with ID " + task_id)
    
    suffix = ".geojson"
    city_key = list(input.city.keys())[0]
    filename = f"{city_key}_{input.prune_measure}{suffix}"

    # Use pathlib to construct the file path
    result_path = Path(PATH["task_output"]) / task_id / filename
    return FileResponse(result_path)
