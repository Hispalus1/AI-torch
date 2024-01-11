import torch
import pyautogui
import random
import time
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
from parser_csv import CSVFileMonitor

# Check for CUDA availability
device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
print(f"Using device: {device}")

# Global variables for storing moves and completion reward
possible_moves_data = []
completion_reward_data = 0

# Q-learning parameters
num_actions = 4  # Actions: Up, Left, Down, Right
num_states = 10 * 10  # Grid size: 10x10
learning_rate = 0.15
discount_factor = 0.95
initial_exploration_prob = 1.0
min_exploration_prob = 0.01
exploration_decay = 0.995
step_penalty = -0.1
completion_reward = 1.0

# Initialize Q-table with zeros (PyTorch tensor)
Q_table = torch.zeros(num_states, num_actions, dtype=torch.float32).to(device)

# Epsilon-greedy policy function
def epsilon_greedy_policy(state, valid_moves, exploration_prob):
    if random.uniform(0, 1) < exploration_prob:
        action = random.choice(valid_moves)
        return action
    else:
        valid_q_values = Q_table[state, valid_moves]
        action = valid_moves[torch.argmax(valid_q_values).item()]
        return action

# Function to simulate keyboard press for movement
def execute_move(action, press_delay=0.1, release_delay=0.1):
    actions = ['w', 'a', 's', 'd']  # Corresponding keyboard keys
    pyautogui.keyDown(actions[action])
    time.sleep(press_delay)
    pyautogui.keyUp(actions[action])
    time.sleep(release_delay)

# Function to compute the next state based on action
def get_next_state(current_x, current_y, action, valid_moves):
    if action in valid_moves:
        if action == 0:  # Up
            current_y = max(current_y - 1, 0)
        elif action == 1:  # Left
            current_x = max(current_x - 1, 0)
        elif action == 2:  # Down
            current_y = min(current_y + 1, 9)
        elif action == 3:  # Right
            current_x = min(current_x + 1, 9)
    return current_x, current_y

# Callback for CSV file update
def on_file_updated(last_line):
    global possible_moves_data, completion_reward_data
    possible_moves = CSVFileMonitor.parse_list(last_line[1]) if last_line[1] != '' else []
    completion_message = int(last_line[2]) if len(last_line) > 2 and last_line[2].isdigit() else 0

    if possible_moves is not None:
        possible_moves_data = possible_moves
    if completion_message is not None:
        completion_reward_data = completion_message

# Functions to access global data
def get_possible_moves_data():
    return possible_moves_data

def get_completion_reward_data():
    return completion_reward_data

# File path for CSV monitoring
file_path = r'C:\AI-torch\AI-torch\rust-maze\moves_data.csv'
directory_path = 'C:\\AI-torch\\AI-torch\\rust-maze'

# Set up CSV file monitor
monitor = CSVFileMonitor(file_path, directory_path, callback=on_file_updated)

exploration_prob = initial_exploration_prob  # Initialize exploration probability

try:
    monitor.start()  # Start monitoring the file
    print("Monitoring file for changes. Press Ctrl+C to stop.")
    current_x, current_y = 0, 0  # Initial position

    # Main loop for Q-learning
    while True:
        current_state = current_y * 10 + current_x  # Adjusted for 10x10 grid
        possible_moves = get_possible_moves_data()

        if not possible_moves:
            time.sleep(1)
            continue

        action = epsilon_greedy_policy(current_state, possible_moves, exploration_prob)
        execute_move(action)

        next_x, next_y = get_next_state(current_x, current_y, action, possible_moves)
        next_state = next_y * 10 + next_x  # Adjusted for 10x10 grid
        reward = completion_reward if completion_reward_data == 1 else step_penalty

        with torch.no_grad():
            Q_table[current_state, action] = (
                Q_table[current_state, action] + 
                learning_rate * (reward + discount_factor * torch.max(Q_table[next_state]) - Q_table[current_state, action])
            )

        current_x, current_y = next_x, next_y
        exploration_prob = max(min_exploration_prob, exploration_prob * exploration_decay)

        if completion_reward_data == 1:
            print("Maze completed!")
            break

except KeyboardInterrupt:
    print("Stopping the monitor...")
    monitor.stop()
    print("Monitor stopped.")

# Additional code for cleanup or further processing if needed
