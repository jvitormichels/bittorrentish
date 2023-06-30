import socket
import time

from RepeatedTimer import RepeatedTimer

TRACKER_IP = socket.gethostname()
TRACKER_PORT = 29283

def client():
    ping_tracker()
    timer = RepeatedTimer(10, ping_tracker)

def ping_tracker():
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client_socket.bind(('', 6881))
    client_socket.connect((TRACKER_IP, TRACKER_PORT))
    data = client_socket.recv(1024).decode()
    print("-- Peer list --\n" + data)
    client_socket.close()


if __name__ == '__main__':
    client()