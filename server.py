import socket

def launch_server():
    hostname = socket.gethostname()
    port = 5000

    server_socket = socket.socket()
    server_socket.bind((hostname, port))

    server_socket.listen()
    conn, address = server_socket.accept()
    print("Connection from: " + str(address))

    while True:
        data = conn.recv(1024).decode()
        # if not data
        #     break
        print("from connected user: " + str(data))
        data = input(' -> ')
        conn.send(data.encode())

    conn.close()

if __name__ == '__main__':
    launch_server()