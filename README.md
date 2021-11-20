# Python_Networking
![Python](https://img.shields.io/badge/Language-Python3.7-orange)
![Networking](https://img.shields.io/badge/Topic-Networking-brightgreen)
![DB](https://img.shields.io/badge/Database-TinyMongo-yellowgreen)
![Sockets](https://img.shields.io/badge/Libraries-Sockets-lightgrey)
![pysimplegui](https://img.shields.io/badge/Libraries-PySimpleGUI-yellow)

Programming in Python using sockets and websockets to establish an intra-network peer-peer network.

## FileSharing
### Description
A platform for peer-peer intra-network file sharing and file synchronising. Developed using websockets library and asynchronous programming in Python and used PySimpleGUI for GUI. 
### Files
  - networking.py

    This file handles straight from the peer connection to closing. It also uses cryptographic encryption for new peers to get connected thus ensuring safety within the network.
  - main.py

    The main.py combines all the files and is responsible for maintaining the GUI using PySimpleGui library.
  - filemanage.py

    filemanage.py is responsible for caching the top 2 Most Recently Modified versions of the file just in case any problem occurs during transfer of file.
  - layouts.py

    This file structures and maintains the layouts for the GUI.
### To run the file
1. pip install -r requirements.txt
2. python3 main.py
