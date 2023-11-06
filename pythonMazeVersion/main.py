import pygame
import random


WIDTH, HEIGHT = 800, 600
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GREEN = (0, 255, 0)


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


running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    screen.fill(WHITE)

   
    pygame.draw.rect(screen, BLACK, (0, 0, WIDTH, HEIGHT), 2)

   
    for y in range(GRID_HEIGHT):
        for x in range(GRID_WIDTH):
            if maze[y][x] == 1:
                pygame.draw.rect(screen, BLACK, (x * GRID_SIZE, y * GRID_SIZE, GRID_SIZE, GRID_SIZE))

    
    pygame.draw.rect(screen, GREEN, (start_x * GRID_SIZE, start_y * GRID_SIZE, GRID_SIZE, GRID_SIZE))
    pygame.draw.rect(screen, GREEN, (finish_x * GRID_SIZE, finish_y * GRID_SIZE, GRID_SIZE, GRID_SIZE))

    pygame.display.flip()

pygame.quit()
