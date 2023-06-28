import socket

def client():
    host = socket.gethostname()
    port = 29282

    client_socket = socket.socket()
    client_socket.connect((host, port))
    data = client_socket.recv(1024).decode()
    print("-- Peer list --\n" + data)

    client_socket.close()

if __name__ == '__main__':
    client()