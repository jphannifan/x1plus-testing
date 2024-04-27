#!/usr/bin/env python3

import os
import json
import time
import dds
import subprocess
from evdev import InputDevice, categorize, ecodes
from logger.custom_logger import CustomLogger

LONG_PRESS_THRESHOLD = 0.850  # seconds
KEY_POWER = 116
KEY_STOP = 128

gpio_dds_publisher = dds.publisher('device/x1plus')
gpio_log = CustomLogger("gpiokeys", "/tmp/gpiokeys.log", 500000, 1, True)

def send_dds(name, press_type):
    dds_payload = json.dumps({
        "gpio": {
            "button": name,
            "event": press_type
        }
    })
    gpio_dds_publisher(dds_payload)
    
def load_button_config(path):
    try:
        with open(path, 'r') as file:
            return json.load(file)
    except Exception as e:
        gpio_log.error(f"Failed to load button configuration: {e}")
        return {}

def _get_sn():
    try:
        return subprocess.check_output(["bbl_3dpsn"], stderr=subprocess.DEVNULL).decode("utf-8").strip()
    except Exception as e:
        gpio_log.error("Error getting serial number: " + str(e))
        return None

class Button:
    def __init__(self, scancode, name):
        self.pressed = None
        self.scancode = scancode
        self.name = name

    def press(self):
        self.pressed = time.time()

    def release(self):
        elapsed_time = time.time() - self.pressed
        press_type = "shortPress" if elapsed_time < LONG_PRESS_THRESHOLD else "longPress"
        action_info = button_config.get(self.name, {}).get(press_type, {})
        action = action_info.get("action")
        if action == "ACTION_MACRO":
            script_path = action_info.get("parameters")
            self.run_macro(script_path)
            gpio_log.info(f"Executing macro for {self.name} button {press_type}: {script_path}")
        else:
        	send_dds(self.name, press_type)
        self.pressed = None

    def run_macro(self, script_path):
        if script_path:
            try:
                subprocess.run(["/opt/python/bin/python3", script_path], check=True)
                gpio_log.info(f"Macro executed successfully: {script_path}")
            except subprocess.CalledProcessError as e:
                gpio_log.error(f"Failed to execute macro: {script_path}, Error: {e}")

buttons = [
    Button(scancode=KEY_POWER, name="power"),
    Button(scancode=KEY_STOP, name="estop"),
]

file_path = '/mnt/sdcard/x1plus/printers/'
serial_number = _get_sn()
if serial_number:
    full_path = os.path.join(file_path, serial_number, "buttons.json")
    if os.path.exists(full_path):
        button_config = load_button_config(full_path)
    else:
        gpio_log.error("Configuration file not found at: " + full_path)
else:
    gpio_log.error("No serial number found, cannot load button configurations.")

device = InputDevice("/dev/input/by-path/platform-gpio-keys-event")
device.grab()

try:
    for event in device.read_loop():
        if event.type != ecodes.EV_KEY:
            continue

        data = categorize(event)
        for button in buttons:
            if button.scancode == data.scancode:
                if data.keystate == 1:  # Key is pressed
                    button.press()
                elif data.keystate == 0:  # Key is released
                    button.release()
                    gpio_log.info(f"{button.name} button action completed.")
                    print(f"{button.name} button action completed.")
except:
    raise
finally:
    device.ungrab()
