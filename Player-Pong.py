import socket
import pygame
import time

# Game Settings (same as Server.py)
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 480
PADDLE_WIDTH = 15
PADDLE_HEIGHT = 100
BALL_SIZE = 20
PADDLE_SPEED = 10

# Pygame Initialization
pygame.init()
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Pong - Player")

# Paddle and Ball Positions
paddle2_y = SCREEN_HEIGHT // 2 - PADDLE_HEIGHT // 2
ball_x = SCREEN_WIDTH // 2
ball_y = SCREEN_HEIGHT // 2

# Network Settings
SERVER_IP = 'server_ip_here'  # Replace with the server's IP address
SERVER_PORT = 12345

def connect_to_server():
    client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client.connect((SERVER_IP, SERVER_PORT))
    return client

def game_loop(client_socket):
    global paddle2_y, ball_x, ball_y

    while True:
        # Receive ball position and paddle1 position from server
        data = client_socket.recv(1024).decode('utf-8')
        if data:
            ball_x, ball_y, paddle1_y = map(int, data.split(','))

        # Move paddle (controlled by AI)
        if ball_y > paddle2_y + PADDLE_HEIGHT // 2:
            paddle2_y += PADDLE_SPEED
        elif ball_y < paddle2_y + PADDLE_HEIGHT // 2:
            paddle2_y -= PADDLE_SPEED

        paddle2_y = max(0, min(paddle2_y, SCREEN_HEIGHT - PADDLE_HEIGHT))

        # Send paddle position to server
        client_socket.send(str(paddle2_y).encode('utf-8'))

        # Draw game
        screen.fill((0, 0, 0))
        pygame.draw.rect(screen, (255, 255, 255), (0, paddle1_y, PADDLE_WIDTH, PADDLE_HEIGHT))
        pygame.draw.rect(screen, (255, 255, 255), (SCREEN_WIDTH - PADDLE_WIDTH, paddle2_y, PADDLE_WIDTH, PADDLE_HEIGHT))
        pygame.draw.circle(screen, (255, 255, 255), (ball_x, ball_y), BALL_SIZE // 2)
        pygame.display.flip()

        time.sleep(0.01)

if __name__ == "__main__":
    client_socket = connect_to_server()
    game_loop(client_socket)
