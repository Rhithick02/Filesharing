import os
import json
import socket
import asyncio
import traceback
import websockets
import tinymongo as tm
import tinydb

from tinymongo import TinyMongoClient

# Minor change to tinymongo for python 3.8 version
class TinyMongoClient(tm.TinyMongoClient):
    @property
    def _storage(self):
        return tinydb.storages.JSONStorage

ok = False
my_NAME = socket.gethostname()
with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as s:
    s.connect(('8.8.8.8', 53))
    my_IP = s.getsockname()[0]

print(my_NAME, my_IP)

__client__ = TinyMongoClient(os.path.join(os.getcwd(), 'data.db'))
db = __client__['data']
shared_files = db.Shares.find()
CONNECTIONS = set()

class ConnectionHandler:
    websocket = None
    hostname = None #Of the connected machine
    uri = None
    state = 'Disconnected'

    async def send(self, message):
        try:
            data = json.dumps(message)
            await self.websocket.send(data)
        except:
            traceback.print_exc()

    async def recv(self):
        try:
            message = await self.websocket.recv()
            data = json.loads(message)
            return data
        except:
            traceback.print_exc()
    
    async def file_send(self, filepath):
        finish = False
        self.state = 'Transfer'
        with open(filepath, 'rb') as f:
            while not finish:
                buffer = f.read(8192)
                if not buffer:
                    buffer = ':EOF'
                    finish = True
                print("Send chunk")
                await self.websocket.send(buffer)                
                await asyncio.sleep(0.0001)
        self.state = 'Connected'

    async def file_recv(self, filename, cache_modified, cache_hash, cache_time):
        # Set up directories for file to save to
        cache_path = os.path.normpath(os.path.join(os.getcwd(), f"cache/{filename}_{cache_time}"))
        os.makedirs(cache_path)

        # Receive the file
        self.state = 'Transfer'
        with open(os.path.join(cache_path, filename), 'wb') as f:
            while True:
                buffer = await self.websocket.recv()
                if buffer == ':EOF':
                    break
                print("Recv chunk")
                f.write(buffer)
                await asyncio.sleep(0.0001)
        # TODO:
        # Verify the remote hash with local hash
        self.state = 'Connected' 


    async def login(self):
        try:
            self.websocket = await websockets.connect(self.uri)
        except ConnectionRefusedError:
            print("Server connection refused.")
            return
        except ConnectionError:
            print("Connection Error")
            return
        except OSError:
            print("OS Error.")
            return
        except websockets.exceptions.ConnectionClosed:
            print("Connection closed")
        except:
            traceback.print_exc()
            return

        await self.send({'hostname': my_NAME})
        challenge = await self.recv()
        if 'challenge' not in challenge or 'hostname' not in challenge:
            return
        if len(challenge['challenge']) > 1024 or len(challenge['hostname']) > 1024:
            return
        self.hostname = challenge['hostname']
        
        # TODO: 
        # Challenge hashing has to be done

        password = {'password': 'password'}
        await self.send(password)
        confirmation = await self.recv()
        confirmed = confirmation.get('Connection')
        if confirmed == 'authorized':
            self.state = 'Connected'
            print(f"Connected to {self.hostname}")
            return

        # TODO:
        # Deal with unauthoried

    async def welcome(self) -> bool:
        greeting = await self.recv()
        if 'hostname' not in greeting:
            return False
        if len(greeting['hostname']) > 1024:
            return False
        self.hostname = greeting['hostname']
        challenge = {'challenge' : '8r4sdvb84edrf4bgh5re47y3kjan', 'hostname': my_NAME}
        await self.send(challenge)
        password = await self.recv()
        if 'password' not in password:
            return False
        if len(password['password']) > 1024:
            return False
        # TODO:
        # Actual crypt stuff has to be done
        if password['password'] == 'password':
            await self.send({'Connection': 'authorized'})
            self.state = 'Connected'
            asyncio.get_event_loop().create_task(self.listener())
            print(f"New connection from {self.hostname}")
            return True
        await self.send({'Connection': 'unauthorized'})
        return False

    async def listener(self):
        try:
            async for message in self.websocket:
                data = json.loads(message)
                op_type = data.get('op_type')
                if op_type == 'status':
                    print(f"{self.hostname} status:\n{data['connections']}\n{data['shares']}")
                    # Get list of connections and check if any of those are neighbour, 
                    # we are not connected to
                    # Check the shares to see if we are looking for any changes to those files
                    # compare those remote shared files against our own
                    global ok
                    if not ok and my_NAME == 'client':
                        ok = True
                        await self.send({'op_type': 'request',
                                         'filename': 'networking.py'})
                if op_type == 'request':
                    print(f"{self.hostname} request:\n{data['filename']}")
                    # Prep all the file details the receipient needs
                    # Send the file
                    for share in shared_files:
                        if share['filename'] == data['filename']:
                            filename = share['filename']
                            cache_modified = share['cache'][-1]['cache_modified']
                            cache_path = share['cache'][-1]['cache_path']
                            cache_hash = share['cache'][-1]['cache_hash']
                            cache_time = share['cache'][-1]['cache_time']
                            await self.send({'op_type': 'sending',
                                             'filename': filename,
                                             'cache_hash': cache_hash,
                                             'cache_modified': cache_modified,
                                             'cache_time': cache_time})

                            await self.file_send(os.path.join(cache_path, filename))
                if op_type == 'sending':
                    print(f"{self.hostname} confirms:\n{data['filename']}")
                    # Take all the details for the file and receive it.
                    await self.file_recv(data['filename'], data['cache_modified'], data['cache_hash'], data['cache_time'])
                    print("Download complete...")
        except websockets.exceptions.ConnectionClosed:
            print(f"Connection Closed from {self.hostname}")
            await unregister(self)
        except:
            traceback.print_exc()
            await unregister(self)
        # finally:
            
    async def close(self):
        state = 'Disconnected'
        try:
            await self.websocket.close()
        except:
            traceback.print_exc()
    

class ServerHandler(ConnectionHandler):
    def __init__(self, websocket):
        self.websocket = websocket


class ClientHandler(ConnectionHandler):
    def __init__(self, uri):
        self.uri = uri

async def port_scanner():
    if not(my_IP[:3] == '192' or my_IP[:3] == '10.' or my_IP[:3] == '172'):
        print("This is not a private network...\nSHUTTING DOWN!!")
        exit()
    ip_range = '.'.join(my_IP.split('.')[:3])
    for i in range(1, 255):
        target_ip = f"{ip_range}.{i}"
        print(target_ip)
        uri = f"ws://{target_ip}:1111"
        connection = ClientHandler(uri)
        await connection.login()
        if connection.state == 'Connected':
            CONNECTIONS.add(connection)
            asyncio.get_event_loop().create_task(connection.listener())
        await asyncio.sleep(0.0001)
        
# Second parameter is path which we dont need
# Server / Receiver side happenings
async def register_client(websocket, _):
    connection = ServerHandler(websocket)
    done = False
    while True:
        if not done:
            if await connection.welcome():
                CONNECTIONS.add(connection)
                done = True
        await asyncio.sleep(0.0001)

async def unregister(connection):
    await connection.close()
    try:
        CONNECTIONS.remove(connection)
    except:
        traceback.print_exc()

async def status_update():
    while True:
        print(f"Updating Status...{len(CONNECTIONS)}")
        connection_list = []
        share_list = []
        for CONNECTION in CONNECTIONS:
            connection_list.append({'hostname': CONNECTION.hostname, 'uri': CONNECTION.uri})
        
        for share in shared_files:
            # from pprint import pprint
            # pprint(share)
            share_list.append({'filename': share['filename'],
                               'cache_modified': share['cache'][-1]['cache_modified'],
                               'cache_hash': share['cache'][-1]['cache_hash'],
                               'cache_time': share['cache'][-1]['cache_time']})

        for CONNECTION in CONNECTIONS:
            if CONNECTION.state == 'Connected':
                await CONNECTION.send({'op_type': 'status', 
                                       'hostname': my_NAME, 
                                       'connections': connection_list,
                                       'shares': share_list})
        await asyncio.sleep(10)

if __name__ == '__main__':
    start_server = websockets.serve(register_client, my_IP, 1111)
    asyncio.get_event_loop().run_until_complete(start_server)
    asyncio.get_event_loop().create_task(status_update())
    asyncio.get_event_loop().run_forever()

