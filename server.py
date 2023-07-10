import asyncio
from collections import defaultdict
import json
import random
from websockets.server import serve, WebSocketServerProtocol

CLIENTS = defaultdict(bool)
SUBSCRIPTIONS = defaultdict(set)


async def client_is_connected(websocket: WebSocketServerProtocol):
    if CLIENTS[websocket.id.hex] == False:
        result = {
            'event': 'error',
            'data': 'Client is not connected'
        }
        await websocket.send(json.dumps(result))
    return CLIENTS[websocket.id.hex]


async def create_subscription(websocket: WebSocketServerProtocol, sensor_id: str) -> None:
    while True:
        if websocket.id.hex not in SUBSCRIPTIONS[sensor_id]:
            break

        result = {
            'event': 'new_sensor_data',
            'data': {
                'sensor_id': sensor_id,
                'sensor_readings': 'SOME_DATA'
            }
        }
        await websocket.send(json.dumps(result))
        await asyncio.sleep(random.randint(1, 10))



async def handler(websocket: WebSocketServerProtocol):
    async for message in websocket:
        message_json = json.loads(message)
        if message_json['event'] == 'client_connect':
            CLIENTS[websocket.id.hex] = True
        elif message_json['event'] == 'client_disconnect':
            CLIENTS[websocket.id.hex] = False
        elif message_json['event'] == 'sensor_connection_status':
            is_connected = await client_is_connected(websocket)
            if not is_connected:
                continue
            sensor_id = message_json['data']['sensor_id']
            result = {
                'event': 'sensor_connection_status',
                'data': {
                    'sensor_id': sensor_id,
                    'connected': random.choice([True, False])
                }
            }
            await websocket.send(json.dumps(result))
        elif message_json['event'] == 'subscribe_sensor':
            is_connected = await client_is_connected(websocket)
            if not is_connected:
                continue
            sensor_id = message_json['data']['sensor_id']
            if websocket.id.hex in SUBSCRIPTIONS[sensor_id]:
                continue
            SUBSCRIPTIONS[sensor_id].add(websocket.id.hex)
            asyncio.create_task(create_subscription(websocket, sensor_id))
        elif message_json['event'] == 'unsubscribe_sensor':
            is_connected = await client_is_connected(websocket)
            if not is_connected:
                continue
            sensor_id = message_json['data']['sensor_id']
            SUBSCRIPTIONS[sensor_id].discard(websocket.id.hex)


async def main():
    async with serve(handler, 'localhost', 8765):
        await asyncio.Future()

if __name__ == '__main__':
    asyncio.run(main())