import torch
import pyautogui
import random
import time
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
from parser_csv import CSVFileMonitor

# Initialize global variables for possible moves and completion reward
possible_moves_data = []
completion_reward_data = 0

# Define Q-learning parameters
num_actions = 4  # Up, Left, Down, Right
num_states = 19 * 19  # 20x20 grid, minus one because 0-indexed
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
        action = random.choice(valid_moves)
        print(f"Exploring: Chosen action {action} from {valid_moves}")
        return action
    else:
        valid_q_values = Q_table[state, valid_moves]
        action = valid_moves[torch.argmax(valid_q_values).item()]
        print(f"Exploiting: Chosen action {action} with Q-values {valid_q_values}")
        return action

# Function to execute a move based on action
def execute_move(action, press_delay=0.4, release_delay=0.4):
    actions = ['w', 'a', 's', 'd']
    pyautogui.keyDown(actions[action])
    time.sleep(press_delay)
    pyautogui.keyUp(actions[action])
    time.sleep(release_delay)
    print(f"Executed move: {actions[action]}")

# Function to get the next state based on current position and action
def get_next_state(current_x, current_y, action, valid_moves):
    if action in valid_moves:
        if action == 0:
            current_y = max(current_y - 1, 0)
        elif action == 1:
            current_x = max(current_x - 1, 0)
        elif action == 2:
            current_y = min(current_y + 1, 18)
        elif action == 3:
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
        print(f"Current State: {current_state}")
        possible_moves = get_possible_moves_data()

        if not possible_moves:
            print("No valid moves available, waiting for update...")
            time.sleep(1)
            continue

        action = epsilon_greedy_policy(current_state, possible_moves)
        execute_move(action, press_delay=0.4, release_delay=0.4)

        next_x, next_y = get_next_state(current_x, current_y, action, possible_moves)
        next_state = next_y * 19 + next_x
        reward = completion_reward if completion_reward_data == 1 else step_penalty

        with torch.no_grad():
            Q_table[current_state, action] = (
                Q_table[current_state, action] + 
                learning_rate * (reward + discount_factor * torch.max(Q_table[next_state]) - Q_table[current_state, action])
            )
        print(f"Q-table updated for state {current_state}, action {action}")

        current_x, current_y = next_x, next_y

        if completion_reward_data == 1:
            print("Maze completed!")
            break

except KeyboardInterrupt:
    print("Stopping the monitor...")
    monitor.stop()
    print("Monitor stopped.")
