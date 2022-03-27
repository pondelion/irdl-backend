from typing import List
from datetime import datetime

from pydantic import BaseModel


class SensorInDBSchema(BaseModel):
    device_name: str
    datetime: datetime
    max_range: float
    min_delay = int
    power = float
    resolution = float
    sensor_name = str
    type = int
    value = float
    vendor = str
    version = int
