from sqlalchemy import Column, Integer, String, create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

from sqlalchemy import Column, Integer, Text, Float, UniqueConstraint, Boolean
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


class F_SimulationTasks(Base):
    __tablename__ = "f_simulation_tasks"

    task_id = Column(UUID(as_uuid=False), primary_key=True)
    prune_measure = Column(Text, nullable=False, default="betweenness")
    prune_quantiles = Column(Integer, nullable=False, default=40)
    h3_zoom = Column(Integer, nullable=False, default=10)
    sanidad = Column(Float, nullable=False, default=1.0)
    educacion = Column(Float, nullable=False, default=2.0)
    administracion = Column(Float, nullable=False, default=2.0)
    aprovisionamiento = Column(Float, nullable=False, default=3.0)
    cultura = Column(Float, nullable=False, default=4.0)
    deporte = Column(Float, nullable=False, default=5.0)
    transporte = Column(Float, nullable=False, default=2.0)
    buffer_walk_distance = Column(Integer, nullable=False, default=500)


class F_SimulationSegment(Base):
    __tablename__ = "f_simulation_edges"

    segment_id = Column(Integer, primary_key=True, autoincrement=True)
    task_id = Column(UUID(as_uuid=False), nullable=False)
    city_id = Column(Text, nullable=False)
    connectivity = Column(Text, nullable=False)
    prune_index = Column(Integer, nullable=False)
    quantile = Column(Float, nullable=False)
    # Allow any geometry type instead of only LINESTRING:
    geometry = Column(Geometry(geometry_type="GEOMETRY", srid=4326), nullable=True)


class F_SimulationCentroid(Base):
    __tablename__ = "f_simulation_nodes"

    id = Column(Integer, primary_key=True, autoincrement=True)
    hex_id = Column(Text, nullable=False)
    task_id = Column(UUID(as_uuid=False), nullable=False)
    city_id = Column(Text, nullable=False)
    weighted_point_count = Column(Float, nullable=False)
    cluster = Column(Integer, nullable=False)
    geometry = Column(Geometry(geometry_type="GEOMETRY", srid=4326), nullable=False)

class F_SimulationCityMetrics(Base):
    __tablename__ = "f_simulation_city_metrics"

    id = Column(Integer, primary_key=True, autoincrement=True)
    task_id = Column(UUID(as_uuid=False), nullable=False)
    city_id = Column(Text, nullable=False)
    is_base = Column(Boolean, default=True, nullable=False)
    prune_index = Column(Integer, nullable=False)
    
    network_type = Column(Text, nullable=True)  # e.g., "biketrack", "carall", etc.

    length = Column(Float, nullable=True)
    length_lcc = Column(Float, nullable=True)
    coverage = Column(Float, nullable=True)
    directness = Column(Float, nullable=True)
    directness_lcc = Column(Float, nullable=True)
    poi_coverage = Column(Integer, nullable=True)
    components = Column(Integer, nullable=True)
    efficiency_global = Column(Float, nullable=True)
    efficiency_local = Column(Float, nullable=True)
    efficiency_global_routed = Column(Float, nullable=True)
    efficiency_local_routed = Column(Float, nullable=True)
    directness_lcc_linkwise = Column(Float, nullable=True)
    directness_all_linkwise = Column(Float, nullable=True)