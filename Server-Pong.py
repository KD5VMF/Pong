import socket

# Network Settings
SERVER_PORT = 12345
SERVER_IP = socket.gethostbyname(socket.gethostname())

def start_server():
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.bind((SERVER_IP, SERVER_PORT))
    server.listen(1)
    print(f"Server is listening on {SERVER_IP}:{SERVER_PORT}")
    print("Waiting for a player to connect...")

    client_socket, addr = server.accept()
    print(f"Connection established with {addr}")

    try:
        # Test Message Exchange
        client_socket.send("TEST_MESSAGE_FROM_SERVER".encode('utf-8'))
        print("Sent: TEST_MESSAGE_FROM_SERVER")

        # Receive a message from the client
        data = client_socket.recv(1024).decode('utf-8')
        print(f"Received from client: {data}")

        if data == "TEST_MESSAGE_FROM_CLIENT":
            print("Message exchange successful!")
        else:
            print("Message exchange failed!")

        # Test Latency
        client_socket.send("PING".encode('utf-8'))
        print("Sent: PING")

        data = client_socket.recv(1024).decode('utf-8')
        if data == "PONG":
            print("Latency test successful!")
        else:
            print("Latency test failed!")
    
    except Exception as e:
        print(f"An error occurred: {e}")

    client_socket.close()
    server.close()

if __name__ == "__main__":
    start_server()
