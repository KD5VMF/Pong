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
BROADCAST_PORT = 12344
BROADCAST_INTERVAL = 1  # in seconds
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

def broadcast_server():
    with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as s:
        s.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
        while not client_connected:
            message = f"PONG_SERVER:{SERVER_IP}:{SERVER_PORT}"
            s.sendto(message.encode('utf-8'), ('<broadcast>', BROADCAST_PORT))
            time.sleep(BROADCAST_INTERVAL)

def handle_client(client_socket):
    global paddle2_y, ball_x, ball_y, ball_dx, ball_dy, score1, score2, client_connected
    client_connected = True

    # Initial handshake
    client_socket.send("READY".encode('utf-8'))
    client_ack = client_socket.recv(1024).decode('utf-8')
    if client_ack == "ACK":
        print("Client acknowledged, starting game...")
    else:
        print("Client did not acknowledge properly.")
        return

    # Wait a moment to ensure both sides are ready
    time.sleep(1)

    while True:
        try:
            # Receive paddle position from client
            data = client_socket.recv(1024).decode('utf-8')
            if data:
                paddle2_y = int(data)
                client_socket.send("ACK".encode('utf-8'))  # Acknowledge receipt of data
        except:
            break

        # Send ball position, paddle1 position, and scores to client
        send_data = f"{ball_x},{ball_y},{paddle1_y},{score1},{score2}"
        try:
            client_socket.send(send_data.encode('utf-8'))
            server_ack = client_socket.recv(1024).decode('utf-8')
            if server_ack != "ACK":
                print("Failed to receive acknowledgment from client.")
        except:
            break

def start_server():
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.bind((SERVER_IP, SERVER_PORT))
    server.listen(1)
    show_waiting_screen("Waiting for Player to Connect...")
    print("Server listening on:", SERVER_IP, SERVER_PORT)

    client_socket, addr = server.accept()
    print(f"Connection established with {addr}")

    client_handler = threading.Thread(target=handle_client, args=(client_socket,))
    client_handler.start()

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

def show_waiting_screen(message):
    screen.fill((0, 0, 0))
    font = pygame.font.SysFont(None, 72)
    text = font.render(message, True, (255, 255, 255))
    screen.blit(text, (SCREEN_WIDTH // 2 - text.get_width() // 2, SCREEN_HEIGHT // 2 - text.get_height() // 2))
    pygame.display.flip()

def game_loop():
    global paddle1_y, client_connected

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                return
            if event.type == pygame.KEYDOWN and event.key == pygame.K_F8:
                pygame.quit()
                return

        if client_connected:
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
    broadcast_thread = threading.Thread(target=broadcast_server, daemon=True)
    broadcast_thread.start()

    server_thread = threading.Thread(target=start_server)
    server_thread.start()

    game_loop()
