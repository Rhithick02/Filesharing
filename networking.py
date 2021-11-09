import socket
import asyncio
import traceback
import websockets

my_NAME = socket.gethostname()
with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as s:
    s.connect(('8.8.8.8', 53))
    my_IP = s.getsockname()[0]

print(my_NAME, my_IP)

async def port_scanner():
    if not(my_IP[:3] == '192' or my_IP[:3] == '10.' or my_IP[:3] == '172'):
        print("This is not a private network...\nSHUTTING DOWN!!")
        exit()
    ip_range = '.'.join(my_IP.split('.')[:3])
    for i in range(1, 255):
        target_ip = f"{ip_range}.{i}"
        print(target_ip)
        uri = f"ws://{target_ip}:1111"
        try:
            connection = await websockets.connect(uri)
            await connection.send("Hello")
            async for message in connection:
                print(message)
                await asyncio.sleep(0.0001)
        except ConnectionRefusedError:
            print("Server connection refused.")
        except ConnectionError, OSError:
            pass
        except websockets.exceptions.ConnectionClosed:
            print("Connection closed")
        except:
            traceback.print_exc()


        
#second parameter is path which we dont need
async def register_client(websocket, _):
    async for message in websocket:
        print(message)
        await websocket.send("Hi there")

if __name__ == '__main__':
    start_server = websockets.serve(register_client, my_IP, 1111)
    asyncio.get_event_loop().run_until_complete(start_server)
    asyncio.get_event_loop().run_forever()

