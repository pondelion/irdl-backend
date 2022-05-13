from datetime import datetime
from typing import List, Optional

from .base import BaseDynamoDBRepository
from ...models.pynamodb import (
    CameraImageModel,
    LocalCameraImageModel,
)
from ...schemas import CameraImageInDBSchema, CameraImageInLocalDBSchema


class CameraImageMetaDataRepository(BaseDynamoDBRepository[CameraImageModel, CameraImageInDBSchema, CameraImageInDBSchema]):

    def __init__(self):
        super().__init__(CameraImageModel)

    def get_by_organization_device(self, organization: str, device_name: str) -> List[CameraImageModel]:
        organization_device = f'{organization}/{device_name}'
        records = self._model.get(hash_key=organization_device)
        return records

    def get_by_datetime_range(
        self,
        organization: str,
        device_name: str,
        datetime_min: Optional[datetime],
        datetime_max: Optional[datetime],
    ) -> List[CameraImageModel]:
        organization_device = f'{organization}/{device_name}'
        query_kwargs = {'hash_key': organization_device}
        range_key_condition = None
        if datetime_min:
            range_key_condition = self._model.datetime >= datetime_min
        if datetime_max:
            if range_key_condition:
                range_key_condition &= self._model.datetime <= datetime_max
            else:
                range_key_condition = self._model.datetime <= datetime_max
        records = self._model.query(**query_kwargs)
        return records


class CameraImageMetaDataLocalRepository(
    BaseDynamoDBRepository[LocalCameraImageModel, CameraImageInLocalDBSchema, CameraImageInLocalDBSchema]
):

    def __init__(self):
        super().__init__(LocalCameraImageModel)

    def get_by_organization_device(self, organization: str, device_name: str) -> List[LocalCameraImageModel]:
        organization_device = f'{organization}/{device_name}'
        records = self._model.get(hash_key=organization_device)
        return records

    def get_by_datetime_range(
        self,
        organization: str,
        device_name: str,
        datetime_min: Optional[datetime],
        datetime_max: Optional[datetime],
    ) -> List[CameraImageModel]:
        organization_device = f'{organization}/{device_name}'
        query_kwargs = {'hash_key': organization_device}
        range_key_condition = None
        if datetime_min:
            range_key_condition = self._model.datetime >= datetime_min
        if datetime_max:
            if range_key_condition:
                range_key_condition &= self._model.datetime <= datetime_max
            else:
                range_key_condition = self._model.datetime <= datetime_max
        if range_key_condition:
            query_kwargs['range_key_condition'] = range_key_condition
        records = self._model.query(**query_kwargs)
        return records
