import math
import argparse
import dds 
import json
import time

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
           
parser = argparse.ArgumentParser(description='Speed adjust: enter value between 30 and 180%')
parser.add_argument('--s', type=int, required=True)

# Example usage:
args = parser.parse_args()
publish_dds = dds.publisher('device/request/print') #specify dds topic
time.sleep(1) #wait for dds to init
speed = max(30, min(180, round(args.s / 2) * 2)) #round it to the nearest even number
msg = {"command": "gcode_line", "param": speed_adjust(speed), "sequence_id":0}
publish_dds(json.dumps(msg))