import subprocess
import sys
import os
import platform

def launch_server(port):
    """Launch server.py in a separate terminal window (cross-platform)."""
    cwd = os.getcwd()
    server_cmd = [sys.executable, "server.py", str(port)]

    system = platform.system()
    if system == "Windows":
        subprocess.Popen(["start", "cmd", "/k"] + server_cmd, shell=True, cwd=cwd)
    elif system == "Linux":
        try:
            subprocess.Popen(["gnome-terminal", "--"] + server_cmd, cwd=cwd)
        except FileNotFoundError:
            subprocess.Popen(["xterm", "-e"] + server_cmd, cwd=cwd)
    elif system == "Darwin":
        apple_script = f'''
        tell application "Terminal"
            do script "cd {cwd} && {sys.executable} server.py {port}"
        end tell
        '''
        subprocess.Popen(["osascript", "-e", apple_script])
    else:
        print(f"[ERROR] Unsupported OS: {system}")

def launch_client(port):
    """Run client.py in the current terminal."""
    subprocess.call([sys.executable, "client.py", str(port)])

if __name__ == "__main__":
    port = int(sys.argv[1]) if len(sys.argv) > 1 else 5555
    launch_server(port)
    launch_client(port)
