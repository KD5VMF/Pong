import socket
import pygame
import time

# Game Settings (same as Server.py)
SCREEN_WIDTH = pygame.display.Info().current_w
SCREEN_HEIGHT = pygame.display.Info().current_h
PADDLE_WIDTH = 15
PADDLE_HEIGHT = 100
BALL_SIZE = 20
PADDLE_SPEED = 10

# Pygame Initialization
pygame.init()
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.FULLSCREEN)
pygame.display.set_caption("Pong - Player")

# Paddle and Ball Positions
paddle2_y = SCREEN_HEIGHT // 2 - PADDLE_HEIGHT // 2
ball_x = SCREEN_WIDTH // 2
ball_y = SCREEN_HEIGHT // 2

# Scores
score1 = 0
score2 = 0

# Network Settings
SERVER_IP = 'server_ip_here'  # Placeholder, the client will find the server automatically
SERVER_PORT = 12345

def find_server():
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        s.connect(("8.8.8.8", 80))
        ip = s.getsockname()[0]
        server_ip = '.'.join(ip.split('.')[:-1]) + '.255'
    except Exception:
        server_ip = '255.255.255.255'
    finally:
        s.close()
    return server_ip

def connect_to_server():
    server_ip = find_server()
    client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client.connect((server_ip, SERVER_PORT))
    return client

def game_loop(client_socket):
    global paddle2_y, ball_x, ball_y, score1, score2

    while True:
        # Receive ball position, paddle1 position, and scores from server
        data = client_socket.recv(1024).decode('utf-8')
        if data:
            ball_x, ball_y, paddle1_y, score1, score2 = map(int, data.split(','))

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
        draw_scoreboard()
        pygame.display.flip()

        time.sleep(0.01)

def draw_scoreboard():
    font = pygame.font.SysFont(None, 48)
    score_text = font.render(f"Server: {score1}  Player: {score2}", True, (255, 255, 255))
    screen.blit(score_text, (SCREEN_WIDTH // 2 - score_text.get_width() // 2, 20))

if __name__ == "__main__":
    client_socket = connect_to_server()
    game_loop(client_socket)
