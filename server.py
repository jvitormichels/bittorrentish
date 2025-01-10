import argparse

import socket
import threading
import json
from datetime import datetime

from RepeatedTimer import RepeatedTimer

BUFFER_SIZE = 4096

class Tracker:
    def __init__(self):
        self.set_args()

        self.updated_client_list = []
        self.last_round_client_list = []
        self.server = None
        self.host = socket.gethostname()
        self.port = 29283
        self.lock = threading.Lock()

    def start(self):
        self.server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server.bind((self.host, self.port))
        self.server.listen(5)
        timer = RepeatedTimer(15, self.update_peer_list)
        print(f"{datetime.now().strftime('%d/%m/%Y %H:%M:%S')} - Tracker iniciado. Aguardando conexões...")

        try:
            self.listen_for_clients()
        except KeyboardInterrupt:
            print("\n\nEncerrando graciosamente...")
            timer.stop()
            self.server.close()

    def listen_for_clients(self):
        while True:
            client_socket, address = self.server.accept()
            client_thread = threading.Thread(target=self.handle_client, args=(client_socket,))
            client_thread.start()

    def handle_client(self, client_socket):
        client_address = client_socket.getpeername()
        self.lock.acquire()

        requester_ip = client_socket.getpeername()[0]
        data = client_socket.recv(BUFFER_SIZE).decode()
        data = json.loads(data)

        if data['msg'] == 'ping':
            print(f"{datetime.now().strftime('%d/%m/%Y %H:%M:%S')} - Ping from {client_address}")
            self.append_client(requester_ip, data)
            peer_list = json.dumps(self.updated_client_list)
            client_socket.send(peer_list.encode())
        elif data['msg'] == 'file_list':
            print(f"{datetime.now().strftime('%d/%m/%Y %H:%M:%S')} - File list from {client_address}")
            self.append_client(requester_ip, data, data['files'])

        self.lock.release()
        client_socket.close()

    def append_client(self, requester_ip, requester_data, file_list=[]):
        comparison_key = 'ip' if self.serve_remote_clients else 'port'
        requester_key_value = requester_ip if self.serve_remote_clients else requester_data['port']

        for client in self.last_round_client_list:
            if client[comparison_key] == requester_key_value:
                client['port'] = requester_data['port']
                if file_list:
                    client['file_list'] = file_list

                return

        to_append = { "ip": requester_ip, "port": requester_data['port'], "file_list": file_list }
        self.last_round_client_list.append(to_append)

    def update_peer_list(self):
        print(f"{datetime.now().strftime('%d/%m/%Y %H:%M:%S')} - Atualizando lista de peers")
        self.updated_client_list = self.merge_arrays(self.updated_client_list, self.last_round_client_list)
        self.last_round_client_list = []

    def merge_arrays(self, arr1, arr2):
        merged = []

        for dict2 in arr2:
            match = next((dict1 for dict1 in arr1 if dict1.get('port') == dict2.get('port')), None)
            if match:
                if "file_list" in match and match['file_list']:
                    if "file_list" in dict2 and dict2['file_list']:
                        merged.append(dict2)
                    else:
                        merged.append(match)
                else:
                    merged.append(dict2)
            else:
                merged.append(dict2)

        return merged

    def set_args(self):
        parser = argparse.ArgumentParser()
        parser.add_argument("--remote", action="store_true", help="Serve remote clients")
        args = parser.parse_args()
        self.serve_remote_clients = args.remote

if __name__ == '__main__':
    tracker = Tracker()
    tracker.start()