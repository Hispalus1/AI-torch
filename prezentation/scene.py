import pygame
import sys

# Inicializace Pygame
pygame.init()

# Nastavení velikosti okna a fontu
width, height = 400, 400  # 10 čtverců po 20 pixelech v každém směru
screen = pygame.display.set_mode((width, height))
pygame.display.set_caption("10x10 Grid")
font = pygame.font.SysFont(None, 24)

# Barvy
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)

# Velikost jednotlivých čtverců
cell_size = 40

# Hlavní smyčka
running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    # Vymazání obrazovky
    screen.fill(WHITE)

    # Vykreslení mřížky a textu
    for x in range(10):
        for y in range(10):
            rect = pygame.Rect(x * cell_size, y * cell_size, cell_size, cell_size)
            pygame.draw.rect(screen, BLACK, rect, 1)
            text = font.render(f"({y},{x})", True, BLACK)
            screen.blit(text, (x * cell_size + 5, y * cell_size + 5))

    # Aktualizace obrazovky
    pygame.display.flip()

# Ukončení Pygame
pygame.quit()
sys.exit()
