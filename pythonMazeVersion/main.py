import pygame
import random
import json
import csv

# Setting up constants
WIDTH, HEIGHT = 800, 800
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GREEN = (0, 255, 0)
RED = (255, 0, 0)
GRAY = (211, 211, 211)

# Initialize Pygame
pygame.init()
programIcon = pygame.image.load('assets/icon.png')
pygame.display.set_icon(programIcon)
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Maze Generator")

# Grid settings
GRID_SIZE = 20
GRID_WIDTH = WIDTH // GRID_SIZE
GRID_HEIGHT = HEIGHT // GRID_SIZE
DIRS = [(0, -1), (1, 0), (0, 1), (-1, 0)]

# Initialize the maze
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

# Start and finish positions
start_x, start_y = 0, 0
finish_x, finish_y = GRID_WIDTH - 2, GRID_HEIGHT - 2

# Player position
player_x, player_y = start_x, start_y

def move_player(dx, dy):
    global player_x, player_y, has_moved, completed
    new_x, new_y = player_x + dx, player_y + dy
    if is_valid(new_x, new_y) and maze[new_y][new_x] == 0:
        player_x, player_y = new_x, new_y
        has_moved = True  # Update the flag when the player moves
        # Check for completion
        if player_x == finish_x and player_y == finish_y:
            completed = True

def get_possible_moves_and_highlight(x, y):
    moves = []
    for dx, dy in DIRS:
        nx, ny = x + dx, y + dy
        if is_valid(nx, ny) and maze[ny][nx] == 0:
            move = None
            if dx == 1: move = "Right"
            if dx == -1: move = "Left"
            if dy == 1: move = "Down"
            if dy == -1: move = "Up"
            if move:
                moves.append(move)
            # Highlight possible moves
            pygame.draw.rect(screen, GRAY, (nx * GRID_SIZE, ny * GRID_SIZE, GRID_SIZE, GRID_SIZE))
    return moves

# Additional flags
has_moved = True
completion_message_printed = False
completed = False
running = True

# Initialize data structures for JSON and CSV
moves_data_json = {
    "moves": {},
    "completion_message": ""
}

moves_data_csv = {
    "moves": {},
    "completion_message": 0
}

# Function to convert move names to numbers for CSV
def convert_move_name(move_name):
    mapping = {"Up": 0, "Left": 1, "Down": 2, "Right": 3}
    return mapping.get(move_name, move_name)

# Function to write data to CSV
def write_to_csv(moves_data_csv):
    with open("possible_moves.csv", "w", newline='') as csvfile:
        csvwriter = csv.writer(csvfile)
        for move, directions in moves_data_csv["moves"].items():
            csvwriter.writerow([move] + directions)
        csvwriter.writerow(["completion_message", moves_data_csv["completion_message"]])

# Function to write data to JSON
def write_to_json(moves_data_json):
    with open("possible_moves.json", "w") as jsonfile:
        json.dump(moves_data_json, jsonfile, indent=4)

# Record the first possible moves
possible_moves = get_possible_moves_and_highlight(player_x, player_y)
moves_data_json["moves"]["Initial move"] = possible_moves
moves_data_csv["moves"]["Initial move"] = [convert_move_name(move) for move in possible_moves]

# Write initial data to files
write_to_csv(moves_data_csv)
write_to_json(moves_data_json)

# Main game loop
move_count = 1
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.KEYDOWN:
            move_made = False
            if event.key == pygame.K_w:
                move_player(0, -1)
                move_made = True
            elif event.key == pygame.K_s:
                move_player(0, 1)
                move_made = True
            elif event.key == pygame.K_a:
                move_player(-1, 0)
                move_made = True
            elif event.key == pygame.K_d:
                move_player(1, 0)
                move_made = True

            if move_made and has_moved:
                possible_moves = get_possible_moves_and_highlight(player_x, player_y)
                moves_data_json["moves"][f"move{move_count}"] = possible_moves
                moves_data_csv["moves"][f"move{move_count}"] = [convert_move_name(move) for move in possible_moves]

                # Write data to files after each move
                write_to_csv(moves_data_csv)
                write_to_json(moves_data_json)

                move_count += 1
                has_moved = False

    screen.fill(WHITE)
    # Draw the maze
    for y in range(GRID_HEIGHT):
        for x in range(GRID_WIDTH):
            if maze[y][x] == 1:
                pygame.draw.rect(screen, BLACK, (x * GRID_SIZE, y * GRID_SIZE, GRID_SIZE, GRID_SIZE))

    # Draw start and finish points
    pygame.draw.rect(screen, GREEN, (start_x * GRID_SIZE, start_y * GRID_SIZE, GRID_SIZE, GRID_SIZE))
    pygame.draw.rect(screen, GREEN, (finish_x * GRID_SIZE, finish_y * GRID_SIZE, GRID_SIZE, GRID_SIZE))

    # Draw the player
    pygame.draw.rect(screen, RED, (player_x * GRID_SIZE, player_y * GRID_SIZE, GRID_SIZE, GRID_SIZE))
    
    if not completed:
        if has_moved:
            possible_moves = get_possible_moves_and_highlight(player_x, player_y)
            has_moved = False

    if completed and not completion_message_printed:
        completion_message = "Congratulations! You've completed the maze!"
        moves_data_json["completion_message"] = completion_message
        moves_data_csv["completion_message"] = 1
        print(completion_message)
        completion_message_printed = True

        # Display completion message
        font = pygame.font.Font(None, 60)
        text = font.render("Congratulations! Maze Completed!", True, RED)
        text_rect = text.get_rect(center=(WIDTH // 2, HEIGHT // 2))
        screen.blit(text, text_rect)

    pygame.display.flip()

# Write final data to files
write_to_csv(moves_data_csv)
write_to_json(moves_data_json)

pygame.quit()
