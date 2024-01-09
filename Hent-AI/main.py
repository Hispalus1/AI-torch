
import torch
import pyautogui
import random
import time
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
from parser_csv import CSVFileMonitor

# Initialize global variables
possible_moves_data = []
completion_reward_data = 0

# Define Q-learning parameters
num_actions = 4  # Actions: Up, Left, Down, Right
num_states = 19 * 19  # Grid size: 19x19 (0-indexed)
learning_rate = 0.1
discount_factor = 0.9
initial_epsilon = 1.0  # Initial exploration probability
epsilon_decay = 0.995  # Decay rate of exploration probability
min_epsilon = 0.01  # Minimum exploration probability
step_penalty = -0.1  # Penalty for each step taken
completion_reward = 1.0  # Reward for completing the task
state_visit_counts = torch.zeros(num_states)  # Track state visits

# Initialize Q-table with zeros (PyTorch tensor)
Q_table = torch.zeros(num_states, num_actions, dtype=torch.float32)

# Epsilon-greedy policy function
def epsilon_greedy_policy(state, valid_moves, epsilon):
    if random.uniform(0, 1) < epsilon:
        action = random.choice(valid_moves)
        print(f"Exploring: Chosen action {action} from {valid_moves}")
        return action
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

epsilon = initial_epsilon  # Initialize epsilon for exploration

try:
    monitor.start()  # Start monitoring the file
    print("Monitoring file for changes. Press Ctrl+C to stop.")
    current_x, current_y = 0, 0  # Initial position

    # Main loop for Q-learning
    while True:
        current_state = current_y * 19 + current_x
        state_visit_counts[current_state] += 1  # Increment visit count for current state
        print(f"Current State: {current_state}")
        possible_moves = get_possible_moves_data()

        # Wait for valid moves if none are available
        if not possible_moves:
            print("No valid moves available, waiting for update...")
            time.sleep(1)
            continue

        # Select and execute an action
        action = epsilon_greedy_policy(current_state, possible_moves, epsilon)
        execute_move(action, press_delay=0.4, release_delay=0.4)

        # Update state and Q-table
        next_x, next_y = get_next_state(current_x, current_y, action, possible_moves)
        next_state = next_y * 19 + next_x
        reward = completion_reward if completion_reward_data == 1 else step_penalty - 0.01 * state_visit_counts[current_state]  # Penalize frequent visits

        # Q-table update (no gradient calculation needed)
        with torch.no_grad():
            Q_table[current_state, action] = (
                Q_table[current_state, action] + 
                learning_rate * (reward + discount_factor * torch.max(Q_table[next_state]) - Q_table[current_state, action])
            )
        print(f"Q-table updated for state {current_state}, action {action}")

        # Update the current position and epsilon
        current_x, current_y = next_x, next_y
        epsilon = max(min_epsilon, epsilon * epsilon_decay)  # Apply decay to epsilon

        # Check for task completion
        if completion_reward_data == 1:
            print("Maze completed!")
            break

except KeyboardInterrupt:
    # Handle manual interruption
    print("Stopping the monitor...")
    monitor.stop()
    print("Monitor stopped.")

    
    
    
    
    
