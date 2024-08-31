import socket
import threading
import pygame
import random
import time

# Pygame Initialization
pygame.init()
screen = pygame.display.set_mode((0, 0), pygame.FULLSCREEN)
SCREEN_WIDTH, SCREEN_HEIGHT = screen.get_size()

# Game Settings
PADDLE_WIDTH = 15
PADDLE_HEIGHT = 100
BALL_SIZE = 20
INITIAL_PADDLE_SPEED = 20
INITIAL_BALL_SPEED_X = 10
INITIAL_BALL_SPEED_Y = 10

# Difficulty Scaling
difficulty_increment = 1.2  # Faster speed increase per level
ai_reaction_time = 0.005  # AI reaction time for faster response

pygame.display.set_caption("Pong - Server")

# Paddle and Ball Positions
paddle1_y = SCREEN_HEIGHT // 2 - PADDLE_HEIGHT // 2
paddle2_y = SCREEN_HEIGHT // 2 - PADDLE_HEIGHT // 2
ball_x = SCREEN_WIDTH // 2
ball_y = SCREEN_HEIGHT // 2
ball_dx = INITIAL_BALL_SPEED_X
ball_dy = INITIAL_BALL_SPEED_Y
paddle_speed = INITIAL_PADDLE_SPEED

# Scores
score1 = 0
score2 = 0
current_level = 1

# Network Settings
SERVER_PORT = 12345
client_connected = False

def get_lan_ip_address():
    try:
        # Create a socket and attempt to connect to a common LAN address
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))  # Using Google's DNS server as a safe bet for a LAN IP
        lan_ip = s.getsockname()[0]
        s.close()
        return lan_ip
    except Exception as e:
        print(f"Failed to get LAN IP address: {e}")
        return '127.0.0.1'  # Fallback to localhost if no LAN IP is available

SERVER_IP = get_lan_ip_address()

def move_ball():
    global ball_x, ball_y, ball_dx, ball_dy, paddle1_y, paddle2_y, score1, score2, current_level

    ball_x += ball_dx
    ball_y += ball_dy

    if ball_y <= 0 or ball_y >= SCREEN_HEIGHT - BALL_SIZE:
        ball_dy = -ball_dy

    # Check collision with paddles and adjust ball direction
    if ball_x <= PADDLE_WIDTH and paddle1_y < ball_y < paddle1_y + PADDLE_HEIGHT:
        ball_dx = -ball_dx
    if ball_x >= SCREEN_WIDTH - PADDLE_WIDTH - BALL_SIZE and paddle2_y < ball_y < paddle2_y + PADDLE_HEIGHT:
        ball_dx = -ball_dx

    # Check if ball goes out of bounds and update score
    if ball_x <= 0:
        score2 += 1
        reset_ball()
        check_winner()
    if ball_x >= SCREEN_WIDTH - BALL_SIZE:
        score1 += 1
        reset_ball()
        check_winner()

def reset_ball():
    global ball_x, ball_y, ball_dx, ball_dy, paddle_speed
    ball_x, ball_y = SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2
    ball_dx = random.choice([INITIAL_BALL_SPEED_X, -INITIAL_BALL_SPEED_X]) * difficulty_increment
    ball_dy = random.choice([INITIAL_BALL_SPEED_Y, -INITIAL_BALL_SPEED_Y]) * difficulty_increment
    paddle_speed = INITIAL_PADDLE_SPEED * difficulty_increment

def draw_game():
    screen.fill((0, 0, 0))
    pygame.draw.rect(screen, (255, 255, 255), (0, paddle1_y, PADDLE_WIDTH, PADDLE_HEIGHT))
    pygame.draw.rect(screen, (255, 255, 255), (SCREEN_WIDTH - PADDLE_WIDTH, paddle2_y, PADDLE_WIDTH, PADDLE_HEIGHT))
    pygame.draw.circle(screen, (255, 255, 255), (ball_x, ball_y), BALL_SIZE // 2)
    draw_scoreboard()
    pygame.display.flip()

def draw_scoreboard():
    font = pygame.font.SysFont(None, 48)
    score_text = font.render(f"Server: {score1}  Player: {score2}  Level: {current_level}", True, (255, 255, 255))
    screen.blit(score_text, (SCREEN_WIDTH // 2 - score_text.get_width() // 2, 20))

def ai_move_paddle():
    global paddle1_y, ball_y
    time.sleep(ai_reaction_time)  # Simulate AI reaction time
    if ball_y > paddle1_y + PADDLE_HEIGHT // 2:
        paddle1_y += paddle_speed
    elif ball_y < paddle1_y + PADDLE_HEIGHT // 2:
        paddle1_y -= paddle_speed
    # Ensure the paddle can move fully up and down
    paddle1_y = max(0, min(paddle1_y, SCREEN_HEIGHT - PADDLE_HEIGHT))

def check_winner():
    global current_level, score1, score2

    if score1 >= 25 or score2 >= 25:
        winner = "Server" if score1 > score2 else "Player"
        show_winner(winner)
        score1, score2 = 0, 0
        current_level += 1
        increase_difficulty()

def show_winner(winner):
    screen.fill((0, 0, 0))
    font = pygame.font.SysFont(None, 72)
    text = font.render(f"{winner} Wins! Level Up!", True, (255, 255, 255))
    screen.blit(text, (SCREEN_WIDTH // 2 - text.get_width() // 2, SCREEN_HEIGHT // 2 - text.get_height() // 2))
    pygame.display.flip()
    time.sleep(3)  # Display winner for 3 seconds before moving to the next level

def increase_difficulty():
    global difficulty_increment, ai_reaction_time
    difficulty_increment += 0.1  # Increase the difficulty increment
    ai_reaction_time = max(0.002, ai_reaction_time - 0.001)  # Faster AI reaction with a limit

def handle_client(client_socket):
    global paddle2_y, ball_x, ball_y, ball_dx, ball_dy, score1, score2, client_connected
    client_connected = True

    try:
        # Initial handshake
        client_socket.send("READY".encode('utf-8'))
        client_ack = client_socket.recv(1024).decode('utf-8')
        if client_ack == "ACK":
            print("Client acknowledged, starting game...")
        else:
            print("Client did not acknowledge properly.")
            return

        # Wait for the client to confirm it's ready to start
        time.sleep(1)
        client_socket.send("START".encode('utf-8'))
        start_ack = client_socket.recv(1024).decode('utf-8')
        if start_ack == "START_ACK":
            print("Client is ready. Game is starting...")
        else:
            print("Client did not respond to start signal.")
            return

        while True:
            # Move the ball and server paddle
            move_ball()
            ai_move_paddle()

            # Send ball position, paddle1 position, and scores to client
            send_data = f"{ball_x},{ball_y},{paddle1_y},{score1},{score2}"
            client_socket.send(send_data.encode('utf-8'))

            # Receive updated paddle position from client
            data = client_socket.recv(1024).decode('utf-8')
            if data:
                if data == "ACK":
                    continue  # Ignore ACK messages
                paddle2_y = int(float(data))  # Properly handle the float value

                # Ensure the player's paddle can move all the way to the top and bottom
                paddle2_y = max(0, min(paddle2_y, SCREEN_HEIGHT - PADDLE_HEIGHT))

            # Always send acknowledgment after receiving data
            client_socket.send("ACK".encode('utf-8'))

            # Draw the game screen
            draw_game()

    except Exception as e:
        print(f"An error occurred: {e}")
    finally:
        client_socket.close()
        print("Client connection closed.")

def show_waiting_screen(message):
    screen.fill((0, 0, 0))
    font = pygame.font.SysFont(None, 72)
    lines = message.split('\n')
    for i, line in enumerate(lines):
        text = font.render(line, True, (255, 255, 255))
        screen.blit(text, (SCREEN_WIDTH // 2 - text.get_width() // 2, SCREEN_HEIGHT // 2 - text.get_height() // 2 + i * 50))
    pygame.display.flip()

def start_server():
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.bind((SERVER_IP, SERVER_PORT))
    server.listen(1)
    show_waiting_screen(f"Waiting for Player to Connect...\nIP: {SERVER_IP}\nPort: {SERVER_PORT}")
    print("Server listening on:", SERVER_IP, SERVER_PORT)

    client_socket, addr = server.accept()
    print(f"Connection established with {addr}")

    handle_client(client_socket)

def game_loop():
    global client_connected

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                return
            if event.type == pygame.KEYDOWN and event.key == pygame.K_F8:
                pygame.quit()
                return

        if client_connected:
            draw_game()
        time.sleep(0.005)  # Reduced delay for faster game loop

if __name__ == "__main__":
    server_thread = threading.Thread(target=start_server)
    server_thread.start()

    game_loop()
