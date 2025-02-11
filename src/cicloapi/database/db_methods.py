from cicloapi.database.database_models import Base, engine, F_POI
from sqlalchemy.orm import Session
from shapely.geometry import shape
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


    def insert_pois(session: Session, poi_data: list):
        """
        poi_data: list of dicts with keys:
        - task_id
        - city_id
        - name
        - poiid
        - geometry: GeoJSON dict, which will be converted to WKT
        """
        poi_objects = []
        for poi in poi_data:
            geom_obj = shape(poi["geometry"])  # Convert GeoJSON dict to Shapely object
            wkt_geometry = geom_obj.wkt
            poi_obj = F_POI(
                task_id=poi["task_id"],
                city_id=poi["city_id"],
                name=poi["name"],
                poiid=poi["poiid"],
                geometry=wkt_geometry
            )
            poi_objects.append(poi_obj)
        session.bulk_save_objects(poi_objects)
        session.commit()
        logger.info(f'Inserted {len(poi_objects)} POIs.')
        return len(poi_objects)


Base.metadata.create_all(bind=engine)


