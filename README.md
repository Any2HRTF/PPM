# PyPPM

Python module to programmatically interface with the parametric pinna model (PPM) [1]. 

## Installation

Get the pre-built Python wheel from the [releases](https://github.com/Any2HRTF/PPM/releases) page (vX.x.x) and install it using pip:

```bash
pip install /path/to/wheel.whl
```

Alternatively, you could build the module from source.

## Usage

The module provides a single class `PPM`.
The constructor will generate a PPM instance with default PPM-parameter values.
   
```python
from ppm import PPM

ppm = PPM()
```

Alternatively, the PPM can be instantiated from a 'blend' file, 'csv' file, or a Python dictionary containing the PPM parameters in the same format as the 'csv' file.

### Parameters

The PPM parameters and their default values are listed below:

<details>
<summary>
Default Parmaeters
</summary>
   
```python
print(ppm)
```

```
Size:
  ∟Bendy:
    ∟Location:
      ∟X: 0.0
      ∟Y: 0.0
      ∟Z: 0.0
    ∟Rotation:
      ∟W: 1.0
      ∟X: 0.0
      ∟Y: 0.0
      ∟Z: 0.0
    ∟Scale:
      ∟X: 1.0
      ∟Y: 1.0
      ∟Z: 1.0
Antitragus-Crease:
  ∟Shape_key:
    ∟0.0
Cavum_conchae-Depth:
  ∟Shape_key:
    ∟0.0
Cymba_conchae-Depth:
  ∟Shape_key:
    ∟0.0
Crus_helicis-Prominence:
  ∟Shape_key:
    ∟0.0
Upper_helix-Depth:
  ∟Shape_key:
    ∟0.0
Middle_helix-Depth:
  ∟Shape_key:
    ∟0.0
Lower_helix-Depth:
  ∟Shape_key:
    ∟0.0
Lobulus-Form:
  ∟Shape_key:
    ∟0.0
Scapha-Depth:
  ∟Shape_key:
    ∟0.0
Fossa_triangularis-Depth:
  ∟Shape_key:
    ∟0.0
Crus_inferius_anthelicis-Lower_crease:
  ∟Shape_key:
    ∟0.0
Crus_inferius_anthelicis-Upper_crease:
  ∟Shape_key:
    ∟0.0
Crus_superius_anthelicis-Lower_crease:
  ∟Shape_key:
    ∟0.0
Crus_superius_anthelicis-Upper_crease:
  ∟Shape_key:
    ∟0.0
Tragus-Upper_dent:
  ∟Shape_key:
    ∟0.0
Crus_helicis-Upper_dent:
  ∟Shape_key:
    ∟0.0
Crus_helicis-Lower_dent:
  ∟Shape_key:
    ∟0.0
Ear_canal-Diameter:
  ∟Shape_key:
    ∟0.0
Lobulus:
  ∟Start:
    ∟Location:
      ∟X: 0.0
      ∟Y: 0.0
      ∟Z: 0.0
    ∟Rotation:
      ∟W: 1.0
      ∟X: 0.0
      ∟Y: 0.0
      ∟Z: 0.0
  ∟End:
    ∟Location:
      ∟X: 0.0
      ∟Y: 0.0
      ∟Z: 0.0
    ∟Rotation:
      ∟W: 1.0
      ∟X: 0.0
      ∟Y: 0.0
      ∟Z: 0.0
  ∟Bendy:
    ∟Scale:
      ∟1.0
Helix_low:
  ∟Start:
    ∟Location:
      ∟X: 0.0
      ∟Y: 0.0
      ∟Z: 0.0
    ∟Rotation:
      ∟W: 1.0
      ∟X: 0.0
      ∟Y: 0.0
      ∟Z: 0.0
  ∟End:
    ∟Location:
      ∟X: 0.0
      ∟Y: 0.0
      ∟Z: 0.0
    ∟Rotation:
      ∟W: 1.0
      ∟X: 0.0
      ∟Y: 0.0
      ∟Z: 0.0
  ∟Bendy:
    ∟Scale:
      ∟1.0
Helix_middle:
  ∟Start:
    ∟Location:
      ∟X: 0.0
      ∟Y: 0.0
      ∟Z: 0.0
    ∟Rotation:
      ∟W: 1.0
      ∟X: 0.0
      ∟Y: 0.0
      ∟Z: 0.0
  ∟End:
    ∟Location:
      ∟X: 0.0
      ∟Y: 0.0
      ∟Z: 0.0
    ∟Rotation:
      ∟W: 1.0
      ∟X: 0.0
      ∟Y: 0.0
      ∟Z: 0.0
  ∟Bendy:
    ∟Scale:
      ∟1.0
Helix_up:
  ∟Start:
    ∟Location:
      ∟X: 0.0
      ∟Y: 0.0
      ∟Z: 0.0
    ∟Rotation:
      ∟W: 1.0
      ∟X: 0.0
      ∟Y: 0.0
      ∟Z: 0.0
  ∟End:
    ∟Location:
      ∟X: 0.0
      ∟Y: 0.0
      ∟Z: 0.0
    ∟Rotation:
      ∟W: 1.0
      ∟X: 0.0
      ∟Y: 0.0
      ∟Z: 0.0
  ∟Bendy:
    ∟Scale:
      ∟1.0
Tragus:
  ∟Start:
    ∟Location:
      ∟X: 0.0
      ∟Y: 0.0
      ∟Z: 0.0
    ∟Rotation:
      ∟W: 1.0
      ∟X: 0.0
      ∟Y: 0.0
      ∟Z: 0.0
  ∟End:
    ∟Location:
      ∟X: 0.0
      ∟Y: 0.0
      ∟Z: 0.0
    ∟Rotation:
      ∟W: 1.0
      ∟X: 0.0
      ∟Y: 0.0
      ∟Z: 0.0
  ∟Bendy:
    ∟Scale:
      ∟1.0
Antitragus:
  ∟Start:
    ∟Location:
      ∟X: 0.0
      ∟Y: 0.0
      ∟Z: 0.0
    ∟Rotation:
      ∟W: 1.0
      ∟X: 0.0
      ∟Y: 0.0
      ∟Z: 0.0
  ∟End:
    ∟Location:
      ∟X: 0.0
      ∟Y: 0.0
      ∟Z: 0.0
    ∟Rotation:
      ∟W: 1.0
      ∟X: 0.0
      ∟Y: 0.0
      ∟Z: 0.0
  ∟Bendy:
    ∟Scale:
      ∟1.0
Antihelix:
  ∟Start:
    ∟Location:
      ∟X: 0.0
      ∟Y: 0.0
      ∟Z: 0.0
    ∟Rotation:
      ∟W: 1.0
      ∟X: 0.0
      ∟Y: 0.0
      ∟Z: 0.0
  ∟End:
    ∟Location:
      ∟X: 0.0
      ∟Y: 0.0
      ∟Z: 0.0
    ∟Rotation:
      ∟W: 1.0
      ∟X: 0.0
      ∟Y: 0.0
      ∟Z: 0.0
  ∟Bendy:
    ∟Scale:
      ∟1.0
Crus_inferius_anthelicis:
  ∟Start:
    ∟Location:
      ∟X: 0.0
      ∟Y: 0.0
      ∟Z: 0.0
    ∟Rotation:
      ∟W: 1.0
      ∟X: 0.0
      ∟Y: 0.0
      ∟Z: 0.0
  ∟End:
    ∟Location:
      ∟X: 0.0
      ∟Y: 0.0
      ∟Z: 0.0
    ∟Rotation:
      ∟W: 1.0
      ∟X: 0.0
      ∟Y: 0.0
      ∟Z: 0.0
  ∟Bendy:
    ∟Scale:
      ∟1.0
Crus_superius_anthelicis:
  ∟Start:
    ∟Location:
      ∟X: 0.0
      ∟Y: 0.0
      ∟Z: 0.0
    ∟Rotation:
      ∟W: 1.0
      ∟X: 0.0
      ∟Y: 0.0
      ∟Z: 0.0
  ∟End:
    ∟Location:
      ∟X: 0.0
      ∟Y: 0.0
      ∟Z: 0.0
    ∟Rotation:
      ∟W: 1.0
      ∟X: 0.0
      ∟Y: 0.0
      ∟Z: 0.0
  ∟Bendy:
    ∟Scale:
      ∟1.0
```

</details>

Set the PPM parameters using the method `set_parameter`.

```python
# change the location of the 'Helix_up' 
ppm.set_parameter(parameter='Helix_up', point='Start', parameter_type='Location', value=(1,0.6), axis='ZX')
```

Get the current PPM-parameter configuration (or a subset) by accessing the property 'parameters': 
```python
print(ppm.parameters)
print(ppm.parameters['Helix_up']['Start']['Location'])
```

### Export options

The module offers the possibility to export the PPM mesh in 'ply' and 'stl' format using the methods `export_ply` and `export_stl`, respectively.
The currently set PPM parameters can be exported to a 'csv' file using the method `export_csv`.

```python
ppm.export_ply('ppm.ply')
ppm.export_stl('ppm.stl')
ppm.export_csv('ppm.csv')
```

To get the points of the current PPM instance, use the method `get_point_cloud` or access the property 'points'.

```python
points = ppm.get_point_cloud()
points = ppm.points
```

The method `render` can be used to render the PPM instance as 'png' or 'exr' (OpenEXR) file in Blender.

```python
ppm.render(filepath='path/to/file', filename='filename', resolution=257)
```

### Math Helpers

The module `math_helpers` provides two helper functions to calculate the minimum pointwise distance and the Hausdorff distance between two PPM instances.

```python
from ppm import PPM
from ppm.math_helpers import minimal_distances, hausdorff_distance

p1 = PPM()
p2 = PPM(from_csv='path/to/file.csv')

# returns an array of the minimal distances between the points of p1 and p2
distances = minimal_distances(p1, p2)

# returns the hausdorff distance between the points of p1 and p2
hausdorff = hausdorff_distance(p1, p2)
```

### Plotting Helpers

Packaged in the module, a helper function is available to visualize the PPM and the minimum pointwise distances between two PPM instances as a 3D plot and a histogram, respectively. `plot_distances` either accepts PPM instances or point clouds.

```python
from ppm import PPM
from ppm.plotting_helpers import plot_distances

p1 = PPM()
p2 = PPM(from_csv='path/to/file.csv')

plot_distances(p1, p2)
```

**Note**:
The plotting helper function requires the matplotlib package to be installed.

## Matlab implementation

For a Matlab implementation please refer to the [matlab](https://github.com/Any2HRTF/PPM/tree/matlab) branch.

## License

This software is licensed under the EUPL-1.2 License. See the [LICENSE](LICENSE.txt) file for details.

## References
The PPM was developed at the Acoustics Research Institute (ARI) of the 
Austrian Academy of Sciences, Vienna, Austria [1-4].

1.  Pollack K.; Pausch F.; Majdak P. (2022) [Parametric pinna model for a 
    realistic representation of listener-specific pinna geometry](https://www.researchgate.net/profile/Florian-Pausch/publication/366977010_Parametric_pinna_model_for_a_realistic_representation_of_listener-specific_pinna_geometry/links/63bc77a1097c7832caa1ffd2/Parametric-pinna-model-for-a-realistic-representation-of-listener-specific-pinna-geometry.pdf?origin=publicationDetail&_sg%5B0%5D=CFr20BsHvQ3k0OmR_gN-XEXvU_IUp2yohXbvrqEzLIKyydtYST3pOQd_ec4Hj_7Dla8Ma5PNwHlp8t0OFyNlXw.vRk-HUSZsPec5Y3v5TJ0n8X0UTQrsWDRO85zyvQJrrni5DtuPXpOFj5yNTsWR3OUDbtwXTIp2qGWwbMbu2O6-w&_sg%5B1%5D=FAr7AoGW3im4MzlZvfT29nywMswK_uXAxcn-6CSJoTZF5IvSbVCKGgdSYxp7jwb1phk1ZGDndKDpqXh0qo_V0F-m2QqukrE0L_4AwshB1m5k.vRk-HUSZsPec5Y3v5TJ0n8X0UTQrsWDRO85zyvQJrrni5DtuPXpOFj5yNTsWR3OUDbtwXTIp2qGWwbMbu2O6-w&_iepl=&_rtd=eyJjb250ZW50SW50ZW50IjoibWFpbkl0ZW0ifQ%3D%3D), 
    Proceedings: A21, Virtual Acoustics, ICA 2022 (International Congress 
    on Acoustics); Gyeongju, S. 168-178. 
 2. Pollack K.; Majdak P.; Brinkmann F.; Kreuzer W. (2021) [Von Fotos zu 
    personalisierter räumlicher Audiowiedergabe](https://link.springer.com/article/10.1007/s00502-021-00891-4). e & i Elektrotechnik und 
    Informationstechnik, S. 250-255.
 3. Pollack K.; Majdak P. (2021) [Evaluation of a Parametric Pinna Model 
    for the Calculation of Head-Related Transfer Functions](https://ieeexplore.ieee.org/abstract/document/9610885). Immersive and 
    3D Audio (I3DA) conference.
 4. Pollack K.; Majdak P.; Furtado H. (2020) [A Parametric Pinna Model for 
    the Calculations of Head-Related Transfer Functions](https://hal.science/hal-03235345/document). Proceedings of 
    Forum Acusticum 2020, Lyon. S. 1357-1360.
