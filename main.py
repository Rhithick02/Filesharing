import sys
import time
import random
import asyncio
import PySimpleGUI as sg

# {'filename':"layouts", 'progress':100}
sg.theme('DarkAmber')
shared_files = []
state = 'init'

def create_layout(files):
    file_names = []
    file_action = []
    for idx, file in enumerate(files):
        file_names.append([sg.Text(file['filename'])])
        file_action.append([sg.Button('X', key=f'remove_{idx}')])

    login = [
        [sg.Text('')],
        [sg.Text('Enter username'), sg.InputText(key='Name')],
        [sg.Text('Enter password'), sg.InputText(password_char='*', key='Pass')],
        [sg.Text('', key='login_status', size=(20, 1))],
        [sg.Button('Connect'), sg.Button('Quit')]
    ]
    
    main = [
        [sg.Text('Online', key='connection_status', size=(70, 1)), sg.Button('Share')],
        [sg.Pane([sg.Column(file_names), sg.Column(file_action)])]
    ]

    share = [
        [sg.Text('Select files you would like to share', size=(70, 1))],
        [sg.Input('', key='browsing', size=(70, 1)), sg.FileBrowse()],
        [sg.Text('', key='share_status')],
        [sg.Button('Send'), sg.Button('Abort')]
    ]

    if state == 'init':
        layout = [
            [sg.Pane([
                        sg.Column(login, key='login_panel'), 
                        sg.Column(main, key='main_panel', visible=False),
                        sg.Column(share, key='share_panel', visible=False)
                    ],
                    relief=sg.RELIEF_FLAT
                )
            ]
        ]
    else:
        layout = [
            [sg.Pane([
                        sg.Column(login, key='login_panel', visible=False), 
                        sg.Column(main, key='main_panel', visible=True),
                        sg.Column(share, key='share_panel', visible=False)
                    ],
                    relief=sg.RELIEF_FLAT
                )
            ]
        ]

    return layout

window = sg.Window('Title', create_layout(shared_files))


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
                print(shared_files)
                window.close()
                print("here")
                time.sleep(1)
                print("here")
                window = sg.Window('Title', create_layout(shared_files), finalize=True)
                # window = sg.Window('Dripbox').Layout(create_layout(shared_files))
                # print("here")
                # window = new_window
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