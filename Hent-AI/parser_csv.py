import os
import time
import csv
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

class CSVFileMonitor:
    def __init__(self, file_path, directory_path, callback=None):
        # Initialize the CSVFileMonitor with file path, directory path, and an optional callback function
        self.file_path = file_path
        self.directory_path = directory_path
        self.last_processed_line = None  # Store the last processed line to avoid duplicate processing
        self.observer = Observer()  # Create an Observer object for monitoring file changes
        self.callback = callback  # Store the callback function to be called on file update

    @staticmethod
    def parse_list(string_list):
        # Static method to parse a string representation of a list into a list of integers
        return [int(x.strip()) for x in string_list.strip('[]').split(',') if x]

    def has_file_updated(self):
        # Check if the file has been updated since the last check
        current_modification_time = os.path.getmtime(self.file_path)
        if current_modification_time > self._last_file_modification_time:
            self._last_file_modification_time = current_modification_time
            return True
        return False

    def process_file(self):
        # Process the CSV file to read its content
        with open(self.file_path, 'r') as file:
            csv_reader = csv.reader(file, delimiter=';')
            next(csv_reader, None)  # Skip the header row

            last_line = None
            for line in csv_reader:
                # Process each line, ensuring it has at least 2 fields
                if not line or len(line) < 2:
                    continue

                # Extract move and possible moves, ensuring correct data types and formats
                move = line[0]
                possible_moves = self.parse_list(line[1]) if len(line) > 1 and line[1] != 'possible_moves' else []
                completion_message = int(line[2]) if len(line) > 2 and line[2].isdigit() else 0

                last_line = line  # Store the last line processed

            # If there's a new line and a callback function, call the callback with the last line
            if last_line and last_line != self.last_processed_line:
                self.last_processed_line = last_line
                if self.callback:
                    self.callback(last_line)

    def get_possible_moves(self):
        # Retrieve the possible moves from the last processed line
        if self.last_processed_line:
            return self.parse_list(self.last_processed_line[1])
        return None

    def get_completion_message(self):
        # Retrieve the completion message from the last processed line
        if self.last_processed_line:
            return int(self.last_processed_line[2])
        return None

    def start(self):
        # Start monitoring the directory for file changes
        event_handler = FileSystemEventHandler()
        # Define on_modified event to process the file if it's the monitored file
        event_handler.on_modified = lambda event: self.process_file() if event.src_path == self.file_path else None
        self.observer.schedule(event_handler, path=self.directory_path, recursive=False)
        self.observer.start()

    def stop(self):
        # Stop monitoring and join the observer thread
        self.observer.stop()
        self.observer.join()
