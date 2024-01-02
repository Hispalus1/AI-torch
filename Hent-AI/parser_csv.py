import time
import csv
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

class CSVFileMonitor:
    def __init__(self, file_path, directory_path):
        self.file_path = file_path
        self.directory_path = directory_path
        self.last_processed_line = None
        self.observer = Observer()

    @staticmethod
    def parse_list(string_list):
        return [int(x.strip()) for x in string_list.strip('[]').split(',') if x]

    def process_file(self):
        with open(self.file_path, 'r') as file:
            last_line = None
            for line in csv.reader(file, delimiter=';'):
                if not line or len(line) < 3:
                    continue

                # Check if the first and third elements are valid integers
                try:
                    move = int(line[0])
                    completion_message = int(line[2])
                except ValueError:
                    continue  # Skip lines where the first or third element is not a valid integer

                if 'possible_moves.csv' in self.file_path:
                    possible_moves = self.parse_list(line[1])  # Parse as a list
                elif 'moves_data.csv' in self.file_path:
                    possible_moves = line[1]  # Use the string directly

                last_line = line

            if last_line and last_line != self.last_processed_line:
                self.last_processed_line = last_line  # Update the last processed line
                print(f"Last Move: {move}, Possible Moves: {possible_moves}, Completion Message: {completion_message}")

    def start(self):
        event_handler = FileSystemEventHandler()
        event_handler.on_modified = lambda event: self.process_file() if event.src_path == self.file_path else None
        self.observer.schedule(event_handler, path=self.directory_path, recursive=False)
        self.observer.start()

    def stop(self):
        self.observer.stop()
        self.observer.join()

# Example usage
file_path = r'C:\AI-torch\AI\rust-maze\moves_data.csv'
directory_path = 'C:\\AI-torch\\AI\\rust-maze'

#file_path = r'C:\AI-torch\AI\pythonMazeVersion\possible_moves.csv'
#directory_path = 'C:\\AI-torch\\AI\\pythonMazeVersion'
monitor = CSVFileMonitor(file_path, directory_path)

try:
    monitor.start()
    print("Monitoring file for changes. Press Ctrl+C to stop.")
    while True:
        time.sleep(1)
except KeyboardInterrupt:
    monitor.stop()
