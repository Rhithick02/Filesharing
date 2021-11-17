import asyncio
import networking

async def client_thing():
    await networking.port_scanner()

if __name__ == '__main__':
    networking.my_NAME = 'client'
    asyncio.get_event_loop().create_task(client_thing())
    asyncio.get_event_loop().create_task(networking.status_update())
    asyncio.get_event_loop().run_forever()
