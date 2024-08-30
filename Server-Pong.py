import socket
import threading
import pygame
import random
import time

# Game Settings (as before)
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 480
PADDLE_WIDTH = 15
PADDLE_HEIGHT = 100
BALL_SIZE = 20
PADDLE_SPEED = 10
BALL_SPEED_X = 5
BALL_SPEED_Y = 5

# Pygame Initialization
pygame.init()
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Pong - Server")

# Paddle and Ball Positions
paddle1_y = SCREEN_HEIGHT // 2 - PADDLE_HEIGHT // 2
paddle2_y = SCREEN_HEIGHT // 2 - PADDLE_HEIGHT // 2
ball_x = SCREEN_WIDTH // 2
ball_y = SCREEN_HEIGHT // 2
ball_dx = BALL_SPEED_X
ball_dy = BALL_SPEED_Y

# Network Settings
SERVER_IP = '0.0.0.0'  # Listen on all interfaces
SERVER_PORT = 12345

def handle_client(client_socket):
    global paddle2_y, ball_x, ball_y, ball_dx, ball_dy
    while True:
        # Receive paddle position from client
        data = client_socket.recv(1024).decode('utf-8')
        if data:
            paddle2_y = int(data)

        # Send ball position and paddle1 position to client
        send_data = f"{ball_x},{ball_y},{paddle1_y}"
        client_socket.send(send_data.encode('utf-8'))

def start_server():
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.bind((SERVER_IP, SERVER_PORT))
    server.listen(1)
    print("Server listening on:", SERVER_IP, SERVER_PORT)

    client_socket, addr = server.accept()
    print(f"Connection established with {addr}")

    client_handler = threading.Thread(target=handle_client, args=(client_socket,))
    client_handler.start()

def move_ball():
    global ball_x, ball_y, ball_dx, ball_dy, paddle1_y, paddle2_y

    ball_x += ball_dx
    ball_y += ball_dy

    # Ball collision with top/bottom walls
    if ball_y <= 0 or ball_y >= SCREEN_HEIGHT - BALL_SIZE:
        ball_dy = -ball_dy

    # Ball collision with paddles
    if ball_x <= PADDLE_WIDTH and paddle1_y < ball_y < paddle1_y + PADDLE_HEIGHT:
        ball_dx = -ball_dx
    if ball_x >= SCREEN_WIDTH - PADDLE_WIDTH - BALL_SIZE and paddle2_y < ball_y < paddle2_y + PADDLE_HEIGHT:
        ball_dx = -ball_dx

    # Ball out of bounds (scoring)
    if ball_x <= 0 or ball_x >= SCREEN_WIDTH - BALL_SIZE:
        ball_x, ball_y = SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2  # Reset ball position
        ball_dx = random.choice([BALL_SPEED_X, -BALL_SPEED_X])
        ball_dy = random.choice([BALL_SPEED_Y, -BALL_SPEED_Y])

def draw_game():
    screen.fill((0, 0, 0))
    pygame.draw.rect(screen, (255, 255, 255), (0, paddle1_y, PADDLE_WIDTH, PADDLE_HEIGHT))
    pygame.draw.rect(screen, (255, 255, 255), (SCREEN_WIDTH - PADDLE_WIDTH, paddle2_y, PADDLE_WIDTH, PADDLE_HEIGHT))
    pygame.draw.circle(screen, (255, 255, 255), (ball_x, ball_y), BALL_SIZE // 2)
    pygame.display.flip()

def game_loop():
    global paddle1_y

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                return

        keys = pygame.key.get_pressed()
        if keys[pygame.K_UP]:
            paddle1_y -= PADDLE_SPEED
        if keys[pygame.K_DOWN]:
            paddle1_y += PADDLE_SPEED

        paddle1_y = max(0, min(paddle1_y, SCREEN_HEIGHT - PADDLE_HEIGHT))

        move_ball()
        draw_game()
        time.sleep(0.01)

if __name__ == "__main__":
    server_thread = threading.Thread(target=start_server)
    server_thread.start()
    game_loop()
