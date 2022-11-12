import json
from datetime import datetime
from enum import Enum
from typing import Any
from uuid import uuid4

from kafka import KafkaProducer

from ...settings import settings


class JobType(Enum):
    IMAGE_CLASSIFICATION = 'IMAGE_CLASSIFICATION'
    OBJECT_DETECTION = 'OBJECT_DETECTION'
    SEGMENTATION = 'SEGMENTATION'


class KafkaAnalysisJobRequest:

    def __init__(
        self,
        topic_name: str = settings.ANALYSIS_SERVER_TOPIC_NAME,
        server_host: str = settings.ANALYSIS_SERVER_HOST,
        port: int = settings.ANALYSIS_SERVER_JOB_PORT,
    ):
        self._topic_name = topic_name
        self._server_host = server_host
        self._port = port
        self._producer = KafkaProducer(
            bootstrap_servers=[f'{server_host}:{port}']
        )

    def send(self, organization_name: str, device_name: str) -> Any:
        job_id = uuid4()
        data = {
            'id': job_id,
            'datetime': datetime.now().isoformat(),
            'organization': organization_name,
            'device': device_name,
            'job_type': 'TODO',
            'job_params': 'TODO',
        }
        result = self._producer.send(self._topic_name, value=json.dumps(data).encode('utf-8'))
        return result
