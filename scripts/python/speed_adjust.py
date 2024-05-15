import paho.mqtt.client as mqtt
import json
import ssl
import time
import os
import math

settings_file = 'mqtt_settings.json'

def speed_interp(speed_percentage):
    """Calculate the speed interpolation values for the given speed percentage."""
    if speed_percentage < 30 or speed_percentage > 180:
        speed_percentage = 100  # Ensure the speed is within the valid range.
    speed_fraction = math.floor(10000 / speed_percentage) / 100
    acceleration_magnitude = math.exp((speed_fraction - 1.0191) / -0.814)
    feed_rate = (0.00006426) * speed_percentage ** 2 + (-0.002484) * speed_percentage + 0.654
    return f"M204.2 K{acceleration_magnitude:.2f}\n" \
           f"M220 K{feed_rate:.2f}\n" \
           f"M73.2 R{speed_fraction}\n"

def on_connect(client, userdata, flags, reason_code, properties):
    if reason_code != 0:
        print("Failed to connect with reason code:", reason_code)

def on_message(client, userdata, message):
    print("Message received:", message.payload.decode("utf-8"))

def save_settings(address, password, dev_id):
    with open(settings_file, 'w') as file:
        json.dump({'address': address, 'password': password, 'dev_id': dev_id}, file)

def load_settings():
    if os.path.exists(settings_file):
        with open(settings_file, 'r') as file:
            return json.load(file)
    return None

def main():
    client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2)
    settings = load_settings()
    if settings is None:
        password = input("Enter Printer LAN code: ")
        address = input("Enter printer IP: ")
        dev_id = input("Enter your device's serial number: ")
        save_settings(address, password, dev_id)
    else:
        address, password, dev_id = settings['address'], settings['password'], settings['dev_id']

    client.username_pw_set('bblp', password)
    client.tls_set(tls_version=ssl.PROTOCOL_TLS, cert_reqs=ssl.CERT_NONE)
    client.tls_insecure_set(True)
    client.on_connect = on_connect
    client.on_message = on_message
    client.connect(address, 8883, 60)
    client.loop_start()

    input_speed = int(input("Enter the initial speed percentage (even value between 30 and 180): "))
    target_speed = int(input("Enter the target speed percentage (even value between 30 and 180): "))
    step_size = int(input("Enter the step size: "))
    time_interval = float(input("Enter the time interval between commands (seconds): "))

    try:
        speed = input_speed
        direction = 1 if target_speed >= input_speed else -1
        while (direction == 1 and speed <= target_speed) or (direction == -1 and speed >= target_speed):
            gcode_command = speed_interp(speed)
            topic = f"device/{dev_id}/request"
            message = {
                "print": {
                    "command": "gcode_line",
                    "sequence_id": 0,
                    "param": gcode_command
                }
            }
            client.publish(topic, json.dumps(message))
            print(f"Message '{message}' sent to topic '{topic}'")
            time.sleep(time_interval)
            speed += step_size * direction
    finally:
        client.loop_stop()
        client.disconnect()

if __name__ == "__main__":
    main()
