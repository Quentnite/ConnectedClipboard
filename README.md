## ConnectedClipboard
ConnectedClipboard is a small Python project that allows you to create a collaborative workspace locally (LAN) or remotely (WAN).
It enables multiple clients to connect to a server, exchange messages, files, and even share content via the clipboard.

---

## Current Features

- Multi-client server based on `socket` and `threading`
- **Real-time** communication between clients
- File transfer between users
- Automatic text copying to clipboard (e.g., path of a received file)
- Startup script `serverNclient.py`:
- - Automatically launches the server in a **new terminal**
- - Launches the client in the current terminal
 - -Port parameter (default `5555`) configurable directly via command

---

## Installation
# Install dependencies
pip install -r requirements.txt

---

## Usage
# Launch server + client automatically
```python
python serverNclient.py
#launches the server in a new terminal and the client in your current terminal with port 5555 (default)

python serverNclient.py 6000
#launches the server in a new terminal and the client in your current terminal with port 6000 (modify as needed)
```

# Launch manually
```python
python server.py        # starts the server. The server will ask for the port
python server.py 5555   # starts the server on port 5555

python client.py        # starts a client. The client will ask for IP and port
```
---

## Project Organization

-server.py → server management (client connections, message/file broadcasting)

-client.py → client application (sending messages, receiving files, clipboard)

-serverNclient.py → utility script to automatically launch server + client

-File/ → directory where received files are stored

---

## Future Developments

Some ideas for the project's future:

# Important ideas:
-Graphical interface (e.g., with tkinter or customtkinter) to simplify usage

-Security improvements: communication encryption (SSL/TLS)

-Screen sharing or specific window sharing

# Secondary 

-User management (usernames, basic authentication)

-Message history (text log or SQLite database)


# If you need help:
Magueur Quentin
quentin.magueur@universite-paris-saclay.fr
Iut d'Orsay BUT 1
