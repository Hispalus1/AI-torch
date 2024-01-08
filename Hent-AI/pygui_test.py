import pyautogui
import time

def test_pyautogui():
    # Wait for 5 seconds before starting
    print("Starting in 5 seconds...")
    time.sleep(5)

    # Press the 's' key    
    pyautogui.press('s')  # Test the movement

    # Type out a text
    text_to_type = "PyAutoGUI is working!"
    print(f"Typing out: '{text_to_type}'")
    pyautogui.write(text_to_type, interval=0.25)

    print("Test completed!")

if __name__ == "__main__":
    test_pyautogui()
