import json
import time
from datetime import datetime, timedelta
from typing import Any, Callable, Dict

from awscrt import io, mqtt
from awsiot import mqtt_connection_builder

from ...settings import settings
from ...utils.config import AWSConfig
from ...utils.logger import Logger


class MessageSubscriber:

    def __init__(
        self,
        endpoint: str = AWSConfig.IOT_ENDPOINT,
        certificate_path: str = AWSConfig.IOT_CERTIFICATE_PATH,
        private_key_path: str = AWSConfig.IOT_PRIVATE_KEY_PATH,
        amazon_root_ca_path: str = AWSConfig.IOT_ROOT_CA_PATH,
    ):
        self._endpoint = endpoint
        self._certificate_path = certificate_path
        self._private_key_path = private_key_path
        self._amazon_root_ca_path = amazon_root_ca_path
        self._client_id = 'central_server'
        self.connect_mqtt()

    def connect_mqtt(self):
        event_loop_group = io.EventLoopGroup(1)
        host_resolver = io.DefaultHostResolver(event_loop_group)
        client_bootstrap = io.ClientBootstrap(event_loop_group, host_resolver)
        self._mqtt_connection = mqtt_connection_builder.mtls_from_path(
            endpoint=self._endpoint,
            cert_filepath=self._certificate_path,
            pri_key_filepath=self._private_key_path,
            client_bootstrap=client_bootstrap,
            ca_filepath=self._amazon_root_ca_path,
            client_id=self._client_id,
            clean_session=False,
            keep_alive_secs=6
        )
        connect_future = self._mqtt_connection.connect()
        connect_future.result()
        print("Connected!")

    def disconnect_mqtt(self):
        disconnect_future = self._mqtt_connection.disconnect()
        disconnect_future.result()

    def subscribe(self, topic: str, message_callback: Callable):
        Logger.i('MessageSubscriber.subscribe', f'Subscribing to {topic}')

        def on_message_received(topic, payload, dup, qos, retain, **kwargs):
            msg_json = json.loads(payload.decode())
            print('MessageSubscriber', "Received message from topic '{}': {}".format(topic, msg_json))
            message_callback(topic, msg_json)

        subscribe_future, packet_id = self._mqtt_connection.subscribe(
            topic=topic,
            qos=mqtt.QoS.AT_LEAST_ONCE,
            callback=on_message_received
        )

    def unsubscribe(self, topic: str) -> None:
        self._mqtt_connection.unsubscribe(topic=topic)


class CentralServerMessageHandler:

    _instance = None
    _subscriber = MessageSubscriber()
    _callbacks = {}
    _responses = {}

    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def subscribe(self):
        self._subscriber.subscribe(
            topic=settings.AWS_IOT_CENTRAL_SERVER_TOPIC_NAME,
            message_callback=self._message_handler
        )

    def _message_handler(self, topic: str, msg_json: Dict):
        self._refresh_callback_queues()
        if 'cmd_id' not in msg_json:
            Logger.w('CentralServerMessageHandler', 'cmd_id key not found in message, ignoreing')
            return
        if msg_json['cmd_id'] not in self._callbacks:
            Logger.w(
                'CentralServerMessageHandler',
                f'callbacks with target cmd_id [{msg_json["cmd_id"]}] not found in registred callbacks, ignoreing'
            )
        else:
            # for cb in self._callbacks[msg_json['cmd_id']]['callback']:
            #     self._responses[msg_json['cmd_id']] = cb(topic, msg_json)
            cb = self._callbacks[msg_json['cmd_id']]['callback']
            # self._responses[msg_json['cmd_id']] = cb(topic, msg_json)
            cb(topic, msg_json)
        self._responses[msg_json['cmd_id']] = msg_json

    def add_receive_callback(
        self,
        cmd_id: str,
        callback: Callable,  # lambda topic, msg: ~
        expires_dt: datetime = datetime.now() + timedelta(minutes=10),
    ):
        cmd_id = str(cmd_id)
        cb_json = {
            'callback': callback,
            'expires_at': expires_dt,
        }
        # if cmd_id not in self._callbacks:
        #     self._callbacks[cmd_id] = [cb_json]
        # else:
        #     self._callbacks[cmd_id].append(cb_json)
        self._callbacks[cmd_id] = cb_json

    def wait_until_response(self, cmd_id: str, timeout_sec: float = 60) -> Any:
        cmd_id = str(cmd_id)
        base_dt = datetime.now()
        while (datetime.now() - base_dt).total_seconds() < timeout_sec:
            print(self._responses.keys()) 
            if cmd_id in self._responses:
                res = self._responses.pop(cmd_id)
                return res
            time.sleep(0.05)
        Logger.w('CentralServerMessageHandler.wait_until_response', 'timeout')
        return None

    def add_receive_callback_and_wait_response(
        self,
        cmd_id: str,
        callback: Callable,  # lambda topic, msg: ~
        expires_dt: datetime = datetime.now() + timedelta(minutes=10),
        timeout_sec: float = 60
    ) -> Any:
        cmd_id = str(cmd_id)
        self.add_receive_callback(cmd_id, callback, expires_dt)
        return self.wait_until_response(cmd_id, timeout_sec)

    def _refresh_callback_queues(self):
        now_dt = datetime.now()
        self._callbacks = {
            cmd_id: v for cmd_id, v in self._callbacks.items() if v['expires_at'] and v['expires_at'] > now_dt
        }
