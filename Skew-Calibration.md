## Skew calibration for Bambu printers

1) Download ["Skew.py"]() from /scripts/python. X1Plus users can run this file directly on the printer by saving it to the SD card and running the following:
   - `python3 /mnt/sdcard/skew.py`
2) Download the [skew calibration model]() or provide your own and print it. 
3) Run the Python script and follow the instructions to calculate your skew. 
... under construction...
4) Apply the correction factor and print the calibration model using the exact same slicer settings and material.
5) Measure the dimensions of the last print, and if your tolerances are greater than 0.1-0.2%, consider repeating the process from Step 1.
   
## Skew calibration for all other Bambu devices

1) Download this Google worksheets document (link coming soon) and download the [skew calibration model](https://github.com/jphannifan/x1plus-testing/blob/main/skew.step)

2) Print the calibration model and using calipers measure 3 of the segments as detailed below. Enter your measurements into the worksheet to obtain the skew correction factor. Note: the printer appears to round to 5 digits (ie if you save a skew of 0.001234, 0.00123 will be the value that is actually saved)

3) Publish MQTT command to apply and save values. If you would prefer to not use MQTT, you may skip 3 and 4 and add the gcode command containing your skew factor to your print startup code. Publish this MQTT command, replacing 
{skew_factor} with your calculated value:
```
device/#/request
Request saved value:

{"print": {"command": "gcode_line", "param": "M1005", "sequence_id": 123}}

Apply and save:
{"print": {"command": "gcode_line", "param": "M1005 I{skew_factor} \n M500\n", "sequence_id": 123}}
```

4) To verify that your skew factor has actually been applied, you can publish the M1005 command with no arguments and the printer will output a response via MQTT. This XY_comp_ang value is the skew factor currently active on youe device. 

## Measurements

This skew calibration model can also be used to check the accuracy of each axis and to calculate a correction factor you can use to correct dimensional inaccuracy in your prints. By measuring the length of the nominal diameter from 3 of the specified sides of the octagon, we can then calculate a skew value that represents the XY skew relative to the X-axis (at this time, skew calibration in other axes is not available). 

<img width="400" alt="image" src="https://github.com/jphannifan/x1plus-testing/assets/149451641/b57a2a0a-4959-42fa-b97d-3f2d16470ffb">


The nominal diameter of the octagon is 100 mm if measured from the edges and 94 mm if measured from the inset. See the diagram below
<img width="400" alt="image" src="https://github.com/jphannifan/x1plus-testing/assets/149451641/b5c2edaf-bc61-475e-8b21-c5091933f575">

under construction...



## Measurement guide

<img width="455" alt="image" src="https://github.com/jphannifan/x1plus-testing/assets/149451641/b5c2edaf-bc61-475e-8b21-c5091933f575">



## Calculations
1. **Calculate CA**:
   - We need to know the length of the side of the square inscribed within the octagon, which we can find by dividing the length of the diagonal EF by SQRT(2).
   - Equation:
     ```math
      CA = \sqrt{2CD^2 + 2AB^2 - 4EF^2} / 2 
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

