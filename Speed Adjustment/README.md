# X1Plus Print Speed Adjustment UI

<img width="400" alt="image" src="https://github.com/user-attachments/assets/e11ab484-d99c-432c-8c42-302a6cab1e0d">

## Background

X1Plus adds a custom UI element that provides greater control over print speed than the OEM UI offers. A dial with an adjustable step size allows users to apply any speed multiplier from 30 to 166%. Additionally, the UI calculates the estimated print time remaining for the selected speed, allowing users to see in real time how these adjustments affect uptime. 

## How to enable

By default, the OEM speed adjustment UI is displayed to all X1Plus users, and this customized UI can be enabled via two methods:
1. Open the speed adjustment menu and press the ">" icon in the corner of the window.
<img width="400" alt="image" src="https://github.com/user-attachments/assets/cfec1aea-106d-4e90-9e0d-f300c9070dd2">

2. Using the X1Plus CLI, set the following setting:

`x1plus settings set printerui.speedadjust true`

X1Plus will remember this choice until you press the "<" icon on the X1Plus speed adjust UI or modify the setting. 

## Step size
The step size of the dial can be adjusted by toggling the 'Step size' button in the window or by modifying the following setting with the X1Plus settings CLI:

`x1plus settings set printerui.speedadjust.stepSize 2`


## Gcode sequence and calculations

Print speed adjustment on X1, P1, and A1 Bambu printers is applied with a series of 4 different Gcode commmands:

### M204.1 K
Acceleration magnitude, or the multiplier that is applied to your slicer profile acceleration settings. For "Normal" mode, K=1.0. The argument of this command is unitless. 

### M220 K
Feed rate multipler is used to adjust extrusion and feed rate. Similarly to the acceleration magnitude command, this command applies a unitless multiplier to your slicer settings (ie, it WILL override your slicer settings). The default value (Normal mode) is K=1.0. 

### M73.2 R
Time remaining multiplier. This parameter supplied to this command is used to adjust both the time remaining estimate and the displayed speed percentage in the slicer, Bambu Handy, and the touchscreen UI. This is easily calculated by dividing the target speed percentage by 100 and taking the inverse of this fraction. For instance, 200% speed would be a time multiplier of 100/200 = 0.5.

### M1002 set_gcode_claim_speed_level
This command is used by the UI to find the correct string value for a speed profile. It does not have any effect on print behavior. If you are applying your own speed profiles, you may exclude this command.

## Interpolating to define custom speed profiles

Below are the parameters for each of Bambu's speed profiles obtained from log data. X1Plus uses cubic spline interpolation and linear extrapolation to calculate acceleration magnitude and feed rate, which it then publishes to the printer when the 'Apply' button is pressed. 

|        | **Speed (%)** | **time_remaining** | **accel. magnitude** | **feed rate** |
|:------:|:-------------:|:------------------:|:--------------------:|:-------------:|
| Silent |       50      |          2         |          0.3         |      0.7      |
| Normal |      100      |          1         |           1          |       1       |
|  Sport |      125      |         0.8        |          1.4         |      1.4      |
|  Luda  |      166      |         0.6        |          1.6         |       2       |

<img width="400" alt="image" src="https://github.com/user-attachments/assets/44748ee8-53ed-481e-83f2-6eadad841b21">
