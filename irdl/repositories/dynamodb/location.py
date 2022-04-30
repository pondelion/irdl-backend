from typing import List, Optional

from .base import BaseDynamoDBRepository
from ...models.pynamodb import (
    LocationModel,
    LocalLocationModel,
)
from ...schemas.location import LocationInDBSchema


class LocationRepository(BaseDynamoDBRepository[LocationModel, LocationInDBSchema, LocationInDBSchema]):

    def __init__(self):
        super().__init__(LocationModel)

    def get_latest(self, device_name: Optional[str] = None) -> LocationModel:
        if device_name is not None:
            location = self._model.query(
                device_name,
                scan_index_forward=False,
                limit=1,
            )
            location = list(location)
        else:
            location = self._model.scan()
            location = [list(location)[-1]]
        return location[0] if len(location) > 0 else None


class LocationLocalRepository(BaseDynamoDBRepository[LocalLocationModel, LocationInDBSchema, LocationInDBSchema]):

    def __init__(self):
        super().__init__(LocalLocationModel)

    def get_latest(self, device_name: Optional[str] = None) -> LocalLocationModel:
        if device_name is not None:
            location = self._model.query(
                device_name,
                scan_index_forward=False,
                limit=1,
            )
            location = list(location)
        else:
            location = self._model.scan()
            location = [list(location)[-1]]
        location = list(location)
        return location[0] if len(location) > 0 else None
