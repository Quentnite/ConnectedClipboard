import socket
import threading
import os
import psutil
import sys

clients = []
BUFFER_SIZE = 4096

def get_local_info():
    """Print local network interfaces for information."""
    for interface, snics in psutil.net_if_addrs().items():
        for snic in snics:
            if snic.family == socket.AF_INET:
                print(f"Interface: {interface}, IPv4: {snic.address}, Netmask: {snic.netmask}")

def get_local_ip():
    """Return local machine's LAN IP address."""
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        s.connect(("8.8.8.8", 80))
        ip = s.getsockname()[0]
    finally:
        s.close()
    return ip

def HandleFile(message, conn):
    filename = message.split("*")[1]
    os.makedirs("File", exist_ok=True)

    with open(f"File/{filename}", "wb") as f:
        while True:
            chunk = conn.recv(BUFFER_SIZE)
            if not chunk:
                break
            if chunk.endswith(b"/EndFileTransfer"):
                f.write(chunk[:-16])  # enlever le marqueur
                break
            f.write(chunk)

    print(f"[+] Fichier reçu : {filename}")
    return filename


def SendFileToClient(filename, client):
    """Renvoie un fichier à un client spécifique"""
    header = f"2*{os.path.basename(filename)}*"
    client.sendall(header.encode("utf-8"))

    with open(filename, "rb") as f:
        while chunk := f.read(BUFFER_SIZE):
            client.sendall(chunk)

    client.sendall(b"/EndFileTransfer")
    print(f"[>] Fichier {filename} envoyé à {client.getpeername()}")



def broadcast(message, sender_conn):
    """Send a message to all connected clients except the sender."""
    for client in clients:
        if client != sender_conn:
            client.sendall(message.encode("utf-8"))

def handle_new_message(message, addr, conn):
    """Handle an incoming message: broadcast text or relay file."""
    if message.startswith("1"):
        broadcast(message, conn)
    elif message.startswith("2"):
        filename = HandleFile(message, conn)
        if filename:
            for client in clients:
                if client != conn:
                    SendFileToClient(filename, client)

def handle_client(conn, addr):
    print(f"[+] Nouveau client connecté : {addr}")
    clients.append(conn)

    try:
        while True:
            header = conn.recv(1024)
            if not header:
                break

            try:
                message = header.decode("utf-8")
            except UnicodeDecodeError:
                continue  # si c'est du binaire, on ignore ici

            if message.startswith("2*"):  # fichier
                filepath = HandleFile(message, conn)
                # 🔥 Rebalancer le fichier à tous les autres
                for client in clients:
                    if client != conn:
                        SendFileToClient(filepath, client)
            else:
                print(f"[{addr}] {message}")
                for client in clients:
                    if client != conn:
                        client.sendall(message.encode("utf-8"))

    except Exception as e:
        print(f"[!] Erreur client {addr}: {e}")
    finally:
        print(f"[-] Client déconnecté : {addr}")
        clients.remove(conn)
        conn.close()

def start_server(host="127.0.0.1", port=5555):
    """Start TCP server and listen for new clients."""
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.bind((host, port))
    server.listen()
    print(f"Server started on {host}:{port}")
    get_local_info()

    while True:
        conn, addr = server.accept()
        threading.Thread(target=handle_client, args=(conn, addr), daemon=True).start()

if __name__ == "__main__":
    ip = get_local_ip()
    port = int(sys.argv[1]) if len(sys.argv) > 1 else int(input(f"Port for server {ip} (default 5555): ") or 5555)
    start_server(host=ip, port=port)
