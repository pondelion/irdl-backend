from typing import List
from datetime import datetime

from pydantic import BaseModel


class LocationInDBSchema(BaseModel):
    device_name: str
    datetime: datetime
    lat: float
    lng: float
