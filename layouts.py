import PySimpleGUI as sg
from PySimpleGUI.PySimpleGUI import RELIEF_FLAT

def create_layout(files, state):
    file_names = []
    file_action = []
    for idx, file in enumerate(files):
        file_names.append([sg.Text(file['filename'], size=(70, 1))])
        file_action.append([sg.Button('X', key=f'remove_{idx}')])

    login = [
        [sg.Text('')],
        # [sg.Text('Enter username'), sg.InputText(key='Name')],
        [sg.Text('Enter password'), sg.InputText(password_char='*', key='Pass')],
        [sg.Text('', key='login_status', size=(20, 1))],
        [sg.Button('Connect'), sg.Button('Quit')]
    ]
    
    main = [
        [sg.Text('Online', key='connection_status', size=(70, 1)), sg.Button('Share')],
        [sg.Pane([sg.Column(file_names), sg.Column(file_action)], 
            relief=RELIEF_FLAT, 
            show_handle=False,
            orientation='horizontal'
        )]
    ]

    share = [
        [sg.Text('Select files you would like to share', size=(70, 1))],
        [sg.Input('', key='browsing', size=(70, 1)), sg.FileBrowse()],
        [sg.Text('', key='share_status', size=(20, 1))],
        [sg.Button('Send'), sg.Button('Abort')]
    ]

    if state == 'init':
        login_panel = sg.Column(login, key='login_panel')
        main_panel = sg.Column(main, key='main_panel', visible=False)
        share_panel = sg.Column(share, key='share_panel', visible=False)
    else:
        login_panel = sg.Column(login, key='login_panel', visible=False)
        main_panel = sg.Column(main, key='main_panel')
        share_panel = sg.Column(share, key='share_panel', visible=False)

    layout = [
        [sg.Pane([login_panel, main_panel, share_panel], relief=sg.RELIEF_FLAT)]
    ]

    return layout