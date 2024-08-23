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
XY-Plane Measurement with 5x5 points probed at 60 GHz; 63,5 GHz; 67 GHz.  
Each point was measured 51 times to evaluate the drift of the phase variation error over time and due to 
non-ideal movement/repetition.  
The following graph shows the maximum phase-difference that occurred when measuring the same point multiple times.  
![Measurement_0004](/docs/Phase%20Variation%20Study/Figures/FreqOffsetVariationStudy_0004.png)  
In the following three graphs show the measured phase-value at each point (each line) over multiple iterations 
(along x-axis). The phase is shown in degrees.  
![Measurement_phaseDevelopment67G_0004](/docs/Phase%20Variation%20Study/Figures/Phase_measured_for_each_XY-Point_67.0_GHz_0004.png)
![Measurement_phaseDevelopment63,5G_0004](/docs/Phase%20Variation%20Study/Figures/Phase_measured_for_each_XY-Point_63.5_GHz_0004.png)
![Measurement_phaseDevelopment60G_0004](/docs/Phase%20Variation%20Study/Figures/Phase_measured_for_each_XY-Point_60.0_GHz_0004.png)  

The measurement was also taken with more resolution in XY-Plane but with only a few repetitions per point.  
Thus no separate graphs about the phase-value over multiple repetitions are shown here.
![Measurement_0003](/docs/Phase%20Variation%20Study/Figures/FreqOffsetVariationStudy_0003.png)
![Measurement_0002](/docs/Phase%20Variation%20Study/Figures/FreqOffsetVariationStudy_0002.png)
![Measurement_0001](/docs/Phase%20Variation%20Study/Figures/FreqOffsetVariationStudy_0001.png)