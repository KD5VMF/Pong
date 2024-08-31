import socket
import pygame
import time

# Game Initialization
pygame.init()
pygame.display.set_caption("Pong - Player")

# Wait for IP and Port Input Before Showing the Game Screen
SERVER_IP = input("Enter the server IP address: ")
SERVER_PORT = int(input("Enter the server port: "))

# Pygame Initialization (after IP and port input)
screen = pygame.display.set_mode((0, 0), pygame.FULLSCREEN)
SCREEN_WIDTH, SCREEN_HEIGHT = screen.get_size()

# Game Settings
PADDLE_WIDTH = 15
PADDLE_HEIGHT = 100
BALL_SIZE = 20
PADDLE_SPEED = 15  # Initial paddle speed
PADDLE_ACCELERATION = 0.3  # Acceleration for smooth paddle movement
BALL_SPEED_INCREASE = 1.2  # Speed multiplier for dynamic ball speed

# Paddle and Ball Positions
paddle2_y = SCREEN_HEIGHT // 2 - PADDLE_HEIGHT // 2

def connect_to_server():
    client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client.connect((SERVER_IP, SERVER_PORT))
    return client

def draw_game(ball_x, ball_y, paddle1_y, paddle2_y, score1, score2):
    screen.fill((0, 0, 0))
    pygame.draw.rect(screen, (255, 255, 255), (0, paddle1_y, PADDLE_WIDTH, PADDLE_HEIGHT))
    pygame.draw.rect(screen, (255, 255, 255), (SCREEN_WIDTH - PADDLE_WIDTH, paddle2_y, PADDLE_WIDTH, PADDLE_HEIGHT))
    pygame.draw.circle(screen, (255, 255, 255), (ball_x, ball_y), BALL_SIZE // 2)
    draw_scoreboard(score1, score2)
    pygame.display.flip()

def draw_scoreboard(score1, score2):
    font = pygame.font.SysFont(None, 48)
    score_text = font.render(f"Server: {score1}  Player: {score2}", True, (255, 255, 255))
    screen.blit(score_text, (SCREEN_WIDTH // 2 - score_text.get_width() // 2, 20))

def game_loop(client_socket):
    global paddle2_y, PADDLE_SPEED

    paddle_velocity = 0

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                return
            if event.type == pygame.KEYDOWN and event.key == pygame.K_F8:
                pygame.quit()
                return

        # Receive data from server
        data = client_socket.recv(1024).decode('utf-8')
        if not data:
            print("Connection lost to the server.")
            break

        if data == "ACK":
            continue

        ball_x, ball_y, paddle1_y, score1, score2 = map(int, data.split(','))

        # Simple AI to follow the ball with smooth movement
        if ball_y > paddle2_y + PADDLE_HEIGHT // 2:
            paddle_velocity = min(paddle_velocity + PADDLE_ACCELERATION, PADDLE_SPEED)
        elif ball_y < paddle2_y + PADDLE_HEIGHT // 2:
            paddle_velocity = max(paddle_velocity - PADDLE_ACCELERATION, -PADDLE_SPEED)
        else:
            paddle_velocity = 0

        paddle2_y += paddle_velocity
        paddle2_y = max(0, min(paddle2_y, SCREEN_HEIGHT - PADDLE_HEIGHT))

        # Send the updated paddle position to server
        client_socket.send(str(paddle2_y).encode('utf-8'))

        # Draw the updated game state
        draw_game(ball_x, ball_y, paddle1_y, paddle2_y, score1, score2)

if __name__ == "__main__":
    print("Player starting up...")
    client_socket = connect_to_server()

    if client_socket.recv(1024).decode('utf-8') == "READY":
        client_socket.send("ACK".encode('utf-8'))
        if client_socket.recv(1024).decode('utf-8') == "START":
            client_socket.send("START_ACK".encode('utf-8'))
            game_loop(client_socket)
        else:
            print("Server did not send the start signal.")
    else:
        print("Failed to connect properly with the server.")
    
    client_socket.close()
