import socket
import threading
from tkinter import filedialog
import clipboard
import os
import psutil
import sys

BUFFER_SIZE = 4096

def receive_messages(sock):
    """Thread target: receive messages from the server and handle clipboard or files."""
    while True:
        try:
            data = sock.recv(1024)
            if not data:
                break
            message = data.decode("utf-8")
            if message[0] == "2":
                HandleFile(message, sock)
            else:
                to_clipboard = message[2:]
                print(f"[INFO] Clipboard updated: {to_clipboard}")
                clipboard.copy(to_clipboard)
        except:
            break

def envoyer_fichier_without_path(sock):
    """Open file dialog, send the selected file to the server."""
    filepath = filedialog.askopenfilename()
    if filepath:
        filename = os.path.basename(filepath)
        sock.send(f"2*{filename}*".encode("utf-8"))
        with open(filepath, "rb") as f:
            sock.sendfile(f)
        sock.send(b"/EndFileTransfer")

def HandleFile(message, client):
    """Receive a file sent by the server and save it under ./File/."""
    file_name = message.split("*")[1]
    os.makedirs("File", exist_ok=True)
    with open(f"File/{file_name}", "wb") as f:
        while True:
            data = client.recv(BUFFER_SIZE)
            if not data:
                return
            if data.endswith(b"/EndFileTransfer"):
                f.write(data[:-16])
                return file_name
            f.write(data)

def get_local_info():
    """Print network interfaces and IPv4 addresses (for debugging)."""
    for interface, snics in psutil.net_if_addrs().items():
        for snic in snics:
            if snic.family == socket.AF_INET:
                print(f"Interface: {interface}, IPv4: {snic.address}, Netmask: {snic.netmask}")

def send_message(sock, msg):
    """Send clipboard text or trigger file sending based on prefix."""
    if msg.startswith("1"):
        sock.sendall(msg.encode("utf-8"))
    elif msg.startswith("2") and len(msg) == 1:
        envoyer_fichier_without_path(sock)

def start_client(host="127.0.0.1", port=5555):
    """Main client loop: connect, start receiver thread, handle user input."""
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.connect((host, port))
    print(f"[+] Connected to server {host}:{port}")

    threading.Thread(target=receive_messages, args=(sock,), daemon=True).start()

    while True:
        msg = input("> ")
        if msg.lower() in ["q", "quit"]:
            break
        if msg:
            send_message(sock, msg)

    sock.close()

def get_local_ip():
    """Get local machine's LAN IP address."""
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        s.connect(("8.8.8.8", 80))
        ip = s.getsockname()[0]
    finally:
        s.close()
    return ip

if __name__ == "__main__":
    get_local_info()
    if len(sys.argv) > 1:
        port = int(sys.argv[1])
        ip = get_local_ip()
    else:
        ip = input("Server IP: ")
        port = int(input(f"Port of {ip}: "))
    start_client(host=ip, port=port)
