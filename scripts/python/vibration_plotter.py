import matplotlib.pyplot as plt
import json
import sys
import numpy as np
import matplotlib.ticker as ticker

# Plot vibration compensation data from X1Plus
# JSON file is located in /mnt/sdcard/x1plus/printer/{serial}/logs/vibration_comp.json

if len(sys.argv) < 2:
    print("Usage: python3 script.py <path_to_json_file>")
    sys.exit(1)

json_file_path = sys.argv[1]

with open(json_file_path, 'r') as file:
    data = json.load(file)

runs = data['runs']

plt.figure(figsize=(10, 6))  

for timestamp, details in runs.items():
    frequencies = sorted([int(freq) for freq in details['axes']['x']['points'].keys()])
    x_responses = [details['axes']['x']['points'][str(freq)].get('a', 0) for freq in frequencies]
    y_responses = [details['axes']['y']['points'][str(freq)].get('a', 0) for freq in frequencies]

    plt.plot(frequencies, x_responses, label=f'X Axis Response @ {timestamp}')
    plt.plot(frequencies, y_responses, label=f'Y Axis Response @ {timestamp}', linestyle='--')

plt.xlabel('Frequency (Hz)')
plt.ylabel('Response Value (a)')
plt.title('Frequency Response for X and Y Axes Across Runs')

desired_ticks = np.linspace(min(frequencies), max(frequencies), 12)
plt.xticks(ticks=desired_ticks, labels=[f"{int(tick)}" for tick in desired_ticks])

plt.legend()
plt.tight_layout()
plt.show()
