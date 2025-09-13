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

def HandleFile(message, client):
    """Receive file data from a client and store it under ./File/."""
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

def SendFileToClient(filename, client):
    """Send a stored file to a specific client."""
    file_path = f"File/{filename}"
    if os.path.isfile(file_path):
        client.send(f"2*{filename}".encode("utf-8"))
        with open(file_path, "rb") as f:
            client.sendfile(f)
        client.send(b"/EndFileTransfer")

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
    """Handle a single client connection (thread target)."""
    print(f"[+] New client connected: {addr}")
    clients.append(conn)
    try:
        while True:
            try:
                data = conn.recv(1024)
                if not data:
                    break
                handle_new_message(data.decode("utf-8"), addr, conn)
            except ConnectionResetError:
                # Client closed connection unexpectedly
                break
    finally:
        print(f"[-] Client disconnected: {addr}")
        if conn in clients:
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
