import sys
import random
import asyncio
import PySimpleGUI as sg
from layouts import create_layout

sg.theme('DarkAmber')
shared_files = []
state = 'init'

window = sg.Window('Title', create_layout(shared_files, state), finalize=True)

async def ui():
    global state, window
    while True:
        event, values = window.read(timeout=1)
        if state == 'init':
            state = 'login'

        if event in (None, 'Quit'):
            sys.exit()

        elif event == 'Connect':
            state = 'connected'
            window['login_panel'].update(visible=False)
            window['main_panel'].update(visible=True)

        elif event == 'Share':
            window['main_panel'].update(visible=False)
            window['share_panel'].update(visible=True)

        elif event in ('Send', 'Abort'):
            if event == 'Send':
                shared_files.append({'filename': values['browsing'], 'progress': 100})
                new_window = sg.Window('Title', create_layout(shared_files, state), finalize=True)
                window.close()
                window = new_window
            window['main_panel'].update(visible=True)
            window['share_panel'].update(visible=False)

        elif event != '__TIMEOUT__':
            print("You entered", values)

        await asyncio.sleep(0.0001)

async def background():
    global state, window
    while True:
        rando = random.randint(2, 209120)
        if state == 'login':
            window['login_status'].update(rando)
        await asyncio.sleep(1)

async def wait_list():
    await asyncio.wait([background(), ui()])

if __name__ == '__main__':
    # Responsible for asynchornous process
    loop = asyncio.get_event_loop()
    # Getting the order to run
    loop.run_until_complete(wait_list())
    loop.close()