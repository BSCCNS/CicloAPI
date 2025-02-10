import psycopg2
from psycopg2 import OperationalError
from psycopg2.extras import execute_values
from cicloapi.core.config import DB_settings
from shapely.geometry import shape
import logging

#from cicloapi.core.endpoints import logger #Probably we should configure the logger in the main file

logger = logging.getLogger("uvicorn.error")

class DatabaseConnectionError(Exception):
    pass

def create_connection():
    try:
        port = int(DB_settings.port)
        # Replace with your actual values
        connection = psycopg2.connect(
            host=DB_settings.host,          # PostgreSQL server hostname
            port=DB_settings.port,               # Port number (use 5432 or the one you exposed)
            database=DB_settings.database,       # Database name
            user=DB_settings.user,              # Username
            password=DB_settings.password        # Password
        )

        logger.info("Connection to PostgreSQL database was successful")
        return connection
    except OperationalError as e:
        logger.error(f"The error '{e}' occurred")
        return None


class Database:
    def __init__(self, connection):
        if not connection:
            raise DatabaseConnectionError('Error connecting to the database.')
        
        self.connection = connection
        self.cursor = connection.cursor()


    def create_task_poi_table(self):
        sql = """
        CREATE TABLE IF NOT EXISTS f_poi (
            task_id UUID,
            city_id TEXT,
            name TEXT,
            poiid TEXT,
            geometry GEOMETRY(Point, 4326)

        );
        """
        self.cursor.execute(sql)
        self.connection.commit()
        logger.info('Table task_poi created or already exists.')


    def insert_pois(self, pois):
        sql = """
        INSERT INTO f_poi (task_id, city_id, name, poiid, geometry)
        VALUES %s
        """
        execute_values(self.cursor, sql, pois)
        self.connection.commit()
        inserted_rows = self.cursor.rowcount
        logger.info(f'POIs inserted into database: {inserted_rows} rows.')
        return inserted_rows

    def insert_network_edges(self, edges):
        sql = """
        INSERT INTO f_network_edges (city_id, network_type_id, u, v, key, osmid, highway, junction, maxspeed, ref, oneway, reversed, length, name, lanes, width, bridge, access, service)
        VALUES %s
        """
        execute_values(self.cursor, sql, edges)
        self.connection.commit()
        logger.info('Network edges inserted into database.')

    def insert_network_nodes(self, nodes):
        sql = """
        INSERT INTO f_network_nodes (osmid, city_id, network_type_id, y, x, street_count, highway, ref)
        VALUES %s
        """
        execute_values(self.cursor, sql, nodes)
        self.connection.commit()
        logger.info('Network nodes inserted into database.')

    def insert_network_types(self, network_types):
        sql = """
        INSERT INTO m_network_types (name)
        VALUES %s
        """
        execute_values(self.cursor, sql, network_types)
        self.connection.commit()
        logger.info('Network types inserted into database.')

    def insert_cities(self, cities):
        sql = """
        INSERT INTO m_cities (name, nominatimstring)
        VALUES %s
        """
        execute_values(self.cursor, sql, cities)
        self.connection.commit()
        logger.info('Cities inserted into database.')




database = Database(create_connection())


