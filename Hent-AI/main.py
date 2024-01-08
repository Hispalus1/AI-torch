import torch
import pyautogui
import random
import time
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
from parser_csv import CSVFileMonitor

# Initialize global variables for possible moves and completion reward
possible_moves_data = []  # Initialize as an empty list
completion_reward_data = 0  # Initialize with a default value, e.g., 0

# Define Q-learning parameters
num_actions = 4  # Up, Left, Down, Right
num_states = 19 * 19  # 20x20 grid
learning_rate = 0.1
discount_factor = 0.9
exploration_prob = 0.3  # Probability of exploration (epsilon-greedy policy)
step_penalty = -0.1  # Penalty for each step
completion_reward = 1.0  # Reward for completing the maze

# Initialize the Q-table with zeros using PyTorch
Q_table = torch.zeros(num_states, num_actions, dtype=torch.float32)

# Epsilon-greedy policy adapted for available moves
def epsilon_greedy_policy(state, valid_moves):
    if random.uniform(0, 1) < exploration_prob:
        return random.choice(valid_moves)  # Explore among valid moves
    else:
        valid_q_values = Q_table[state, valid_moves]
        return valid_moves[torch.argmax(valid_q_values).item()]  # Exploit

# Function to execute a move based on action
def execute_move(action):
    if action == 0:   # Up
        pyautogui.press('w')
    elif action == 1: # Left
        pyautogui.press('a')
    elif action == 2: # Down
        pyautogui.press('s')
    elif action == 3: # Right
        pyautogui.press('d')

# Function to get the next state based on current position and action
def get_next_state(current_x, current_y, action, valid_moves):
    if action in valid_moves:
        if action == 0:   # Up
            current_y = max(current_y - 1, 0)
        elif action == 1: # Left
            current_x = max(current_x - 1, 0)
        elif action == 2: # Down
            current_y = min(current_y + 1, 18)
        elif action == 3: # Right
            current_x = min(current_x + 1, 18)
    return current_x, current_y

# Callback function for file update
def on_file_updated(last_line):
    global possible_moves_data, completion_reward_data
    possible_moves = CSVFileMonitor.parse_list(last_line[1]) if last_line[1] != '' else []
    completion_message = int(last_line[2]) if len(last_line) > 2 and last_line[2].isdigit() else 0

    if possible_moves is not None:
        possible_moves_data = possible_moves
        print(f"Possible Moves: {possible_moves_data}")

    if completion_message is not None:
        completion_reward_data = completion_message
        print(f"Completion Reward: {completion_reward_data}")

# Access stored data functions
def get_possible_moves_data():
    return possible_moves_data

def get_completion_reward_data():
    return completion_reward_data

# File path for CSVFileMonitor
file_path = r'C:\AI-torch\AI-torch\rust-maze\moves_data.csv'
directory_path = 'C:\\AI-torch\\AI-torch\\rust-maze'

# Create an instance of CSVFileMonitor
monitor = CSVFileMonitor(file_path, directory_path, callback=on_file_updated)


try:
    monitor.start()
    print("Monitoring file for changes. Press Ctrl+C to stop.")
    current_x, current_y = 0, 0  # Starting position

    while True:
        current_state = current_y * 19 + current_x
        possible_moves = get_possible_moves_data()

        if not possible_moves:  # Wait for first update with valid moves
            print("No valid moves available, waiting for update...")
            time.sleep(1)  # Delay before checking again
            continue

        # Choose an action using the epsilon-greedy policy
        action = epsilon_greedy_policy(current_state, possible_moves)
        # Execute the chosen action in the maze
        execute_move(action)

        # Artificial delay to wait for the environment to process the move and update the CSV
        time.sleep(2)

        # Fetch the next state and reward after the move
        next_x, next_y = get_next_state(current_x, current_y, action, possible_moves)
        next_state = next_y * 19 + next_x
        reward = completion_reward if completion_reward_data == 1 else step_penalty

        # Update the Q-table using the Q-learning update rule
        with torch.no_grad():
            Q_table[current_state, action] = (
                Q_table[current_state, action] + 
                learning_rate * (reward + discount_factor * torch.max(Q_table[next_state]) - Q_table[current_state, action])
            )

        # Update current state
        current_x, current_y = next_x, next_y

        if completion_reward_data == 1:
            print("Maze completed!")
            break  # Exit the loop if the maze is completed

except KeyboardInterrupt:
    print("Stopping the monitor...")
    monitor.stop()
    print("Monitor stopped.")

 