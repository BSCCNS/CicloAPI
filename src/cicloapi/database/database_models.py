from sqlalchemy import Column, Integer, String, create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

from sqlalchemy import Column, Text
from sqlalchemy.dialects.postgresql import UUID
from geoalchemy2 import Geometry


DATABASE_URL = "postgresql://roger:rogerbsc@localhost:5433/CICLOAPI"

engine = create_engine(DATABASE_URL, echo = True)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

class F_POI(Base):
    __tablename__ = "f_poi"
    poi_id = Column(Integer, primary_key=True, autoincrement=True)
    task_id = Column(UUID(as_uuid=False))
    city_id = Column(Text, nullable=False)
    name = Column(Text, nullable=True)
    poi_category = Column(Text, nullable=True)
    geometry = Column(Geometry(geometry_type="POINT", srid=4326), nullable=True)