import pyglet
from pyglet import shapes
import random
import math

# Window setup
window = pyglet.window.Window(fullscreen=True)
width, height = window.get_size()

# Game constants
BALL_RADIUS = 20
PADDLE_WIDTH = 12
PADDLE_HEIGHT = 120
PADDLE_SPEED_GROWTH = 0.5
BALL_SPEED_MULTIPLIER = 1.1
BASE_BALL_SPEED = 400
BALL_SCALING = 20
TRAIL_LENGTH = 15
PADDLE_MAX_SPEED = 1200

# Game state
paddle1_y = height // 2
paddle2_y = height // 2
paddle1_speed = 300
paddle2_speed = 300
ball_x = width // 2
ball_y = height // 2
ball_dx = random.choice([-1, 1]) * BASE_BALL_SPEED
ball_dy = random.uniform(-1, 1) * BASE_BALL_SPEED / 2

score1 = 0
score2 = 0
trail = []

# Batch drawing
batch = pyglet.graphics.Batch()
background_batch = pyglet.graphics.Batch()
foreground_batch = pyglet.graphics.Batch()

# Background effects: animated stars
grid_lines = [
    shapes.Line(x, 0, x, height, color=(30, 30, 30), batch=background_batch) for x in range(0, width, 60)
] + [
    shapes.Line(0, y, width, y, color=(30, 30, 30), batch=background_batch) for y in range(0, height, 60)
]

# Game elements
center_line = shapes.Rectangle(width // 2 - 2, 0, 4, height, color=(80, 80, 80), batch=foreground_batch)
ball = shapes.Circle(ball_x, ball_y, BALL_RADIUS, color=(255, 50, 50), batch=foreground_batch)
paddle1 = shapes.Rectangle(40, paddle1_y - PADDLE_HEIGHT // 2, PADDLE_WIDTH, PADDLE_HEIGHT, color=(0, 255, 100), batch=foreground_batch)
paddle2 = shapes.Rectangle(width - 40 - PADDLE_WIDTH, paddle2_y - PADDLE_HEIGHT // 2, PADDLE_WIDTH, PADDLE_HEIGHT, color=(0, 100, 255), batch=foreground_batch)

# Fonts and Labels
score_font = pyglet.font.load('Courier New', 36)
label_score1 = pyglet.text.Label(text=f'{score1}', font_size=36, font_name='Courier New', x=100, y=height - 80, anchor_x='center', anchor_y='center', color=(255, 255, 0, 255))
label_score2 = pyglet.text.Label(text=f'{score2}', font_size=36, font_name='Courier New', x=width - 100, y=height - 80, anchor_x='center', anchor_y='center', color=(255, 255, 0, 255))
label_info = pyglet.text.Label(text='', font_size=20, font_name='Courier New', x=width // 2, y=height - 40, anchor_x='center', color=(200, 200, 255, 255))


def reset_ball(direction):
    global ball_x, ball_y, ball_dx, ball_dy, trail
    ball_x = width // 2
    ball_y = height // 2
    trail = []
    speed = BASE_BALL_SPEED + BALL_SCALING * (paddle1_speed if direction == 1 else paddle2_speed) / 100
    ball_dx = direction * speed
    ball_dy = random.uniform(-1, 1) * speed / 2


@window.event
def on_key_press(symbol, modifiers):
    if symbol == pyglet.window.key.Q:
        pyglet.app.exit()


def update(dt):
    global ball_x, ball_y, ball_dx, ball_dy
    global paddle1_y, paddle2_y, paddle1_speed, paddle2_speed
    global score1, score2, trail

    turn = 'left' if ball_dx < 0 else 'right'

    # Update paddle
    if turn == 'left':
        if paddle1_y < ball_y:
            paddle1_y += min(paddle1_speed * dt, height - PADDLE_HEIGHT // 2 - paddle1_y)
        else:
            paddle1_y -= min(paddle1_speed * dt, paddle1_y - PADDLE_HEIGHT // 2)
    else:
        if paddle2_y < ball_y:
            paddle2_y += min(paddle2_speed * dt, height - PADDLE_HEIGHT // 2 - paddle2_y)
        else:
            paddle2_y -= min(paddle2_speed * dt, paddle2_y - PADDLE_HEIGHT // 2)

    # Move ball
    ball_x += ball_dx * dt
    ball_y += ball_dy * dt
    trail.append((ball_x, ball_y))
    if len(trail) > TRAIL_LENGTH:
        trail.pop(0)

    if ball_y < BALL_RADIUS or ball_y > height - BALL_RADIUS:
        ball_dy *= -1

    if ball_x < 40 + PADDLE_WIDTH + BALL_RADIUS:
        if paddle1_y - PADDLE_HEIGHT // 2 - 10 < ball_y < paddle1_y + PADDLE_HEIGHT // 2 + 10:
            ball_dx *= -BALL_SPEED_MULTIPLIER
            ball_dy *= BALL_SPEED_MULTIPLIER
            paddle1_speed = min(paddle1_speed + PADDLE_SPEED_GROWTH, PADDLE_MAX_SPEED)
        else:
            score2 += 1
            reset_ball(1)
    elif ball_x > width - 40 - PADDLE_WIDTH - BALL_RADIUS:
        if paddle2_y - PADDLE_HEIGHT // 2 - 10 < ball_y < paddle2_y + PADDLE_HEIGHT // 2 + 10:
            ball_dx *= -BALL_SPEED_MULTIPLIER
            ball_dy *= BALL_SPEED_MULTIPLIER
            paddle2_speed = min(paddle2_speed + PADDLE_SPEED_GROWTH, PADDLE_MAX_SPEED)
        else:
            score1 += 1
            reset_ball(-1)

    # Update objects
    ball.x = int(ball_x)
    ball.y = int(ball_y)
    paddle1.y = int(paddle1_y - PADDLE_HEIGHT // 2)
    paddle2.y = int(paddle2_y - PADDLE_HEIGHT // 2)

    label_score1.text = f'{score1}'
    label_score2.text = f'{score2}'
    label_info.text = f'TURN: {turn.upper()}   P1 SPD: {paddle1_speed:.1f}   P2 SPD: {paddle2_speed:.1f}'


@window.event
def on_draw():
    window.clear()
    background_batch.draw()

    # Draw ball trail with fading
    for i, (x, y) in enumerate(trail):
        alpha = int(255 * (i + 1) / len(trail))
        t = shapes.Circle(int(x), int(y), BALL_RADIUS // 2, color=(255, 100, 100))
        t.opacity = alpha
        t.draw()

    foreground_batch.draw()
    label_score1.draw()
    label_score2.draw()
    label_info.draw()


pyglet.clock.schedule_interval(update, 1/240.0)
pyglet.app.run()
