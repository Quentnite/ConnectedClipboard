import socket
import threading
from tkinter import filedialog
import clipboard
import os
import psutil
import sys



BUFFER_SIZE = 4096


def receive_messages(sock):
    """Thread de réception côté client"""
    while True:
        try:
            header = sock.recv(1024)
            if not header:
                break

            try:
                message = header.decode("utf-8")
            except UnicodeDecodeError:
                continue  # si jamais binaire, on ignore

            if message.startswith("2*"):  # début de transfert fichier
                filename = message.split("*")[1]
                receive_file(sock, filename)
            else:
                to_clipboard = message[2:]
                print(f"[INFO] Clipboard updated: {to_clipboard}")
                clipboard.copy(to_clipboard)

        except Exception as e:
            print(f"[!] Erreur réception: {e}")
            break

def envoyer_fichier_without_path(sock):
    """Open file dialog, send the selected file to the server."""
    filepath = filedialog.askopenfilename()
    if filepath:
        filename = os.path.basename(filepath)
        sock.send(f"2*{filename}*".encode("utf-8"))
        with open(filepath, "rb") as f:
            while chunk := f.read(4096):
                sock.sendall(chunk)
        sock.send(b"/EndFileTransfer")
        print(f"[>] Fichier envoyé : {filename}")

def receive_file(sock, filename):
    """Réception d'un fichier en binaire"""
    os.makedirs("File", exist_ok=True)
    filepath = f"File/{filename}"

    with open(filepath, "wb") as f:
        while True:
            chunk = sock.recv(BUFFER_SIZE)
            if not chunk:
                break
            if chunk.endswith(b"/EndFileTransfer"):
                f.write(chunk[:-16])  # on enlève le marqueur
                break
            f.write(chunk)

    print(f"[+] Nouveau fichier reçu : {filename} (sauvé dans {filepath})")


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
