import os
import tempfile
from datetime import datetime, timezone
from enum import Enum
from threading import Thread
from typing import Dict, Optional
from uuid import UUID, uuid4

from pydantic import BaseModel

from ...models.pynamodb.camera_image import (CameraImageModel,
                                             LocalCameraImageModel)
from ...repositories.storage.s3 import LocalS3Repository, RemoteS3Repository
from ...settings import settings
from ...utils import Logger
from .publisher import MessagePublisher


class CommandList(Enum):
    GET_STATUS = 'GET_STATUS'
    TAKE_PICTURE = 'TAKE_PICTURE'
    TAKE_SUCCESSIVE_PICTURE = 'TAKE_SUCCESSIVE_PICTURE'
    STATR_LOGGING = 'START_LOGGING'
    STOP_LOGGING = 'STOP_LOGGING'
    BEEP = 'BEEP'
    TTS = 'TTS'
    START_STREAMING = 'START_STREAMING'
    STOP_STREAMING = 'STOP_STREAMING'


class RemoteCommandParams(BaseModel):
    cmd: CommandList
    params: Dict = {}
    cmd_id: UUID = uuid4()


class RemoteCommand:

    def __init__(self):
        self._publisher = MessagePublisher()
        self._remote_s3_repo = RemoteS3Repository()
        self._local_s3_repo = LocalS3Repository()

    def execute_command(self, organization_name: str, device_name: str, remote_command_params: RemoteCommandParams):
        Logger.i('RemoteCommand.execute_command', f'{organization_name} : {device_name} : {remote_command_params}')
        res = None
        if remote_command_params.cmd == CommandList.TAKE_PICTURE:
            if 's3_filepath' not in remote_command_params.params:
                # raise ValueError('s3_filepath must be specified for TAKE_PICTURE command params.')
                print('[WARNING] s3_filepath is not specified for TAKE_PICTURE command')
                remote_command_params.params['s3_filepath'] = os.path.join(
                    settings.S3_CAMERA_IMAGE_URI, organization_name, device_name, f"{datetime.now().strftime('%Y%m%d%H%M%S%f')}.png"
                )
            res = self.take_picture(
                organization_name=organization_name,
                device_name=device_name,
                params=remote_command_params,
                s3_filepath=remote_command_params.params['s3_filepath']
            )
        elif remote_command_params.cmd == CommandList.TAKE_SUCCESSIVE_PICTURE:
            if 'interval_sec' not in remote_command_params.params:
                raise ValueError('interval_sec must be specified for TAKE_SUCCESSIVE_PICTURE command params.')
            if 's3_filedir' not in remote_command_params.params:
                print('[WARNING] s3_filedir is not specified for TAKE_SUCCESSIVE_PICTURE command')
                remote_command_params.params['s3_filedir'] = os.path.join(
                    settings.S3_CAMERA_IMAGE_URI, organization_name, device_name, f"{datetime.now().strftime('%Y%m%d%H%M%S%f')}"
                )
        elif remote_command_params.cmd == CommandList.BEEP:
            res = self.beep(
                organization_name=organization_name,
                device_name=device_name,
                params=remote_command_params,
            )
        elif remote_command_params.cmd == CommandList.STATR_LOGGING:
            res = self.start_logging(
                organization_name=organization_name,
                device_name=device_name,
                params=remote_command_params,
                target=remote_command_params.params['target']
            )
        elif remote_command_params.cmd == CommandList.STOP_LOGGING:
            res = self.stop_logging(
                organization_name=organization_name,
                device_name=device_name,
                params=remote_command_params,
                target=remote_command_params.params['target']
            )
        elif remote_command_params.cmd == CommandList.GET_STATUS:
            res = self.get_status(
                organization_name=organization_name,
                device_name=device_name,
                params=remote_command_params,
            )
        elif remote_command_params.cmd == CommandList.START_STREAMING:
            if 'url' not in remote_command_params.params:
                raise ValueError('url must be specified for START_STREAMING command params.')
            res = self.start_streaming(
                organization_name=organization_name,
                device_name=device_name,
                params=remote_command_params,
                url=remote_command_params.params['url'],
            )
        Logger.i('RemoteCommand.execute_command', 'command done')
        return res

    def take_picture(
        self,
        organization_name: str, device_name: str,
        params: RemoteCommandParams, s3_filepath: str
    ) -> Optional[str]:
        topic = f'{settings.AWS_IOT_COMMAND_TOPIC_NAME}/{organization_name}/{device_name}'
        cmd_json = {
            'cmd': CommandList.TAKE_PICTURE.value,
            's3_filepath': s3_filepath,
            'cmd_id': str(params.cmd_id),
        }
        self._publisher.publish(
            topic=topic,
            message=cmd_json,
        )
        local_filepath = os.path.join(tempfile.gettempdir(), os.path.basename(s3_filepath))
        res = self._remote_s3_repo.get(
            s3_filepath=s3_filepath,
            local_filepath=local_filepath,
            n_retry=30,
            retry_interval_sec=0.2,
        )
        if settings.USE_LOCAL_S3:
            # Copy image file in remote S3 to local S3.
            Thread(
                target=lambda: self._local_s3_repo.save(local_filepath, s3_filepath),
            ).start()
        model_kwargs = {
            'organization_device_name': f'{organization_name}/{device_name}',
            'datetime': datetime.now(timezone.utc).isoformat(),
            's3_filepath': s3_filepath,
        }
        camera_obj = CameraImageModel(**model_kwargs)
        camera_obj.save()
        # try:
        #     local_camera_obj = LocalCameraImageModel(**model_kwargs)
        #     local_camera_obj.save()
        # except Exception as e:
        #     Logger.w('RemoteCommand.take_picture', f'Failed to save came image data to local dynamodb : {e}')
        return res

    def start_logging(self, organization_name: str, device_name: str, params: RemoteCommandParams, target: str) -> None:
        topic = f'{settings.AWS_IOT_COMMAND_TOPIC_NAME}/{organization_name}/{device_name}'
        cmd_json = {
            'cmd': CommandList.STATR_LOGGING.value,
            'target': target,
            'cmd_id': str(params.cmd_id),
        }
        self._publisher.publish(
            topic=topic,
            message=cmd_json,
        )

    def stop_logging(self, organization_name: str, device_name: str, params: RemoteCommandParams, target: str) -> None:
        topic = f'{settings.AWS_IOT_COMMAND_TOPIC_NAME}/{organization_name}/{device_name}'
        cmd_json = {
            'cmd': CommandList.STOP_LOGGING.value,
            'target': target,
            'cmd_id': str(params.cmd_id),
        }
        self._publisher.publish(
            topic=topic,
            message=cmd_json,
        )

    def beep(self, organization_name: str, device_name: str, params: RemoteCommandParams) -> None:
        topic = f'{settings.AWS_IOT_COMMAND_TOPIC_NAME}/{organization_name}/{device_name}'
        cmd_json = {
            'cmd': CommandList.BEEP.value,
            'cmd_id': str(params.cmd_id),
        }
        self._publisher.publish(
            topic=topic,
            message=cmd_json,
        )

    def get_status(self, organization_name: str, device_name: str, params: RemoteCommandParams) -> None:
        topic = f'{settings.AWS_IOT_COMMAND_TOPIC_NAME}/{organization_name}/{device_name}'
        cmd_json = {
            'cmd': CommandList.GET_STATUS.value,
            'cmd_id': str(params.cmd_id),
        }
        self._publisher.publish(
            topic=topic,
            message=cmd_json,
        )

    def start_streaming(
        self,
        organization_name: str, device_name: str,
        params: RemoteCommandParams,
        url: str,
    ) -> None:
        topic = f'{settings.AWS_IOT_COMMAND_TOPIC_NAME}/{organization_name}/{device_name}'
        cmd_json = {
            'cmd': CommandList.STATR_LOGGING.value,
            'url': url,
            'cmd_id': str(params.cmd_id),
        }
        self._publisher.publish(
            topic=topic,
            message=cmd_json,
        )
