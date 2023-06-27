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
        print(f"\nNova conexão: {client_address}.\n")
        self.lock.acquire()
        self.clients.append(client_socket)
        self.lock.release()

        while True:
            data = client_socket.recv(1024).decode()
            if not data:
                break
            print(f"{client_address} -> " + str(data))
            data = data[::-1]
            client_socket.send(data.encode())
        
        self.lock.acquire()
        print(f"\nCliente {client_address} desconectado.\n")
        self.lock.release()
        client_socket.close()

if __name__ == '__main__':
    tracker = Tracker()
    tracker.start()