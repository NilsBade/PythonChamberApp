# Probe Antenna Effects in Measurement
> This directory and file is meant to document all thoughts and findings about the effects of the probe antenna 
> on the measurement results. The plots/pictures are generated with scripts from [another repository](https://github.com/NilsBade/Projektarbeit-E3/tree/master/CST%20Python%20Sim)
> and compare real measurement data to simulation results.

## Effect of Aperture Size
The aperture size of the probe antenna is the first straight forward effect that can be observed.
E.g. the standrad OERWG probe V2 (open ended rectangular waveguide) for 60GHz has an opening of 3.759mm x 1.88mm.
Thus power over this area is received by the antenna and the sum/integral can be measured by the PNA behind the probe.  
Therefor the probe-aperture size has to be considered when probing fields with a high gradients and small 'features'.
As soon as the aperture is larger than features one wants to measure in the nearfield, the probe kind of "smeres out" the
real power-distribution in space.

This effect can be seen in the next plot. In the upper two plots the distribution exported from CST is whoen and in
the lower two plots a 'virtual antenna' was moved over the field-data from CST and for each point probe the integral 
over the ideal power-distribution was calculated. It can be seen, that once the aperture size comes close to the
'feature-sizes' of the power-density-distribution, the results start to deviate from the real distribution more and more.

![ApertureSizeEffect-VirtualAntenna](/docs/Probe%20Antenna%20Effects/Figures/Math_Integral_Probe_effect_at_Z200.png)

## Effect of Probe Antenna
> AUT: 60GHz Horn, Probe: OERWG V2

It is not clear which effect the probe antenna has on the measured field distribution so far.
From probing an area of 100x100mm in Z-distance of 200mm in the real Measurement Setup and comparing the ideal 
power-density distribution (from CST) as well as the simulated S21 parameter for each position of the probe antenna 
calculated in CST, it can be seen that the probe antenna has a significant effect on the measured field distribution.
Even though there should be close to no reflections in the simulation with both antennas in space, the S21 results are
very close to the measured S21 parameters already.  
Thus the effect is likely by the probe antenna itself or its interaction with the AUT but not by the rest of the 
measurement setup.  

![Sim1000_Meas0014_FieldZ200_Heatmaps_over_available_Planes.png](/docs/Probe%20Antenna%20Effects/Figures/Sim1000_Meas0014_FieldZ200_Heatmaps_over_available_Planes.png)

![Sim1000_Meas0014_FieldZ200_Lineplots_Along_X_and_Y_axis.png](/docs/Probe%20Antenna%20Effects/Figures/Sim1000_Meas0014_FieldZ200_Lineplots_Along_X_and_Y_axis.png)

More closeup on the 100x100 plane:

![Sim1000_Meas0014_FieldZ200_Closeup_Heatmaps_over_available_Planes.png](/docs/Probe%20Antenna%20Effects/Figures/Sim1000_Meas0014_FieldZ200_Closeup_Heatmaps_over_available_Planes.png)
![Sim1000_Meas0014_FieldZ200_Closeup_Lineplots_Along_X_and_Y_axis.png](/docs/Probe%20Antenna%20Effects/Figures/Sim1000_Meas0014_FieldZ200_Closeup_Lineplots_Along_X_and_Y_axis.png)

This effect becomes more interesting when the probe is moved longer distances along X- and Y-axis and closer or even 
further away from the AUT.