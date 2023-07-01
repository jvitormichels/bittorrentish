import socket
import threading
import json
from datetime import datetime

from RepeatedTimer import RepeatedTimer

class Tracker:
    def __init__(self):
        self.updated_client_list = []  # Lista de clientes conectados
        self.last_round_client_list = []
        self.server = None
        self.host = socket.gethostname()  # Endereço IP do Tracker
        self.port = 29282  # Porta para o Tracker ouvir as conexões
        self.max_clients = 40  # Número máximo de clientes que podem se conectar
        self.lock = threading.Lock()  # Lock para sincronização

    def start(self):
        # estudar tirar a limitação de clientes no tracker
        self.server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server.bind((self.host, self.port))
        self.server.listen(5)
        timer = RepeatedTimer(15, self.update_peer_list)
        print("Tracker iniciado. Aguardando conexões...")

        while True:
            client_socket, address = self.server.accept()
            if len(self.updated_client_list) < self.max_clients:
                client_thread = threading.Thread(target=self.handle_client, args=(client_socket,))
                client_thread.start()
            else:
                client_socket.send("Servidor cheio. Tente novamente mais tarde.".encode())
                client_socket.close()

    def handle_client(self, client_socket):
        client_address = client_socket.getpeername()
        self.lock.acquire()
        self.append_client(client_socket)
        print(f"{datetime.now().strftime('%d/%m/%Y %H:%M:%S')} - Connection from {client_address}")

        peer_list = self.connected_peers()
        client_socket.send(peer_list.encode())
        self.lock.release()
        client_socket.close()

    def append_client(self, client_socket):
        requester_ip = client_socket.getpeername()[0]
        requester_data = client_socket.recv(1024).decode()
        requester_data = json.loads(requester_data)
        # print("Data from client\n" + data)
        for client in self.last_round_client_list:
            if client['ip'] == requester_ip:
                client['port'] = requester_data['port']
                client['have_pieces'] = requester_data['have_pieces']
                client['have_all'] = requester_data['have_all']
                return
                
        requester_data['ip'] = requester_ip
        self.last_round_client_list.append(requester_data)

    # def append_client_gambiarra(self, client_socket):
    #     requester_ip = client_socket.getpeername()[0]
    #     requester_port = client_socket.getpeername()[1]
    #     requester_data = client_socket.recv(1024).decode()
    #     requester_data = json.loads(requester_data)
    #     # print("Data from client\n" + data)
    #     for client in self.last_round_client_list:
    #         if client['id'] == requester_port:
    #             client['port'] = requester_data['port']
    #             client['have_pieces'] = requester_data['have_pieces']
    #             client['have_all'] = requester_data['have_all']
    #             return
                
    #     requester_data['ip'] = requester_ip
    #     requester_data['id'] = requester_port
    #     self.last_round_client_list.append(requester_data)

    def update_peer_list(self):
        self.updated_client_list = self.last_round_client_list
        self.last_round_client_list = []

    def connected_peers(self):
        # estudar um join método bonitinho build-in pra transformar array em string
        client_list = ""
        for idx, client_data in enumerate(self.updated_client_list, start=1):
            client_list += f"{client_data}\n"
        return client_list

if __name__ == '__main__':
    tracker = Tracker()
    tracker.start()