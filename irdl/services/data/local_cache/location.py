from datetime import datetime, timedelta
from typing import Dict, List, Optional, Union

from pynamodb.expressions.condition import Comparison

from ....models.pynamodb.location import LocalLocationModel, LocationModel
from ....repositories.dynamodb import LocationRepository, LocationLocalRepository
from ....utils.logger import Logger


class LocationLocalCache:

    def __init__(self, sync_time_sec: float = 60*30):
        self._local_dynamo_repo = LocationLocalRepository()
        self._remote_dynamo_repo = LocationRepository()
        self._sync_time_sec = sync_time_sec

    def get_all(self) -> Union[LocationModel, LocalLocationModel]:
        local_latest_record = self._local_dynamo_repo.get_latest()

    def get(
        self,
        hash_key: Union[str, int, float],
        range_key: Optional[Union[str, int, float, Comparison]] = None,
        filter_condition: Optional[Comparison] = None,
    ) ->  List[Union[LocationModel, LocalLocationModel]]:
        local_latest_record = self._local_dynamo_repo.get_latest(
            device_name=hash_key
        )
        if local_latest_record is None:
            Logger.d('LocationLocalCache', f'Record for device {hash_key} does not exists in local dynamodb, fetching from remote dynamodb.')
        elif datetime.now() > local_latest_record.created_at + timedelta(seconds=self._sync_time_sec):
            Logger.d('LocationLocalCache', f'Record for device {hash_key} in local dynamodb is old, syncing with remote dynamodb.')
        else:
            Logger.d('LocationLocalCache', f'Record for device {hash_key} founds in local dynamodb, using local data as cache')
