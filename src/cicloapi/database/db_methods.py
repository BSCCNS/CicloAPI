import psycopg2
from psycopg2 import OperationalError
from cicloapi.core.config import DB_settings
from shapely.geometry import shape

from cicloapi.core.endpoints import logger #Probably we should configure the logger in the main file

def create_connection():
    try:
        # Replace with your actual values
        connection = psycopg2.connect(
            host=DB_settings.host,          # PostgreSQL server hostname
            port=DB_settings.port,               # Port number (use 5432 or the one you exposed)
            database=DB_settings.database,       # Database name
            user=DB_settings.user,              # Username
            password=DB_settings.password        # Password
        )

        print("Connection to PostgreSQL database was successful")
        return connection
    except OperationalError as e:
        print(f"The error '{e}' occurred")
        return None


class Database():
    def __init__(self, connection):
        super(Database, self).__init__()

        if not connection:
            raise Exception('Error connecting database.')
        
        self.connection = connection
        self.cursor = connection.cursor()

    def writegeojson(self, gjson, table):
        for feature in gjson["features"]:
            name = feature["properties"].get("name", "Unknown")
            geom = shape(feature["geometry"])  # Convert to Shapely geometry
            wkt_geom = geom.wkt  # Convert to WKT format

            sql = f"INSERT INTO {table} (name, geom) VALUES (%s, ST_GeomFromText(%s, 4326));"
            self.cursor.execute(sql, (name, wkt_geom))

        logger.info('GeoJSON object written to database.')




database = Database(create_connection())


