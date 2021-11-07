import os
import sys
import shutil
import random
import asyncio
import datetime
import PySimpleGUI as sg
from layouts import create_layout
import tinymongo as tm
import tinydb
from tinymongo import TinyMongoClient

# Minor change to tinymongo for python 3.8 version
class TinyMongoClient(tm.TinyMongoClient):
    @property
    def _storage(self):
        return tinydb.storages.JSONStorage

# Initialising database
__client__ = TinyMongoClient(os.path.join(os.getcwd(), 'data.db'))
db = __client__['data']

# Getting password
SETTINGS = db.Settings.find_one({'_id': 'settings'})
if not SETTINGS:
    SETTINGS = {'_id': 'settings', 'password': ''}
    db.Settings.insert(SETTINGS)

sg.theme('DarkAmber')
shared_files = db.Shares.find()

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
            if values['Pass'] == SETTINGS['password']:
                state = 'connected'
                window['login_panel'].update(visible=False)
                window['main_panel'].update(visible=True)

        elif event == 'Share':
            window['main_panel'].update(visible=False)
            window['share_panel'].update(visible=True)

        elif event == 'Send':
            path = os.path.normpath(values['browsing'])
            # Check whether the filepath is valid
            if not os.path.isfile(path):
                window['share_status'].update("File Not Found")
            else:
                # Creating cache file
                basefile = os.path.basename(path)
                cache_time = datetime.datetime.utcnow()
                proper_time = cache_time.strftime("%Y%m%d_%H%M%S")
                cache_path = os.path.join(os.getcwd(), f'cache/{basefile}_{proper_time}')
                os.makedirs(cache_path)
                shutil.copy2(path, os.path.join(cache_path, basefile))

                db.Shares.insert({
                    'filename': basefile, 
                    'share_path': values['browsing'], 
                    'progress': 100,
                    'cache': [{'cache_path': cache_path, 'cache_time': proper_time}]
                })
                shared_files = db.Shares.find()
                new_window = sg.Window('Title', create_layout(shared_files, state), finalize=True)
                window.close()
                window = new_window
                window['main_panel'].update(visible=True)
                window['share_panel'].update(visible=False)

        elif event == 'Abort':
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