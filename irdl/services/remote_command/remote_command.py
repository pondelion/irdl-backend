from datetime import datetime
from enum import Enum
import os
from threading import Thread
from typing import Dict, Optional
import tempfile

import numpy as np
from pydantic import BaseModel

from .publisher import MessagePublisher
from ...settings import settings
from ...repositories.storage.s3 import (
    RemoteS3Repository,
    LocalS3Repository,
)


class CommandList(Enum):
    GET_STATUS = 'GET_STATUS'
    TAKE_PICTURE = 'TAKE_PICTURE'
    STATR_LOGGING = 'START_LOGGING'


class RemoteCommandParams(BaseModel):
    cmd: CommandList
    params: Optional[Dict] = {}


class RemoteCommand:

    def __init__(self):
        self._publisher = MessagePublisher()
        self._remote_s3_repo = RemoteS3Repository()
        self._local_s3_repo = LocalS3Repository()

    def take_picture(self, device_name: str, s3_filepath: str) -> str:
        topic = f'{settings.AWS_IOT_COMMAND_TOPIC_NAME}/{device_name}'
        cmd_json = {
            'cmd': CommandList.TAKE_PICTURE.value,
            's3_filepath': s3_filepath,
        }
        self._publisher.publish(
            topic=topic,
            message=cmd_json,
        )
        local_filepath = os.path.join(tempfile.gettempdir(), os.path.basename(s3_filepath))
        self._remote_s3_repo.get(
            s3_filepath=s3_filepath,
            local_filepath=local_filepath,
            n_retry=30,
            retry_interval_sec=0.2,
        )
        Thread(
            target=lambda: self._local_s3_repo.save(local_filepath, s3_filepath),
        ).start()
        return local_filepath

    def execute_command(self, device_name: str, remote_command_params: RemoteCommandParams):
        if remote_command_params.cmd == CommandList.TAKE_PICTURE:
            if 's3_filepath' not in remote_command_params.params:
                # raise ValueError('s3_filepath must be specified for TAKE_PICTURE command params.')
                print('[WARNING] s3_filepath is not specified for TAKE_PICTURE command')
                remote_command_params.params['s3_filepath'] = os.path.join(
                    settings.S3_CAMERA_IMAGE_URI, device_name, f"{datetime.now().strftime('%Y%m%d%H%M%S%f')}.png"
                )
            return self.take_picture(
                device_name=device_name,
                s3_filepath=remote_command_params.params['s3_filepath']
            )
