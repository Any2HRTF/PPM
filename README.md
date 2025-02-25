# PyBezierPPM

Python interface to a parametric pinna model based on cubic Bézier curves (BezierPPM). 

## Requirement

Python 3.11 is required to use the software.

## Installation

Get the pre-built Python wheel from the [releases](https://github.com/Any2HRTF/PPM/releases/latest) page and install it using pip:

```bash
$ pip install /path/to/wheel.whl
```

## Usage

The module provides a single class `BezierPPM`.
The constructor will generate a BezierPPM instance with default PPM-parameter values.
   
```python
from bezierppm import BezierPPM

ppm = BezierPPM()
```

Alternatively, the PPM can be instantiated from a 'blend' file, 'csv' file, or a Python dictionary containing the PPM parameters in the same format as the 'csv' file.

### Centering

Use the method `center_mesh` to either move the PPM's center of mass, i.e. the center of the bounding box surrounding the PPM, or the center of the ear-canal entrance to the origin of the global coordinate system. 

```python
ppm.center_mesh(reference_point='ear_canal_entrance')
ppm.center_mesh(reference_point='center_of_mass')
```

### Parameters

To see the currently set parameters, use the `print` function.
```python
print(ppm)
print(ppm.parameters['Helix up']['Start']['Location'])
```

Set the BezierPPM parameters using the method `set_parameter`.



```python
# Scale 'Parent' (bendy bone, anisotropic scaling possible) 
ppm.set_parameter(name='Parent', type='Scale', value=(0.75, 1.5, 0.0), axis='ZXY')

# Translate 'Helix_up' (start point) 
ppm.set_parameter(name='Helix up', point='Start', type='Location', value=(1,0.6), axis='ZX')

# Rotate 'Parent' by 90 degrees around the X-axis via a quaternion
q = (np.sqrt(2)/2, np.sqrt(2)/2, 0, 0)
ppm.set_parameter(name='Parent', point='Bendy', type='Rotation', value=q, axis='WXYZ')

# Modify the shape key 'Ear_canal-Diameter'
pmod.set_parameter(name='Ear canal-Diameter', type='Shape key', value=(-1))
```

### Export Options

The module offers the possibility to export the PPM mesh in 'stl' format using the method `export_stl`.
The currently set PPM parameters can be exported to a 'csv' file using the method `export_csv`.

```python
ppm.export_stl('ppm.stl')
ppm.export_csv('ppm.csv')
```

To get the points of the current PPM instance, use the method `get_point_cloud` or access the property 'points'.

```python
points = ppm.get_point_cloud()
points = ppm.points
```

The method `render` can be used to render the PPM instance as 'png' and optionally 'exr' (OpenEXR) file in Blender.

```python
ppm.render(file="/path/to/render/file/location/filename", resolution=512)
```

### Math Helpers

The module `math_helpers` provides two helper functions to calculate the minimum pointwise distance and the Hausdorff distance between two PPM instances.

```python
from bezierppm import BezierPPM
from bezierppm.math_helpers import minimal_distances, hausdorff_distance

p1 = BezierPPM()
p2 = BezierPPM(from_csv='path/to/file.csv')

# returns an array of the minimal distances between the points of p1 and p2
distances = minimal_distances(p1, p2)

# returns the hausdorff distance between the points of p1 and p2
hausdorff = hausdorff_distance(p1, p2)
```

### Plotting Helpers

Packaged in the module, a helper function is available to visualize the PPM and the minimum pointwise distances between two PPM instances as a 3D plot and a histogram, respectively. `plot_distances` either accepts PPM instances or point clouds.

```python
from bezierppm import BezierPPM
from bezierppm.plotting_helpers import plot_distances

p1 = BezierPPM()
p2 = BezierPPM(from_csv='path/to/file.csv')

plot_distances(p1, p2)
```

## Additional Software

For the CloudCompare Blender Plugin helping to perform manual registrations please refer to the [PointCloudCompare](https://github.com/Any2HRTF/PPM/tree/PointCloudCompare) branch.
For a Matlab implementation please refer to the [matlab](https://github.com/Any2HRTF/PPM/tree/matlab) branch.

## License

This software is licensed under the EUPL-1.2 License. See the [LICENSE](LICENSE.txt) file for details.

## Cite

Please cite the following paper if you use this code in your work:

* Perfler F.; Pausch F.; Pollack K.; Holighaus N.; Majdak P. (**2025**) Parametric model of the human pinna based on Bézier curves and concave deformations. _Computers in Biology and Medicine_ 188: 109817. DOI: [10.1016/j.compbiomed.2025.109817](https://doi.org/10.1016/j.compbiomed.2025.109817).

```bibtex
@article{Perfler2025
  title={Parametric model of the human pinna based on Bézier curves and concave deformations},
  author = {Felix Perfler and Florian Pausch and Katharina Pollack and Nicki Holighaus and Piotr Majdak},
  journal = {Computers in Biology and Medicine},
  volume = {188},
  pages = {109817},
  year = {2025},
  issn = {0010-4825},
  doi = {https://doi.org/10.1016/j.compbiomed.2025.109817},
  url = {https://www.sciencedirect.com/science/article/pii/S0010482525001672},
}
```

## References
The BezierPPM was developed at the Acoustics Research Institute (ARI) of the 
Austrian Academy of Sciences, Vienna, Austria [1-5].

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
5. Perfler F.; Pausch F.; Pollack K.; Holighaus N.; Majdak P. (2025) [Parametric model of the human pinna based on Bézier curves and concave deformations](https://doi.org/10.1016/j.compbiomed.2025.109817). Computers in Biology and Medicine, Volume 188, 2025, 109817, ISSN 0010-4825,
