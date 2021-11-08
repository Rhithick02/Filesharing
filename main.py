import os
import sys
import shutil
import random
import asyncio
import datetime
import PySimpleGUI as sg
import tinymongo as tm
import tinydb

from tinymongo import TinyMongoClient
from layouts import create_layout
from filemanage import get_cache, check_local_file#, get_hash, update_cache

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

async def cache_and_send(path):
    basefile, proper_time, cache_modified, cache_hash, cache_path = await get_cache(path)
    db.Shares.insert({
        'filename': basefile, 
        'share_path': path, 
        'progress': 100,
        'cache': [{'cache_path': cache_path,
                   'cache_time': proper_time,
                   'cache_modified': cache_modified,
                   'cache_hash': cache_hash
                }]
    })
    files = db.Shares.find()
    return files

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
            elif db.Shares.find_one({'share_path': path}):
                window['share_status'].update("File exists!")
            else:
                # Creating cache file
                shared_files =  await cache_and_send(path)
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
    await asyncio.wait([background(), ui(), check_local_file(db)])

if __name__ == '__main__':
    # Responsible for asynchornous process
    loop = asyncio.get_event_loop()
    # Getting the order to run
    loop.run_until_complete(wait_list())
    loop.close()