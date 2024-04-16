# Bambu Print Speed Adjustment:

### Gcode command
```
M204.2 K0.3 ; acceleration magnitude (unitless)
M220 K0.7 ; feed rate (unitless)
M73.2 R2.0 ; time remaining constant (unitless)
M1002.set_gcode_claim_speed_level 5 ; speed level
```
## Parameters from BL's speed levels
|        | **Speed (%)** | **time_remaining** | **accel. magnitude** | **feed rate** |
|:------:|:-------------:|:------------------:|:--------------------:|:-------------:|
| Silent |       50      |          2         |          0.3         |      0.7      |
| Normal |      100      |          1         |           1          |       1       |
|  Sport |      125      |         0.8        |          1.4         |      1.4      |
|  Luda  |      166      |         0.6        |          1.6         |       2       |

## Fitting trendlines to these data:
<img width="1000" alt="interpolate" src="https://github.com/jphannifan/x1plus-testing/assets/149451641/df6884e5-860b-4f17-9166-12ae04747be9">

```
speed_fraction =  Math.floor(10000/speed_percent)/100}
acc_mag = Math.exp((speed_percent-1.0191)/-0.8139) 
feed_rate = (6.426*10^-5)*speed_percent**2 - (2.484*10^-3)*speed_percent + 0.654
```

## Interpolated data from trendlines
|        | **Speed (%)** | **time_remaining** | **accel. magnitude** | **feed rate** |
|:------:|:-------------:|:------------------:|:--------------------:|:-------------:|
| Silent |       50      |          2         |         0.300        | 0.690         |
| Normal |      100      |          1         |         1.024        | 1.048         |
|  Sport |      125      |         0.8        |         1.309        | 1.348         |
|  Luda  |      166      |        0.602       |         1.669        | 2.012         |

## Notes:
- The X1C and X1E (and probably A1 and P1) are only able to display speed %s that are whole even numbers between 0 and 510%. Keep this in mind when applying custom speed levels
- The percentage speed reported by the slicer and the printer are calculated solely from the parameter of M73.2. This is also the value used to calculate the time remaining estimate. Make sure your feed rate and acceleration magnitude are scaled properly if you extrapolate (ie applying speeds above 166%)
