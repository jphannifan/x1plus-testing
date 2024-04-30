
import os
import sys
import re
import json
from logger.custom_logger import CustomLogger
from collections import namedtuple
from logger.tail import TailLog
import dds
import math
import time

### M1005 logging and persistence:
# 1) Replace /opt/syslog_shim.py with this script
# 2) Optional: Save your calculated skew correction factor (value in radians) in a text file*** in /mnt/sdcard/skew.txt 
#   - This command alters the toolhead's positioning, so I highly advise making this file read only 
#   - Make it read-only: chmod 444 /mnt/sdcard/skew.txt
# 3) Reboot or restart the logging service and now all XY_comp_ang data will be sent to /tmp/x1plus_data.log
#    and if you have a skew correction value stored in skew.txt, it will apply it when the printer is rebooted
# 4) This modification will be overwritten the next time you install an x1p file. 
# *** Do not include the gcode command in this file! Only the value, e.g. "0.00113"
#######################################
skew_file_path = "/mnt/sdcard/skew.txt"
#######################################
log_path = (
    "/mnt/sdcard/log/"
    if os.path.exists("/tmp/.syslog_to_sd") and os.path.exists("/mnt/sdcard/log/")
    else "/tmp/"
)
shim_log_path = os.path.join(log_path,"x1plus_data.log")
syslog_log = CustomLogger("Syslog shim data", shim_log_path, 500000, 1)
log_path = os.path.join(log_path,"syslog.log")


# Define a basic mechanism for "do something when you see some particular
# type of line in the syslog".
RegexHandler = namedtuple("RegexHandler", ["regex", "callback"])

dds_publish_mc_print = dds.publisher("device/report/mc_print")
dds_m1005 = dds.publisher("device/request/print")
time.sleep(3)
try:
    skew_factor = 0
    if not os.path.exists('/tmp/m1005'):
        if os.path.exists(skew_file_path):
            with open(skew_file_path, 'r') as f:
                skew_factor = f.read().strip()
                skew_factor = float(skew_factor)

        if math.fabs(skew_factor) > 0:
            cmd = f"M1005 I{skew_factor}\nM500\n" 
            open('/tmp/m1005', 'w').close()
        else:
            cmd = "M1005" 
        dds_m1005(json.dumps({"command": "gcode_line", "param": cmd, "sequence_id": 0}))
except (IOError, ValueError) as e:
    print(f"Error reading skew factor from file: {str(e)}")
    skew_factor = 0
        
def RegexParser(regex, format):
	"""
	A RegexHandler that takes a reformatter lambda and wraps it in a DDS publisher.
	"""
	compiled_regex = re.compile(regex)
	def fn(match):
		obj = format(match)
		print(f"Publishing matched object: {obj}", file=sys.stderr)
		syslog_log.info(f"[x1p] - {json.dumps(obj)}")
		dds_publish_mc_print(json.dumps(obj))

	return RegexHandler(compiled_regex, fn)


# Paired with X1Plus.BedMeshCalibration and X1Plus.ShaperCalibration.
syslog_data = [
    # Bed Mesh data
    RegexParser(
            r".*\[BMC\]\s*X(-?\d+\.\d*)\s*Y(-?\d+\.\d*),z_c=\s*(-?\d+\.\d*)",
        lambda match: {
            "command": "mesh_data",
            "param": {
                "x": float(match.group(1)),
                "y": float(match.group(2)),
                "z": float(match.group(3)),
            },
        },
    ),
    # Vibration compensation
    RegexParser(
            r".*\[BMC\]\s*f=(-?\d+\.\d*),\s*a=(-?\d+\.\d*),\s*ph=\s*(-?\d+\.\d*),\s*err\s*(\d+)",
        lambda match: {
            "command": "vc_data",
            "param": {
                "f": float(match.group(1)),
                "a": float(match.group(2)),
                "ph": float(match.group(3)),
                "err": int(match.group(4)),
            },
        },
    ),
    # Vibration compensation
    RegexParser(
            r".*\[BMC\]\s*wn(-?\d+\.\d*),ksi(-?\d+\.\d*),\s*pk(-?\d+\.\d*),l(-?\d+\.\d*),h(-?\d+\.\d*)",
        lambda match: {
            "command": "vc_params",
            "param": {
                "wn": float(match.group(1)),
                "ksi": float(match.group(2)),
                "pk": float(match.group(3)),
                "l": float(match.group(4)),
                "h": float(match.group(5)),
            },
        },
    ),
    # Vibration compensation
    RegexParser(
        r".*\[BMC\]\s*(M975\s*S1)",
        lambda match: {"command": "vc_enable"},
    ),
	# K values
    RegexParser(
            r".*\[BMC\]\s*M900\s*power\s*law:K(-?\d+\.?\d*),N(-?\d+\.?\d*)",
        lambda match: {
            "command": "k_values",
            "param": {
                "K": float(match.group(1)),
                "N": float(match.group(2)),
            },
        },
    ),
   # z offset
    RegexParser(
        r".*z_trim:(-?\d+\.\d*)",
        lambda match: {
            "command": "z_offset",
            "param": {
                "z_offset": float(match.group(1)),
            },
        },
    ),
    # detected build plate id
    RegexParser(
        r".*detected\s*build\s*plate\s*id:\s*(-?\d)",
        lambda match: {
            "command": "build_plate_id",
            "param": {
                "id": int(match.group(1)),
            },
        },
    ),
    # bed strain sensitivity
    RegexParser(
        r".*strain\s*(\d)*\s*sensitivity\s*=\s*(-?\d+\.?\d*),p=(-?\d+\.\d*),Vs=(-?\d+\.\d*)",
        lambda match: {
            "command": "bed_strain",
            "param": {
                "sensitivity": float(match.group(1)),
                "p": float(match.group(2)),
                "Vs": float(match.group(3)),
            },
        },
    ),
   # M1005 skew factor
    RegexParser(
        r".*M1005:(new|current)\s*XY_comp_ang\s*=\s*(-?\d+\.?\d*)",
        lambda match: {
            "command": "M1005",
            "param": {
                "skew":  match.group(1),
                "XY_comp_ang":  float(match.group(2)),
            },
        },
    ),
]
	
 
def main():

    tail_syslog = TailLog(log_path)
    for line in tail_syslog.lines():
        for handler in syslog_data:
            match = handler.regex.match(line)
            if match:
                handler.callback(match)


if __name__ == "__main__":
    try:
        main()
    except:
        dds.shutdown()
        raise
