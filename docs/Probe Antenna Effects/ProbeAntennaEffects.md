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

To conclude the effect of the probe antenna on the measured field (power distribution), three paths are run in parallel.
Firstly a field simulation was done in CST and the poynting-vector was calculated in each point to get the power-density.
Secondly The Probe antenna model was moved over the same area in CST and all S21 parameters were calculated and saved --
the same procedure that is done in the MeasurementChamber.  
Thirdly the measurement was done in the real chamber with the same probe antenna and the same AUT.

To compare the measured S-parameters and the calculated power-density distribution exported from CST, the 
S-parameter value has to be squared before translating it to dB-scale since S-parameters are signal-ampplitude referred
while power are squared-proportional to the field-strength.

