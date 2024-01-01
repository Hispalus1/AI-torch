import time
import csv
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
# this is just the parser that will be used in the ai learning process to get the data from the csv files
# Global variable to store the last processed line
last_processed_line = None

def parse_list(string_list):
    return [int(x.strip()) for x in string_list.strip('[]').split(',') if x]

def process_file(file_path):
    global last_processed_line

    with open(file_path, 'r') as file:
        last_line = None
        for line in csv.reader(file, delimiter=';'):
            # Skip empty lines or lines with insufficient data
            if not line or len(line) < 3:
                continue

            # Check if the first and third elements are valid integers
            try:
                move = int(line[0])
                completion_message = int(line[2])
            except ValueError:
                continue  # Skip lines where the first or third element is not a valid integer

            if 'possible_moves.csv' in file_path:
                possible_moves = parse_list(line[1])  # Parse as a list
            elif 'moves_data.csv' in file_path:
                possible_moves = line[1]  # Use the string directly

            last_line = line

        if last_line and last_line != last_processed_line:
            last_processed_line = last_line  # Update the last processed line

            print(f"Last Move: {move}, Possible Moves: {possible_moves}, Completion Message: {completion_message}")


# Rest of the script remains the same


class FileModifiedHandler(FileSystemEventHandler):
    def __init__(self, file_path):
        self.file_path = file_path

    def on_modified(self, event):
        if event.src_path == self.file_path:
            process_file(self.file_path)

# Set the file path and directory path
#file_path = r'C:\AI-torch\AI\rust-maze\moves_data.csv'
#directory_path = 'C:\\AI-torch\\AI\\rust-maze'
file_path = r'C:\AI-torch\AI\pythonMazeVersion\possible_moves.csv'
directory_path = 'C:\\AI-torch\\AI\\pythonMazeVersion'

# Set up the observer
observer = Observer()
event_handler = FileModifiedHandler(file_path)
observer.schedule(event_handler, path=directory_path, recursive=False)
observer.start()

print("Monitoring file for changes. Press Ctrl+C to stop.")

try:
    while True:
        time.sleep(1)
except KeyboardInterrupt:
    observer.stop()

observer.join()
