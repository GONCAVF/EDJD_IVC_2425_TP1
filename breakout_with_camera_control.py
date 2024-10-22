import pygame
from pygame.locals import *
import cv2
import numpy as np

pygame.init()

screen_width = 600
screen_height = 600

screen = pygame.display.set_mode((screen_width, screen_height))
pygame.display.set_caption('Breakout')

# Define font
font = pygame.font.SysFont('Constantia', 30)

# Define colors
bg = (234, 218, 184)
block_red = (242, 85, 96)
block_green = (86, 174, 87)
block_blue = (69, 177, 232)
paddle_col = (142, 135, 123)
paddle_outline = (100, 100, 100)
text_col = (78, 81, 139)

# Define game variables
cols = 6
rows = 6
clock = pygame.time.Clock()
fps = 60
live_ball = False
game_over = 0

# OpenCV setup
cap = cv2.VideoCapture(0)

# Check if the camera is opened correctly
if not cap.isOpened():
    print("Error: Could not open webcam.")
    pygame.quit()
    exit()

# Define color range for segmentation
lower_blue = np.array([100, 150, 0])  # Lower bound for HSV (example: baby blue)
upper_blue = np.array([140, 255, 255])  # Upper bound for HSV

lower_red1 = np.array([0, 120, 70])
upper_red1 = np.array([10, 255, 255])
lower_red2 = np.array([170, 120, 70])
upper_red2 = np.array([180, 255, 255])

# Function to process the webcam input
def process_frame():
    ret, frame = cap.read()
    if not ret:
        return None, None

    # Flip frame to avoid mirrored view
    frame = cv2.flip(frame, 1)

    # Convert frame to HSV
    hsv_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)

    # Create mask for blue
    mask_blue = cv2.inRange(hsv_frame, lower_blue, upper_blue)

    # Create two masks for red color
    mask_red1 = cv2.inRange(hsv_frame, lower_red1, upper_red1)
    mask_red2 = cv2.inRange(hsv_frame, lower_red2, upper_red2)

    # Combine the two red masks
    mask_red = mask_red1 + mask_red2

    # Find contours of the blue object
    contours_blue, _ = cv2.findContours(mask_blue, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    contours_red, _ = cv2.findContours(mask_red, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    # Initialize coordinates
    cx_blue, cx_red = None, None

    # Find the largest contour for blue
    if contours_blue:
        largest_contour = max(contours_blue, key=cv2.contourArea)
        M = cv2.moments(largest_contour)
        if M["m00"] > 0:
            cx_blue = int(M["m10"] / M["m00"])

    # Find the largest contour for red
    if contours_red:
        largest_contour = max(contours_red, key=cv2.contourArea)
        M = cv2.moments(largest_contour)
        if M["m00"] > 0:
            cx_red = int(M["m10"] / M["m00"])

    return cx_blue, cx_red

# Function for outputting text onto the screen
def draw_text(text, font, text_col, x, y):
    img = font.render(text, True, text_col)
    screen.blit(img, (x, y))

# Paddle class
class Paddle:
    def __init__(self):
        self.width = int(screen_width / cols)
        self.height = 20
        self.reset()

    def move(self, object_x):
        if object_x is not None:
            self.rect.x = object_x - (self.width // 2)
        if self.rect.left < 0:
            self.rect.left = 0
        if self.rect.right > screen_width:
            self.rect.right = screen_width

    def draw(self):
        pygame.draw.rect(screen, paddle_col, self.rect)
        pygame.draw.rect(screen, paddle_outline, self.rect, 3)

    def reset(self):
        self.x = int((screen_width / 2) - (self.width / 2))
        self.y = screen_height - (self.height * 2)
        self.rect = Rect(self.x, self.y, self.width, self.height)

# GameBall class
class GameBall:
    def __init__(self, x, y):
        self.ball_rad = 10
        self.x = x
        self.y = y
        self.rect = Rect(self.x, self.y, self.ball_rad * 2, self.ball_rad * 2)
        self.speed_x = 4
        self.speed_y = -4
        self.game_over = 0

    def move(self):
        if self.rect.left < 0 or self.rect.right > screen_width:
            self.speed_x *= -1
        if self.rect.top < 0:
            self.speed_y *= -1
        if self.rect.bottom > screen_height:
            self.game_over = -1

        if self.rect.colliderect(player_paddle.rect):
            if abs(self.rect.bottom - player_paddle.rect.top) < 5 and self.speed_y > 0:
                self.speed_y *= -1

        self.rect.x += self.speed_x
        self.rect.y += self.speed_y
        return self.game_over

    def draw(self):
        pygame.draw.circle(screen, paddle_col, (self.rect.x + self.ball_rad, self.rect.y + self.ball_rad), self.ball_rad)
        pygame.draw.circle(screen, paddle_outline, (self.rect.x + self.ball_rad, self.rect.y + self.ball_rad), self.ball_rad, 3)

    def reset(self, x, y):
        self.rect.x = x - self.ball_rad
        self.rect.y = y
        self.speed_x = 4
        self.speed_y = -4
        self.game_over = 0

# Wall class
class Wall:
    def __init__(self):
        self.width = screen_width // cols
        self.height = 50

    def create_wall(self):
        self.blocks = []
        for row in range(rows):
            block_row = []
            for col in range(cols):
                block_x = col * self.width
                block_y = row * self.height
                rect = pygame.Rect(block_x, block_y, self.width, self.height)
                strength = 3 if row < 2 else 2 if row < 4 else 1
                block_row.append([rect, strength])
            self.blocks.append(block_row)

    def draw_wall(self):
        for row in self.blocks:
            for block in row:
                block_col = block_blue if block[1] == 3 else block_green if block[1] == 2 else block_red
                pygame.draw.rect(screen, block_col, block[0])
                pygame.draw.rect(screen, bg, block[0], 2)

# Create a wall
wall = Wall()
wall.create_wall()

# Create paddle
player_paddle = Paddle()

# Create ball
ball = GameBall(player_paddle.x + (player_paddle.width // 2), player_paddle.y - player_paddle.height)

# Main game loop
run = True
while run:
    clock.tick(fps)

    # Process camera input
    cx_blue, cx_red = process_frame()

    screen.fill(bg)

    # Draw all objects
    wall.draw_wall()
    player_paddle.draw()
    ball.draw()

    if live_ball:
        player_paddle.move(cx_blue)
        game_over = ball.move()
        if game_over != 0:
            live_ball = False

    # Display instructions
    if not live_ball:
        if game_over == 0:
            draw_text('CLICK ANYWHERE TO START', font, text_col, 100, screen_height // 2 + 100)
        elif game_over == 1:
            draw_text('YOU WON!', font, text_col, 240, screen_height // 2 + 50)
            draw_text('CLICK ANYWHERE TO START', font, text_col, 100, screen_height // 2 + 100)
        elif game_over == -1:
            draw_text('YOU LOST!', font, text_col, 240, screen_height // 2 + 50)
            draw_text('CLICK ANYWHERE TO START', font, text_col, 100, screen_height // 2 + 100)

    # Handle events
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            run = False
        if event.type == pygame.MOUSEBUTTONDOWN and not live_ball:
            live_ball = True
            ball.reset(player_paddle.x + (player_paddle.width // 2), player_paddle.y - player_paddle.height)
            player_paddle.reset()
            wall.create_wall()

    pygame.display.update()

    # Criar uma janela para mostrar as coordenadas
    coord_window = np.zeros((200, 400, 3), dtype=np.uint8)
    if cx_blue is not None:
        cv2.putText(coord_window, f'Azul: {cx_blue}', (10, 50), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2)
    if cx_red is not None:
        cv2.putText(coord_window, f'Vermelho: {cx_red}', (10, 100), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2)

    cv2.imshow('Coordenadas', coord_window)
    cv2.imshow('Webcam', cap.read()[1])  # Mostra a feed da câmara
    cv2.imshow('Máscara Azul e Vermelha', cv2.inRange(cv2.cvtColor(cap.read()[1], cv2.COLOR_BGR2HSV), lower_blue, upper_blue) + cv2.inRange(cv2.cvtColor(cap.read()[1], cv2.COLOR_BGR2HSV), lower_red1, upper_red1) + cv2.inRange(cv2.cvtColor(cap.read()[1], cv2.COLOR_BGR2HSV), lower_red2, upper_red2))

pygame.quit()
cap.release()
cv2.destroyAllWindows()