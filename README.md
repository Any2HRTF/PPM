# PyPPM

Python module to programmatically interface with the PPM[1]. 

## Installation

Get the prebuild Python wheel from the [releases](https://github.com/Any2HRTF/PPM/releases) page and install it with pip:

```bash
pip install /path/to/wheel.whl
```

Alternatively, you could build the module from source.

## Usage

The module provides a single class 'PPM'.
Using the default constructor will load the default PPM with the default parameters.
   
```python
from ppm import PPM

ppm = PPM()
```

Alternatively the PPM can be loaded from a *.blend, *.csv or a Python dictionary containing the PPM parameters in the same format as the *.csv files.

### Parameters

The default PPM parameters are as follows:
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

They can be set using the 'set_parameter' method.

```python
# change the location of the 'Helix_up' 
ppm.set_parameter(parameter='Helix_up', point='Start', parameter_type='Location', value=(1,0.6), axis='ZX')
```

### Exporting the PPM

The module offers the possibility to export the PPM mesh in the *.ply and *.stl format using the 'export_plt' and 'export_stl' methods respectively.
The currently set parameters can be stored to a *.csv file using the 'export_csv' method.

```python
ppm.export_ply('ppm.ply')
ppm.export_stl('ppm.stl')
ppm.export_csv('ppm.csv')
```

If you want to use the points of the current PPM configuration in your own code, you can use the 'get_point_cloud' method or the 'points' property.

```python
points = ppm.get_point_cloud()
points = ppm.points
```

The 'render' method can be used to render the PPM in Blender.

```python
ppm.render(filepath='path/to/file', filename='filename', resolution=257)
```

### Math Helpers

Found in the 'math_helpers' module are two helper functions to calculate the minimal distance between two points and the hausdorff distance between two PPM realisations.

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

Packaged into the model is a helper function to visualise the PPM in a 3D plot and a histogram of the distances between the points of two PPMs.

```python
from ppm import PPM
from ppm.plotting_helpers import plot_distances

p1 = PPM()
p2 = PPM(from_csv='path/to/file.csv')

plot_distances(p1, p2)
```

**Note**
The plotting helper function requires the matplotlib  packages to be installed.

## Matlab implementation

For a Matlab implementation please refer to the [matlab](https://github.com/Any2HRTF/PPM/tree/matlab) branch.

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
