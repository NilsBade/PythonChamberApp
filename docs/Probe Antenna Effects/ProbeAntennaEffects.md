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

### Comparison Chamber Measurements to poyntig vector at different heights
![Comparison_Z50](/docs/Probe%20Antenna%20Effects/Figures/AxisComparisons_02.10.24/Comparison_at_Z=50.0_mm.png)
![Comparison_Z100](/docs/Probe%20Antenna%20Effects/Figures/AxisComparisons_02.10.24/Comparison_at_Z=100.0_mm.png)
![Comparison_Z150](/docs/Probe%20Antenna%20Effects/Figures/AxisComparisons_02.10.24/Comparison_at_Z=150.0_mm.png)
![Comparison_Z200](/docs/Probe%20Antenna%20Effects/Figures/AxisComparisons_02.10.24/Comparison_at_Z=200.0_mm.png)
![Comparison_Z250](/docs/Probe%20Antenna%20Effects/Figures/AxisComparisons_02.10.24/Comparison_at_Z=250.0_mm.png)
![Comparison_Z300](/docs/Probe%20Antenna%20Effects/Figures/AxisComparisons_02.10.24/Comparison_at_Z=300.0_mm.png)
![Comparison_Z350](/docs/Probe%20Antenna%20Effects/Figures/AxisComparisons_02.10.24/Comparison_at_Z=350.0_mm.png)
![Comparison_Z400](/docs/Probe%20Antenna%20Effects/Figures/AxisComparisons_02.10.24/Comparison_at_Z=400.0_mm.png)

## Effect of probing-mesh
> AUT: 60GHz Horn, Probe: OERWG V2

Especially in cases where the phase of the field is important, the probing-mesh-density has to be considered.
In case of too dense meshes the measurement just takes very long time.  
In case of a too low mesh-density phase, as well as amplitude display get worse. If fields are measured, that have 
features (e.g. lobes or similar) in the same order of size as the steps of the probing mesh, it is likely that the
the lobes deform or disappear completely.  
For valid phase information it is important to choose the mesh-density (probe steps) in every direction significantly 
smaller than the wavelength of the frquencies that are measured. Otherwise the displayed phase distribution can
fastly become totally invalid as shown below.  
__Figures: 1. Sim1003, 2. Meas0020, 3. Meas0021__

![ProbingMeshEffect1_Sim1003](/docs/Probe%20Antenna%20Effects/Figures/Sim1003_YZ_Plane_Measurement.png)
![ProbingMeshEffect2_Meas0020](/docs/Probe%20Antenna%20Effects/Figures/Meas0020_XZ_Plane_Measurement.png)
![ProbingMeshEffect3_Meas0021](/docs/Probe%20Antenna%20Effects/Figures/Meas0021_YZ_Plane_Measurement.png)

Here a measurement of the YZ-Plane was taken with Z-steps of 5mm. The measured frequencies were 60, 63.5 and 67 GHz.
It can be seen that the phase distribution at 60GHz looks totally different in the mid section compared to the 67GHz plot.
This is due to the probe movement of exactly or pretty close to one wavelength at 60GHz, which lead to measuring the 
same phase at each point along z-direction. Of course there can not be a constant phase along z-direction since the 
wave travels this direction. To validate this effect, the same measurement was done in CST with relatively moved antennas,
which lead to the same effect at 60GHz.  
This example should show the importance of choosing the right probing-mesh-density.

