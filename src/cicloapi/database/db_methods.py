from cicloapi.database.database_models import Base, engine, F_POI, F_SimulationTasks, F_SimulationSegment, F_SimulationCentroid
from sqlalchemy.orm import Session
import logging

#from cicloapi.core.endpoints import logger #Probably we should configure the logger in the main file

logger = logging.getLogger("uvicorn.error")

class DatabaseConnectionError(Exception):
    pass


class Database:
    def __init__(self, session: Session):
        if not session:
            raise DatabaseConnectionError('Error connecting to the database.')
        self.session = session


    def insert_pois(session: Session, poi_data: dict):
        """
        poi_data: dict where each value is a dict with keys:
        - task_id
        - city_id
        - name
        - poi_category
        - geometry: GeoJSON dict, which will be converted to WKT
        """
        poi_objects = []
        print(poi_data)
        for poi in poi_data.values():
            poi_obj = F_POI(
                task_id=poi["task_id"],
                city_id=poi["city_id"],
                name=poi["name"],
                poi_category=poi["poi_category"],
                geometry=poi["geometry"]
            )
            poi_objects.append(poi_obj)
        session.bulk_save_objects(poi_objects)
        session.commit()
        logger.info(f'Inserted {len(poi_objects)} POIs.')
        return len(poi_objects)

    def insert_simulation_task(self, simulation_data: dict):
        """
        simulation_data: dict with keys:
        - task_id
        - prune_measure
        - prune_quantiles
        - h3_zoom
        - sanidad
        - educacion
        - administracion
        - aprovisionamiento
        - cultura
        - deporte
        - transporte
        - buffer_walk_distance
        """
        new_task = F_SimulationTasks(
            task_id=simulation_data["task_id"],
            prune_measure=simulation_data["prune_measure"],
            prune_quantiles=simulation_data["prune_quantiles"],
            h3_zoom=simulation_data["h3_zoom"],
            sanidad=simulation_data["sanidad"],
            educacion=simulation_data["educacion"],
            administracion=simulation_data["administracion"],
            aprovisionamiento=simulation_data["aprovisionamiento"],
            cultura=simulation_data["cultura"],
            deporte=simulation_data["deporte"],
            transporte=simulation_data["transporte"],
            buffer_walk_distance=simulation_data["buffer_walk_distance"]
        )
        self.session.add(new_task)
        self.session.commit()
        logger.info(f'Inserted simulation task with id {simulation_data["task_id"]}.')
        return new_task
    
    def insert_simulation_segments(self, segments_data: list):
        """
        segments_data: list of dicts with keys:
        - task_id
        - city_id
        - prune_index
        - quantile
        - geometry (WKT string representing a LineString)
        Inserts simulation segments into the database.
        """
        segment_objects = []
        for seg in segments_data:
            seg_obj = F_SimulationSegment(
                task_id=seg["task_id"],
                city_id=seg["city_id"],
                connectivity=seg["connectivity"],
                prune_index=seg["prune_index"],
                quantile=seg["quantile"],
                geometry=seg["geometry"]
            )
            segment_objects.append(seg_obj)
        self.session.bulk_save_objects(segment_objects)
        self.session.commit()
        logger.info(f"Inserted {len(segment_objects)} simulation segments.")
        return segment_objects
    
    def insert_simulation_nodes(self, node_data):
        """
        Inserts F_SimulationCentroid objects (simulation nodes) into the database.

        :param node_data: List of dictionaries with keys:
                        'hex_id', 'task_id', 'city_id', 
                        'weighted_point_count', 'cluster', 'geometry'
        :return: List of inserted F_SimulationCentroid objects.
        """

        node_objects = []
        for data in node_data:
            node_obj = F_SimulationCentroid(
                hex_id=data['hex_id'],
                task_id=data['task_id'],
                city_id=data['city_id'],
                weighted_point_count=data['weighted_point_count'],
                cluster=data['cluster'],
                geometry=data['geometry']
            )
            node_objects.append(node_obj)

        self.session.bulk_save_objects(node_objects)
        self.session.commit()
        logger.info(f"Inserted {len(node_objects)} simulation nodes.")
        return node_objects

Base.metadata.create_all(bind=engine)


