import asyncio

async def hi():
    print("hi")

async def hello():
    print("hello")
    await asyncio.sleep(2)

async def wait_list():
    await asyncio.wait([hello(), hi()])

if __name__ == '__main__':
    loop = asyncio.get_event_loop()
    loop.run_until_complete(wait_list())
    loop.close()