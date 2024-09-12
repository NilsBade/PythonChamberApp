# Phase Variation Study on Measurement Chamber
> This document describes the approach how the phase (and amplitude) variation error of the chamber, due to moving coax-cables, 
> was quantified. It also evaluates the possibility of using lookuptables to correct the error.

## Description
In the setup of the measurement chamber, HF signals are tramsitted via coaxial cables to and from the AUT and 
the probe antenna. Due to movement of the antennas relative to each other, while probing the AUT's near-field, 
movement of the coaxial cables is inevitable.  
At high frequencies like 60GHz and above, with wavelengths of 5mm and less, this cable movement can cause the phase
of the received signals at the PNA to vary.  
This 'phase variation error' should be studied and quantified to evaluate if it is an effect that always acts the same, 
so that simple approaches like a lookup table, based on a reference measurement, can increase the measurement accuracy 
of the chamber-setup.

To study the induced **phase variation error due to the probe antenna's movement in the XY Plane**, a short is screwed to 
the RWG-adapter, so that the S11 Parameter can be measured. This measurement gives information about amplitude, as well 
as phase variation due to the movement of the coaxial cables/probe-head. Ideally, since the short is a perfect reflect,
there should be a constant S11 amplitude and a constant phase over every point probed.  
If that is not the case, the next interesting thing is if the variation at each point in the XY plane is always the
same. Since that would mean that a correction of the error by simple subtraction of the phase- and amplitude-error is possible.  
The results of the taken measurements are shown in the [Measurements XY-Plane section](#measurements-xy-plane).

## Measurements XY-Plane 
> Measurements [0001-0004]

XY-Plane Measurement with 5x5 points probed at 60 GHz; 63,5 GHz; 67 GHz.  
Each point was measured 51 times to evaluate the drift of the phase variation error over time and due to 
non-ideal movement/repetition.  
The following graph shows the maximum phase-difference that occurred when measuring the same point multiple times.  
![Measurement_0004](/docs/Phase%20Variation%20Study/Figures/FreqOffsetVariationStudy_0004.png)  
In the following three graphs the measured phase-value at each point (each line) over multiple iterations 
(along x-axis) is shown. The phase is shown in degrees.  
![Measurement_phaseDevelopment67G_0004](/docs/Phase%20Variation%20Study/Figures/Phase_measured_for_each_XY-Point_67.0_GHz_0004.png)
![Measurement_phaseDevelopment63,5G_0004](/docs/Phase%20Variation%20Study/Figures/Phase_measured_for_each_XY-Point_63.5_GHz_0004.png)
![Measurement_phaseDevelopment60G_0004](/docs/Phase%20Variation%20Study/Figures/Phase_measured_for_each_XY-Point_60.0_GHz_0004.png)  
For the 60 GHz measurement the phase variation/drift of each point is significantly higher than for the other two frequencies. At the same time it looks 
like the phase of all measured points, independent of their location, drifts roughly the same amount or at least in 
the same direction. This leads to the assumption that this error is induced by the PNA e.g. by thermal effects but not 
by the chamber and its moving cables.  
The behaviour of the PNA's phase measurement over longer periods of time should be observed in future measurements. 

The same measurement was also taken with more resolution in XY-Plane but with only a few repetitions per point.  
Thus no separate graphs about the phase-value over multiple repetitions are shown here.
![Measurement_0003](/docs/Phase%20Variation%20Study/Figures/FreqOffsetVariationStudy_0003.png)
![Measurement_0002](/docs/Phase%20Variation%20Study/Figures/FreqOffsetVariationStudy_0002.png)
![Measurement_0001](/docs/Phase%20Variation%20Study/Figures/FreqOffsetVariationStudy_0001.png)

## Phase Variation Compensation
> This compensation algorithm is realized in the [CalibrationMatrixGenerator script](/SpecialScripts/CalibrationMatrixGenerator.py)

The phase variation error due to moving wire is compensated as follows:
1. A Phase reference (=0°) is chosen for each frequency that was measured by selecting the lowest phase value measured in "the whole volume"
2. All Phase values are offset by subtracting the chosen zero-phase-reference value (for each frequency)
3. Now the remaining average phase value for each XY-point is calculated by taking the mean value for each frequency at each XY-point along z-axis (= over all repetitions).  
    This average phase is assumed to be the **phase-offset** that is **linked to the position in XY-plane** and stored in the "phase_xy_calib_matrix".
4. The calculated phase-offsets for each position are subtracted from all phase-values at the corresponding position. Thus all XY-positions now have a mean-phase-value of 0°.  

Now the remaining phase-variation despite the compensation can be displayed with the [XYPhaseOffsetVariation script](/SpecialScripts/XYPhaseOffsetVariation.py) to conclude the achievable
accuracy of phase measurements in the chamber-setup.
![Measurement_phaseDevelopment67G_0004_compensated](/docs/Phase%20Variation%20Study/Figures/Phase_measured_for_each_XY-Point_67.0_GHz_0004_compensated.png)
![Measurement_phaseDevelopment63,5G_0004_compensated](/docs/Phase%20Variation%20Study/Figures/Phase_measured_for_each_XY-Point_63.5_GHz_0004_compensated.png)
![Measurement_phaseDevelopment60G_0004_compensated](/docs/Phase%20Variation%20Study/Figures/Phase_measured_for_each_XY-Point_60.0_GHz_0004_compensated.png)  

## Comparison Compensation Matrices
> Measurements [0002-0004]

The following image shows three graphs for the measurements [0002, 0003, 0004].
The graphs display the calculated coordinate-related phase-offset (XY axis in chamber coordinates, Z-axis the 
associated phase-offset in degree) for each measurement.
It can be seen, that the overall development of offsets over chamber-positions is similar for all three measurements.
The deviation needs to be quantified by separate measurements that have the same XY-resolution/-points measured.
However, the image suggests that the concept of constant phase offsets for each XY point across multiple measurements 
holds true to some extent.
![PhaseOffsetComparison_0002-0004](/docs/Phase%20Variation%20Study/Figures/Phase_Calibration_Matrix_Comparison_0002_0003_0004.png)
![PhaseOffsetComparison_0005-0007](/docs/Phase%20Variation%20Study/Figures/Phase_Calibration_Matrix_Comparison_0005_0006_0007.png)

## Longterm Measurements XY-Plane
> Measurements [0005-0008]

The following image shows the phase development over time for the measurements [0005, 0006, 0007, 0008].
Measurements [0005-0007] took about 4 hours, measurement [0008] took 12 hours.  
It can be seen, that the phase drift is still dominated by effects not related to the chamber-setup/-movement.
This can be concluded from all lines (= positions in XY-plane) drifting together by magnitudes much larger than "their own noise".

Moreover, measurements that take longer seem to have spikes/larger drifts in phase in a short amount of time.
Those can hardly be correlated to the chamber-setup as well, but are more likely to be caused by the PNA itself.
How these spikes in phase drift are triggered and when/how often they occur must be studied by e.g. even longer measurements.

Measurement [0005-0007] also measured the S22 parameter with a short connected to the fixed second PNA-cable.
This is just for comparison of the phase drift of the PNA on its own. The phase-drifts that were measured on S11 and S22 are
very different, which is likely caused by the separate TX/RX-stages of Port 1 and Port 2 of the PNA. They are probably
differently compensated for thermal effects, independent of each other and therefor behave different over time.  
Even the spikes that can be seen on the S11 parameter are not visible on the S22 parameter which leads to the conclusion,
that also these spikes are triggered at the TX/RX-stages of the PNA right behind the Ports.

![Measurement_phaseDevelopment67G_0006_compensated](/docs/Phase%20Variation%20Study/Figures/Phase_measured_for_each_XY-Point_67.0_GHz_0006_compensated.png)
![Measurement_phaseDevelopment63,5G_0006_compensated](/docs/Phase%20Variation%20Study/Figures/Phase_measured_for_each_XY-Point_63.5_GHz_0006_compensated.png)
![Measurement_phaseDevelopment60G_0006_compensated](/docs/Phase%20Variation%20Study/Figures/Phase_measured_for_each_XY-Point_60.0_GHz_0006_compensated.png)  
![Measurement_phaseDevelopment67G_0007_compensated](/docs/Phase%20Variation%20Study/Figures/Phase_measured_for_each_XY-Point_67.0_GHz_0007_compensated.png)
![Measurement_phaseDevelopment63,5G_0007_compensated](/docs/Phase%20Variation%20Study/Figures/Phase_measured_for_each_XY-Point_63.5_GHz_0007_compensated.png)
![Measurement_phaseDevelopment60G_0007_compensated](/docs/Phase%20Variation%20Study/Figures/Phase_measured_for_each_XY-Point_60.0_GHz_0007_compensated.png)  

For the longterm measurement [0008], taking 12 hours, the phase drift appears to be more stable and without spikes in
the order of magnitude as seen in the shorter measurements. The measurement was done over night 20:00 to 8:00.  
It may be, that the spikes in phase were less due to the longer on-time (warm-up) of the PNA or due to nobody entering
the room or disturbing the measurement in any other way during night.

![Measurement_phaseDevelopment67G_0008_compensated](/docs/Phase%20Variation%20Study/Figures/Phase_measured_for_each_XY-Point_67.0_GHz_0008_compensated.png)
![Measurement_phaseDevelopment63,5G_0008_compensated](/docs/Phase%20Variation%20Study/Figures/Phase_measured_for_each_XY-Point_63.5_GHz_0008_compensated.png)
![Measurement_phaseDevelopment60G_0008_compensated](/docs/Phase%20Variation%20Study/Figures/Phase_measured_for_each_XY-Point_60.0_GHz_0008_compensated.png)

In Measurement [0008] also the S22 Parameter was measured and a short was attached behinde the AUT-coax-cable. The 
short/cable was fixed to the AUT-plate by clamping it with the Horn-AUT-fixture as can be seen in the next picture.
The S22 Parameter stands out with lower "noise", probably due to the plate not moving between XY-position-changes. Thus
all separate line are closer to each other than for S11. Still the Phase of S22 drifts significantly over time as well.
To be able to differentiate between a **phase-drift due to the moving AUT-plate or due to thermal reasons/time**, another 
measurement needs to be conducted with the AUT plate moving longer distances in a short period of time. This will be 
done by leaving the probe head in one position while running the AUT plate all the way down the chamber and taking S22-
measurements.

![Measurement_phaseDevelopment67G_0008_S22](/docs/Phase%20Variation%20Study/Figures/Phase_measured_for_each_XY-Point_S22_67.0_GHz_0008_compensated.png)
![Measurement_phaseDevelopment63,5G_0008_S22](/docs/Phase%20Variation%20Study/Figures/Phase_measured_for_each_XY-Point_S22_63.5_GHz_0008_compensated.png)
![Measurement_phaseDevelopment60G_0008_S22](/docs/Phase%20Variation%20Study/Figures/Phase_measured_for_each_XY-Point_S22_60.0_GHz_0008_compensated.png)