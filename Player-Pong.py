import socket
import pygame
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

pygame.display.set_caption("Pong - Player")

# Paddle and Ball Positions
paddle2_y = SCREEN_HEIGHT // 2 - PADDLE_HEIGHT // 2
ball_x = SCREEN_WIDTH // 2
ball_y = SCREEN_HEIGHT // 2

# Scores
score1 = 0
score2 = 0

# Network Settings
SERVER_PORT = 12345
BROADCAST_PORT = 12344

def find_server():
    with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as s:
        s.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
        s.bind(('', BROADCAST_PORT))
        print("Listening for server broadcasts...")

        while True:
            data, addr = s.recvfrom(1024)
            message = data.decode('utf-8')
            if message.startswith("PONG_SERVER"):
                _, server_ip, server_port = message.split(':')
                print(f"Found server at {server_ip}:{server_port}")
                return server_ip, int(server_port)

def connect_to_server(server_ip, server_port):
    client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client.connect((server_ip, server_port))
    print(f"Connected to server at {server_ip}:{server_port}")
    return client

def game_loop(client_socket):
    global paddle2_y, ball_x, ball_y, score1, score2

    while True:
        data = client_socket.recv(1024).decode('utf-8')
        if data:
            ball_x, ball_y, paddle1_y, score1, score2 = map(int, data.split(','))

        if ball_y > paddle2_y + PADDLE_HEIGHT // 2:
            paddle2_y += PADDLE_SPEED
        elif ball_y < paddle2_y + PADDLE_HEIGHT // 2:
            paddle2_y -= PADDLE_SPEED

        paddle2_y = max(0, min(paddle2_y, SCREEN_HEIGHT - PADDLE_HEIGHT))

        client_socket.send(str(paddle2_y).encode('utf-8'))

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
    server_ip, server_port = find_server()
    client_socket = connect_to_server(server_ip, server_port)
    game_loop(client_socket)
