[![Build Python Wheels](https://github.com/Any2HRTF/PPM/actions/workflows/build_wheels.yaml/badge.svg)](https://github.com/Any2HRTF/PPM/actions/workflows/build_wheels.yaml)

# Installation

Download the Python wheel from the [releases page](https://github.com/Any2HRTF/PPM/releases). Then use pip to install the package in a virtual environment with Python 3.10:

```bash
pip install /path/to/whell/*.whl
```

# Usage
    
```python
from ppm import PPM
from ppm.plotting import plot_hausdorff, plot
from ppm.geometric_metrics import hausdorff_distance

ppm = PPM()
```
Calling the constructor without arguments will initialize the default parameters. Alternatively a blender file can be passed to the initializer.

```python
ppm = PPM(from_blender_file="/path/to/blender/file.blend")
```
Parameters can also be set manually.

```python
ppm_target = PPM()

ppm_target.set_ppm_params(
    {
        'Location_Antitragus-End_X':-10,
        'Location_Antitragus-End_Y':-10,
        'Location_Antitragus-End_Z':-10
    }
)
```

The function ``plot_hausdorff`` can be used to plot the Hausdorff distance between two PPMs

```python
plot_hausdorff(ppm_target, ppm)
```

resulting in the following plot:

![Hausdorff distance](https://github.com/Any2HRTF/PPM/blob/main/doc/hs_plot.png "Hausdorff distance")

Realisations can also be rendered or plotted (from various positions if cam_loc is set).

```python
plot(ppm_target)
```

![PPM plot](https://github.com/Any2HRTF/PPM/blob/main/doc/render.png "PPM plot")]

In ''geometric_metrics'' the Hausdorff distance between two PPMs can be calculated.

```python
hausdorff_distance(ppm_target, ppm, 'gen')
```
