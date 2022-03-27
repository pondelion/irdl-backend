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

    def get_latest(self, device_name: str) -> LocalLocationModel:
        location = LocationModel.query(
            device_name,
            scan_index_forward=False,
            limit=1,
        )
        return list(location)[0]


class LocationLocalRepository(BaseDynamoDBRepository[LocalLocationModel, LocationInDBSchema, LocationInDBSchema]):

    def __init__(self):
        super().__init__(LocalLocationModel)

    def get_latest(self, device_name: str) -> LocalLocationModel:
        location = LocationModel.query(
            device_name,
            scan_index_forward=False,
            limit=1,
        )
        return list(location)[0]
