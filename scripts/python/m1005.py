import math
import os
import time
import re
import dds
import json

# This is pretty shitty code
stored_value = {}

def pub_dds(ddspub, cmd):
    msg = {"command": "gcode_line", "param": cmd, "sequence_id": 0}
    ddspub(json.dumps(msg))
    print(f"Command {cmd} published")

def handle_new_value(match, ddspub):
    print(f"M1005 new value: {match.group(1)}")
    if input("Save this value? (y/n): ").lower() == 'y':
        stored_value['XY_comp_ang'] = match.group(1)
        pub_dds(ddspub, "M500")
        print("Value saved and command sent to printer.")

def handle_old_value(match):
    print(f"Current XY_comp_ang: {match.group(1)}")

def log_monitor(ddspub, regex_actions):
    try:
        with open("/tmp/syslog.log", "r") as file:
            file.seek(0, os.SEEK_END)  # Start at the end of the file
            while True:
                line = file.readline()
                if not line:
                    time.sleep(0.5)  # Sleep briefly to avoid busy waiting
                    continue
                for pattern, action in regex_actions:
                    if match := re.search(pattern, line):
                        action(match)  # Pass only the match object
                        return  # Exit after first match to stop the log monitor
    except Exception as e:
        print(f"Failed to monitor log file: {e}")

def delete_values(ddspub):
    stored_value.clear()
    pub_dds(ddspub, "M1005 I0 \nM500 \n")
    print("M1005 I0 - skew compensation factor set to 0.")

def get_values(ddspub, regex_actions):
    pub_dds(ddspub, "M1005")
    log_monitor(ddspub, regex_actions)  # Start and stop monitoring upon finding a match

def calculate_geometry(ddspub):
    try:
        CD = float(input("Enter measurement for CD: "))
        AB = float(input("Enter measurement for AB: "))
        AC = float(input("Enter measurement for EF: ")) / math.sqrt(2)
        CB = round(math.sqrt(2 * CD**2 + 2 * AB**2 - 4 * AC**2) / 2,2)
        skew_factor = -round(math.tan(math.pi/2 - math.acos((CD**2 - CB**2 - AC**2) / (2 * CB * AC))),5)
        print(f"Calculated skew factor: {skew_factor}")
        stored_value['CB'] = CB
        stored_value['Skew Factor'] = skew_factor
        if input(f"Apply gcode M1005 I{skew_factor}? (y/n): ").lower() == 'y':
            pub_dds(ddspub, f"M1005 I{skew_factor}")
            if input(f"Save gcode M1005 I{skew_factor}? (y/n): ").lower() == 'y':
                pub_dds(ddspub, "M500")
                print(f"Skew factor {skew_factor} applied and saved")
    except Exception as e:
        print(f"An error occurred during calculation: {e}")

def main_menu(ddspub):
    regex_actions = [
        (r".*M1005:new\s*XY_comp_ang\s*=\s*(-?\d+\.?\d*)", lambda match: handle_new_value(match, ddspub)),
        (r".*M1005:current\s*XY_comp_ang\s*=\s*(-?\d+\.?\d*)", lambda match: handle_old_value(match)),
    ]
    while True:
        skew_factor = stored_value.get('Skew Factor')
        if skew_factor is not None:
            printstr = f"3. Apply and save calculated factor: {skew_factor}"
        else:
            printstr = "3. Calculate compensation factor"
        print("\nMenu Options:")
        print("1. Delete current skew values on the printer")
        print("2. Get current values on the printer")
        print(printstr)
        print("4. Apply and save your own skew compensation")
        choice = input("Enter your choice: ")
        if choice == '1':
            delete_values(ddspub)
        elif choice == '2':
            get_values(ddspub, regex_actions)
        elif choice == '3':
            if skew_factor is not None:
                pub_dds(ddspub, f"M1005 I{skew_factor} \nM500 \n")
                print(f"Publishing M1005 {skew_factor} M500")
            else:
                calculate_geometry(ddspub)
        elif choice == '4':    
            custom_skew = float(input("Enter skew factor: "))
            pub_dds(ddspub, f"M1005 I{custom_skew} \nM500 \n")
            print(f"Publishing M1005 {custom_skew} M500")
        else:
            print("Invalid option, please try again.")

def main():
    pub = dds.publisher('device/request/print')
    time.sleep(1.5
    )
    main_menu(pub)

if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        dds.shutdown()
        print(f"An error occurred: {e}")
        raise
