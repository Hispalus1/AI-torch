import torch
import torch.nn as nn
import torch.optim as optim
import pyautogui
import time
import sys
import csv
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
from parser_csv import CSVFileMonitor
import random

# Initialize global variables for possible moves and completion reward
possible_moves_data = []  # Initialize as an empty list
completion_reward_data = 0  # Initialize with a default value, e.g., 0

# Define Q-learning parameters
num_actions = 4  # Up, Left, Down, Right
learning_rate = 0.1
discount_factor = 0.9
exploration_prob = 0.3  # Probability of exploration (epsilon-greedy policy)
step_penalty = -0.1  # Penalty for each step taken

# Define the number of states for a 10x10 maze
num_states = 10 * 10  # 100 unique positions in a 10x10 maze

# Initialize the Q-table with zeros using PyTorch
Q_table = torch.zeros((num_states, num_actions), dtype=torch.float32)

# Define the epsilon-greedy policy
def epsilon_greedy_policy(state, valid_moves):
    if torch.rand(1) < exploration_prob:
        return random.choice(valid_moves)  # Explore among valid moves
    else:
        # Exploit: choose the action with the highest Q-value among valid moves
        q_values = Q_table[state, valid_moves]
        max_q_index = torch.argmax(q_values).item()
        return valid_moves[max_q_index]

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

# Callback function for file update
def on_file_updated(last_line):
    global possible_moves_data, completion_reward_data

    possible_moves = CSVFileMonitor.parse_list(last_line[1]) if len(last_line) > 1 else []
    completion_message = int(last_line[2]) if len(last_line) > 2 else 0

    if possible_moves is not None:
        possible_moves_data = possible_moves
        print(f"Possible Moves: {possible_moves}")

    if completion_message is not None:
        completion_reward_data = completion_message
        print(f"Completion Reward: {completion_reward_data}")

# Define functions to access the stored data
def get_possible_moves_data():
    return possible_moves_data

def get_completion_reward_data():
    return completion_reward_data

# rust-maze-version        
file_path = r'C:\AI-torch\AI-torch\rust-maze\moves_data.csv'
directory_path = 'C:\\AI-torch\\AI-torch\\rust-maze'

# Create an instance of CSVFileMonitor
monitor = CSVFileMonitor(file_path, directory_path, callback=on_file_updated)

# Starting position and grid width for the maze
row, column = 0, 0
grid_width = 10

try:
    monitor.start()
    print("Monitoring file for changes. Press Ctrl+C to stop.")
    while True:
        # Calculate the current state based on the agent's position
        state = row * grid_width + column

        possible_moves = get_possible_moves_data()
        if not possible_moves:  # No available moves means the maze is finished
            reward = get_completion_reward_data()  # Get the completion reward
            done = True
        else:
            action = epsilon_greedy_policy(state, possible_moves)
            execute_move(action)
            reward = step_penalty  # Apply step penalty
            done = False

            # Update agent's position based on the action taken
            if action == 0:  # Up
                row -= 1
            elif action == 1: # Left
                column -= 1
            elif action == 2: # Down
                row += 1
            elif action == 3: # Right
                column += 1

            # Ensure row and column stay within the grid bounds
            row = max(0, min(row, grid_width - 1))
            column = max(0, min(column, grid_width - 1))

        # Update the Q-table using the Q-learning update rule
        # Add logic for updating the state, handling the end of an episode, etc.

        if done:
            break  # Exit the loop if the maze is completed

except KeyboardInterrupt:
    print("Stopping the monitor...")
    monitor.stop()
    print("Monitor stopped.")
