# Turn-Based Self-Playing Pong (Fullscreen, Press Q to Quit)

import random
import pygame
import sys
from pygame.locals import *

# Initialize Pygame
pygame.init()
fps = pygame.time.Clock()

# Colors
WHITE = (255, 255, 255)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLACK = (0, 0, 0)
YELLOW = (255, 255, 0)

# Screen setup
info = pygame.display.Info()
WIDTH, HEIGHT = info.current_w, info.current_h

BALL_RADIUS = 20
PAD_WIDTH = 8
PAD_HEIGHT = 100
HALF_PAD_WIDTH = PAD_WIDTH // 2
HALF_PAD_HEIGHT = PAD_HEIGHT // 2

# Globals
ball_pos = [0, 0]
ball_vel = [0, 0]
paddle1_pos = [0, 0]
paddle2_pos = [0, 0]
l_score = 0
r_score = 0
turn = "left"  # whose turn it is to move


# Create fullscreen window
window = pygame.display.set_mode((WIDTH, HEIGHT), pygame.FULLSCREEN)
pygame.display.set_caption('Turn-Based Pong')


def ball_init(right):
    """Spawn ball in center with velocity towards `right` or `left`."""
    global ball_pos, ball_vel
    ball_pos = [WIDTH // 2, HEIGHT // 2]
    horz = random.randrange(4, 6)
    vert = random.randrange(2, 4)
    ball_vel = [horz if right else -horz, -vert]


def init():
    """Initialize paddles, scores, ball."""
    global paddle1_pos, paddle2_pos, l_score, r_score, turn
    paddle1_pos = [HALF_PAD_WIDTH, HEIGHT // 2]
    paddle2_pos = [WIDTH - HALF_PAD_WIDTH, HEIGHT // 2]
    l_score = 0
    r_score = 0
    turn = "left"
    ball_init(random.choice([True, False]))


def draw(canvas):
    """Draw game frame and update positions."""
    global paddle1_pos, paddle2_pos, ball_pos, ball_vel, l_score, r_score, turn

    canvas.fill(BLACK)
    pygame.draw.line(canvas, WHITE, [WIDTH // 2, 0], [WIDTH // 2, HEIGHT], 1)
    pygame.draw.circle(canvas, WHITE, [WIDTH // 2, HEIGHT // 2], 70, 1)

    # Move paddle based on whose turn it is
    track_speed = 6
    if turn == "left":
        if paddle1_pos[1] < ball_pos[1] - 10 and paddle1_pos[1] < HEIGHT - HALF_PAD_HEIGHT:
            paddle1_pos[1] += track_speed
        elif paddle1_pos[1] > ball_pos[1] + 10 and paddle1_pos[1] > HALF_PAD_HEIGHT:
            paddle1_pos[1] -= track_speed
    elif turn == "right":
        if paddle2_pos[1] < ball_pos[1] - 10 and paddle2_pos[1] < HEIGHT - HALF_PAD_HEIGHT:
            paddle2_pos[1] += track_speed
        elif paddle2_pos[1] > ball_pos[1] + 10 and paddle2_pos[1] > HALF_PAD_HEIGHT:
            paddle2_pos[1] -= track_speed

    # Update ball
    ball_pos[0] += ball_vel[0]
    ball_pos[1] += ball_vel[1]

    # Ball-wall collisions
    if ball_pos[1] <= BALL_RADIUS or ball_pos[1] >= HEIGHT - BALL_RADIUS:
        ball_vel[1] = -ball_vel[1]

    # Ball-paddle collisions and gutter scoring
    if ball_pos[0] <= PAD_WIDTH + BALL_RADIUS:
        if paddle1_pos[1] - HALF_PAD_HEIGHT <= ball_pos[1] <= paddle1_pos[1] + HALF_PAD_HEIGHT:
            ball_vel[0] = -ball_vel[0] * 1.1
            ball_vel[1] *= 1.1
            turn = "right"  # switch turn
        else:
            r_score += 1
            ball_init(True)
            turn = "left"

    elif ball_pos[0] >= WIDTH - PAD_WIDTH - BALL_RADIUS:
        if paddle2_pos[1] - HALF_PAD_HEIGHT <= ball_pos[1] <= paddle2_pos[1] + HALF_PAD_HEIGHT:
            ball_vel[0] = -ball_vel[0] * 1.1
            ball_vel[1] *= 1.1
            turn = "left"  # switch turn
        else:
            l_score += 1
            ball_init(False)
            turn = "right"

    # Draw ball and paddles
    pygame.draw.circle(canvas, RED, (int(ball_pos[0]), int(ball_pos[1])), BALL_RADIUS)
    pygame.draw.rect(canvas, GREEN, (paddle1_pos[0] - HALF_PAD_WIDTH, paddle1_pos[1] - HALF_PAD_HEIGHT, PAD_WIDTH, PAD_HEIGHT))
    pygame.draw.rect(canvas, GREEN, (paddle2_pos[0] - HALF_PAD_WIDTH, paddle2_pos[1] - HALF_PAD_HEIGHT, PAD_WIDTH, PAD_HEIGHT))

    # Draw scores
    font = pygame.font.SysFont("Comic Sans MS", 32)
    l_text = font.render(f"Score: {l_score}", True, YELLOW)
    r_text = font.render(f"Score: {r_score}", True, YELLOW)
    canvas.blit(l_text, (50, 30))
    canvas.blit(r_text, (WIDTH - 200, 30))

    # Indicate turn
    t_text = font.render(f"Turn: {'LEFT' if turn == 'left' else 'RIGHT'}", True, WHITE)
    canvas.blit(t_text, (WIDTH // 2 - 80, 30))


# Start the game
init()

# Game loop
while True:
    draw(window)
    for event in pygame.event.get():
        if event.type == QUIT:
            pygame.quit()
            sys.exit()
        elif event.type == KEYDOWN:
            if event.key == K_q:
                pygame.quit()
                sys.exit()

    pygame.display.update()
    fps.tick(60)
