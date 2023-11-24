import pygame
import random

WIDTH, HEIGHT = 800, 600
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GREEN = (0, 255, 0)
RED = (255, 0, 0)
BLUE = (0, 0, 255)

pygame.init()
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Maze Generator")

GRID_SIZE = 20
GRID_WIDTH = WIDTH // GRID_SIZE
GRID_HEIGHT = HEIGHT // GRID_SIZE

DIRS = [(0, -1), (1, 0), (0, 1), (-1, 0)]

maze = [[1 for _ in range(GRID_WIDTH)] for _ in range(GRID_HEIGHT)]


def is_valid(x, y):
    return 0 <= x < GRID_WIDTH and 0 <= y < GRID_HEIGHT


def generate_maze(x, y):
    maze[y][x] = 0
    random.shuffle(DIRS)
    for dx, dy in DIRS:
        nx, ny = x + dx * 2, y + dy * 2
        if is_valid(nx, ny) and maze[ny][nx] == 1:
            maze[y + dy][x + dx] = 0
            generate_maze(nx, ny)


generate_maze(0, 0)

start_x, start_y = 0, 0
finish_x, finish_y = GRID_WIDTH - 2, GRID_HEIGHT - 2

player_x, player_y = start_x, start_y
player_dx, player_dy = 0, 0

MOVE_EVENT = pygame.USEREVENT + 1
pygame.time.set_timer(MOVE_EVENT, 150)  # Change this value to adjust the speed of movement

def move_player(dx, dy):
    global player_x, player_y
    new_x, new_y = player_x + dx, player_y + dy
    if is_valid(new_x, new_y) and maze[new_y][new_x] == 0:
        player_x, player_y = new_x, new_y

running = True
completed = False
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == MOVE_EVENT:
            move_player(player_dx, player_dy)
            if player_x == finish_x and player_y == finish_y:
                completed = True
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_w:
                player_dy = -1
            elif event.key == pygame.K_s:
                player_dy = 1
            elif event.key == pygame.K_a:
                player_dx = -1
            elif event.key == pygame.K_d:
                player_dx = 1
        elif event.type == pygame.KEYUP:
            if event.key == pygame.K_w and player_dy == -1:
                player_dy = 0
            elif event.key == pygame.K_s and player_dy == 1:
                player_dy = 0
            elif event.key == pygame.K_a and player_dx == -1:
                player_dx = 0
            elif event.key == pygame.K_d and player_dx == 1:
                player_dx = 0

    screen.fill(WHITE)

    pygame.draw.rect(screen, BLACK, (0, 0, WIDTH, HEIGHT), 2)

    for y in range(GRID_HEIGHT):
        for x in range(GRID_WIDTH):
            if maze[y][x] == 1:
                pygame.draw.rect(screen, BLACK, (x * GRID_SIZE, y * GRID_SIZE, GRID_SIZE, GRID_SIZE))

    pygame.draw.rect(screen, GREEN, (start_x * GRID_SIZE, start_y * GRID_SIZE, GRID_SIZE, GRID_SIZE))
    pygame.draw.rect(screen, GREEN, (finish_x * GRID_SIZE, finish_y * GRID_SIZE, GRID_SIZE, GRID_SIZE))
    pygame.draw.rect(screen, RED, (player_x * GRID_SIZE, player_y * GRID_SIZE, GRID_SIZE, GRID_SIZE))

    if completed:
        font = pygame.font.Font(None, 60)
        text = font.render("Complete!", True, RED)
        text_rect = text.get_rect(center=(WIDTH // 2, HEIGHT // 2))
        screen.blit(text, text_rect)

    pygame.display.flip()

pygame.quit()
