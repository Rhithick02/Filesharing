import PySimpleGUI as sg

def create_layout(files):
    file_names = []
    file_action = []
    for idx, file in files:
        file_names.append(files['filename'])
        file_action.append(sg.Button('X', key=f'remove_{idx}'))

    login = [
        [sg.Text('')],
        [sg.Text('Enter username'), sg.InputText(key='Name')],
        [sg.Text('Enter password'), sg.InputText(password_char='*', key='Pass')],
        [sg.Text('', key='login_status', size=(20, 1))],
        [sg.Button('Connect'), sg.Button('Quit')]
    ]
    
    main = [
        [sg.Text('Online', key='connection_status', size=(70, 1)), sg.Button('Share')],
        [sg.Pane([
            sg.Column(file_names),
            sg.Column(file_action)
        ])]
    ]
    
    share_files = sg.Column(file_names)
    share_action = sg.Column(file_action)

    share = [
        [sg.Text('Select files you would like to share', size=(70, 1))],
        [sg.Input('', key='browsing', size=(70, 1)), sg.FileBrowse()],
        [sg.Text('', key='share_status')],
        [sg.Button('Send'), sg.Button('Abort')]
    ]

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

    return layout

# def rebuild(files):
#     new_window = sg.Window('Title', create_layout(files))
#     return new_window