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

def get_server_details():
    """Prompts the user for the server IP and port."""
    server_ip = input("Enter the server IP address: ")
    server_port = int(input("Enter the server port: "))
    return server_ip, server_port

def connect_to_server(server_ip, server_port):
    client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client.settimeout(10)  # Increase the timeout to prevent hanging
    try:
        client.connect((server_ip, server_port))
        
        # Wait for the "READY" signal from the server before starting the game
        ready_signal = client.recv(1024).decode('utf-8')
        if ready_signal == "READY":
            client.send("ACK".encode('utf-8'))  # Send acknowledgment to server
            time.sleep(1)  # Wait to ensure synchronization

            start_signal = client.recv(1024).decode('utf-8')
            if start_signal == "START":
                client.send("START_ACK".encode('utf-8'))
                print("Game has started. Good luck!")  # Print once when the game starts
            else:
                return None
        else:
            return None
    except socket.timeout:
        client.close()
        return None
    except socket.error as e:
        client.close()
        return None
    return client

def ai_move_paddle():
    global paddle2_y, ball_y
    if ball_y > paddle2_y + PADDLE_HEIGHT // 2:
        paddle2_y += PADDLE_SPEED
    elif ball_y < paddle2_y + PADDLE_HEIGHT // 2:
        paddle2_y -= PADDLE_SPEED

    # Ensure the paddle can move all the way to the bottom
    paddle2_y = max(0, min(paddle2_y, SCREEN_HEIGHT - PADDLE_HEIGHT))

def game_loop(client_socket):
    global paddle2_y, ball_x, ball_y, score1, score2

    last_score_displayed = None  # Keep track of the last displayed score to reduce printing

    while True:
        try:
            data = client_socket.recv(1024).decode('utf-8')
            if not data:
                break
            
            # Now correctly handle the float values
            ball_x, ball_y, paddle1_y, score1, score2 = map(float, data.split(','))
            ball_x, ball_y = int(ball_x), int(ball_y)
            paddle1_y, score1, score2 = int(paddle1_y), int(score1), int(score2)

            # Update AI paddle position
            ai_move_paddle()

            # Send updated paddle position to server
            client_socket.send(str(paddle2_y).encode('utf-8'))

            # Wait for acknowledgment from the server
            try:
                ack = client_socket.recv(1024).decode('utf-8')
                if ack != "ACK":
                    break
            except socket.timeout:
                break

            # Only print score updates when the score changes
            if (score1, score2) != last_score_displayed:
                print(f"Score - Server: {score1}, Player: {score2}")
                last_score_displayed = (score1, score2)

        except socket.error as e:
            break

    client_socket.close()

if __name__ == "__main__":
    server_ip, server_port = get_server_details()
    client_socket = connect_to_server(server_ip, server_port)
    if client_socket:
        game_loop(client_socket)
    else:
        print("Failed to connect to the server. Exiting.")

