from cicloapi.database.database_models import Base, engine, F_POI
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


Base.metadata.create_all(bind=engine)


