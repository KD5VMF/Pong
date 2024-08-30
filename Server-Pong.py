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
PADDLE_SPEED = 10
BALL_SPEED_X = 5
BALL_SPEED_Y = 5

pygame.display.set_caption("Pong - Server")

# Paddle and Ball Positions
paddle1_y = SCREEN_HEIGHT // 2 - PADDLE_HEIGHT // 2
paddle2_y = SCREEN_HEIGHT // 2 - PADDLE_HEIGHT // 2
ball_x = SCREEN_WIDTH // 2
ball_y = SCREEN_HEIGHT // 2
ball_dx = BALL_SPEED_X
ball_dy = BALL_SPEED_Y

# Scores
score1 = 0
score2 = 0

# Network Settings
SERVER_PORT = 12345
client_connected = False

def get_ip_address():
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        s.connect(("8.8.8.8", 80))
        ip = s.getsockname()[0]
    except Exception:
        ip = '127.0.0.1'
    finally:
        s.close()
    return ip

SERVER_IP = get_ip_address()

def move_ball():
    global ball_x, ball_y, ball_dx, ball_dy, paddle1_y, paddle2_y, score1, score2

    ball_x += ball_dx
    ball_y += ball_dy

    if ball_y <= 0 or ball_y >= SCREEN_HEIGHT - BALL_SIZE:
        ball_dy = -ball_dy

    if ball_x <= PADDLE_WIDTH and paddle1_y < ball_y < paddle1_y + PADDLE_HEIGHT:
        ball_dx = -ball_dx
    if ball_x >= SCREEN_WIDTH - PADDLE_WIDTH - BALL_SIZE and paddle2_y < ball_y < paddle2_y + PADDLE_HEIGHT:
        ball_dx = -ball_dx

    if ball_x <= 0:
        score2 += 1
        reset_ball()
    if ball_x >= SCREEN_WIDTH - BALL_SIZE:
        score1 += 1
        reset_ball()

def reset_ball():
    global ball_x, ball_y, ball_dx, ball_dy
    ball_x, ball_y = SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2
    ball_dx = random.choice([BALL_SPEED_X, -BALL_SPEED_X])
    ball_dy = random.choice([BALL_SPEED_Y, -BALL_SPEED_Y])

def draw_game():
    screen.fill((0, 0, 0))
    pygame.draw.rect(screen, (255, 255, 255), (0, paddle1_y, PADDLE_WIDTH, PADDLE_HEIGHT))
    pygame.draw.rect(screen, (255, 255, 255), (SCREEN_WIDTH - PADDLE_WIDTH, paddle2_y, PADDLE_WIDTH, PADDLE_HEIGHT))
    pygame.draw.circle(screen, (255, 255, 255), (ball_x, ball_y), BALL_SIZE // 2)
    draw_scoreboard()
    pygame.display.flip()

def draw_scoreboard():
    font = pygame.font.SysFont(None, 48)
    score_text = font.render(f"Server: {score1}  Player: {score2}", True, (255, 255, 255))
    screen.blit(score_text, (SCREEN_WIDTH // 2 - score_text.get_width() // 2, 20))

def ai_move_paddle():
    global paddle1_y, ball_y
    if ball_y > paddle1_y + PADDLE_HEIGHT // 2:
        paddle1_y += PADDLE_SPEED
    elif ball_y < paddle1_y + PADDLE_HEIGHT // 2:
        paddle1_y -= PADDLE_SPEED
    paddle1_y = max(0, min(paddle1_y, SCREEN_HEIGHT - PADDLE_HEIGHT))

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
            print(f"Sending data to client: {send_data}")
            client_socket.send(send_data.encode('utf-8'))

            # Receive updated paddle position from client
            data = client_socket.recv(1024).decode('utf-8')
            if data:
                print(f"Received data from client: {data}")
                paddle2_y = int(data)

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
        time.sleep(0.01)

if __name__ == "__main__":
    server_thread = threading.Thread(target=start_server)
    server_thread.start()

    game_loop()
