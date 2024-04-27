## Skew calibration for X1c running X1Plus

1) Download ["m1005.py"](https://github.com/jphannifan/x1plus-testing/blob/main/scripts/python/m1005.py) from /scripts/python and save it to your printer in the folder `/opt/`
2) Download the [skew calibration model](https://github.com/jphannifan/x1plus-testing/blob/main/skew.step) (or use your own) and print it. I print mine at 100% scale with PLA and default slicer settings.
3) Launch the script from Step 1 by opening an SSH session with your printer and running the following command:
   `/opt/python/bin/python3 /opt/m1005.py`
4) Follow the command line instructions. The script will complete all of the calculations and enter the gcode commands necessary. You can view the current skew compensation value saved on your printer by running option 2
   <img width="354" alt="image" src="https://github.com/jphannifan/x1plus-testing/assets/149451641/7ae77a62-22d9-4396-a781-363d97af46d2">
5) After applying the correction factor, print the same model again in the same orientation with the same settings. Then start this process over again from step 3 until you're satisfied with the result.

## Skew calibration for all other Bambu devices

1) Download this Google worksheets document (link coming soon) and download the [skew calibration model](https://github.com/jphannifan/x1plus-testing/blob/main/skew.step)

2) Print the calibration model and using calipers measure 3 of the segments as detailed below. Enter your measurements into the worksheet to obtain the skew correction factor. Note: the printer appears to round to 4 digits (ie if you save a skew of 0.00113, 0.0011 will be the value that is actually saved)

3) Publish MQTT command to apply and save values. If you would prefer to not use MQTT, you may skip 3 and 4 and add the gcode command containing your skew factor to your print startup code. Publish this MQTT command, replacing 
{skew_factor} with your calculated value:
```
device/#/request

{"print": {"command": "gcode_line", "param": "M1005 I{skew_factor} \n M500\n", "sequence_id": 123}}
```

4) To verify that your skew factor has actually been applied, you can publish the M1005 command with no arguments and the printer will output a response via MQTT. This XY_comp_ang value is the skew factor currently active on youe device. 

## Measurements

This skew calibration model can also be used to check the accuracy of each axis and to calculate a correction factor you can use to correct dimensional inaccuracy in your prints. For skew calibration, you only need to make 3 measurements. The skew calibration model I have made allows you to make the same 3 measurements from different sides of an octagon, so if you are using a different model you may need to confirm you are measuring the correct segments.

<img width="300" alt="image" src="https://github.com/jphannifan/x1plus-testing/assets/149451641/72596bf0-5565-40c8-ab55-13b8242b759e">
<img width="320" alt="image" src="https://github.com/jphannifan/x1plus-testing/assets/149451641/54bf52c5-6b32-4c25-b739-dbde8dd32669">

The diameter of this octagon (at 100% scale) is 85 mm. If you are using the notches for aligning caliper jaws, the diameter will be 79 mm. 

Enter your measurements into the script prompts and to apply the skew factor, press 'y'.

<img width="266" alt="image" src="https://github.com/jphannifan/x1plus-testing/assets/149451641/7a0cee41-e47a-491a-8be1-77eae9b843cc">



## Measurement guide

<img width="300" alt="image" src="https://github.com/jphannifan/x1plus-testing/assets/149451641/7fc27ecf-0f12-4bcf-8c12-271cc8fbed67">

<img width="300" alt="image" src="https://github.com/jphannifan/x1plus-testing/assets/149451641/db4e5fc5-f98a-4521-993f-2c11c4d23048">


## Explanation


#### Step 1: Measurement Collection
1. **Segment CD**: Measurement of diagonal across the octagon between points C and D.
2. **Segment AB**: Measure another diagonal, perpendicular to the first between points A and B.
3. **Segment EF**: Measurement of a 3rd diagonal of the octagon between points E and F.

#### Step 2: Calculations
1. **Calculate CB**:
   - We need to know the length of the side of the square inscribed within the octagon, which we can find by dividing the length of the diagnol EF by SQRT(2). 
   - Equation:
     ```math
      CB = \sqrt{2CD^2 + 2AB^2 - 4EF^2} / 2 
     ```

3. **Calculate Skew Factor**:
   - Equation:
     ```math
      \text{skew factor} = -\tan\left(\frac{\pi}{2} - \cos^{-1}\left(\frac{CD^2 - CB^2 - AC^2}{2 \times CB \times AC}\right)\right) 
     ```
   - This calculates the tangent of the skew angle to find the skew factor necessary for adjustment.

#### Gcode command:
- Apply skew factor:  M1005 I{-skew factor}
- Save the applied skew factor:  M500

