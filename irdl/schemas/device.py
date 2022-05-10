from typing import List, Optional
from datetime import datetime

from pydantic import BaseModel


class DeviceSchema(BaseModel):
    device_name: str
    organization: str
    sub: Optional[str]
    created_at: Optional[datetime]
    updated_at: Optional[datetime]
    enabled: Optional[bool]
