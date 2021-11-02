import PySimpleGUI as sg
import asyncio
import time
import random

sg.theme('DarkAmber')
layout = [
    [sg.Text('Enter username'), sg.InputText(key='Name')],
    [sg.Text('Enter password'), sg.InputText(password_char='*', key='Pass')],
    [sg.Button('Ok'), sg.Button('Cancel')]
]
window = sg.Window('Title', layout)

async def ui():
    while True:
        event, values = window.read(timeout=1)
        if event in (None, 'Cancel'):
            break
        if event != '__TIMEOUT__':
            print("You entered", values)
        await asyncio.sleep(0.0001)
    window.close()

async def background():
    while True:
        print(random.randint(2, 209120))
        await asyncio.sleep(1)

async def wait_list():
    await asyncio.wait([background(), ui()])

if __name__ == '__main__':
    loop = asyncio.get_event_loop()
    loop.run_until_complete(wait_list())
    loop.close()