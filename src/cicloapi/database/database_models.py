from sqlalchemy import Column, Integer, create_engine, ForeignKey, Text, Float, Boolean, Index
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy.dialects.postgresql import UUID
from geoalchemy2 import Geometry

DATABASE_URL = "postgresql://roger:rogerbsc@localhost:5433/CICLOAPI"

engine = create_engine(DATABASE_URL, echo=True)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()
DATABASE_URL = "postgresql://roger:rogerbsc@localhost:5433/CICLOAPI"

engine = create_engine(DATABASE_URL, echo=True)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

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
    # Primary key usually creates an index

class F_POI(Base):
    __tablename__ = "f_poi"
    poi_id = Column(Integer, primary_key=True, autoincrement=True)
    task_id = Column(UUID(as_uuid=False), ForeignKey("f_simulation_tasks.task_id"), index=True)
    city_id = Column(Text, nullable=False, index=True)
    name = Column(Text, nullable=True)
    poi_category = Column(Text, nullable=True)
    geometry = Column(Geometry(geometry_type="POINT", srid=4326), nullable=True)

class F_SimulationSegment(Base):
    __tablename__ = "f_simulation_edges"
    segment_id = Column(Integer, primary_key=True, autoincrement=True)
    task_id = Column(UUID(as_uuid=False), ForeignKey("f_simulation_tasks.task_id"), nullable=False, index=True)
    city_id = Column(Text, nullable=False, index=True)
    connectivity = Column(Text, nullable=False, index=True)
    prune_index = Column(Integer, nullable=False, index=True)
    quantile = Column(Float, nullable=False)
    geometry = Column(Geometry(geometry_type="GEOMETRY", srid=4326), nullable=True)
    
    __table_args__ = (
        Index("ix_simulation_edges_task_city", "task_id", "city_id"),
    )

class F_SimulationCentroid(Base):
    __tablename__ = "f_simulation_nodes"
    id = Column(Integer, primary_key=True, autoincrement=True)
    hex_id = Column(Text, nullable=False, index=True)
    task_id = Column(UUID(as_uuid=False), ForeignKey("f_simulation_tasks.task_id"), nullable=False, index=True)
    city_id = Column(Text, nullable=False, index=True)
    weighted_point_count = Column(Float, nullable=False)
    cluster = Column(Integer, nullable=False)
    geometry = Column(Geometry(geometry_type="GEOMETRY", srid=4326), nullable=False)

class F_SimulationCityMetrics(Base):
    __tablename__ = "f_simulation_city_metrics"
    id = Column(Integer, primary_key=True, autoincrement=True)
    task_id = Column(UUID(as_uuid=False), ForeignKey("f_simulation_tasks.task_id"), nullable=False, index=True)
    city_id = Column(Text, nullable=False, index=True)
    is_base = Column(Boolean, default=True, nullable=False)
    prune_index = Column(Integer, nullable=False, index=True)
    
    network_type = Column(Text, nullable=True)
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
    
    __table_args__ = (
        Index("ix_simulation_city_metrics_task_city", "task_id", "city_id"),
    )

class City(Base):
    __tablename__ = "m_cities"
    db_cty_id = Column(Integer, primary_key=True, autoincrement=True)
    placeid = Column(Text, nullable=False, unique=True)
    nominatimstring = Column(Text, nullable=False)
    countryid = Column(Text, nullable=True)
    name = Column(Text, nullable=True)

    __table_args__ = (
        Index("ix_m_cities_placeid", "placeid", unique=True),
    )
