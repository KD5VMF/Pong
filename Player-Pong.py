import socket
import time

# Game Settings
PADDLE_SPEED = 10
PADDLE_HEIGHT = 100
SCREEN_HEIGHT = 480  # Assuming a fixed screen height for calculations

# Paddle and Ball Positions
paddle2_y = SCREEN_HEIGHT // 2 - PADDLE_HEIGHT // 2
ball_x = SCREEN_HEIGHT // 2
ball_y = SCREEN_HEIGHT // 2

# Scores
score1 = 0
score2 = 0

# Network Settings
SERVER_PORT = 12345
BROADCAST_PORT = 12344

def debug_print(message):
    """Prints a debug message and flushes the output."""
    print(message)
    import sys
    sys.stdout.flush()

def find_server():
    with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as s:
        s.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
        s.bind(('', BROADCAST_PORT))
        debug_print("Listening for server broadcasts...")

        while True:
            data, addr = s.recvfrom(1024)
            message = data.decode('utf-8')
            if message.startswith("PONG_SERVER"):
                _, server_ip, server_port = message.split(':')
                debug_print(f"Found server at {server_ip}:{server_port}")
                return server_ip, int(server_port)

def connect_to_server(server_ip, server_port):
    client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        debug_print("Attempting to connect to the server...")
        client.connect((server_ip, server_port))
        debug_print(f"Connected to server at {server_ip}:{server_port}")
        
        # Wait for the "READY" signal from the server before starting the game
        ready_signal = client.recv(1024).decode('utf-8')
        if ready_signal == "READY":
            debug_print("Received 'READY' signal. Sending ACK...")
            client.send("ACK".encode('utf-8'))  # Send acknowledgment to server
            time.sleep(2)  # brief delay before game starts
    except socket.error as e:
        debug_print(f"Connection failed: {e}")
        client.close()
        return None
    return client

def ai_move_paddle():
    global paddle2_y, ball_y
    if ball_y > paddle2_y + PADDLE_HEIGHT // 2:
        paddle2_y += PADDLE_SPEED
    elif ball_y < paddle2_y + PADDLE_HEIGHT // 2:
        paddle2_y -= PADDLE_SPEED
    paddle2_y = max(0, min(paddle2_y, SCREEN_HEIGHT - PADDLE_HEIGHT))
    debug_print(f"Paddle position updated to {paddle2_y}")

def game_loop(client_socket):
    global paddle2_y, ball_x, ball_y, score1, score2
    debug_print("Starting game loop...")

    while True:
        try:
            debug_print("Waiting to receive data from server...")
            data = client_socket.recv(1024).decode('utf-8')
            if not data:
                debug_print("No data received, exiting...")
                break
            debug_print(f"Data received: {data}")
            ball_x, ball_y, paddle1_y, score1, score2 = map(int, data.split(','))

            # Update AI paddle position
            ai_move_paddle()

            debug_print(f"Sending paddle position to server: {paddle2_y}")
            client_socket.send(str(paddle2_y).encode('utf-8'))
            ack = client_socket.recv(1024).decode('utf-8')
            if ack != "ACK":
                debug_print("Server did not acknowledge properly, exiting...")
                break

            # Display game state in the console
            debug_print(f"Ball position: ({ball_x}, {ball_y}), Paddle1 position: {paddle1_y}, Paddle2 position: {paddle2_y}")
            debug_print(f"Score - Server: {score1}, Player: {score2}")

        except socket.error as e:
            debug_print(f"Connection lost to the server: {e}")
            break

    client_socket.close()
    debug_print("Game loop ended. Socket closed.")

if __name__ == "__main__":
    debug_print("Player starting up...")
    server_ip, server_port = find_server()
    client_socket = connect_to_server(server_ip, server_port)
    if client_socket:
        game_loop(client_socket)
    else:
        debug_print("Failed to connect to the server. Exiting.")
