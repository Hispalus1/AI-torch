import torch
import pyautogui
import random
import time
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
from parser_csv import CSVFileMonitor

# Kontrola dostupnosti CUDA
device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
print(f"Using device: {device}")

# Globální proměnné pro ukládání pohybů a odměny za dokončení
possible_moves_data = []  # Seznam možných tahů
completion_reward_data = 0  # Odměna za dokončení hry

# Parametry Q-učení
num_actions = 4  # Akce: Nahoru, Doleva, Dolu, Doprava
num_states = 10 * 10  # Velikost mřížky: 10x10 (0-indexována)
learning_rate = 0.15
discount_factor = 0.95
initial_exploration_prob = 1.0
min_exploration_prob = 0.01
exploration_decay = 0.995
step_penalty = -0.1
completion_reward = 1.0

# Inicializace Q-tabulky s nulami a přesunutí na GPU, pokud je dostupné
Q_table = torch.zeros(num_states, num_actions, dtype=torch.float32).to(device)

# Funkce pro epsilon-greedy politiku
def epsilon_greedy_policy(state, valid_moves, exploration_prob):
    if random.uniform(0, 1) < exploration_prob:
        action = random.choice(valid_moves)
        return action
    else:
        valid_q_values = Q_table[state, valid_moves]
        action = valid_moves[torch.argmax(valid_q_values).item()]
        return action

# Funkce pro simulaci stisku klávesnice pro provedení tahu
def execute_move(action, press_delay=0.1, release_delay=0.1):
    actions = ['w', 'a', 's', 'd']  # Příslušné klávesy klávesnice
    pyautogui.keyDown(actions[action])
    time.sleep(press_delay)
    pyautogui.keyUp(actions[action])
    time.sleep(release_delay)

# Funkce pro výpočet dalšího stavu na základě akce
def get_next_state(current_x, current_y, action, valid_moves):
    if action in valid_moves:
        if action == 0:  # Nahoru
            current_y = max(current_y - 1, 0)
        elif action == 1:  # Doleva
            current_x = max(current_x - 1, 0)
        elif action == 2:  # Dolů
            current_y = min(current_y + 1, 9)
        elif action == 3:  # Doprava
            current_x = min(current_x + 1, 9)
    return current_x, current_y

# Callback pro aktualizaci CSV souboru
def on_file_updated(last_line):
    global possible_moves_data, completion_reward_data
    possible_moves = CSVFileMonitor.parse_list(last_line[1]) if last_line[1] != '' else []
    completion_message = int(last_line[2]) if len(last_line) > 2 and last_line[2].isdigit() else 0

    if possible_moves is not None:
        possible_moves_data = possible_moves
    if completion_message is not None:
        completion_reward_data = completion_message

# Funkce pro přístup k globálním datům
def get_possible_moves_data():
    return possible_moves_data

def get_completion_reward_data():
    return completion_reward_data

# Cesta k monitorovanému CSV souboru a cesta k adresáři s CSV souborem
file_path = r'C:\AI-torch\AI-torch\rust-maze\moves_data.csv'
directory_path = 'C:\\AI-torch\\AI-torch\\rust-maze'

# Nastavení monitoru pro CSV soubor
monitor = CSVFileMonitor(file_path, directory_path, callback=on_file_updated)

exploration_prob = initial_exploration_prob  # Inicializace pravděpodobnosti pro průzkum

try:
    monitor.start()  # Spuštění monitorování souboru
    print("Monitoring file for changes. Press Ctrl+C to stop.")
    current_x, current_y = 0, 0  # Počáteční pozice

    while True:
        current_state = current_y * 9 + current_x  # Převedení pozice na stav
        possible_moves = get_possible_moves_data()  # Získání možných tahů

        if not possible_moves:
            time.sleep(1)  # Pokud nejsou žádné možné tahy, čekej 1 sekundu a pokračuj
            continue

        # Volba akce pomocí epsilon-greedy politiky
        action = epsilon_greedy_policy(current_state, possible_moves, exploration_prob)
        execute_move(action)  # Provedení vybrané akce

        next_x, next_y = get_next_state(current_x, current_y, action, possible_moves)  # Získání následující pozice
        next_state = next_y * 10 + next_x  # Převedení následující pozice na stav
        reward = completion_reward if completion_reward_data == 1 else step_penalty  # Výpočet odměny za akci

        with torch.no_grad():
            # Aktualizace Q-hodnoty pro daný stav a akci
            Q_table[current_state, action] = (
                Q_table[current_state, action] + 
                learning_rate * (reward + discount_factor * torch.max(Q_table[next_state]) - Q_table[current_state, action])
            )

        current_x, current_y = next_x, next_y  # Aktualizace pozice na následující pozici
        exploration_prob = max(min_exploration_prob, exploration_prob * exploration_decay)  # Aktualizace pravděpodobnosti průzkumu

        if completion_reward_data == 1:
            print("Maze completed!")  # Pokud je hra dokončena, vypiš zprávu a ukonči smyčku
            break

except KeyboardInterrupt:
    print("Stopping the monitor...")  # Po stisknutí Ctrl+C zastav monitorování
    monitor.stop()
    print("Monitor stopped.")
