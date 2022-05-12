from typing import List, Optional
from datetime import datetime

from pydantic import BaseModel


class CameraImageInDBSchema(BaseModel):
    organization_device_name: str
    datetime: str
    s3_filepath: str


class CameraImageInLocalDBSchema(CameraImageInDBSchema):
    created_at: Optional[datetime]
