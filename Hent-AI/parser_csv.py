import os
import time
import csv
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

class CSVFileMonitor:
    def __init__(self, file_path, directory_path, callback=None):
        self.file_path = file_path
        self.directory_path = directory_path
        self.last_processed_line = None
        self.observer = Observer()
        self.callback = callback

    @staticmethod
    def parse_list(string_list):
        return [int(x.strip()) for x in string_list.strip('[]').split(',') if x]

    def has_file_updated(self):
        current_modification_time = os.path.getmtime(self.file_path)
        if current_modification_time > self._last_file_modification_time:
            self._last_file_modification_time = current_modification_time
            return True
        return False

    def process_file(self):
        with open(self.file_path, 'r') as file:
            csv_reader = csv.reader(file, delimiter=';')
            next(csv_reader, None)  # Skip the header row

            last_line = None
            for line in csv_reader:
                if not line or len(line) < 2:  # Check for at least 2 fields
                    continue

                move = line[0]  # Always expect a move
                possible_moves = self.parse_list(line[1]) if len(line) > 1 and line[1] != 'possible_moves' else []  # Check for header or missing possible_moves
                completion_message = int(line[2]) if len(line) > 2 and line[2].isdigit() else 0  # Safely handle non-numeric completion_message

                last_line = line

            if last_line and last_line != self.last_processed_line:
                self.last_processed_line = last_line
                if self.callback:
                    self.callback(last_line)


    def get_possible_moves(self):
        if self.last_processed_line:
            return self.parse_list(self.last_processed_line[1])
        return None

    def get_completion_message(self):
        if self.last_processed_line:
            return int(self.last_processed_line[2])
        return None

    def start(self):
        event_handler = FileSystemEventHandler()
        event_handler.on_modified = lambda event: self.process_file() if event.src_path == self.file_path else None
        self.observer.schedule(event_handler, path=self.directory_path, recursive=False)
        self.observer.start()

    def stop(self):
        self.observer.stop()
        self.observer.join()


