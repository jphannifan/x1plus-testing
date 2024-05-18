# Bambu Labs Gcode Commands - Under construction!


## Overview

This wiki provides documentation over BambuLabs Gcode, specifically for the X1 series. A majority of these commands work on other Bambu devices, but we have not tested on other devices. Several of these commands are being documented for the first time, and please take caution when using them. See below for information on the commands that X1Plus uses. 

## Table of Contents
- [Overview](#overview)
- [Homing and Positioning Commands](#homing)
- [Heaters](#heaters)
- [Fans](#fans)
- [Movement Commands](#movement)
  - [Linear Movements](#g0-and-g1)
  - [Arc Movements](#g2-and-g3)
- [Coordinates](#coordinates)
  - [Coordinate system commands](#coordinate-commands)
  - [Useful Coordinates](#useful-coordinates)


## Identifying Gcode format and parameters

On the X1C and X1E, every Gcode command that the printer parses can be followed in realtime by monitoring the service `forward` or by viewing the output it generates in syslog.log. I have written a [script](https://github.com/jphannifan/x1plus-testing/blob/main/scripts/python/log_monitor.py) that automates this monitoring step, allowing you to view the output of any Gcode command without needing to open log files. To run this script, place it on your SD card and run
`python3 /sdcard/log_monitor.py`

You'll then be prompted to enter a Gcode command. Multiline Gcode commands must be separated by an escape character. If you discover new commands or find that a command on this page is documented incorrectly, please notify me or file an issue. When you publish a command that the device does not recognize, you'll typically receive this response: 

`Gcode process inject cmd {command} fail!(0x11000005)
`

<img width="350" alt="log_monitor" src="https://github.com/jphannifan/x1plus-testing/assets/149451641/36c6e61d-f3ce-4523-a866-e8e6c8b00c06">

## Homing
| Command  | Argument | Use   |
|---|---|---|
| G29  | -  | Bed mesh calibration |
| G29.1  | Z{z_offset}  | Set z offset (mm)*, **|
| G28  | -  | Home all axes  |
| G28  | X  | XY homing  |
| G28  | Z P0  | Low precision Z home  |
| G28  | Z P0 T[temp]  | Lower precision Z home + heated nozzle  |
| G38  | S2 Z[z] F[speed]  | Move Z axis only (Z: mm, F: mm/s)  |
| G380***  | S2 Z[z] F[speed]  | Move Z axis only (Z: mm, F: mm/s)  |

*include brackets in this command \
** default = 0.00 mm \
*** G380 is the same as G38

## Heaters
| Command  | Argument  | Range | Use |
|---|---|---|---|
| M104  | S[temp]  | 0-300  | Set hotend temperature  |
| M140  | S[temp]  | 0-300  | Pause Gcode execution until set nozzle temp is reached  |
| M109  | S[temp]  | 0-110  | Set bed temperature  |
| M190  | S[temp]  | 0-110  |  Pause Gcode execution until set bed temp is reached  |

## Fans
| Command  | Argument  | Range | Use |
|---|---|---|---|
| M106  | P1 S[speed]  | 0-255  | Adjust part fan  |
| M106  | P2 S[speed]  | 0-255  | Adjust aux fan  |
| M106  | P3 S[speed]  | 0-255  | Adjust chamber fan  |
note: M106 P4 and P5 work as well, but these are not currently useful to us 

## Movement

### G0 and G1
| Command  | X Y Z  |  F  |  E  | Usage |
|---|---|---|---|---|
| G0 |  Absolute or relative (mm)  | Feed rate used from start to end point (mm/s) | N/A | Linear non-print movement |
| G1 |  Absolute or relative (mm)  | Feed rate used from start to end point (mm/s) | Abs/rel extrusion (mm) | Linear print movement |
```gcode
Usage:
G0 X0 Y0 F10000 ; Linear move to 0,0 at 10,000 mm/s^2 without extrusion
G1 X0 Y0 F10000 E5 ; Linear move to 0,0 at 10,000 mm/s^2 while extruding 5 mm of filament
G1 F20000 ; adjust acceleration to be used with upcoming movements
Note: the coordinate settings (relative or absolute) should always be specified before and after these movements
```

### G2 and G3
| Command  | X Y Z  |  I  |  J  |  R  |  F  |  E  | Usage |
|---|---|---|---|---|---|---|---|
| G2 |  Absolute or relative (mm)  | X offset (relative, mm) | Y offset (relative, mm) | Radius  |  Feed rate used from start to end point (mm/s) | Abs/rel extrusion (mm) | Clockwise arc |
| G3 |  Absolute or relative (mm)  | X offset (relative, mm) | Y offset (relative, mm) | Radius  |  Feed rate used from start to end point (mm/s) |Abs/rel extrusion (mm) (mm) | Counter-clockwise arc |
```gcode
G3 X2 Y7 I-4 J-3  ; Counter-clockwise arc movement offset by (-4,-3) - no extrusion
G2 X2 Y7 I-4 J-3  ; Clockwise arc movement offset by (-4,-3) - no extrusion
G3 X2 Y7 R5 ; Counter-clockwise arc movement with radius of 5 (mm)
G3 X20 Y20 R5 E0.5 ; Counter-clockwise arc around (20,20) with a radius of 5, extruding 0.5mm of filament
```

## Coordinates
### Coordinate commands
| Command  | Usage  
|---|---
| G90  | Absolute coordinates  
| G91  | Relative coordinates  
| G92 E0  | Reset extruder position  
| M83  | Set extruder relative  

### Useful coordinates
| Location  | X  | Y | Z |
|---|---|---|---|
| Center of build plate  | 128  | 128  | -  |
| LiDAR reference grid  | 240  | 90  | 8  |
| Print finished position  | 65  | 260  | 10  |
| Bed tramming screw 1  | 134.8  | 242.8  | -  |
| Bed tramming screw 2  | 33.2  | 13.2  | -  |
| Bed tramming screw 3  | 222.8  | 13.2  | -  |
| Build plate nozzle wipe tab | 135  | 253  | -  |

## Motor controls
| Command  | Argument  | Usage  
|---|---|---|
|  M17 | X Y Z  | Set stepper current (amps)  
|  M17 | R  | Restore default values  
|  M17 | S  | Enable steppers  
|  M18  | none  |  Disable all steppers   
|  M18  | X Y Z E  |  Disable steppers for certain axes  
Note: (X,Y,Z) = (1.2, 1.2, 0.75) defined as defaults in slicer

## Limit and endstop commands
| Command  | Argument |  Default |  Usage
|---|---|---|---|
| M201  | Z (mm/s) | -  | Z axis acceleration limit  |
| M204.2  | K  | 1.0  | Set acceleration multiplier
| M220  | S  | 100  | Set Feed Rate
| M204  | S  | -  | Acceleration limit (mm/s^2)
| M205  | X Y Z E (mm/s) | 0  | Set jerk limits
| M211  | X Y Z  (mm) | -  | Set soft endstops
| M221  | S  | 100  | Set Flow Rate
| M221  | S  | -  | Push soft endstop status
| M221  | Z0  | -  | Turn off Z endstop
```gcode
M221 S100 ; set the flow ratio to default (100%)
M221 S ; Push soft endstop status
M221 X0 Y0 Z1 ; turn off X and Y endstops, turn on Z endstop
M221 Z1 ; enable Z endstop
```

## Printer configuration
| Command  | Arguments | Usage  |
|---|---|---
| M412  | S0/S1  | Toggle filament runout detection 
| M302  | S70 P0/P1  | Toggle cold extrusion 
| M975  | S0/S1  | Toggle vibration compensation  
| M982.2  | C0/C1  |  Disable motor noise cancellation 
| G29.2 | S0/S1  |  Toggle bed mesh compensation
| M1003 | S0/S1  |  Toggle power loss recovery 
| M500  |  -    | Save to EEPROM

## Print Speed - [Click here for more info](https://github.com/jphannifan/x1plus-testing/blob/main/BL-speed-adjust.md)
| Command  | Argument  | Usage  |
|---|---|---|
| M204.2  | K (unitless)  | acceleration magnitude (default=1)  |
| M220  | K (unitless) | feed rate (default=1)  |
| M73.2  | R (unitless) | time constant (default=1)  |
| M1002  | set_gcode_claim_speed_level  | (default=5)  |

## Vibration Compensation
| Command  | Arguments   | Usage
|---|---|---
| M970  | Q A B C H K  | Vibration compensation frequency sweep
| M970.3  | Q A B C H K  | Vibration compensation fast sweep  
| M974  | Q S2 P0  | Apply curve fitting to vibration compensation data
| M975  | S0/S1  | Toggle vibration compensation  

```gcode
Vibration compensation:
M970 Q1 A7 B10 C125 K0 ; X axis range 1
M970 Q1 A7 B125 C250 K1 ; X axis range 2
M974 Q1 S2 P0 ; X axis curve fit
M970 Q0 A9 B10 C125 H20 K0 ; Y axis range 1
M970 Q0 A9 B125 C250 K1; Y axis range 2
M974 Q0 S2 P0 ; Y axis curve fit
M975 S1 ; enable vibration comp

Q: 0 for X axis, 1 for Y axis
A: amplitude (Hz)
B: lower range of sweep (Hz)
C: upper range of sweep (Hz)
H: undefined - optional parameter - units in Hz
K: not sure but = 0 or 1
```

| Command  |  Arguments  |  Usage 
|---|---|---|
| M900  | K L M  | Apply pressure advance to active filament preset  |
| M900  | - | Publish to return currently saved pressure advance |


## Skew compensation
| Command  | Argument |  Usage
|---|---|---|
| M1005  | X Y (mm) | Calculates skew (rad) from lengths of diagonals measured  |
| M1005  | I (rad)  | Overwrite skew value on printer  |
| M1005  | -  | Return current skew value stored on the printer  |
| M290.2  | X Y (mm) |  XY compensation  |


## LED controls
| Argument | Value  | Usage  |
|---|---|---|
|  M960 S1  | 0 or 1  | Toggle horizontal laser |
|  M960 S2  | 0 or 1  | Toggle vertical laser  | 
|  M960 S3  | 0 or 1  | Toggle toolhead LED  | 
|  M960 S4  | 0 or 1  | Toggle nozzle LED |  
|  M960 S0  | 0 or 1  | Toggle all LEDs  |  

## Camera Controls
| Command | S  |  P |  Usage  
|---|---|---|---|
| M973  | S3  | - | Nozzle cam on  
| M973  | S4  | - | Nozzle cam off  
| M973  | S1  |  |  Nozzle cam autoexpose 
| M973  | S  | P[exposure]  | Set nozzle camera exposure  
| M971  | S  | P[exposure]  | Capture image to /userdata/log/ 
| M976  | S1  | P[num]  | First layer scan
| M976  | S2  | P1  | Hotbed scan
| M976  | S3  | P2  | Register void printing detection
| M991  | S0  | P0  | Notify printer of layer change
| M991  | S0  | P-1  | End smooth timelapse at safe pos
| M981  | S0 | P20000  | Spaghetti detector off
| M981  | S1 | P20000  | Spaghetti detector on 
| M972  | S5 | P0  | Measure Xcam clarity 


```gcode
M973 S6 P0 ; auto expose for horizontal laser
M973 S6 P1 ; auto expose for vertical laser
```

| Command  | Argument  | Usage
|---|---|---
| M1002  | gcode_claim_action  | Display message on LCD
| M1002  | judge_flag  | Display message on LCD  
| M1002  | set_gcode_claim_speed_level  |  Update speed profile setting on LCD 
```gcode
0  Clear
1  Auto bed levelling
2  Heatbed preheating
3  Sweeping XY mech mode
4  Changing filament
5  M400 pause
6  Paused due to filament runout
7  Heating hotend
8  Calibrating extrusion
9  Scanning bed surface
10  Inspecting first layer
11  Identifying build plate type
12  Calibrating Micro Lidar
13  Homing toolhead
14  Cleaning nozzle tip
15  Checking extruder temperature
16  Paused by the user
17  Pause due to the falling off of the tool head’s front cover
18  Calibrating the micro lidar
19  Calibrating extruder flow
20  Paused due to nozzle temperature malfunction
21  Paused due to heat bed temperature malfunction
```


| Command  | Argument  | Usage
|---|---|---|
| M400  | -  | Finish the current | Pause until last Gcode command is complete
| M400  | S[t]  | Wait for last command to complete + delay in seconds  
| M400  | P[t]  | Wait for last command to complete + delay in milliseconds  
| M400  | U1  | Wait until user presses 'Resume'  
| G4  | S90  | Delay 90 seconds (does not block Gcode execution)*
| M73  | P[p] R[r]  | Update print progress
| M73.2  | R1.0  | Reset print progress
*note: 90s is max value that can be delayed with G4. To delay for > 90 sec, run multiple G4 S90

### AMS
```gcode
M622 J{j}
```

```gcode
M623
```

Retract filament
```gcode
M620 S255
; retraction gcode
M621 S255
```
```gcode
M622.1 S1 
```
# Select extruder
```gcode
T255
```



|  Command  |  Argument | Usage
|---|---|---
| T | 255 | Switch to empty tool
| T | 1000 | Switch to nozzle
| T | 1100 | Switch to scanning space

note: X1 uses M620 to perform actual toolchange 


M620 M
M620 S[initial_no_support_extruder]A 
M621 S[initial_no_support_extruder]A
M620.1 E F{accel} T{temp}

M620
M620 C# - calibrate AMS by AMS index
M620 R# - refresh AMS by tray index
M620 P# - select AMS tray by tray index
M620 S# - select AMS by tray index
M621
M621 S#- load filament in AMS by tray index
Stolen from Doridian's repo https://github.com/Doridian/OpenBambuAPI/blob/main/gcode.md

# undocumented still
```gcode
G29.4 S0/S1 - toggles "high freq z comp" 
G29.5 - "G29.5 failed: invalid params"
G29.6, G29.7, G29.8 - runs normal bed probing sequence? 
M969 S1 N3 A2000
M964: NO_NEW_EXTRIN_CALI_PARA
M963 squence dismatch! Need(15) Get(15) rtn=0x1
M967
M966
M980.3 A B C D E F G H I J K 
G92.1 E0
noise cancellation:
M982 Q P V D L T I
M982.4 S V
```
