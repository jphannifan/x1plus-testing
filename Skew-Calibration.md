## Skew calibration

1) Download ["m1005.py"](https://github.com/jphannifan/x1plus-testing/blob/main/scripts/python/m1005.py) from /scripts/python and save it to your printer in the folder `/opt/`
2) Download the [skew calibration model](https://github.com/jphannifan/x1plus-testing/blob/main/skew.step) (or use your own) and print it. I print mine at 100% scale with PLA and default slicer settings.
3) Launch the script from Step 1 by opening an SSH session with your printer and running the following command:
   `/opt/python/bin/python3 /opt/m1005.py`
4) Follow the command line instructions. The script will complete all of the calculations and enter the gcode commands necessary. You can view the current skew compensation value saved on your printer by running option 2
   <img width="354" alt="image" src="https://github.com/jphannifan/x1plus-testing/assets/149451641/7ae77a62-22d9-4396-a781-363d97af46d2">
5) After applying the correction factor, print the same model again in the same orientation with the same settings. Then start this process over again from step 3 until you're satisfied with the result.

## Measurements

This skew calibration model can also be used to check the accuracy of each axis. For skew calibration, you only need to make 3 measurements. The skew calibration model I have made allows you to make the same 3 measurements from different sides of an octagon, so if you are using a different model you may need to confirm you are measuring the correct segments.

<img width="300" alt="image" src="https://github.com/jphannifan/x1plus-testing/assets/149451641/72596bf0-5565-40c8-ab55-13b8242b759e">
<img width="320" alt="image" src="https://github.com/jphannifan/x1plus-testing/assets/149451641/54bf52c5-6b32-4c25-b739-dbde8dd32669">

The diameter of this octagon (at 100% scale) is 85 mm. If you are using the notches for aligning caliper jaws, the diameter will be 79 mm. 

Enter your measurements into the script prompts and to apply the skew factor, press 'y'.

<img width="266" alt="image" src="https://github.com/jphannifan/x1plus-testing/assets/149451641/7a0cee41-e47a-491a-8be1-77eae9b843cc">



## Measurement guide

<img width="300" alt="image" src="https://github.com/jphannifan/x1plus-testing/assets/149451641/7fc27ecf-0f12-4bcf-8c12-271cc8fbed67">

<img width="300" alt="image" src="https://github.com/jphannifan/x1plus-testing/assets/149451641/db4e5fc5-f98a-4521-993f-2c11c4d23048">

