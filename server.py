import socket
import threading

class Tracker:
    def __init__(self):
        self.clients = []  # Lista de clientes conectados
        self.server = None
        self.host = socket.gethostname()  # Endereço IP do Tracker
        self.port = 29282  # Porta para o Tracker ouvir as conexões
        self.max_clients = 4  # Número máximo de clientes que podem se conectar
        self.lock = threading.Lock()  # Lock para sincronização

    def start(self):
        # estudar tirar a limitação de clientes no tracker
        self.server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server.bind((self.host, self.port))
        self.server.listen(5)
        print("Tracker iniciado. Aguardando conexões...")

        while True:
            client_socket, address = self.server.accept()
            if len(self.clients) < self.max_clients:
                client_thread = threading.Thread(target=self.handle_client, args=(client_socket,))
                client_thread.start()
            else:
                client_socket.send("Servidor cheio. Tente novamente mais tarde.".encode())
                client_socket.close()

    def handle_client(self, client_socket):
        client_address = client_socket.getpeername()
        self.lock.acquire()
        self.append_client(client_socket)

        print(f"Nova conexão: {client_address}.")

        peer_list = self.connected_peers()
        client_socket.send(peer_list.encode())
        self.lock.release()
        client_socket.close()

    def append_client(self, client_socket):
        client_address = client_socket.getpeername()
        client_data = f"{client_address[0]}:{client_address[1]}"
        
        if client_data not in self.clients:
            self.clients.append(client_data)

    def connected_peers(self):
        client_list = ""
        for idx, client_data in enumerate(self.clients, start=1):
            client_list += f"{client_data}\n"
        return client_list

if __name__ == '__main__':
    tracker = Tracker()
    tracker.start()