import pygame
from pygame.locals import *
from camera_processing import process_frame, release_camera, initializate_cameras

pygame.init()

screen_width = 600
screen_height = 600
screen = pygame.display.set_mode((screen_width, screen_height))
pygame.display.set_caption('Breakout')

font = pygame.font.SysFont('Constantia', 30)
text_col = (78, 81, 139)
bg = (234, 218, 184)

def draw_text(text, font, text_col, x, y):
    img = font.render(text, True, text_col)
    screen.blit(img, (x, y))

# Menu
def menu_inicial():
    while True:
        screen.fill(bg)
        draw_text("Escolha o número de jogadores:", font, text_col, 100, screen_height // 2 - 60)
        draw_text("1 Jogador", font, text_col, 220, screen_height // 2)
        draw_text("2 Jogadores", font, text_col, 200, screen_height // 2 + 60)

        pygame.display.update()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                exit()
            if event.type == pygame.MOUSEBUTTONDOWN:
                x, y = event.pos
                if 220 < x < 380 and screen_height // 2 < y < screen_height // 2 + 40:
                    screen.fill(bg)
                    draw_text("A carregar...", font, text_col, 220, screen_height // 2)
                    pygame.display.update()
                    return 1
                if 200 < x < 400 and screen_height // 2 + 60 < y < screen_height // 2 + 100:
                    screen.fill(bg)
                    draw_text("A carregar...", font, text_col, 220, screen_height // 2)
                    pygame.display.update()
                    return 2

num_players = menu_inicial()

cam, cam2 = initializate_cameras(num_players)

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
paddle_green = (86, 174, 87)
paddle_blue = (69, 177, 232)
paddle_outline = (100, 100, 100)
text_col = (78, 81, 139)

# Define game variables
cols = 6
rows = 6
clock = pygame.time.Clock()
fps = 60
live_ball = False
game_over = 0

# Function for outputting text onto the screen
def draw_text(text, font, text_col, x, y):
    img = font.render(text, True, text_col)
    screen.blit(img, (x, y))

# Paddle class
class Paddle:
    def __init__(self, color):
        self.width = int(screen_width / cols)
        self.height = 20
        self.color = color
        self.reset()

    def move(self, object_x):
        if object_x is not None:
            self.rect.x = object_x - (self.width // 2)
        # Ensure paddle stays within screen bounds
        if self.rect.left < 0:
            self.rect.left = 0
        if self.rect.right > screen_width:
            self.rect.right = screen_width

    def draw(self):
        pygame.draw.rect(screen, self.color, self.rect)
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

        # Collision with paddles
        if self.rect.colliderect(first_paddle.rect):
            if abs(self.rect.bottom - first_paddle.rect.top) < 5 and self.speed_y > 0:
                self.speed_y *= -1
        if cam2:
            if self.rect.colliderect(second_paddle.rect):
                if abs(self.rect.bottom - second_paddle.rect.top) < 5 and self.speed_y > 0:
                    self.speed_y *= -1

        # Collision with blocks (check each block in the wall)
        for row in wall.blocks:
            for block in row:
                if self.rect.colliderect(block[0]):
                    # Destroy block by reducing its strength
                    self.speed_y *= -1
                    block[1] -= 1
                    if block[1] <= 0:
                        row.remove(block)

        self.rect.x += self.speed_x
        self.rect.y += self.speed_y
        return self.game_over

    def draw(self):
        pygame.draw.circle(screen, paddle_green, (self.rect.x + self.ball_rad, self.rect.y + self.ball_rad), self.ball_rad)
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
                block_col = block_blue if block[1] == 3 else block_red if block[1] == 2 else block_red
                pygame.draw.rect(screen, block_col, block[0])
                pygame.draw.rect(screen, bg, block[0], 2)

# Create a wall
wall = Wall()
wall.create_wall()

# Create paddles
first_paddle = Paddle(paddle_green)
if cam2:
    second_paddle = Paddle(paddle_blue)

# Create ball
ball = GameBall(first_paddle.x + (first_paddle.width // 2), first_paddle.y - first_paddle.height)

# Main game loop
run = True
while run:
    clock.tick(fps)

    # Process camera input
    if cam2:
        object_x_green, object_x_blue = process_frame(cam, cam2)
    else:
        object_x_green = process_frame(cam, cam2)

    screen.fill(bg)

    # Draw all objects
    wall.draw_wall()
    first_paddle.draw()
    if cam2:
        second_paddle.draw()
    ball.draw()

    if live_ball:
        # Move paddles based on detected colors
        first_paddle.move(object_x_green)
        if cam2:
            second_paddle.move(object_x_blue)
        game_over = ball.move()
        if game_over != 0:
            live_ball = False

    # Display instructions
    if not live_ball:
        if game_over == 0:
            if num_players == 1:
                draw_text('CLICAR PARA COMEÇAR', font, text_col, 140, screen_height // 2 + 80)
                draw_text('COR VERDE A JOGAR', font, text_col, 140, screen_height // 2 + 130)
            else:
                draw_text('CLICAR PARA COMEÇAR', font, text_col, 140, screen_height // 2 + 80)
                draw_text('COR VERDE E AZUL A JOGAR', font, text_col, 140, screen_height // 2 + 130)
        elif game_over == -1:
            draw_text('FIM DO JOGO!', font, text_col, 240, screen_height // 2 + 50)
            draw_text('CLICAR PARA COMEÇAR', font, text_col, 100, screen_height // 2 + 100)
        ball.reset(first_paddle.x + (first_paddle.width // 2), first_paddle.y - first_paddle.height)
        first_paddle.reset()
        if cam2:
            second_paddle.reset()

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            run = False
        if event.type == pygame.MOUSEBUTTONDOWN and not live_ball:
            live_ball = True

    pygame.display.update()

release_camera(cam, cam2)
pygame.quit()