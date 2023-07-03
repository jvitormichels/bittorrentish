import socket
import threading
import time
import json
import os
from datetime import datetime

from RepeatedTimer import RepeatedTimer

TRACKER_IP = socket.gethostname()
TRACKER_PORT = 29283
FILES_FOLDER = 'files'

class Client:
    def __init__(self):
        self.host = socket.gethostname()
        self.listening_port = 0
        self.lock = threading.Lock()

    def start(self):
        client_thread = threading.Thread(target=self.listen_requests, args=())
        client_thread.start()
        ping_tracker_timer = RepeatedTimer(10, self.ping_tracker)
        send_file_list_timer = RepeatedTimer(180, self.send_tracker_file_list)

    def ping_tracker(self):
        tracker_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        tracker_socket.connect((TRACKER_IP, TRACKER_PORT))
        data = self.get_data_to_tracker("ping")
        tracker_socket.send(data.encode())
        data = tracker_socket.recv(1024).decode()
        print(f"{self.listening_port} - {datetime.now().strftime('%d/%m/%Y %H:%M:%S')} - Received peer list from tracker \n{data}")
        # print("-- Peer list --\n" + data)
        tracker_socket.close()

    def get_data_to_tracker(self, msg):
        if msg == 'ping':
            data = { "port": self.listening_port }
        elif msg == 'file_list':
            file_list = self.get_file_list()
            data = { "port": self.listening_port, 'files': file_list }
        data['msg'] = msg
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

    def send_tracker_file_list(self):
        data = self.get_data_to_tracker("file_list")

        tracker_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        tracker_socket.connect((TRACKER_IP, TRACKER_PORT))
        tracker_socket.send(data.encode())
        tracker_socket.close()

    def get_file_list(self):
        file_list = []
        if os.path.exists(FILES_FOLDER):
            file_list = os.listdir(FILES_FOLDER)
        else:
            os.makedirs(FILES_FOLDER)

        return file_list

if __name__ == '__main__':
    client = Client()
    client.start()