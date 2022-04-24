from typing import Dict, Union
import json

import boto3


class MessagePublisher:

    def __init__(self):
        self._iot_client = boto3.client('iot-data')

    def publish(self, topic: str, message: Union[str, Dict]) -> None:
        if isinstance(message, dict):
            payload = json.dumps(message, ensure_ascii=False)
        else:
            payload = message
        self._iot_client.publish(
            topic=topic,
            qos=1,
            payload=payload
        )
