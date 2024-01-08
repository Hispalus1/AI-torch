import pyautogui
import time

def press_and_release_key(key, press_delay=0.1, release_delay=2):
    # Press the key
    pyautogui.keyDown(key)
    
    # Wait for a short period while the key is pressed
    time.sleep(press_delay)

    # Release the key
    pyautogui.keyUp(key)

    # Wait for a longer period after release, if needed
    time.sleep(release_delay)

# Example: Press and release 's' with a specific delay
time.sleep(2)
press_and_release_key('s', press_delay=0.4, release_delay=0.4)