import gym
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

def execute_move(action):
    if action == 0:   # Up
        pyautogui.press('w')
    elif action == 1: # Left
        pyautogui.press('a')
    elif action == 2: # Down
        pyautogui.press('s')
    elif action == 3: # Right
        pyautogui.press('d')
        
def on_file_updated(last_line):
    possible_moves = CSVFileMonitor.parse_list(last_line[1]) if len(last_line) > 1 else []
    completion_message = int(last_line[2]) if len(last_line) > 2 else 0

    if possible_moves is not None:
        print(f"Possible Moves: {possible_moves}")

    if completion_message is not None:
        print(f"Completion Message: {completion_message}")

        
# rust-maze-version        
file_path = r'C:\AI-torch\AI\rust-maze\moves_data.csv'
directory_path = 'C:\\AI-torch\\AI\\rust-maze'

# Create an instance of CSVFileMonitor
monitor = CSVFileMonitor(file_path, directory_path, callback=on_file_updated)

try:
    monitor.start()
    print("Monitoring file for changes. Press Ctrl+C to stop.")
    while True:
        time.sleep(1)  # This loop now just keeps the script running

except KeyboardInterrupt:
    print("Stopping the monitor...")
    monitor.stop()
    print("Monitor stopped.")
