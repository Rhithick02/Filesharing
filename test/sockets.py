import socket
import asyncio
import traceback
import websockets

my_NAME = socket.gethostname()
my_IP = socket.gethostbyname(my_NAME)
with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as s:
    s.connect(('8.8.8.8', 53))
    my_IP = s.getsockname()

if __name__ == '__main__':
    start_server = websockets.serve()
