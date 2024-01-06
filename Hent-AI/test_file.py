import torch
import pyautogui
import time
import csv
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
from parser_csv import CSVFileMonitor
import numpy as np
import random

# Define Q-learning parameters
num_actions = 4  # Up, Left, Down, Right
num_states = 100  # Assuming a 10x10 maze
learning_rate = 0.1
discount_factor = 0.9
exploration_prob = 0.3  # Probability of exploration (epsilon-greedy policy)

# Initialize the Q-table with zeros using PyTorch
Q_table = torch.zeros(num_states, num_actions, dtype=torch.float32)

# Define the epsilon-greedy policy
def epsilon_greedy_policy(state):
    if random.uniform(0, 1) < exploration_prob:
        return torch.randint(0, num_actions, (1,)).item()  # Explore
    else:
        return torch.argmax(Q_table[state]).item()  # Exploit

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
    
    # Check if last_line[2] is a valid integer string; if not, default to 0
    completion_message = 0
    if len(last_line) > 2 and last_line[2].isdigit():
        completion_message = int(last_line[2])

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

try:
    monitor.start()
    print("Monitoring file for changes. Press Ctrl+C to stop.")
    while True:
        time.sleep(1)  # This loop now just keeps the script running

        # TODO: Implement code to get the current state, check if the episode is done,
        # get the reward, and determine the next state based on the maze data.

        # state = # Code to get the current state
        # done = # Code to check if the episode is done
        # reward = # Code to get the reward
        # next_state = # Code to get the next state

        # Choose an action using the epsilon-greedy policy
        # action = epsilon_greedy_policy(state)

        # Execute the chosen action
        # execute_move(action)

        # Update the Q-table using the Q-learning update rule
        # Q_table[state, action] = Q_table[state, action] + learning_rate * (reward + discount_factor * torch.max(Q_table[next_state]) - Q_table[state, action])

except KeyboardInterrupt:
    print("Stopping the monitor...")
    monitor.stop()
    print("Monitor stopped.")
