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
        
        
# rust-maze-version        
file_path = r'C:\AI-torch\AI\rust-maze\moves_data.csv'
directory_path = 'C:\\AI-torch\\AI\\rust-maze'


# pythonMazeVersion
#file_path = r'C:\AI-torch\AI\pythonMazeVersion\possible_moves.csv'
#directory_path = 'C:\\AI-torch\\AI\\pythonMazeVersion'

# Create an instance of CSVFileMonitor
monitor = CSVFileMonitor(file_path, directory_path)


# Start monitoring
monitor.start()

# Keep the script running and handle Ctrl+C to stop monitoring
try:
    print("Monitoring file for changes. Press Ctrl+C to stop.")
    while True:
        time.sleep(1)
except KeyboardInterrupt:
    monitor.stop()

