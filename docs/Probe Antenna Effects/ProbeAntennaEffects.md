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
> AUT: 60GHz Horn, Probe: OERWG V3

To conclude the effect of the probe antenna on the measured field (power distribution), three paths are run in parallel.
Firstly a field simulation was done in CST and the poynting-vector was calculated in each point to get the power-density.
Secondly The Probe antenna model was moved over the same area as in the real measurements in CST and all S21 (S12) parameters were calculated and saved --
the same procedure that is done in the MeasurementChamber.  
Thirdly the measurement was done in the real chamber with the same probe antenna and the same AUT.

To compare the measured S-parameters and the calculated power-density distribution exported from CST, the 
S-parameter value has to be squared before translating it to dB-scale since S-parameters are signal-amplitude referred
while power is squared-proportional to the field-strength.

### Angle of Incidence to probeantenna

The angle of incidence of the (AUT-)field to the probeantenna likely has an impact on the measured power-density.
This can already be concluded from the difference in the simulated power-density distribution of the horn antenna alone
compared to the simulated probing with a probe antenna and calculating the effective power-density distribution from the simulated S-parameters.  

> todo put in plot comparing simulated powerdens from poyntingvector / fieldmonitor to simulated powerdens from S-parameters

One approach to investigate the impact of the changing angle of incidence on the measurement results is to plot the 
power density difference between the simulated field/power-distrubution and the simulated probing with the probe antenna.
When probing along the X- and Y-axis at different heights, the angle of incidence on the probing antenna changes for each height at different rate.
Thus the effect is supposed to be stronger for low heights with larger angles of incidence than at higher distances (z-wise).

To quantify the effect of the changing angle of incidence to the probe antenna, the farfield pattern was simulated for each probe antenna
and its gain was used to look for a compensation method.
Since in the measurement approach, only relative powerdensities are compared, always using the maximum measured powerdensity somewhere in a plane as reference point,
this 0dB-point must be the reference for the angle-compensation as well. For Probing the 60 GHz horn, this position is always at XY = (0,0) in the middle of the horn.
The angle of incidence at this position is 0° for phi and theta.
Moving away from the center, the angle of incidence starts to change and the power-density measured, based on the S12 parameter, starts to deviate from the ideal simulated distribution.
To check if the farfield gain pattern of the used probe antenna is a valid measure to look for a compensation, the difference between the simulated powerdensity and 
the calculated powerdensity based on the measured/simulated S12 parameter was plotted together with the gain pattern of the used probe antenna.
For each point probed, the angle of incidence was calculated and the gain at this angle was looked up from the simulated farfield pattern.
Using the maximum dBi gain of the probeantenna at phi = theta = 0° as reference point, the gain at each point was subtracted from the reference gain and the difference was plotted at each coordinate.
The results can be seen below for a real measurement with an OERWG probe and a simulated measurement with a horn-probe and a DRWG-probe.
The important difference between these probe antennas is the gain pattern which features a significant main-lobe for the horn antenna with a relatively small opening angle and 
a very wide main-lobe for the OERWG and the DRWG probe antenna.

![DRWG_sim_AngleCompensation](/docs/Probe%20Antenna%20Effects/Figures/Effect%20of%20Probe%20Antenna/PowerdensDiff_angle_DRWG_sim/Z_200.0.png)
![OERWG_sim_AngleCompensation](/docs/Probe%20Antenna%20Effects/Figures/Effect%20of%20Probe%20Antenna/PowerdensDiff_angle_OERWG_sim/Z_200.0.png)
![Horn_sim_AngleCompensation](/docs/Probe%20Antenna%20Effects/Figures/Effect%20of%20Probe%20Antenna/PowerdensDiff_angle_HornV1_sim/Z_200.0.png)

It can be seen, that for higher focussing probe antennas, an angle compensation based on the farfield pattern is a valid approach to correct (largely) deviating powerdensities.
Since for small angles the antenna gain deviates significantly already, this impact needs to be taken into account when measuring a power-density distribution in space.  
For the OERWG and DRWG probe antennas, the gain pattern is very wide and the main-lobe is very flat. Therefor the angle of incidence has a much smaller impact 
on the measured power-density distribution and occuring deviation.  
Looking at the real measurement results with the OERWG probe antenna, the deviations are pretty small already and the angle compensation that would be applied is very small as well.
For low heights, where the angle changes significantly, the angle compensation seems to fit (at Z=50mm) more or less.
But for larger heights, where the angle only changes a little, the compensation seems to have no relation to the measured difference. In other words, the angle of 
incidence to the probe antenna has no significant impact on the measurement result. Other effects seem to dominate those scenarios.

![OERWGv3_meas_AngleCompensation_z50](/docs/Probe%20Antenna%20Effects/Figures/Effect%20of%20Probe%20Antenna/PowerdensDiff_angle_OERWG_realMeas/Z_50.0.png)
![OERWGv3_meas_AngleCompensation_z100](/docs/Probe%20Antenna%20Effects/Figures/Effect%20of%20Probe%20Antenna/PowerdensDiff_angle_OERWG_realMeas/Z_100.0.png)
![OERWGv3_meas_AngleCompensation_z150](/docs/Probe%20Antenna%20Effects/Figures/Effect%20of%20Probe%20Antenna/PowerdensDiff_angle_OERWG_realMeas/Z_150.0.png)
![OERWGv3_meas_AngleCompensation_z200](/docs/Probe%20Antenna%20Effects/Figures/Effect%20of%20Probe%20Antenna/PowerdensDiff_angle_OERWG_realMeas/Z_200.0.png)
![OERWGv3_meas_AngleCompensation_z250](/docs/Probe%20Antenna%20Effects/Figures/Effect%20of%20Probe%20Antenna/PowerdensDiff_angle_OERWG_realMeas/Z_250.0.png)
![OERWGv3_meas_AngleCompensation_z300](/docs/Probe%20Antenna%20Effects/Figures/Effect%20of%20Probe%20Antenna/PowerdensDiff_angle_OERWG_realMeas/Z_300.0.png)
![OERWGv3_meas_AngleCompensation_z350](/docs/Probe%20Antenna%20Effects/Figures/Effect%20of%20Probe%20Antenna/PowerdensDiff_angle_OERWG_realMeas/Z_350.0.png)
![OERWGv3_meas_AngleCompensation_z400](/docs/Probe%20Antenna%20Effects/Figures/Effect%20of%20Probe%20Antenna/PowerdensDiff_angle_OERWG_realMeas/Z_400.0.png)

What stands out for larger heights is the fact that the measured power-density distribution deviates 'the same way' for different heights.
e.g. along X-axis for X < 0, the powerdensity is always overestimated and for X > 0 underestimated. This effect can not be related to the angle of incidence to the probe antenna because of its asymmetry.

*One note worth mentioning, is that it can be seen that for lower heights, e.g. shorter distances, the measured power-density-difference seems to become more noisy / oscillating and simply larger amplitude-wise.
This can likely be related to reflections inside the chamber that occur despite the absorber-attachment and still have a noticeable impact when the measurement distance and
consequently the free-space-path-loss are low enough. To reduce those differences, one would probably have to improve the absorber setup further. A compensation approach for these
error-effects is hardly possible since the reflections are ~~not deterministic~~ difficult to calculate and quantify and the interference pattern changes with each point probed.*


#### Wire Error
One approach to explain the asymmetric deviation is by investigating the impact of the moving wiring of the probe antenna on the measurement.
So far only its influence on the phase-measurement was studied, but the measured power-density amplitude might be affected as well.
The wiring would be a valid source for the asymmetric deviation in the measured power-density distribution.
To investigate this effect, instead of the oerwg probe a short was screwed to the probehead and the S11 parameter was measured while probing the same mesh
along X- and Y-axis as before. Ideally, the S11 parameter should not change throughout the measurement at each position. But in the real measurement, 
one might be able to see the same asymmetric behaviour around XY = (0,0) as in the power-density measurement-deviations.

![WireErrorS11_alongXYaxis](/docs/Probe%20Antenna%20Effects/Figures/WireError/Wire_error_along_X_and_Y_axis_300.png)

From the plots we can conclude, that the effect of the moving wire on the amplitude and phase is very small and can be neglected considering the accuracy of the measurement so far.
The deviation from the ideal value as plotted in the above chapter, deals with differences in the range of +- 1dB. The wire deviation is in a range below +- 0.1dB.  
For the phase value the same can be concluded. The wire deviation is in the range of +- 1° (over 300mm axis) while the deviation of the measured to the simulated phase values grows much quicker towards the sides.  

Analyzing the plots in more detail it stands out that sometimes the maximal measured powerdensity (0dB reference) is not at XY = (0,0) but at some other point.
Thus also powerdensities occur that are larger than zero / than the reference point. This lack of symmetry / missposition of the 0dB reference can be related to a misalignment of the probe antenna to the AUT.
The assumed zero-position, that is the root of the probing-mesh, when the measurement was started was a little bit off. 
To evaluate the effect of a wrong zero-position, the figures below show a real measurement with an OERWG probe in the absorber-equipped chamber compared to the simulated probing with the OERWG probe.
The given measurements 0032 and 0033 seem to be a little bit off center, having their maximum value at about XY = (-1, 1).
Below given are plots comparing the measured phase and power from the measurement and the simulation, but with different zero-position offsets/corrections.
The effect on the occuring deviations can easily be seen.

> Plots comparing the measured power-density and phase to the simulated (probed) power-density and phase with different zero-position offsets.
> 
> Plots with original measurement zero position at XY = (0, 0)

![Powerdens_compare_noOffset](/docs/Probe%20Antenna%20Effects/Figures/WireError/Comparison_Simulated_Probing_vs._Real_Probing_Z=200mm_-_Powerdensity.png)
![Phase_compare_noOffset](/docs/Probe%20Antenna%20Effects/Figures/WireError/Comparison_Simulated_Probing_vs._Real_Probing_Z=200mm_-_Phase.png)

> Plots with position-compensation zero at XY = (-1, 1)

![Powerdens_compare_offset1](/docs/Probe%20Antenna%20Effects/Figures/WireError/Comparison_Simulated_Probing_vs._Real_Probing_Z=200mm_-_Powerdensity_CORRECTED_POSITION.png)
![Phase_compare_offset1](/docs/Probe%20Antenna%20Effects/Figures/WireError/Comparison_Simulated_Probing_vs._Real_Probing_Z=200mm_-_Phase_CORRECTED_POSITION.png)

> Plots with position-compensation zero at XY = (-2, 2) >> Over-compensation! Asymmetric deviation now other way around.

![Powerdens_compare_offset2](/docs/Probe%20Antenna%20Effects/Figures/WireError/Comparison_Simulated_Probing_vs._Real_Probing_Z=200mm_-_Powerdensity_OVER_CORRECTED_POSITION.png)
![Phase_compare_offset2](/docs/Probe%20Antenna%20Effects/Figures/WireError/Comparison_Simulated_Probing_vs._Real_Probing_Z=200mm_-_Phase_OVER_CORRECTED_POSITION.png)

From these plots can be concluded, that the asymmetric deviation in the power-density distribution and phase is likely related to a misalignment of the probe antenna to the AUT.
This is the biggest source of error in the measurement setup up to this point (05.12.2024). 
It could be reduced by improving the alignment-method of the probe antenna to the AUT in some way.

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

## Double Ridge Waveguide Probe antenna
> AUT: 60GHz Horn, Probe: DRWG (??)

As alternative to the regular RWG probe, one can think of a double ridged waveguide to use as probe antenna.
* Benefits:
  * smaller aperture size theoretically leads to better resolution (as long as mesh density is high enough)
* Drawbacks:
  * more complex to build, silver(?)
  * less efficient / more losses(?!)

To compare the achievable results, a DRWG was optimized in CST to have minimum aperture size while achieving maximum transmission.
> do CST model and optimization

![CST DRWG parameter](/docs/Probe%20Antenna%20Effects/Figures/DoubleRidgeRWG/DRWG_CST_parameter.png)

Then the DRWG probe was moved across the same lines as the RWG probe in the MPSims 1004-1010 and 'achievable results' were compared.
> how does the DRWG probe perform compared to the RWG probe?

> Sources:
> https://www.microwaves101.com/encyclopedias/double-ridged-waveguide  
> ?

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

## Effect of the measurement setup on the measurement results
### Noise level
During the first measurements (000, no absorbers were 0013-0025 (at least)), no absorbers were attached to the chamber setup.
For the measurements 0022-0025 one can look at the 50mm distance measurement's phaseplot to get an idea where the measurement-range
of the setup is exhausted and major noise appears.

![Powerdens_at_Z50_dBmax_Meas0022_withNoise](/docs/Probe%20Antenna%20Effects/Figures/EffectOfReflectionsAndInterference/Power_comparison_at_Z=50.0_mm_with_Noiselevel.png)
![Phase_at_Z50_Meas0022_withNoise](/docs/Probe%20Antenna%20Effects/Figures/EffectOfReflectionsAndInterference/Phase_comparison_at_Z=50.0_mm_with_Noiselevel.png)

At the point where the phase of the real measurement starts to deviate from the phase measured in the simulated probing/measurement,
one can expect that the measurement range of the real setup was reached. Therefor the amplitude plot gets 'saturated' by noise and the 
phase plot just drifts away.  
Cross-referencing the point where the phase plot starts to drift to the measured amplitude at that point, 
one can see a dBmax value at x = +/- 65mm of -46dB / -41dB and y = +125 / -114 of -39.5dB / -39dB. One can conclude that the measurement 
range, referenced to the maximum power density at z=50mm in the center, is about -39dB.

From there, one can compare the maximum amplitues (power densities) measured at the XY center at each z-height to translate 
this noise-floor into an expected noise-floor on the other heights.

![Powerdens_at_multZ_dBmax](/docs/Probe%20Antenna%20Effects/Figures/EffectOfReflectionsAndInterference/Powerdens_at_different_heights_dBmax_Meas0022.png)

This leads to assumed noise levels of roughly:
  * -39dB @ 50mm (starting point)
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
But often those oscillations (amplitude) are above the assumed noise-level and the measured phase still follows the phase of the simulated field.  
E.g. at z = 150mm along Y-axis or z = 250mm along Y-axis.  
Also when comparing different measurements 0022/0023 and 0024/0025, which had the chamber-sides open in the first two and 
closed in the second two measurements, the power-densities and phases are pretty similar.
All four measurements were configured with low IF Bandwidth of 10Hz and averaging of 10.  
Still, both measurements agree in the kind of oscillation pattern of the powerdensity moving further away from the XY center.

Therefor it is likely that this up- and down-behaviour is associated with the real measurement-setup and seems to be pretty independent of the side-panels.
It is probable that the 'oscillation' is caused by (multiple) reflections on the chamber floor and ceiling as well as the probehead itself.
Those reflections interfere with the direct signal and each other and lead to a distributed interference pattern (of the powerdensity) in space.

> Picture of how power-distribution changes with and without the chamber in simulation

![YZ_Powerdens_WithAndWithoutChamber](/docs/Probe%20Antenna%20Effects/Figures/EffectOfReflectionsAndInterference/YZ-plane_heatmaps_Comparison.png)
![XZ_Powerdens_WithAndWithoutChamber](/docs/Probe%20Antenna%20Effects/Figures/EffectOfReflectionsAndInterference/XZ-plane_heatmaps_Comparison.png)
![XY_Powerdens_WithAndWithoutChamber](/docs/Probe%20Antenna%20Effects/Figures/EffectOfReflectionsAndInterference/Comparison%20-%20InterferencePoewDens%20and%20Measurements%20to%20ideal%20powerdens-distribution/2DHeatmaps_CompareInterferenzSimAndMeas.png)

> Closeup of interference pattern in power-distribution due to reflections on probehead from simulation

![XZ_Powerdens_CloseUp](/docs/Probe%20Antenna%20Effects/Figures/EffectOfReflectionsAndInterference/XZ-plane_heatmaps_Comparison-Closeup.png)

Simulating the whole setup for each point separately (like done for the simulated measurement files 1004-1010) to compare the 
real measurements results to is not feasible anymore - 
at least with the integration-solver - since one simulation already takes 5h (2 sym planes), 10h (1 sym plane) or 
20h (no sym) dependent if there are symmetries left or not. Without the chamber objects one iteration took about 2-3 minutes.  
Thus only a qualitative comparison can be done by comparing the general behaviour of the powerdensity distribution in the
chamber to the one of the horn alone for some probehead positions. Those plots can be seen above as heatmaps.

For a better insight one can compare the ideal power distribution (Horn alone in simulation) to some probehead positions in simulation
(calculating the interference pattern at theoretical probe-antenna-height) and to the real measurements along X- and Y-axis in a 2D-plot.  
It appears that, dependent on the head-position in the simulation, the resulting interference pattern along the whole X-/Y-axis
is strongly varying amplitude-wise. Thus care must be taken when comparing the amplitude values far away from a simulation's 
probehead position to the values from the real measurement. Even though they might seem to be very similar 
in some places, the real and the simulated surroundings (head and x-gantry position) might be totally different and similarities are more 
"lucky" than being any proof of correctness.

To sum it up, the interference pattern inside the chamber setup is very dynamic and changes with every point that is probed, 
since the main distributors for reflections - the probehead, X-gantry and ceiling - change there relative position to the horn inbetween each coordinate.
Consequently, the interference pattern can not be simulated for the probehead in one position 
and compared along the whole X or Y axis. Still, since one simulation takes several hours, below are some plots given 
that do the comparison along the whole axis - ideal distribution to simulated interference pattern and real measurement results.

> Plots that show the difference between ideal power-density distribution, simulated power-distribution pattern with reflections 
> and real measurement results along X- and Y-axis

![LineplotXY_z200_HeadCenter](/docs/Probe%20Antenna%20Effects/Figures/EffectOfReflectionsAndInterference/Comparison%20-%20InterferencePoewDens%20and%20Measurements%20to%20ideal%20powerdens-distribution/Lineplots_XY_at_Z200_HeadCenter.png)
![LineplotXY_z200_HeadX100](/docs/Probe%20Antenna%20Effects/Figures/EffectOfReflectionsAndInterference/Comparison%20-%20InterferencePoewDens%20and%20Measurements%20to%20ideal%20powerdens-distribution/Lineplots_XY_at_Z200_HeadX100.png)
![LineplotXY_z200_HeadY100](/docs/Probe%20Antenna%20Effects/Figures/EffectOfReflectionsAndInterference/Comparison%20-%20InterferencePoewDens%20and%20Measurements%20to%20ideal%20powerdens-distribution/Lineplots_XY_at_Z200_HeadY100.png)
![LineplotXY_z400_HeadCenter](/docs/Probe%20Antenna%20Effects/Figures/EffectOfReflectionsAndInterference/Comparison%20-%20InterferencePoewDens%20and%20Measurements%20to%20ideal%20powerdens-distribution/Lineplots_XY_at_Z400_HeadCenter.png)
![LineplotXY_z400_HeadX100](/docs/Probe%20Antenna%20Effects/Figures/EffectOfReflectionsAndInterference/Comparison%20-%20InterferencePoewDens%20and%20Measurements%20to%20ideal%20powerdens-distribution/Lineplots_XY_at_Z400_HeadX100.png)
![LineplotXY_z400_HeadX150](/docs/Probe%20Antenna%20Effects/Figures/EffectOfReflectionsAndInterference/Comparison%20-%20InterferencePoewDens%20and%20Measurements%20to%20ideal%20powerdens-distribution/Lineplots_XY_at_Z400_HeadX150.png)
![LineplotXY_z400_HeadX200](/docs/Probe%20Antenna%20Effects/Figures/EffectOfReflectionsAndInterference/Comparison%20-%20InterferencePoewDens%20and%20Measurements%20to%20ideal%20powerdens-distribution/Lineplots_XY_at_Z400_HeadX200.png)
![LineplotXY_z400_HeadY100](/docs/Probe%20Antenna%20Effects/Figures/EffectOfReflectionsAndInterference/Comparison%20-%20InterferencePoewDens%20and%20Measurements%20to%20ideal%20powerdens-distribution/Lineplots_XY_at_Z400_HeadY100.png)

Without comparing those plots in too much detail, one can see that the difference to the ideal distribution is in the same
magnitude order for the simulation and the real measurement. Moreover both show the same kind of oscillation pattern
along the axis. Having the same oscillation pattern and amplitudes is a goal out of reach given the above arguments about
the probehead only in several discrete positions in the simulation.

### Absorber strategy
To reduce the effect of the overall measurement setup on the results, considering the reflection topic above, absorbers
were attached to the chamber setup.  
Comparing the measurement results taken so far we already noticed almost no difference in the power density pattern 
when attaching or detaching the side-panels.  

> Achtung roter faden -- dieses argument is nötig um zu zeigen warum das simulationsmodell im kapitel davor **nur** decke, boden, xgantry und probehad enthält!

Coming from that observation, we can conclude that the main-impact on the measurement result comes from the reflections
on the top panel, x-gantry and probehead. Therefor the absorbers were attached to those parts of the setup.  
Between every different absorber-setup the measurement was repeated to see the effect of the newly attached absorbers on the results.
The impact can be seen easily looking at the probed XY plane, since the interference pattern is most visible there.
> Below can be seen a comparison of the simulated power density distribution (left), a real measurement without absorbers 
> attached to the chamber setup (middle) and finally with the main-absorbers attached to the top-panel, x-gantry and probehead (right).

![Heatsmaps_Powerdens_XY_Plane_Z200](/docs/Probe%20Antenna%20Effects/Figures/EffectOfReflectionsAndInterference/Absorber-Strategy/Comparison_PowerdensZ200_Sim_noAbsorb_FullAbsorb.png)

On the way to the resulted Heatmaps above, the X- and Y-axis were probed at different heights for different absorber configurations.
To give more detailed insights about each absorber's impact, following are the measured amplitude and phase plots in different absorber configs 
(no, top/bot only, top/bot + xgantry/probehead) compared to the simulated power and phase distribution/measurement.

1. Setup: No absorbers with long probe antenna-- every result above, measurements 0027-0029
![ChamberSetup_noAbsorber](/docs/Probe%20Antenna%20Effects/Figures/EffectOfReflectionsAndInterference/Absorber-Strategy/Config-NoAbsorber/Chamber_noAbsorberCfg.JPG)

2. Setup: Absorbers on top/bot-panel -- measurements 0030-0031
![ChamberSetup_Absorb1_overall](/docs/Probe%20Antenna%20Effects/Figures/EffectOfReflectionsAndInterference/Absorber-Strategy/Config-Absorber1/Chamber_AbsorberCfg1_Overall.JPG)
![ChamberSetup_Absorb1_closeup](/docs/Probe%20Antenna%20Effects/Figures/EffectOfReflectionsAndInterference/Absorber-Strategy/Config-Absorber1/Chamber_AbsorberCfg1_Closeup.JPG)

3. Setup: Absorbers on top/bot-panel + x-gantry and ProbeHead  -- measurements 0032-0034
![ChamberSetup_Absorb2_overall](/docs/Probe%20Antenna%20Effects/Figures/EffectOfReflectionsAndInterference/Absorber-Strategy/Config-Absorber2/Chamber_AbsorberCfg2_Overall1.JPG)
![ChamberSetup_Absorb2_closeup](/docs/Probe%20Antenna%20Effects/Figures/EffectOfReflectionsAndInterference/Absorber-Strategy/Config-Absorber2/Chamber_AbsorberCfg2_Closeup.JPG)

Below given are lineplots for phase and powerdensity along X and Y axis for the different absorber configurations at heights 50, 100, 150, 200, 250, 300, 350, 400.
All of them are probed with the regular OERWG V3 probe antenna./docs

![LineplotXY_z50_pow_absorbComp](/docs/Probe%20Antenna%20Effects/Figures/EffectOfReflectionsAndInterference/Absorber-Strategy/Absorber-LinePlot-Comparison/Power_comparison_at_Z=50.0_mm.png)
![LineplotXY_z50_phase_absorbComp](/docs/Probe%20Antenna%20Effects/Figures/EffectOfReflectionsAndInterference/Absorber-Strategy/Absorber-LinePlot-Comparison/Phase_comparison_at_Z=50.0_mm.png)
![LineplotXY_z100_pow_absorbComp](/docs/Probe%20Antenna%20Effects/Figures/EffectOfReflectionsAndInterference/Absorber-Strategy/Absorber-LinePlot-Comparison/Power_comparison_at_Z=100.0_mm.png)
![LineplotXY_z100_phase_absorbComp](/docs/Probe%20Antenna%20Effects/Figures/EffectOfReflectionsAndInterference/Absorber-Strategy/Absorber-LinePlot-Comparison/Phase_comparison_at_Z=100.0_mm.png)
![LineplotXY_z150_pow_absorbComp](/docs/Probe%20Antenna%20Effects/Figures/EffectOfReflectionsAndInterference/Absorber-Strategy/Absorber-LinePlot-Comparison/Power_comparison_at_Z=150.0_mm.png)
![LineplotXY_z150_phase_absorbComp](/docs/Probe%20Antenna%20Effects/Figures/EffectOfReflectionsAndInterference/Absorber-Strategy/Absorber-LinePlot-Comparison/Phase_comparison_at_Z=150.0_mm.png)
![LineplotXY_z200_pow_absorbComp](/docs/Probe%20Antenna%20Effects/Figures/EffectOfReflectionsAndInterference/Absorber-Strategy/Absorber-LinePlot-Comparison/Power_comparison_at_Z=200.0_mm.png)
![LineplotXY_z200_phase_absorbComp](/docs/Probe%20Antenna%20Effects/Figures/EffectOfReflectionsAndInterference/Absorber-Strategy/Absorber-LinePlot-Comparison/Phase_comparison_at_Z=200.0_mm.png)
![LineplotXY_z250_pow_absorbComp](/docs/Probe%20Antenna%20Effects/Figures/EffectOfReflectionsAndInterference/Absorber-Strategy/Absorber-LinePlot-Comparison/Power_comparison_at_Z=250.0_mm.png)
![LineplotXY_z250_phase_absorbComp](/docs/Probe%20Antenna%20Effects/Figures/EffectOfReflectionsAndInterference/Absorber-Strategy/Absorber-LinePlot-Comparison/Phase_comparison_at_Z=250.0_mm.png)
![LineplotXY_z300_pow_absorbComp](/docs/Probe%20Antenna%20Effects/Figures/EffectOfReflectionsAndInterference/Absorber-Strategy/Absorber-LinePlot-Comparison/Power_comparison_at_Z=300.0_mm.png)
![LineplotXY_z300_phase_absorbComp](/docs/Probe%20Antenna%20Effects/Figures/EffectOfReflectionsAndInterference/Absorber-Strategy/Absorber-LinePlot-Comparison/Phase_comparison_at_Z=300.0_mm.png)
![LineplotXY_z350_pow_absorbComp](/docs/Probe%20Antenna%20Effects/Figures/EffectOfReflectionsAndInterference/Absorber-Strategy/Absorber-LinePlot-Comparison/Power_comparison_at_Z=350.0_mm.png)
![LineplotXY_z350_phase_absorbComp](/docs/Probe%20Antenna%20Effects/Figures/EffectOfReflectionsAndInterference/Absorber-Strategy/Absorber-LinePlot-Comparison/Phase_comparison_at_Z=350.0_mm.png)
![LineplotXY_z400_pow_absorbComp](/docs/Probe%20Antenna%20Effects/Figures/EffectOfReflectionsAndInterference/Absorber-Strategy/Absorber-LinePlot-Comparison/Power_comparison_at_Z=400.0_mm.png)
![LineplotXY_z400_phase_absorbComp](/docs/Probe%20Antenna%20Effects/Figures/EffectOfReflectionsAndInterference/Absorber-Strategy/Absorber-LinePlot-Comparison/Phase_comparison_at_Z=400.0_mm.png)




