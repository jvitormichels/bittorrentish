import socket
import time
import json

from RepeatedTimer import RepeatedTimer

TRACKER_IP = socket.gethostname()
TRACKER_PORT = 29283

def client():
    ping_tracker()
    timer = RepeatedTimer(10, ping_tracker)

def ping_tracker():
    tracker_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    tracker_socket.connect((TRACKER_IP, TRACKER_PORT))
    data = get_data_to_tracker()
    tracker_socket.send(data.encode())
    data = tracker_socket.recv(1024).decode()
    print("-- Peer list --\n" + data)
    tracker_socket.close()

def get_data_to_tracker():
    # wip
    data = { "port": 8080, "have_pieces": ['1.jpg', '2.jpg'], "have_all": False } # substituir pela porta do socker que escuta
    return json.dumps(data)


if __name__ == '__main__':
    client()