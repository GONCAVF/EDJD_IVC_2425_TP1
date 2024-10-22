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

# Define color range for segmentation (adjust for your cellphone color)
# For a baby blue cellphone, you may need to adjust these values.
lower_color = np.array([100, 150, 0])  # Lower bound for HSV (example: baby blue)
upper_color = np.array([140, 255, 255])  # Upper bound for HSV

# Function to process the webcam input
def process_frame():
    ret, frame = cap.read()
    if not ret:
        return None
    
    # Flip frame to avoid mirrored view
    frame = cv2.flip(frame, 1)
    
    # Convert frame to HSV
    hsv_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
    
    # Create mask for detecting the object by color
    mask = cv2.inRange(hsv_frame, lower_color, upper_color)
    
    # Find contours of the object
    contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    # Show the frame and the mask (for debugging purposes)
    cv2.imshow('Webcam', frame)  # Show the actual camera feed
    cv2.imshow('Mask', mask)  # Show the mask after segmentation
    
    # Find the largest contour by area (assuming it's the object of interest)
    if contours:
        largest_contour = max(contours, key=cv2.contourArea)
        M = cv2.moments(largest_contour)
        if M["m00"] > 0:
            # Calculate the center of the object
            cx = int(M["m10"] / M["m00"])
            print(f"Object X Coordinate: {cx}")  # Print x-coordinate for debugging
            return cx  # Return x-coordinate of the object's center
    
    return None

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
            # Adjust paddle position based on object detected
            # Mapping the object's x-coordinate to the paddle's position
            self.rect.x = object_x - (self.width // 2)
        # Ensure paddle stays within screen bounds
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
        self.speed_max = 5
        self.game_over = 0

    def move(self):
        # Collision with walls (left and right)
        if self.rect.left < 0 or self.rect.right > screen_width:
            self.speed_x *= -1
        # Collision with top
        if self.rect.top < 0:
            self.speed_y *= -1
        # Collision with bottom (game over)
        if self.rect.bottom > screen_height:
            self.game_over = -1

        # Collision with paddle
        if self.rect.colliderect(player_paddle.rect):
            if abs(self.rect.bottom - player_paddle.rect.top) < 5 and self.speed_y > 0:
                self.speed_y *= -1

        # Collision with blocks (check each block in the wall)
        for row in wall.blocks:
            for block in row:
                if self.rect.colliderect(block[0]):
                    # Destroy block by reducing its strength
                    self.speed_y *= -1  # Bounce the ball
                    block[1] -= 1
                    if block[1] <= 0:
                        row.remove(block)  # Remove block if strength is zero or less

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
    object_x = process_frame()
    
    screen.fill(bg)
    
    # Draw all objects
    wall.draw_wall()
    player_paddle.draw()
    ball.draw()

    if live_ball:
        player_paddle.move(object_x)
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

pygame.quit()
cap.release()
cv2.destroyAllWindows()
