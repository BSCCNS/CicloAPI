from sqlalchemy import Column, Integer, String, create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

from sqlalchemy import Column, Text
from sqlalchemy.dialects.postgresql import UUID
from geoalchemy2 import Geometry


DATABASE_URL = "postgresql://roger:rogerbsc@localhost:5433/CICLOAPI"

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

class F_POI(Base):
    __tablename__ = "f_poi"
    task_id = Column(UUID(as_uuid=True), primary_key=True)
    city_id = Column(Text, nullable=False)
    name = Column(Text, nullable=False)
    poiid = Column(Text, nullable=False)
    geometry = Column(Geometry(geometry_type="POINT", srid=4326), nullable=False)