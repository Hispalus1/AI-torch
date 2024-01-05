import torch
import torch.nn as nn
import torch.optim as optim
import pyautogui
import time
import sys
import csv
import numpy as np
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
from parser_csv import CSVFileMonitor

# Define Q-learning parameters
num_actions = 4  # Up, Left, Down, Right
learning_rate = 0.1
discount_factor = 0.9
exploration_prob = 0.3  # Probability of exploration (epsilon-greedy policy)

# Define the number of states (unique maze configurations)
# num_states =  # Replace with the appropriate number of states based on your dynamic environment

# Initialize the Q-table with zeros
Q_table = np.zeros((num_states, num_actions))

# Define the epsilon-greedy policy
def epsilon_greedy_policy(state):
    if np.random.uniform(0, 1) < exploration_prob:
        return np.random.choice(num_actions)  # Explore
    else:
        return np.argmax(Q_table[state, :])  # Exploit (choose the action with the highest Q-value)

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

# Define variables to store possible moves and completion reward
possible_moves_data = None
completion_reward_data = None

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

# Define a function to access the stored data
def get_possible_moves_data():
    return possible_moves_data

def get_completion_reward_data():
    return completion_reward_data

# rust-maze-version        
file_path = r'C:\AI-torch\AI\rust-maze\moves_data.csv'
directory_path = 'C:\\AI-torch\\AI\\rust-maze'

# Create an instance of CSVFileMonitor
monitor = CSVFileMonitor(file_path, directory_path, callback=on_file_updated)

try:
    monitor.start()
    print("Monitoring file for changes. Press Ctrl+C to stop.")
    while True:
        """
        time.sleep(1)  # This loop now just keeps the script running
        
        # Implement code to get the current state from your maze representation
        state =  # Replace with code to get the current state

        # Choose an action using the epsilon-greedy policy
        action = epsilon_greedy_policy(state)

        # Execute the chosen action in the maze
        execute_move(action)

        # Implement code to check if the episode is done (maze completed or other termination condition)
        done =  # Replace with code to check if the episode is done

        # Implement code to get the reward for the action
        reward =  # Replace with code to get the reward

        # Update the Q-table using the Q-learning update rule
        next_state =  # Replace with code to get the next state based on the action
        Q_table[state, action] = Q_table[state, action] + learning_rate * (reward + discount_factor * np.max(Q_table[next_state, :]) - Q_table[state, action])
        """
except KeyboardInterrupt:
    print("Stopping the monitor...")
    monitor.stop()
    print("Monitor stopped.")
