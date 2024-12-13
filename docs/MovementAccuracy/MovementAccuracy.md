# Movement Accuracy of the Measurement Chamber
To validate the movement accuracy in all directions, as well as the orthogoanlity of the XY-axis, the following tests were performed. 
These tests were done after all the measurements that are presented in Nils Bade's master thesis. 
So the observed positioning errors have all been part of the first Horn-measurements for system validation and improvement.

## Drawing on a piece of paper - 09.12.2024
In a first approach, a pen (for technical drawings, width 0.35 mm) was fixed to the probehead and used to draw rectangles with specific 
side lengths on a piece of paper. Challenging was firstly the positioning of the pen on the paper. Since one does not
know the force with which the pen is pressed onto the paper, the pen might not draw all the time (too high) or damage 
the paper (too low) due to the imperfect bed leveling. Still, it was possible to draw in an area of 22x18cm (A4 paper size)
without big problems.  
The drawn rectangles were scanned by a printer with 600x600 dpi resolution and the side lengths and angles were measured 
based on the pixels in inkscape. The results are shown in the following two pictures.

![bigRectOnPaper](/docs/MovementAccuracy/Figures/BigRectAnnotated_V1.png)
![smallRectOnPaper](/docs/MovementAccuracy/Figures/SmallRectAnnotated_V1.png)

From the measurements one can conclude, that the accuracy of the printer XY-wise is below the used pen width of 0.35 mm.
The movement-error is in a range in which the digital point-placement in inkscape reflects in the taken error-measurement values.
Thus, another, more precise method must be used to determine the movement accuracy of the chamber in the future.
Considering the orthogonality of the XY-axis one can conclude an imperfect alignment of the two axes in orders of 0.2°-0.3°.
Therefor instead of a perfect square shaped mesh, the probed meshes were slight stretched into a parallelogram shape. 

## Movement accuracy in Z-direction
> [!Note] The chamber is equipped with an BL-Touch sensor for z-leveling. The repeatability check from Klipper returned the following log:

``` 
Send: PROBE_ACCURACY
Recv: // PROBE_ACCURACY at X:358.000 Y:25.500 Z:150.000 (samples=10 retract=10.000 speed=7.0 lift_speed=7.0)
Recv: // probe at 358.000,25.500 is z=-0.011174
Recv: // probe at 358.000,25.500 is z=-0.011799
Recv: // probe at 358.000,25.500 is z=-0.011174
Recv: // probe at 358.000,25.500 is z=-0.012424
Recv: // probe at 358.000,25.500 is z=-0.011174
Recv: // probe at 358.000,25.500 is z=-0.012424
Recv: // probe at 358.000,25.500 is z=-0.012424
Recv: // probe at 358.000,25.500 is z=-0.010549
Recv: // probe at 358.000,25.500 is z=-0.008674
Recv: // probe at 358.000,25.500 is z=-0.010549
Recv: // probe accuracy results: maximum -0.008674, minimum -0.012424, range 0.003750, average -0.011237, median -0.011174, standard deviation 0.001099
```

> So the accuracy of the sensor is in a range of $$\Delta Z_{error} ≤ |\pm 0.002mm|$$ judged from sampling the same point 10 times.

The movement accuracy of the print-bed z-wise was not possible to validate with the pen-drawing method.
Instead, two other methods are used.  
Firstly, a laser distance sensor is placed on the print-bed and measures its distance to the ground underneath.
This way the relative movement precision as well as the repeatability can be measured in the range of the laser-sensor's 
precision.  
The results are collected in a table below:

> [!Note] The used Laser sensor is the 'STABILA LD520' with a given precision of $\pm 1mm$ in a range of 0,05-200m.

| Target Z | Measured Z [m] - Run 1 | Measured Z - Run 2 | Measured Z - Run 3 | Measured Z - Run 4 | Measured Z - Run 5 | Average Z | Standard Deviation Z |
|:--------:|:----------------------:|:------------------:|:------------------:|:------------------:|:------------------:|:---------:|:--------------------:|
|    0     |         1.381          |       1,380        |       1,380        |       1,380        |       1,380        |     ?     |          ?           |
|    5     |         1,375          |       1,376        |       1,376        |       1,375        |       1,374        |     ?     |          ?           |
|    10    |         1,371          |       1,371        |       1,371        |       1,370        |       1,370        |     ?     |          ?           |
|   100    |         1,281          |       1,281        |       1,281        |       1,281        |       1,281        |     ?     |          ?           |
|   150    |         1,231          |       1,230        |       1,231        |       1,231        |       1,231        |     ?     |          ?           |
|   200    |         1,181          |       1,180        |       1,181        |       1,181        |       1,180        |     ?     |          ?           |
|   250    |         1,130          |       1,130        |       1,130        |       1,130        |       1,130        |     ?     |          ?           |
|   300    |         1,081          |       1,080        |       1,081        |       1,080        |       1,080        |     ?     |          ?           |
|   400    |         0,980          |       0,980        |       0,980        |       0,980        |       0,980        |     ?     |          ?           |
|   500    |         0,881          |       0,881        |       0,880        |       0,880        |       0,880        |     ?     |          ?           |
|   600    |         0,781          |       0,781        |       0,780        |       0,780        |       0,780        |     ?     |          ?           |
|   700    |         0,680          |       0,680        |       0,680        |       0,679        |       0,680        |     ?     |          ?           |
|   800    |         0,580          |       0,580        |       0,580        |       0,580        |       0,580        |     ?     |          ?           |
|   900    |         0,480          |       0,480        |       0,480        |       0,479        |       0,479        |     ?     |          ?           |

It can be seen, that the error that should be measured is below the precision of the laser sensor since over all repetitions
the measured value just 'toggles' $1mm$ which is also given as its accuracy. Therefor to quantify the chamber's positioning 
error in Z-direction, the second method needs to be used.

The second method to validate the movement accuracy in Z-direction is by mounting a dial gauge to the probehead.
In the same manner as used to align axes in a manual milling machine, the dial gauge is used to measure 
the distance to the print bed while hovering the probehead over it. Secondly, the whole bed will be moved in Z-direction
within the measurement range of the dial gauge and the distance to the probehead is measured.  
This way high precision measurements of the Z-movement can be made with the accuracy of the dial gauge.

> Sketch of probed lines with dial gauge

![DialGaugeSketch](/docs/MovementAccuracy/Figures/Z_Measurements_on_bed_WB.png)

The used dial gauge introduces an accuracy of $0.01 mm$ for the Z-measurements.
To calculate the angular error of the bed-plane to the probehead movement plane, the measured z-offset can be used by
$\phi_{error} = arctan(\frac{|z_{min}|}{distance})$ with the distance being the maximum distance between the first and 
the last point measured along each axis.  
Having measured $425 mm$ along Y-axis and $458 mm$ along X-axis, the angular errors that can be estimated are accurate to
$\Delta\phi_{error,Y} = \arctan(\frac{0.01 mm}{425 mm}) \approx 0.0014°$ and 
$\Delta\phi_{error,X} = \arctan(\frac{0.01 mm}{458 mm}) \approx 0.0013°$.

![BedAngleErrors](/docs/MovementAccuracy/Figures/Bed-Misalignment_AngleErrors_WB.png)

> Probe along Y axis, error around X-axis

| Position [X,Y,Z] | Measured Z [m] - Run 1 | Measured Z - Run 2 | Measured Z - Run 3 | Average Z |
|:----------------:|:----------------------:|:------------------:|:------------------:|:---------:|
| [358;425.5;7.3]  |    0.0 (reference)     |        0.01        |        0.01        |   0.01    |
|   [.;375.5;.]    |          0.02          |        0.02        |        0.03        |   0.02    |
|      325.5       |          0.03          |        0.03        |        0.04        |   0.03    |
|      275.5       |          0.03          |        0.03        |        0.04        |   0.03    |
|      225.5       |          0.05          |        0.05        |        0.06        |   0.05    |
|      175.5       |          0.07          |        0.07        |        0.08        |   0.07    |
|      125.5       |          0.11          |        0.11        |        0.12        |   0.11    |
|       75.5       |          0.14          |        0.14        |        0.14        |   0.14    |
|       25.5       |          0.14          |        0.14        |        0.14        |   0.14    |
|       0.5        |          0.14          |        0.14        |        0.14        |   0.14    |

From the averaged values one can estimate **an angular error around X-axis of 
$\phi_{error,X} = arctan(\frac{0.13 mm}{425 mm}) = 0.0175° \approx 0.018°$** 
for the bed referenced to the plane in which the probehead moves ($\phi$ positive around chamber-X-axis).


> Probe along X axis, error around Y-axis

| Position [X,Y,Z] | Measured Z [m] - Run 1 | Measured Z - Run 2 | Measured Z - Run 3 | Average Z |
|:----------------:|:----------------------:|:------------------:|:------------------:|:---------:|
|  [458;80;7.35]   |    0.0 (reference)     |        0.01        |        0.0         |    0.0    |
|    [408;.;.]     |         -0.01          |       -0.02        |       -0.02        |   -0.02   |
|       358        |          0.0           |       -0.01        |       -0.02        |   -0.01   |
|       308        |          0.01          |        0.01        |        0.0         |   0.01    |
|       258        |         -0.01          |       -0.02        |       -0.03        |   -0.02   |
|       208        |         -0.03          |       -0.03        |       -0.04        |   -0.03   |
|       158        |         -0.02          |       -0.02        |       -0.03        |   -0.02   |
|       108        |          0.0           |        0.0         |       -0.01        |    0.0    |
|        58        |          0.01          |        0.02        |        0.01        |   0.01    |
|        8         |          0.04          |        0.05        |        0.04        |   0.04    |
|        0         |          0.04          |        0.05        |        0.04        |   0.04    |

From the averaged Z-offsets measured along X-axis one can not reliably estimate the angular error around Y-axis.
Since the measured Z-offset shows no steady trend moved along axis-direction over a long path of $X=458$ to $X=108$ and then 
suddenly deviates by a comparably large number, it is more likely that this offset originates from an imperfect bed-surface
than from a misaligned bed-plane. Therefor the **angular error around Y-axis is estimated to be $\phi_{error,Y} ≤ |\pm0.005°|$** which is
the angular error calculated from the maximum averaged z-offset that occurred in the measurement.

> Along Z axis, small steps elevation at Position XY [225;80]

| Z-Coordinate |     Measured Z [m] - Run 1     | Measured Z - Run 2 | Measured Z - Run 3 |
|:------------:|:------------------------------:|:------------------:|:------------------:|
|     7.54     | 0.0 (reference, came from top) |    0.0-(-0.01)     |      Upwards       |
|     7.53     |              0.0               |        0.0         |        0.0         |
|     7.52     |              0.0               |        0.01        |        0.0         |
|     7.51     |              0.01              |        0.02        |        0.01        |
|     7.5      |              0.02              |        0.03        |        0.02        |
|     7.49     |              0.03              |        0.04        |        0.03        |
|     7.48     |              0.04              |        0.06        |        0.04        |
|     7.47     |              0.05              |        0.07        |        0.05        |
|     7.46     |              0.06              |        0.08        |        0.06        |
|     7.45     |              0.07              |        0.09        |        0.07        |
|     6.95     |              0.58              |        0.59        |        0.58        |
|     6.45     |              1.08              |        1.09        |        1.08        |
|     5.95     |              1.58              |        1.59        |        1.58        |
|     5.45     |              2.08              |        2.09        |        2.08        |
|     4.95     |              2.58              |        2.60        |        2.58        |
|     4.45     |              3.08              |    ^Backwards^     |        3.08        |

One observation that stood out probing the same point at different heights, was that the movement in Z-direction does 
not change instantly once one changes direction!
After going down, going up follows about $0.02 mm$ later than meant to. The other way around after going up, going down 
lacks about $0.02mm$ height compared to the values measured when going up. Those can likely be attributed to the use of 
[decouplers](https://ratrig.com/catalog/product/view/id/1439/s/rat-rig-bi-material-lead-screw-decoupler/category/45/) in the z-actuation system.  
Combined with the tolerance in the lead-screw threading, those probably add up to the observed error.
**Thus, an error estimation of $\pm0.02mm$ is made for the z-accuracy of the chamber.**



## XY-orthogonality
To measure the angular error of the X and Y axis precisely, a dial gauge is mounted to the probehead.  
A stop angle is placed on the printbed and the dial gauge is positioned to measure the distance of the probehead to the stop angle horizontally.
Then the stop angle is (roughly) repositioned until one side of it is closely aligned with the X-Axis of the chamber.  
Now the dial gauge is rotated by $90°$ and the second side of the stop angle is probed with the dial gauge. From the distance change
while moving along the edges of the stop angle, one can precisely calculate the angle between the reference-edge and
the chamber's movement-axis.

The Setup is pictured in the figure below:
![XY-OrthogonalitySetup](/docs/MovementAccuracy/Figures/Bed-Misalignment_XYOrthogonality_WB.png)

Once $\varphi_{X}$ anf $\varphi_{Y}$ are calculated from the measurements, one can add (or subtract) them from the 90°
reference angle to get the total angle between the X- and Y-axis of the chamber's XY-actuation.
To get more confidence in the measurement results, the same measurement was conducted three times with the reference positioned
in different places and angles on the print-bed. The notes taken while the measurements were made can be 
found [here](/docs/MovementAccuracy/XY_Winkel_Fehler_Masterarbeit.pdf).    
The measured distances of each run are collected in the tables below for overview:

> [!Note] In the tables below, negative measured distances mean that the distance lowered compared to the starting-/reference-point.
> Positive values mean that the distance increased compared to the starting-/reference-point. This is important to know
> when calculating the total angle between XY because one must decide if one subtracts or adds the $\varphi$ values.

### 1. Measurement Run
1. Measurement along x-axis

| X-position [mm] | Measured Distance [mm] | Referenced Start/Stop [mm] | Angle [°] |
|:---------------:|:----------------------:|:--------------------------:|:---------:|
|       0.0       |          0.00          |            0.00            |     -     |
|      50.0       |           -            |             -              |     -     |
|      100.0      |           -            |             -              |     -     |
|      110.0      |         -0.09          |           -0.09            |   0.047   |

Here the distance to the reference grows by $0.09 mm$ moving 110 mm in positive X-direction.
Thus, the chamber's x-axis is rotated by $\varphi_{X} = arctan(\frac{0.09 mm}{110 mm}) = 0.047°$ 'away' from the 
reference edge.


2. Measurement along y-axis

| Y-position [mm] | Measured Distance [mm] | Referenced Start/Stop [mm] | Angle [°] |
|:---------------:|:----------------------:|:--------------------------:|:---------:|
|       0.0       |          0.01          |            0.00            |     -     |
|      50.0       |         -0.09          |           -0.10            |   0.115   |
|      100.0      |         -0.12          |           -0.13            |   0.075   |
|      110.0      |         -0.14          |           -0.15            |   0.078   |

Here the distance to the reference grows as well by $0.15 mm$ moving 110 mm in positive Y-direction.
Thus, the chamber's y-axis is rotated by $\varphi_{Y} = arctan(\frac{0.15 mm}{110 mm}) = 0.078°$ 'away' from the 
reference edge.

3. Calculation of $\phi_{XY}$  
Assuming the reference has an ideal 90° angle, the total angle between the X- and Y-axis of the chamber's XY-actuation is
$$\phi_{XY} = 90° + (\varphi_{X} + \varphi_{Y}) = 90° + (0.047° + 0.078°) = 90.125°$$ which is an angular error of 
$$\phi_{error, XY} = +0.125°$$.

### 2. Measurement Run
1. Measurement along x-axis

| X-position [mm] | Measured Distance [mm] | Referenced Start/Stop [mm] | Angle [°] |
|:---------------:|:----------------------:|:--------------------------:|:---------:|
|       0.0       |          0.07          |            0.00            |     -     |
|      50.0       |          0.08          |            0.01            |   0.011   |
|      100.0      |          0.08          |            0.01            |   0.011   |
|      110.0      |          0.09          |            0.02            |   0.010   |

Here the distance to the reference grows by very little, almost not measurable by the dial gauge.
Still there is a constant trend in the distance (growing), which is why it makes sense to calculate an angle between 
reference edge and chamber axis. $\varphi_{X} = arctan(\frac{0.02 mm}{110 mm}) = 0.010°$ is the angle with which the 
chamber's x-axis is rotated 'into' the reference edge.

2. Measurement along y-axis

| Y-position [mm] | Measured Distance [mm] | Referenced Start/Stop [mm] | Angle [°] |
|:---------------:|:----------------------:|:--------------------------:|:---------:|
|       0.0       |          0.34          |            0.00            |     -     |
|      50.0       |          0.33          |           -0.01            |   0.011   |
|      100.0      |          0.18          |           -0.16            |   0.092   |
|      110.0      |          0.05          |           -0.29            |   0.151   |

Here the distance to the reference grows by $0.29 mm$ moving 110 mm in positive Y-direction.
Thus, the chamber's y-axis is rotated by $\varphi_{Y} = arctan(\frac{0.29 mm}{110 mm}) = 0.151°$ 'away' from the 
reference edge.

3. Calculation of $\phi_{XY}$
Assuming the ideal 90° angle of the reference, the total angle between the X- and Y-axis of the chamber's XY-actuation is
$$\phi_{XY} = 90° + (-\varphi_{X} + \varphi_{Y}) = 90° + (-0.010° + 0.151°) = 90.141°$$ which is an angular error of
$$\phi_{error, XY} = +0.141°$$.

### 3. Measurement Run
1. Measurement along x-axis

| X-position [mm] | Measured Distance [mm] | Referenced Start/Stop [mm] | Angle [°] |
|:---------------:|:----------------------:|:--------------------------:|:---------:|
|       0.0       |          2.02          |            0.00            |     -     |
|      50.0       |          3.37          |            1.35            |   1.547   |
|      100.0      |          4.81          |            2.79            |   1.598   |
|      110.0      |          5.08          |            3.06            |   1.593   |

Here the reference comes closer to the probehead by $3.06 mm$ moving 110 mm in positive X-direction.
Thus, the chamber's x-axis is rotated by $\varphi_{X} = arctan(\frac{3.06 mm}{110 mm}) = 1.593°$ 'into' the
reference edge.

2. Measurement along y-axis

| Y-position [mm] | Measured Distance [mm] | Referenced Start/Stop [mm] | Angle [°] |
|:---------------:|:----------------------:|:--------------------------:|:---------:|
|       0.0       |          4.36          |            0.00            |     -     |
|      50.0       |          2.75          |           -2.61            |   2.988   |
|      100.0      |          1.15          |           -3.21            |   1.838   |
|      110.0      |          0.84          |           -3.52            |   1.832   |

Here the distance to the reference grows by $3.52 mm$ moving 110 mm in positive Y-direction.
Thus, the chamber's y-axis is rotated by $\varphi_{Y} = arctan(\frac{3.52 mm}{110 mm}) = 1.832°$ 'away' from the
reference edge.

3. Calculation of $\phi_{XY}$
Assuming the ideal 90° angle of the reference, the total angle between the X- and Y-axis of the chamber's XY-actuation is
$$\phi_{XY} = 90° + (-\varphi_{X} + \varphi_{Y}) = 90° + (-1.593° + 1.832°) = 90.239°$$ which is an angular error of
$$\phi_{error, XY} = +0.239°$$

### Conclusion  
Averaging over the three conducted measurements, the total angular error between the X- and Y-axis of the chamber's XY-actuation
is estimated to be $\phi_{error, XY} = +0.168°$ with a standard deviation of $\sigma_{\phi_{error, XY}} = 0.057°$ or in other words 
$$\phi_{error, XY} \approx +0.2°$$

## Precise XY-movement measurement
Lastly with an orthographic camera setup, the movement accuracy of the chamber was measured.  
The orthographic camera was fixed to the printhed, looking straight down on the print-bed.
The camera used was the *'UI-1640LE-C-HQ'* from IDS Imaging Development Systems GmbH with a resolution of 1280x1024 pixels. [SpecSheet here](/docs/MovementAccuracy/Datasheets/UI-1640LE-C-HQ.pdf).
The field of sight of the camera is 4,608 mm x 3,686 mm, leading to a size of 3.6 um per pixel.
On the bed precise distance measures from a milling machine were placed and the camera was moved over their known length.
From the pictures taken, measurements can be made to determine the movement accuracy of the chamber below the 1mm range precisely.

> todo add documentation about measurement and results with orthographic camera!