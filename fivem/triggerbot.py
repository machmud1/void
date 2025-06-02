import threading
import time
import sys
import winsound
import pyautogui
import cv2
import numpy as np
from pynput import keyboard, mouse
import win32api
import win32con
import ctypes
import hashlib
import os

CORRECT_PASSWORD_HASH = "445be54d48a2e6294369c84c61cd0929209d4e1084536159bdf7002bddfe094b"

def check_password():
    while True:
        ctypes.windll.kernel32.SetConsoleTitleW("MP4 to MP3 Audio Convertor")
        password = input("MP4 file path: ")
        password_hash = hashlib.sha256(password.encode()).hexdigest()
        
        if password_hash == CORRECT_PASSWORD_HASH:
            os.system('cls')
            ctypes.windll.kernel32.SetConsoleTitleW("Void TriggerBot")
            return True
        
        print("Invalid Directory")

SCREEN_WIDTH, SCREEN_HEIGHT = pyautogui.size()
x, y = SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2

INITIAL_COLOR_RGB = (224, 224, 224)

def rgb_to_hsv(rgb_color):
    color_bgr = np.uint8([[rgb_color[::-1]]])
    color_hsv = cv2.cvtColor(color_bgr, cv2.COLOR_BGR2HSV)[0][0]
    return tuple(int(v) for v in color_hsv)

INITIAL_COLOR_HSV = rgb_to_hsv(INITIAL_COLOR_RGB)

TOLERANCE_H = 10
TOLERANCE_S = 10
TOLERANCE_V = 10

CHECK_INTERVAL = 0.05
SHOOT_INTERVAL = 0.05

clicking_enabled = False
stop_script = False
right_button_pressed = False

lock = threading.Lock()

def on_press(key):
    global clicking_enabled
    try:
        if key == keyboard.Key.insert:
            with lock:
                clicking_enabled = not clicking_enabled
                if clicking_enabled:
                    print(" [SUCCESS] Enabled")
                    winsound.Beep(1000, 150)
                else:
                    print(" [SUCCESS] Disabled")
                    winsound.Beep(500, 150)
    except AttributeError:
        pass

def on_click(x_click, y_click, button, pressed):
    global right_button_pressed
    if button == mouse.Button.right:
        with lock:
            right_button_pressed = pressed

def start_keyboard_listener():
    with keyboard.Listener(on_press=on_press) as listener:
        listener.join()

def start_mouse_listener():
    with mouse.Listener(on_click=on_click) as listener:
        listener.join()

def get_pixel_color_hsv(px, py):
    try:
        color_rgb = pyautogui.pixel(px, py)
        bgr = np.uint8([[color_rgb[::-1]]])
        color_hsv = cv2.cvtColor(bgr, cv2.COLOR_BGR2HSV)[0][0]
        return tuple(int(v) for v in color_hsv)
    except Exception as e:
        return None

def is_color_initial(color_hsv):
    if color_hsv is None:
        return False
    c_h, c_s, c_v = color_hsv
    i_h, i_s, i_v = INITIAL_COLOR_HSV

    hue_diff = abs(c_h - i_h)
    hue_diff = min(hue_diff, 180 - hue_diff)

    sat_diff = abs(c_s - i_s)
    val_diff = abs(c_v - i_v)

    if (hue_diff <= TOLERANCE_H and
        sat_diff <= TOLERANCE_S and
        val_diff <= TOLERANCE_V):
        return True
    return False

def shoot():
    try:
        win32api.mouse_event(win32con.MOUSEEVENTF_LEFTDOWN, 0, 0, 0, 0)
        time.sleep(0.01)
        win32api.mouse_event(win32con.MOUSEEVENTF_LEFTUP, 0, 0, 0, 0)
    except Exception as e:
        pass

def main_loop():
    os.system('color 05')
    print("""  
    __      __   _     _ 
    \ \    / /  (_)   | |
     \ \  / /__  _  __| |
      \ \/ / _ \| |/ _` |
       \  / (_) | | (_| |
        \/ \___/|_|\__,_|
                      
                      """)
    os.system('color 0F')
    print(" Press Insert to start/stop the triggerbot\n")
    global stop_script

    kb = threading.Thread(target=start_keyboard_listener, daemon=True)
    ms = threading.Thread(target=start_mouse_listener, daemon=True)
    kb.start()
    ms.start()

    try:
        while not stop_script:
            with lock:
                local_on = clicking_enabled
                local_rp = right_button_pressed

            if local_on:
                if local_rp:
                    current_hsv = get_pixel_color_hsv(x, y)
                    if current_hsv is None:
                        time.sleep(CHECK_INTERVAL)
                        continue

                    if not is_color_initial(current_hsv):
                        shoot()
                        time.sleep(SHOOT_INTERVAL)

            time.sleep(CHECK_INTERVAL)

    except KeyboardInterrupt:
        stop_script = True
    except Exception as e:
        stop_script = True

def main():
    if check_password():
        main_loop()
    else:
        sys.exit(1)

if __name__ == "__main__":
    main()
