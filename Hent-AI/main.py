import torch
import pyautogui
import random
import time
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
from parser_csv import CSVFileMonitor

# Global variables for storing moves and completion reward
possible_moves_data = []
completion_reward_data = 0

# Q-learning parameters
num_actions = 4  # Actions: Up, Left, Down, Right
num_states = 19 * 19  # Grid size: 19x19 (0-indexed)
learning_rate = 0.1
discount_factor = 0.9
exploration_prob = 0.3  # Epsilon for epsilon-greedy policy
step_penalty = -0.1  # Penalty for each step taken
completion_reward = 1.0  # Reward for completing the task

# Initialize Q-table with zeros (PyTorch tensor)
Q_table = torch.zeros(num_states, num_actions, dtype=torch.float32)

# Epsilon-greedy policy function
def epsilon_greedy_policy(state, valid_moves):
    # Exploration: randomly choose an action from valid moves
    if random.uniform(0, 1) < exploration_prob:
        action = random.choice(valid_moves)
        print(f"Exploring: Chosen action {action} from {valid_moves}")
        return action
    # Exploitation: choose the best action based on Q-table
    else:
        valid_q_values = Q_table[state, valid_moves]
        action = valid_moves[torch.argmax(valid_q_values).item()]
        print(f"Exploiting: Chosen action {action} with Q-values {valid_q_values}")
        return action

# Function to simulate keyboard press for movement
def execute_move(action, press_delay=0.4, release_delay=0.4):
    actions = ['w', 'a', 's', 'd']  # Corresponding keyboard keys
    pyautogui.keyDown(actions[action])
    time.sleep(press_delay)
    pyautogui.keyUp(actions[action])
    time.sleep(release_delay)
    print(f"Executed move: {actions[action]}")

# Function to compute the next state based on action
def get_next_state(current_x, current_y, action, valid_moves):
    # Update coordinates based on the action taken
    if action in valid_moves:
        if action == 0:  # Up
            current_y = max(current_y - 1, 0)
        elif action == 1:  # Left
            current_x = max(current_x - 1, 0)
        elif action == 2:  # Down
            current_y = min(current_y + 1, 18)
        elif action == 3:  # Right
            current_x = min(current_x + 1, 18)
    return current_x, current_y

# Callback for CSV file update
def on_file_updated(last_line):
    global possible_moves_data, completion_reward_data
    # Parse new data from the CSV file
    possible_moves = CSVFileMonitor.parse_list(last_line[1]) if last_line[1] != '' else []
    completion_message = int(last_line[2]) if len(last_line) > 2 and last_line[2].isdigit() else 0

    # Update global variables with new data
    if possible_moves is not None:
        possible_moves_data = possible_moves
        print(f"Possible Moves: {possible_moves_data}")

    if completion_message is not None:
        completion_reward_data = completion_message
        print(f"Completion Reward: {completion_reward_data}")

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

try:
    monitor.start()  # Start monitoring the file
    print("Monitoring file for changes. Press Ctrl+C to stop.")
    current_x, current_y = 0, 0  # Initial position

    # Main loop for Q-learning
    while True:
        current_state = current_y * 19 + current_x
        print(f"Current State: {current_state}")
        possible_moves = get_possible_moves_data()

        # Wait for valid moves if none are available
        if not possible_moves:
            print("No valid moves available, waiting for update...")
            time.sleep(1)
            continue

        # Select and execute an action
        action = epsilon_greedy_policy(current_state, possible_moves)
        execute_move(action, press_delay=0.4, release_delay=0.4)

        # Update state and Q-table
        next_x, next_y = get_next_state(current_x, current_y, action, possible_moves)
        next_state = next_y * 19 + next_x
        reward = completion_reward if completion_reward_data == 1 else step_penalty

        # Q-table update (no gradient calculation needed)
        with torch.no_grad():
            Q_table[current_state, action] = (
                Q_table[current_state, action] + 
                learning_rate * (reward + discount_factor * torch.max(Q_table[next_state]) - Q_table[current_state, action])
            )
        print(f"Q-table updated for state {current_state}, action {action}")

        # Update the current position
        current_x, current_y = next_x, next_y

        # Check for task completion
        if completion_reward_data == 1:
            print("Maze completed!")
            break

except KeyboardInterrupt:
    # Handle manual interruption
    print("Stopping the monitor...")
    monitor.stop()
    print("Monitor stopped.")
