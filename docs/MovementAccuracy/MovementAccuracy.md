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

> So the accuracy of the sensor is in a range of ~0.005mm judged from sampling the same point 10 times.

The movement accuracy of the print-bed z-wise was not possible to validate with the pen-drawing method.
Instead, two other methods will be used.
Firstly, a laser distance sensor will be placed on the print-bed and measure its distance to the ground underneath.
This way the relative movement precision as well as the repeatability can be measured in ranges that the laser-sensor's 
precision allows.  
The results are collected in a table below:

> [!Note] The used Laser sensor was the 'STABILA LD520' with a given precision of +-1mm in a range of 0,05-200m.

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

The second method to validate the movement accuracy in Z-direction by mounting a dial gauge to the probehead.
In the same manner as used to align axes in a manual milling machine, the dial gauge will be used to measure the firstly
the distance to the print bed while hovering the probehead over it. Secondly, the whole bed will be moved in Z-direction
within the measurement range of the dial gauge and the distance will be measured again.  
This way also high precision measurements of the achievable z-accuracy can be made.

> Along Y axis

| Position [X,Y,Z] | Measured Z [m] - Run 1 | Measured Z - Run 2 | Measured Z - Run 3 | Average Z | Standard Deviation Z |
|:----------------:|:----------------------:|:------------------:|:------------------:|:---------:|:--------------------:|
| [358;425.5;7.3]  |    0.0 (reference)     |        0.01        |        0.01        |           |                      |
|   [.;375.5;.]    |          0.02          |        0.02        |        0.03        |           |                      |
|      325.5       |          0.03          |        0.03        |        0.04        |           |                      |
|      275.5       |          0.03          |        0.03        |        0.04        |           |                      |
|      225.5       |          0.05          |        0.05        |        0.06        |           |                      |
|      175.5       |          0.07          |        0.07        |        0.08        |           |                      |
|      125.5       |          0.11          |        0.11        |        0.12        |           |                      |
|       75.5       |          0.14          |        0.14        |        0.14        |           |                      |
|       25.5       |          0.14          |        0.14        |        0.14        |           |                      |
|       0.5        |          0.14          |        0.14        |        0.14        |           |                      |


> Along X axis

| Position [X,Y,Z] | Measured Z [m] - Run 1 | Measured Z - Run 2 | Measured Z - Run 3 | Average Z | Standard Deviation Z |
|:----------------:|:----------------------:|:------------------:|:------------------:|:---------:|:--------------------:|
|  [458;80;7.35]   |    0.0 (reference)     |        0.01        |        0.0         |           |                      |
|    [408;.;.]     |         -0.01          |       -0.02        |       -0.02        |           |                      |
|       358        |          0.0           |       -0.01        |       -0.02        |           |                      |
|       308        |          0.01          |        0.01        |        0.0         |           |                      |
|       258        |         -0.01          |       -0.02        |       -0.03        |           |                      |
|       208        |         -0.03          |       -0.03        |       -0.04        |           |                      |
|       158        |         -0.02          |       -0.02        |       -0.03        |           |                      |
|       108        |          0.0           |        0.0         |       -0.01        |           |                      |
|        58        |          0.01          |        0.02        |        0.01        |           |                      |
|        8         |          0.04          |        0.05        |        0.04        |           |                      |
|        0         |          0.04          |        0.05        |        0.04        |           |                      |

> Along Z axis, small steps elevation at Position XY [225;80]

| Z-Coordinate |     Measured Z [m] - Run 1     | Measured Z - Run 2 | Measured Z - Run 3 | Average Z | Standard Deviation Z |
|:------------:|:------------------------------:|:------------------:|:------------------:|:---------:|:--------------------:|
|     7.54     | 0.0 (reference, came from top) |    0.0-(-0.01)     |      Upwards       |           |                      |
|     7.53     |              0.0               |        0.0         |        0.0         |           |                      |
|     7.52     |              0.0               |        0.01        |        0.0         |           |                      |
|     7.51     |              0.01              |        0.02        |        0.01        |           |                      |
|     7.5      |              0.02              |        0.03        |        0.02        |           |                      |
|     7.49     |              0.03              |        0.04        |        0.03        |           |                      |
|     7.48     |              0.04              |        0.06        |        0.04        |           |                      |
|     7.47     |              0.05              |        0.07        |        0.05        |           |                      |
|     7.46     |              0.06              |        0.08        |        0.06        |           |                      |
|     7.45     |              0.07              |        0.09        |        0.07        |           |                      |
|     6.95     |              0.58              |        0.59        |        0.58        |           |                      |
|     6.45     |              1.08              |        1.09        |        1.08        |           |                      |
|     5.95     |              1.58              |        1.59        |        1.58        |           |                      |
|     5.45     |              2.08              |        2.09        |        2.08        |           |                      |
|     4.95     |              2.58              |        2.60        |        2.58        |           |                      |
|     4.45     |              3.08              |    ^Backwards^     |        3.08        |           |                      |

One observation that stood out, was that the movement in Z-direction does not react directly once one changes direction!
After going down, going up follows about 0.02 mm later than meant to. The other way aroung after going up, going down 
lacks about 0.02mm height compared to the values measured when going up. Those can likely be attributed to the use of 
[decouplers](https://ratrig.com/catalog/product/view/id/1439/s/rat-rig-bi-material-lead-screw-decoupler/category/45/) in
the z-actuation system. Combined with the tolerance in the lead-screw threading, those probably add up to the observed error.



## XY-orthogonality
To measure the angular error of the X and Y axis precisely, a dial gauge was mounted to the probehead.  
A stop angle was placed on the printbed and the dial gauge was positioned to measure the distance to the stop angle horizontally.
Then the stop angle was repositioned until one side of it was precisly aligned with the X-Axis of the chamber.  
Now the dial gauge was turned 90° and the second side of the stop angle was probed with the dial gauge. From the distance change
while moving along Y-axis along the stop angle, one can precisely calculate the andular error between x and y axis.
The results are collected below:

> todo add documentation about measurement and results with dial gauge!

These measurements were used to calibrate and improve the chamber setup. By readjusting the X-Gantry via the dial gauge,
the angular error could be reduced from 0.3° to ?°.

## Precise XY-movement measurement
Lastly with an orthographic camera setup, the movement accuracy of the chamber was measured.  
The orthographic camera was fixed to the printhed, looking straight down on the print-bed.
The camera used was the *'UI-1640LE-C-HQ'* from IDS Imaging Development Systems GmbH with a resolution of 1280x1024 pixels. [SpecSheet here](/docs/MovementAccuracy/Datasheets/UI-1640LE-C-HQ.pdf).
The field of sight of the camera is 4,608 mm x 3,686 mm, leading to a size of 3.6 um per pixel.
On the bed precise distance measures from a milling machine were placed and the camera was moved over their known length.
From the pictures taken, measurements can be made to determine the movement accuracy of the chamber below the 1mm range precisely.

> todo add documentation about measurement and results with orthographic camera!