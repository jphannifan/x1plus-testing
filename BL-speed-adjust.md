# Bambu Print Speed Gcode:

### Gcode commands the printer and slicer user to apply speed profiles:
```
Compatible with A1, P1, and X1 series printers:
M204.2 K1.0 ; acceleration magnitude (unitless)
M220 K1.0 ; feed rate (unitless)
M73.2 R1.0 ; time remaining constant (unitless)
M1002 set_gcode_claim_speed_level 5 ; speed level
```
### M204.2
This is a previously undocumented command that sets the "acceleration magnitude" for all axes of the printer. The multiplier in this command is applied (at runtime) to the acceleration values defined in the slicer. See the table below for the multipliers used for each speed profile. `M204.2 K1.0` is the default, or "Normal" profile.

### M220
This command has previously been identified as the "feed rate reset" command, however it functions similarly to M204.2 in that it applies a multiplier to the values defined in the slicer. `M220 K1.0` is the default, or "Normal" profile.

### M73.2
This is the "time remaining" command. The printer monitors how long it takes to print a single layer at a given speed and then it's able to estimate the total print time. It uses the multiplier in this command to scale its time estimates. The multiplier used in this command is the inverse value of the percentage speed. Note: the speed displayed by the printer, slicer, and app are calculated by the inverse of this multiplier. 

### M1002
This is a function that updates the status text on the print progress timeline. This command is not necessary to change print speeds!

## Parameters from BL's speed levels
|        | **Speed (%)** | **time_remaining** | **accel. magnitude** | **feed rate** |
|:------:|:-------------:|:------------------:|:--------------------:|:-------------:|
| Silent |       50      |          2         |          0.3         |      0.7      |
| Normal |      100      |          1         |           1          |       1       |
|  Sport |      125      |         0.8        |          1.4         |      1.4      |
|  Luda  |      166      |         0.6        |          1.6         |       2       |

## Fitting trendlines to these data:
<img width="1000" alt="interpolate" src="https://github.com/jphannifan/x1plus-testing/assets/149451641/df6884e5-860b-4f17-9166-12ae04747be9">

- **Speed Fraction**:
```math
$$ \text{speed\_fraction} = floor\left\lfloor \frac{10000}{\text{speed\_percent}} \right\rfloor / 100 $$
```
- **Acceleration Magnitude**:
```math
$$ \text{acc\_mag} = \exp\left(\frac{\text{speed\_percent} - 1.0191}{-0.8139}\right) $$
```
- **Feed Rate**:
```math
$$ \text{feed\_rate} = 6.426 \times 10^{-5} \times \text{speed\_percent}^2 - 2.484 \times 10^{-3}  \text{speed\_percent} + 6.54\times 10^{-1} $$
```
## Interpolated data from trendlines
|        | **Speed (%)** | **time_remaining** | **accel. magnitude** | **feed rate** |
|:------:|:-------------:|:------------------:|:--------------------:|:-------------:|
| Silent |       50      |          2         |         0.300        | 0.690         |
| Normal |      100      |          1         |         1.024        | 1.048         |
|  Sport |      125      |         0.8        |         1.309        | 1.348         |
|  Luda  |      166      |        0.602       |         1.669        | 2.012         |


## Notes
- The purpose of fitting trendlines and carefully scaling these parameters is to ensure consistent extrusion rates over the range being interpolated. You can modify M204.2 or M220 separately, but this will result in erratic extrusion profiles. 
- The tested range for these trendlines is 30% to 180%. It is possible to extrapolate and go above 180% up to around 500%, however these trendlines will not work. 
- These trendlines and Gcode commands can be used to apply custom speed levels to A1, P1, and X1 printers. The same Gcode commands will work, however the X1 is the only model with direct support for this feature.
- M204.2 impacts the toolhead speed during print startup. This could result in unexpected high speed toolhead movements. You can also use this to increase the speed of the touchscreen extruder controls. 
