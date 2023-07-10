import asyncio
from collections import defaultdict
import json
from typing import Union

from websockets.client import connect
from websockets.exceptions import ConnectionClosedError, ConnectionClosedOK


class Client:
    def __init__(self, host: str, port: Union[str, int]):
        self.host = host
        self.port = int(port)
        self.connect_websocket = connect(f'ws://{host}:{port}')
        self.connect_instance = None
        self.connected = False

        self.task_recv = None
        self.sensor_statuses = {}
        self.callbacks_by_sensor_id = defaultdict(list)
        self.subscribe_by_sensor_id = defaultdict(bool)
    
    async def _task_recv(self):
        while True:
            try:
                message = await self.connect_instance.recv()
            except ConnectionClosedOK:
                pass
            message_json = json.loads(message)
            if message_json['event'] == 'sensor_connection_status':
                sensor_id = message_json['data']['sensor_id']
                connected_status = message_json['data']['connected']
                self.sensor_statuses[sensor_id] = connected_status
            if message_json['event'] == 'new_sensor_data':
                sensor_id = message_json['data']['sensor_id']
                sensor_readings = message_json['data']['sensor_readings']
                for callback, callback_args in self.callbacks_by_sensor_id[sensor_id]:
                    callback(sensor_id, sensor_readings, *callback_args)

    async def _send_message(self, message: dict) -> None:
        if not self.connected:
            raise Exception('Client do not connected')
        error = False
        if self.connect_instance is not None:
            try:
                await self.connect_instance.send(json.dumps(message))
            except ConnectionClosedError:
                error = True
        if self.connect_instance is None or error:
            while True:
                try:
                    self.connect_instance = await self.connect_websocket
                    await self.connect_instance.send(json.dumps(message))
                except ConnectionClosedError:
                    continue
                else:
                    break
    
    async def connect(self) -> None:
        self.connected = True
        message = {'event': 'client_connect', 'data': ''}
        await self._send_message(message)
        self.task_recv = asyncio.create_task(self._task_recv())

    async def disconnect(self) -> None:
        if self.connected:
            message = {'event': 'client_disconnect', 'data': ''}
            await self._send_message(message)
            self.connected = False
            await self.connect_instance.close()
            self.task_recv.cancel()
    
    async def sensor_connected(self, sensor_id: str) -> bool:
        message = {
            'event': 'sensor_connection_status',
            'data': {
                'sensor_id': sensor_id
            }
        }
        await self._send_message(message)
        while sensor_id not in self.sensor_statuses:
            await asyncio.sleep(0.001)
        return self.sensor_statuses.pop(sensor_id)
    
    async def subscribe(self, sensor_id: str) -> None:
        message = {
            'event': 'subscribe_sensor',
            'data': {
                'sensor_id': sensor_id,
            }
        }
        await self._send_message(message)
        self.subscribe_by_sensor_id[sensor_id] = True
    
    async def unsubscribe(self, sensor_id: str) -> None:
        message = {
            'event': 'unsubscribe_sensor',
            'data': {
                'sensor_id': sensor_id,
            }
        }
        await self._send_message(message)
        self.subscribe_by_sensor_id[sensor_id] = False
    
    async def register_callback(self, sensor_id: str, callback, callback_args: tuple):
        self.callbacks_by_sensor_id[sensor_id].append((callback, callback_args))
        if not self.subscribe_by_sensor_id[sensor_id]:
            await self.subscribe(sensor_id)
    
    def remove_callback(self, sensor_id: str) -> None:
        self.callbacks_by_sensor_id.pop(sensor_id, None)
