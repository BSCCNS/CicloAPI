# schemas.py

from pydantic import BaseModel, Field, ConfigDict
from typing import Optional, Dict
import asyncio


class InputCity(BaseModel):
    city: dict = {"viladecans": {"nominatimstring": "Viladecans, Barcelona, Spain"}}


class InputData(InputCity):
    prune_measure: str = "betweenness"
    prune_quantiles: int = 40
    h3_zoom: int = 10
    sliders: Dict[str, float] = {
        "sanidad": 1.0,
        "educacion": 2.0,
        "administracion": 2.0,
        "aprovisionamiento": 3.0,
        "cultura": 4.0,
        "deporte": 5.0,
        "transporte": 2.0,
    }
    buffer_walk_distance: int = 500


class InputResults(InputCity):
    expansion_index: list[int] = [0, 1, 2, 3, 4, 5, 6, 7, 8, 9]
    task_id: str


class ModelTask(BaseModel):
    task: Optional[asyncio.Task] = Field(default=None, exclude=True)
    start_time: str
    model_config = ConfigDict(arbitrary_types_allowed=True)
