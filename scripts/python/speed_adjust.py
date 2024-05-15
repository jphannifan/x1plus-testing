import paho.mqtt.client as mqtt
import json
import ssl
import time
import os
import math

settings_file = 'mqtt_settings.json'

## Speed Adjustment for Bambu printers
# Please refer to this page for info on how I created these trendlines:
# https://github.com/jphannifan/x1plus-testing/blob/main/BL-speed-adjust.md
#
# These trendlines allow us to apply "speeds" between 30 and 180%, maintaining
# consistent extrusion profiles. This gcode should work on any Bambu device, and
# Bambu Studio and the Bambu app will update their reported speeds and time estimates
# accordingly. The slicer, app, and printer do not display odd numbered speed values
# For this reason, the speed is rounded to the nearest even number. If designing a 
# UI with this, I recommend using a slider or dial with a step size of 2, from 30 to 180.
# X1Plus provides native touchscreen support for this feature.
# See Wolf_with_sword's HA workflow for the HA implementation of this feature.

speed_interp = {
    'speed_fraction': lambda speed_percentage: math.floor(10000 / speed_percentage) / 100,
    'acceleration_magnitude': lambda speed_fraction: math.exp((speed_fraction - 1.0191) / -0.814),
    'feed_rate': lambda speed_percentage: (0.00006426) * speed_percentage ** 2 + (-0.002484) * speed_percentage + 0.654,
    'level': lambda acceleration_magnitude: (1.549 * acceleration_magnitude ** 2 - 0.7032 * acceleration_magnitude + 4.0834)
}

def speed_adjust(speed_percentage):
    if speed_percentage < 30 or speed_percentage > 180: #these trendlines should not be used to extrapolate! 
        speed_percentage = 100
    
    speed_fraction = speed_interp['speed_fraction'](speed_percentage)
    acceleration_magnitude = speed_interp['acceleration_magnitude'](speed_fraction)
    feed_rate = speed_interp['feed_rate'](speed_percentage)



    return f"M204.2 K{acceleration_magnitude:.2f}\n" \
           f"M220 K{feed_rate:.2f}\n" \
           f"M73.2 R{speed_fraction}\n" 


def on_connect(client, userdata, flags, reason_code, properties):
    if reason_code == "Unsupported protocol version":
        print("something wrong!")
    if reason_code == "Client identifier not valid":
        print("something wrong!")

def on_message(client, userdata, message):
    print("Message received: " + str(message.payload.decode("utf-8")))

def save_settings(address, password,dev_id):
    with open(settings_file, 'w') as file:
        json.dump({'address': address, 'password': password, 'dev_id':dev_id}, file)

def load_settings():
    if os.path.exists(settings_file):
        with open(settings_file, 'r') as file:
            return json.load(file)
    else:
        return None

def main():

    client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2)
    settings = load_settings()
    if settings is None:
        password = input("Enter Printer LAN code: ")
        address = input("Enter printer ip: ")
        dev_id = input("Enter your device's serial number: ")
        save_settings(address, password,dev_id)
    else:
        address = settings['address']
        password = settings['password']
        dev_id = settings['dev_id']

    client.username_pw_set('bblp', password)

    client.tls_set(tls_version=ssl.PROTOCOL_TLS, cert_reqs=ssl.CERT_NONE)
    client.tls_insecure_set(True)
    client.on_connect = on_connect
    client.on_message = on_message
    client.connect(address, 8883, 60)
    client.loop_start()

    try:
        while True:
            gcode_command = int(input("Enter an even-numbered value between 30 and 180 (speed %) or type 0 to exit: "))
            if gcode_command == '0':
                break

            topic = f"device/{dev_id}/request"
            message = {
                "print": {
                    "command": "gcode_line",
                    "sequence_id": 0,
                    "param": speed_adjust(gcode_command)
                }
            }
            client.publish(topic, json.dumps(message))
            print(f"Message '{message}' sent to topic '{topic}'")
            time.sleep(1)  

    finally:
        client.loop_stop()
        client.disconnect()

if __name__ == "__main__":
    main()
