import sys
import random
import asyncio
import PySimpleGUI as sg

# User Interface layout definition
sg.theme('DarkAmber')
layout = [
    [sg.Text('')],
    [sg.Text('Enter username'), sg.InputText(key='Name')],
    [sg.Text('Enter password'), sg.InputText(password_char='*', key='Pass')],
    [sg.Text('', key='status', size=(20, 1))],
    [sg.Button('Ok'), sg.Button('Cancel')]
]

window = sg.Window('Title', layout)

# Functions
async def ui():
    while True:
        event, values = window.read(timeout=1)
        if event in (None, 'Cancel'):
            sys.exit()
        if event != '__TIMEOUT__':
            print("You entered", values)
        await asyncio.sleep(0.0001)
    window.close()

async def background():
    while True:
        rando = random.randint(2, 209120)
        window['status'].update(rando)
        await asyncio.sleep(1)

async def wait_list():
    await asyncio.wait([background(), ui()])

if __name__ == '__main__':
    # Responsible for asynchornous process
    loop = asyncio.get_event_loop()
    # Getting the order to run
    loop.run_until_complete(wait_list())
    loop.close()