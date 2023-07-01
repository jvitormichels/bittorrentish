import socket
import threading
import time
import json
from datetime import datetime

from RepeatedTimer import RepeatedTimer

TRACKER_IP = socket.gethostname()
TRACKER_PORT = 29283

class Client:
    def __init__(self):
        self.host = socket.gethostname()
        self.listening_port = 0
        self.lock = threading.Lock()

    def start(self):
        client_thread = threading.Thread(target=self.listen_requests, args=())
        client_thread.start()
        timer = RepeatedTimer(10, self.ping_tracker)

    def ping_tracker(self):
        tracker_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        tracker_socket.connect((TRACKER_IP, TRACKER_PORT))
        data = self.get_data_to_tracker()
        tracker_socket.send(data.encode())
        data = tracker_socket.recv(1024).decode()
        print("-- Peer list --\n" + data)
        tracker_socket.close()

    def get_data_to_tracker(self):
        data = { "port": self.listening_port, "have_pieces": ['1.jpg', '2.jpg'], "have_all": False }
        return json.dumps(data)

    def listen_requests(self):
        server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server.listen()
        self.listening_port = server.getsockname()[1]

        while True:
            server_socket, address = server.accept()
            client_thread = threading.Thread(target=self.handle_piece_request, args=(server_socket,))
            client_thread.start()

    def handle_piece_request(self, server_socket):
        client_address = server_socket.getpeername()
        self.lock.acquire()
        print(f"{datetime.now().strftime('%d/%m/%Y %H:%M:%S')} - Connection from another peer: {client_address}")

        stri = "you successfully connected to another peer!"
        server_socket.send(stri.encode())
        self.lock.release()
        server_socket.close()


if __name__ == '__main__':
    client = Client()
    client.start()