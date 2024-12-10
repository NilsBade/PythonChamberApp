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
The movement accuracy of the print-bed z-wise was not possible to validate with the pen-drawing method.
Instead, two other methods will be used.
Firstly, a laser distance sensor will be placed on the print-bed and measure its distance to the ground underneath.
This way the relative movement precision as well as the repeatability can be measured in ranges that the laser-sensor's 
precision allows.  
The results are collected in a table below:

> [!Note] The used Laser sensor was the '...' with a given precision of ... in a range of ... mm.

| Target Z | Measured Z - Run 1 | Measured Z - Run 2 | Measured Z - Run 3 | Measured Z - Run 4 | Measured Z - Run 5 | Average Z | Standard Deviation Z |
|:--------:|:------------------:|:------------------:|:------------------:|:------------------:|:------------------:|:---------:|:--------------------:|
|   100    |         ?          |         ?          |         ?          |         ?          |         ?          |     ?     |          ?           |
|   105    |         ?          |         ?          |         ?          |         ?          |         ?          |     ?     |          ?           |
|   110    |         ?          |         ?          |         ?          |         ?          |         ?          |     ?     |          ?           |
|   150    |         ?          |         ?          |         ?          |         ?          |         ?          |     ?     |          ?           |
|   200    |         ?          |         ?          |         ?          |         ?          |         ?          |     ?     |          ?           |
|   250    |         ?          |         ?          |         ?          |         ?          |         ?          |     ?     |          ?           |
|   300    |         ?          |         ?          |         ?          |         ?          |         ?          |     ?     |          ?           |
|   400    |         ?          |         ?          |         ?          |         ?          |         ?          |     ?     |          ?           |
|   500    |         ?          |         ?          |         ?          |         ?          |         ?          |     ?     |          ?           |
|   600    |         ?          |         ?          |         ?          |         ?          |         ?          |     ?     |          ?           |
|   700    |         ?          |         ?          |         ?          |         ?          |         ?          |     ?     |          ?           |
|   800    |         ?          |         ?          |         ?          |         ?          |         ?          |     ?     |          ?           |

The second method to validate the movement accuracy in Z-direction by mounting a dial gauge to the probehead.
In the same manner as used to align axes in a manual milling machine, the dial gauge will be used to measure the firstly
the distance to the print bed while hovering the probehead over it. Secondly, the whole bed will be moved in Z-direction
within the measurement range of the dial gauge and the distance will be measured again.  
This way also high precision measurements of the achievable z-accuracy can be made.

> todo put in pictures of dial gauge setup and results

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