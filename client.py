import socket
import threading
import time
import json
import os
from collections import Counter
import random
from datetime import datetime

from RepeatedTimer import RepeatedTimer

TRACKER_IP = socket.gethostname()
TRACKER_PORT = 29283
FILES_FOLDER = "files"
BUFFER_SIZE = 4096

class Client:
    def __init__(self):
        self.host = socket.gethostname()
        self.listening_port = 0
        self.lock = threading.Lock()
        self.peer_list = []

    def start(self):
        client_thread = threading.Thread(target=self.listen_requests, args=()).start()
        download_timer = RepeatedTimer(30, self.manage_downloads)
        ping_tracker_timer = RepeatedTimer(10, self.ping_tracker)
        send_file_list_timer = RepeatedTimer(20, self.send_tracker_file_list)

    def ping_tracker(self):
        try:
            tracker_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            tracker_socket.connect((TRACKER_IP, TRACKER_PORT))
            data = self.get_data_to_tracker("ping")
            tracker_socket.send(data.encode())
            data = tracker_socket.recv(BUFFER_SIZE).decode()
            self.peer_list = json.loads(data)
            print(f"\n{datetime.now().strftime('%d/%m/%Y %H:%M:%S')} - Received peer list from tracker")
            for peer in self.peer_list: print(peer)
            tracker_socket.close()
        except (ConnectionRefusedError, ConnectionResetError):
            print(f"\n{datetime.now().strftime('%d/%m/%Y %H:%M:%S')} - Communication problem with tracker")

    def get_data_to_tracker(self, msg):
        if msg == 'ping':
            data = { "port": self.listening_port }
        elif msg == 'file_list':
            file_list = self.get_file_list()
            data = { "port": self.listening_port, 'files': file_list }
        data['msg'] = msg
        return json.dumps(data)

    def manage_downloads(self):
        filename = self.select_file()
        if not filename: return
        peer_info = self.select_peer(filename)
        self.request_piece(filename, peer_info)
        print(f"\n{datetime.now().strftime('%d/%m/%Y %H:%M:%S')} - Send request for file to: {peer_info['ip']}:{peer_info['port']}")
        print(f" * Filename: {filename}")

    def request_piece(self, filename, peer_info):
        download_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        try:
            download_socket.connect((peer_info['ip'], peer_info['port']))
            
            data = json.dumps({"filename": filename})
            download_socket.send(data.encode())

            file_path = os.path.join(self.get_files_folder_path(), filename)

            with open(file_path, "wb") as f:
                while True:
                    bytes_read = download_socket.recv(BUFFER_SIZE)
                    if not bytes_read:
                        break
                    f.write(bytes_read)

            download_socket.close()
        except (ConnectionRefusedError, ConnectionResetError):
            print(f"\n{datetime.now().strftime('%d/%m/%Y %H:%M:%S')} - Communication problem with peer {peer_info['ip']}:{peer_info['port']}")

    def select_file(self):
        rank = self.rank_file_rarity(self.peer_list)
        available_files = set()
        for item in self.peer_list:
            file_list = item["file_list"]
            available_files.update(file_list)

        available_file_list = list(available_files)
        missing_files =set(available_files) - set(self.get_file_list())
        selected_file = ""
        for available_file in available_file_list:
            if available_file in missing_files:
                selected_file = available_file
                break
        
        return selected_file

    def rank_file_rarity(self, data):
        all_values = []
        for item in data:
            file_list = item["file_list"]
            all_values.extend(file_list)

        counts = Counter(all_values)
        return counts.most_common()[::-1]

    def select_peer(self, filename):
        peers = self.peer_list
        available_peers = [peer for peer in peers if filename in peer['file_list']]
        selected_peer = random.choice(available_peers)
        return selected_peer

    def listen_requests(self):
        server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server.listen(5)
        self.listening_port = server.getsockname()[1]

        while True:
            server_socket, address = server.accept()
            client_thread = threading.Thread(target=self.handle_piece_request, args=(server_socket,))
            client_thread.start()

    def handle_piece_request(self, file_transfer_socket):
        client_address = file_transfer_socket.getpeername()
        data = json.loads(file_transfer_socket.recv(BUFFER_SIZE).decode())
        filename = data['filename']
        self.lock.acquire()
        print(f"\n{datetime.now().strftime('%d/%m/%Y %H:%M:%S')} - Receiving request for file from: {client_address}")
        print(f" * Filename: {filename}")

        file_path = os.path.join(self.get_files_folder_path(), filename)
        with open(file_path, "rb") as f:
            while True:
                bytes_read = f.read(BUFFER_SIZE)
                if not bytes_read:
                    break
                file_transfer_socket.sendall(bytes_read)

        self.lock.release()
        file_transfer_socket.close()

    def send_tracker_file_list(self):
        data = self.get_data_to_tracker("file_list")
        try:
            tracker_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            tracker_socket.connect((TRACKER_IP, TRACKER_PORT))
            tracker_socket.send(data.encode())
            tracker_socket.close()
        except (ConnectionRefusedError, ConnectionResetError):
            print(f"\n{datetime.now().strftime('%d/%m/%Y %H:%M:%S')} - Communication problem with tracker")

    def get_file_list(self):
        file_list = []
        if os.path.exists(FILES_FOLDER):
            file_list = os.listdir(FILES_FOLDER)
        else:
            os.makedirs(FILES_FOLDER)

        return file_list

    def get_files_folder_path(self):
        current_dir = os.getcwd()
        full_path = os.path.join(current_dir, FILES_FOLDER)
        return full_path

if __name__ == '__main__':
    client = Client()
    client.start()