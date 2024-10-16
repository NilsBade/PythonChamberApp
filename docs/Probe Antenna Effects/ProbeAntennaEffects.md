# Probe Antenna Effects in Measurement
> This directory and file is meant to document all thoughts and findings about the effects of the probe antenna 
> on the measurement results. The plots/pictures are generated with scripts from [another repository](https://github.com/NilsBade/Projektarbeit-E3/tree/master/CST%20Python%20Sim)
> to compare real measurement data to simulation results.

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
Secondly The Probe antenna model was moved over the same area as in the real measurements in CST and all S21 (S12) parameters were calculated and saved --
the same procedure that is done in the MeasurementChamber.  
Thirdly the measurement was done in the real chamber with the same probe antenna and the same AUT.

To compare the measured S-parameters and the calculated power-density distribution exported from CST, the 
S-parameter value has to be squared before translating it to dB-scale since S-parameters are signal-amplitude referred
while power is squared-proportional to the field-strength.

### Comparison Chamber Measurements to poyntig vector at different heights
> **Data:** 
> * Real measurement files namingscheme: 00xx_...
> * CST 'measurement' files per simulation: 10xx_MPSim_...
> * CST poynting vector files per simulation: Pow_f60_...

Details about data-files:
* 0020 / 0021 Measurement files
  * Mesh steps: 2.5mm
  * IF-Bandwidth: 100 Hz
  * no averaging
  * frequencies: 60, 63.5, 67 GHz
* 0022 / 0023 Measurement files
  * Mesh steps: 1mm
  * IF-Bandwidth: 10 Hz
  * Average number: 10
  * frequencies: 60, 63.5, 67 GHz
* 1004 - 1010 Simulation measurement files
  * Mesh steps: 1mm
  * frequency: 60 GHz
* Pow_f60_... CST poynting vector files (ideal power density distribution)
  * Mesh steps: 1mm
  * frequency: 60 GHz
  * source project: CST_60G_Horn_FieldMonitors.cst

![Power_comparison_Z50](/docs/Probe%20Antenna%20Effects/Figures/AxisComparisons_02.10.24/Power_comparison_at_Z=50.0_mm.png)
![Phase_comparison_Z50](/docs/Probe%20Antenna%20Effects/Figures/AxisComparisons_02.10.24/Phase_comparison_at_Z=50.0_mm.png)
![Power_comparison_Z100](/docs/Probe%20Antenna%20Effects/Figures/AxisComparisons_02.10.24/Power_comparison_at_Z=100.0_mm.png)
![Phase_comparison_Z100](/docs/Probe%20Antenna%20Effects/Figures/AxisComparisons_02.10.24/Phase_comparison_at_Z=100.0_mm.png)
![Power_comparison_Z150](/docs/Probe%20Antenna%20Effects/Figures/AxisComparisons_02.10.24/Power_comparison_at_Z=150.0_mm.png)
![Phase_comparison_Z150](/docs/Probe%20Antenna%20Effects/Figures/AxisComparisons_02.10.24/Power_comparison_at_Z=150.0_mm.png)
![Power_comparison_Z200](/docs/Probe%20Antenna%20Effects/Figures/AxisComparisons_02.10.24/Power_comparison_at_Z=200.0_mm.png)
![Phase_comparison_Z200](/docs/Probe%20Antenna%20Effects/Figures/AxisComparisons_02.10.24/Phase_comparison_at_Z=200.0_mm.png)
![Power_comparison_Z250](/docs/Probe%20Antenna%20Effects/Figures/AxisComparisons_02.10.24/Power_comparison_at_Z=250.0_mm.png)
![Phase_comparison_Z250](/docs/Probe%20Antenna%20Effects/Figures/AxisComparisons_02.10.24/Phase_comparison_at_Z=250.0_mm.png)
![Power_comparison_Z300](/docs/Probe%20Antenna%20Effects/Figures/AxisComparisons_02.10.24/Power_comparison_at_Z=300.0_mm.png)
![Phase_comparison_Z300](/docs/Probe%20Antenna%20Effects/Figures/AxisComparisons_02.10.24/Phase_comparison_at_Z=300.0_mm.png)
![Power_comparison_Z350](/docs/Probe%20Antenna%20Effects/Figures/AxisComparisons_02.10.24/Power_comparison_at_Z=350.0_mm.png)
![Phase_comparison_Z350](/docs/Probe%20Antenna%20Effects/Figures/AxisComparisons_02.10.24/Phase_comparison_at_Z=350.0_mm.png)
![Power_comparison_Z400](/docs/Probe%20Antenna%20Effects/Figures/AxisComparisons_02.10.24/Power_comparison_at_Z=400.0_mm.png)
![Phase_comparison_Z400](/docs/Probe%20Antenna%20Effects/Figures/AxisComparisons_02.10.24/Phase_comparison_at_Z=400.0_mm.png)

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

__Figures: 4. Meas0017 YZ @60 GHz, 5. Meas0017 YZ @67 GHz__

![ProbingMeshEffect4_Meas0017_YZ_60GHz](/docs/Probe%20Antenna%20Effects/Figures/Meas0017_YZ_Plane_Measurement_60GHz.png)
![ProbingMeshEffect5_Meas0017_YZ_67GHz](/docs/Probe%20Antenna%20Effects/Figures/Meas0017_YZ_Plane_Measurement_67GHz.png)


Here a measurement of the YZ-Plane was taken with Z-steps of 5mm. The measured frequencies were 60, 63.5 and 67 GHz.
It can be seen that the phase distribution at 60GHz looks totally different in the mid section compared to the 67GHz plot.
This is due to the probe movement of exactly or pretty close to one wavelength at 60GHz, which lead to measuring the 
same phase at each point along z-direction. Of course there can not be a constant phase along z-direction since the 
wave travels this direction. To validate this effect, the same measurement was done in CST with relatively moved antennas,
which lead to the same effect at 60GHz.  
This example should show the importance of choosing the right probing-mesh-density.

## Effect of Reflections and Interference
### Noise level
During the first measurements (000, no absorbers were 0013-0025 (at least)), no absorbers were attached to the chamber setup.
For the measurements 0022-0025 one can look at the 50mm distance measurement's phaseplot to get an idea where the measurement-
range of the setup is exhausted and major noise appears.

![Powerdens_at_Z50_dBmax_Meas0022_withNoise](/docs/Probe%20Antenna%20Effects/Figures/EffectOfReflectionsAndInterference/Power_comparison_at_Z=50.0_mm_with_Noiselevel.png)
![Phase_at_Z50_Meas0022_withNoise](/docs/Probe%20Antenna%20Effects/Figures/EffectOfReflectionsAndInterference/Phase_comparison_at_Z=50.0_mm_with_Noiselevel.png)

At the point where the phase of the real measurement starts to deviate from the phase measured in the simulated probing/measurement,
one can expect that the measurement range of the real setup was reached. Therefor the amplitude plot gets saturated and noise and the phase plot just drifts away.  
Cross-referencing the point where the phase plot starts to drift to the measured amplitude at that point, one can see a dBmax value at 
x = +/- 65mm of -46dB / -41dB and y = +125 / -114 of -39.5dB / -39dB. One can conclude that the measurement range, referenced to the maximum power density at z=50mm in the center,
is about -39dB.

From there, one can compare the maximum amplitues (power densities) measured at the XY center at each z-height to translate 
this noise-floor into an expected noise-floor on the other heights.

![Powerdens_at_multZ_dBmax](/docs/Probe%20Antenna%20Effects/Figures/EffectOfReflectionsAndInterference/Powerdens_at_different_heights_dBmax_Meas0022.png)

This leads to assumed noise levels of roughly:
  * -39dB @ 50mm
  * -37dB @ 100mm
  * -34.5dB @ 150mm
  * -32.5dB @ 200mm
  * -30.8dB @ 250mm
  * -29.4dB @ 300mm
  * -28.1dB @ 350mm
  * -27.0dB @ 400mm

Plotting those levels into each amplitude-plots looks as follows:  
(In the phase plots multiple noise-levels are plotted since they are calculated from the first crossing of the noise-level looking from the middle XY=[0,0].
Since the measurements are not ideally symmetric, the noise-levels occur multiple times.)

![Powerdens_at_Z100_dBmax_Meas0022_withNoise](/docs/Probe%20Antenna%20Effects/Figures/EffectOfReflectionsAndInterference/Power_comparison_at_Z=100.0_mm_with_Noiselevel.png)
![Phase_at_Z100_Meas0022_withNoise](/docs/Probe%20Antenna%20Effects/Figures/EffectOfReflectionsAndInterference/Phase_comparison_at_Z=100.0_mm_with_Noiselevel.png)
![Powerdens_at_Z150_dBmax_Meas0022_withNoise](/docs/Probe%20Antenna%20Effects/Figures/EffectOfReflectionsAndInterference/Power_comparison_at_Z=150.0_mm_with_Noiselevel.png)
![Phase_at_Z150_Meas0022_withNoise](/docs/Probe%20Antenna%20Effects/Figures/EffectOfReflectionsAndInterference/Phase_comparison_at_Z=150.0_mm_with_Noiselevel.png)
![Powerdens_at_Z200_dBmax_Meas0022_withNoise](/docs/Probe%20Antenna%20Effects/Figures/EffectOfReflectionsAndInterference/Power_comparison_at_Z=200.0_mm_with_Noiselevel.png)
![Phase_at_Z200_Meas0022_withNoise](/docs/Probe%20Antenna%20Effects/Figures/EffectOfReflectionsAndInterference/Phase_comparison_at_Z=200.0_mm_with_Noiselevel.png)
![Powerdens_at_Z250_dBmax_Meas0022_withNoise](/docs/Probe%20Antenna%20Effects/Figures/EffectOfReflectionsAndInterference/Power_comparison_at_Z=250.0_mm_with_Noiselevel.png)
![Phase_at_Z250_Meas0022_withNoise](/docs/Probe%20Antenna%20Effects/Figures/EffectOfReflectionsAndInterference/Phase_comparison_at_Z=250.0_mm_with_Noiselevel.png)
![Powerdens_at_Z300_dBmax_Meas0022_withNoise](/docs/Probe%20Antenna%20Effects/Figures/EffectOfReflectionsAndInterference/Power_comparison_at_Z=300.0_mm_with_Noiselevel.png)
![Phase_at_Z300_Meas0022_withNoise](/docs/Probe%20Antenna%20Effects/Figures/EffectOfReflectionsAndInterference/Phase_comparison_at_Z=300.0_mm_with_Noiselevel.png)
![Powerdens_at_Z350_dBmax_Meas0022_withNoise](/docs/Probe%20Antenna%20Effects/Figures/EffectOfReflectionsAndInterference/Power_comparison_at_Z=350.0_mm_with_Noiselevel.png)
![Phase_at_Z350_Meas0022_withNoise](/docs/Probe%20Antenna%20Effects/Figures/EffectOfReflectionsAndInterference/Phase_comparison_at_Z=350.0_mm_with_Noiselevel.png)
![Powerdens_at_Z400_dBmax_Meas0022_withNoise](/docs/Probe%20Antenna%20Effects/Figures/EffectOfReflectionsAndInterference/Power_comparison_at_Z=400.0_mm_with_Noiselevel.png)
![Phase_at_Z400_Meas0022_withNoise](/docs/Probe%20Antenna%20Effects/Figures/EffectOfReflectionsAndInterference/Phase_comparison_at_Z=400.0_mm_with_Noiselevel.png)

### Reflections and Interference
Looking at the plots from last section, one can notice that the measured power-densities 'oscilllate' once coordinates
are reached several millimeters away from the center and main-lobe of the horn.  
But those oscillations (amplitude) stays above the assumed noise-level and the measured phase still follows the phase of the simulated field.
Also when comparing different measurements 0022/0023 and 0024/0025, which had the chamber-sides open in the first two and 
closed in the second two measurements, the power-densities and phases are pretty similar.
All four measurements were configured with low IF Bandwidth of 10Hz and averaging of 10.  
Still, both measurements agree in the kind of oscillation pattern of the powerdensity moving further away from the XY center.

Therefor it is likely that this up- and down-behaviour must be associated with the real measurement-setup and is pretty independent of the side-panels.
It is probable that the oscillation is caused by (multiple) reflections on the chamber floor and ceiling as well as the probehead itself.
Those reflections interfere with the direct signal and each other and lead to a distributed interference pattern (of the powerdensity) in space.

> insert plot of Horn powerdens in YZ plane in chamber and alone from CST HEATMAPS

This interference pattern is dynamic and changes with every point that is probed, since the main distributors for 
reflections - the probehead, X-gantry and ceiling - change there relative position to the horn inbetween each coordinate.
Consequently, the interference pattern is not (totally) static and can not be simulated for the probehead in one position 
and compared along the whole X or Y axis. Instead, one would have to simulate the whole setup with the probehead in each
position separately and compose the resulting powerdensity distribution from each simulation for each single point.

Simulating the whole setup for each point separately is not feasible - at least with the integration-solver - since one 
simulation already takes 5h (2 sym planes), 10h (1 sym plane) or 20h (no sym) dependent if there are symmetries left or not.
Thus only a qualitative comparison can be done by comparing the general behaviour of the powerdensity distribution in the
chamber to the one of the horn alone.

> insert plot of ideal Horn power dens, Horn in chamber power dens and measurement along Y axis (Show1D_PowerDifference.py)

It appears that the real measurement looks generally closer to the ideal distribution of the powerdensity by the horn 
alone (data from CST) than the simulated distribution with the reflecting parts in the model. 

This could be due to the probehead model affecting the power distribution more outside its XY-center due to bending 
the fields than it influences the distribution right underneath it in the center. This accounts at least for the case 
when probeantenna and AUT are exactly aligned XY-wise like in the first simulations.

