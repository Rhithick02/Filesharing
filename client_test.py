import asyncio
import networking

async def client_thing():
    await networking.port_scanner()

if __name__ == '__main__':
    asyncio.get_event_loop().run_until_complete(client_thing())
    asyncio.get_event_loop().run_forever()
