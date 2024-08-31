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
PADDLE_SPEED = 15  # Initial paddle speed
PADDLE_ACCELERATION = 0.3  # Acceleration for smooth paddle movement
BALL_SPEED_X = 12  # Initial ball speed
BALL_SPEED_Y = 12  # Initial ball speed
BALL_SPEED_INCREASE = 1.2  # Speed multiplier for dynamic ball speed

# Difficulty Scaling
difficulty_increment = 1.5  # Faster speed increase per level
ai_reaction_time = 0.004  # Reduced AI reaction time for faster response

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

def get_lan_ip_address():
    try:
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
    global ball_x, ball_y, ball_dx, ball_dy, paddle1_y, paddle2_y, score1, score2

    ball_x += ball_dx
    ball_y += ball_dy

    # Ball bounces off the top and bottom of the screen
    if ball_y <= 0 or ball_y >= SCREEN_HEIGHT - BALL_SIZE:
        ball_dy = -ball_dy

    # Ball bounces off the paddles
    if ball_x <= PADDLE_WIDTH and paddle1_y < ball_y < paddle1_y + PADDLE_HEIGHT:
        ball_dx = -ball_dx
        adjust_ball_angle(paddle1_y, ball_y)
        ball_dx *= BALL_SPEED_INCREASE
        ball_dy *= BALL_SPEED_INCREASE
    if ball_x >= SCREEN_WIDTH - PADDLE_WIDTH - BALL_SIZE and paddle2_y < ball_y < paddle2_y + PADDLE_HEIGHT:
        ball_dx = -ball_dx
        adjust_ball_angle(paddle2_y, ball_y)
        ball_dx *= BALL_SPEED_INCREASE
        ball_dy *= BALL_SPEED_INCREASE

    # Ball goes out of bounds and score is updated
    if ball_x <= 0:
        score2 += 1
        reset_ball()
        increase_difficulty()
    if ball_x >= SCREEN_WIDTH - BALL_SIZE:
        score1 += 1
        reset_ball()
        increase_difficulty()

def adjust_ball_angle(paddle_y, ball_y):
    # Adjust the ball's angle based on where it hits the paddle
    relative_intersect_y = (paddle_y + PADDLE_HEIGHT / 2) - ball_y
    normalized_intersect_y = relative_intersect_y / (PADDLE_HEIGHT / 2)
    bounce_angle = normalized_intersect_y * 75  # Angle in degrees

    # Convert angle to radians and calculate new velocity components
    ball_dy = -BALL_SPEED_Y * normalized_intersect_y
    if abs(ball_dy) < 1:  # Prevents the ball from moving horizontally only
        ball_dy = random.choice([-1, 1])

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
    time.sleep(ai_reaction_time)  # Simulate AI reaction time
    if ball_y > paddle1_y + PADDLE_HEIGHT // 2:
        paddle1_y += PADDLE_SPEED
    elif ball_y < paddle1_y + PADDLE_HEIGHT // 2:
        paddle1_y -= PADDLE_SPEED

    # Ensure the paddle can move fully up and down
    paddle1_y = max(0, min(paddle1_y, SCREEN_HEIGHT - PADDLE_HEIGHT))

def increase_difficulty():
    global PADDLE_SPEED, BALL_SPEED_X, BALL_SPEED_Y, ai_reaction_time
    PADDLE_SPEED += difficulty_increment
    BALL_SPEED_X += difficulty_increment
    BALL_SPEED_Y += difficulty_increment
    ai_reaction_time = max(0.001, ai_reaction_time - 0.001)  # Faster AI reaction with a limit

def handle_client(client_socket):
    global paddle2_y, ball_x, ball_y, ball_dx, ball_dy, score1, score2, client_connected
    client_connected = True

    try:
        client_socket.send("READY".encode('utf-8'))
        client_ack = client_socket.recv(1024).decode('utf-8')
        if client_ack == "ACK":
            print("Client acknowledged, starting game...")
        else:
            print("Client did not acknowledge properly.")
            return

        time.sleep(1)
        client_socket.send("START".encode('utf-8'))
        start_ack = client_socket.recv(1024).decode('utf-8')
        if start_ack == "START_ACK":
            print("Client is ready. Game is starting...")
        else:
            print("Client did not respond to start signal.")
            return

        while True:
            move_ball()
            ai_move_paddle()

            send_data = f"{ball_x},{ball_y},{paddle1_y},{score1},{score2}"
            client_socket.send(send_data.encode('utf-8'))

            data = client_socket.recv(1024).decode('utf-8')
            if data:
                if data == "ACK":
                    continue
                paddle2_y = int(float(data))

                paddle2_y = max(0, min(paddle2_y, SCREEN_HEIGHT - PADDLE_HEIGHT))

            client_socket.send("ACK".encode('utf-8'))

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
        time.sleep(0.005)

if __name__ == "__main__":
    server_thread = threading.Thread(target=start_server)
    server_thread.start()

    game_loop()
