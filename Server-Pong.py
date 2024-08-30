import socket
import time

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
        for i in range(10):  # Simulate 10 game updates
            # Send paddle position and ball position
            message = f"UPDATE_{i}_PADDLE1_POS,BALL_POS"
            client_socket.send(message.encode('utf-8'))
            print(f"Sent: {message}")

            # Receive updated paddle position from client
            data = client_socket.recv(1024).decode('utf-8')
            print(f"Received from client: {data}")
        
        print("Extended message exchange successful!")

        # Latency Test
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
