import asyncio

from sensor_client import Client

def my_callback(sensor_id: str, some_readigs: str, arg1):
    print(sensor_id, some_readigs, arg1)

        
async def main():
    client = Client('localhost', '8765')
    await client.connect()

    sensor_status = await client.sensor_connected('ABC')
    print(sensor_status)

    await client.register_callback('ABC', my_callback, (42, ))
    await asyncio.sleep(60)
    
    await client.disconnect()


asyncio.run(main())