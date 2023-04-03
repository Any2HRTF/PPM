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

Please find the doumentation at the [releases page](https://github.com/Any2HRTF/PPM/releases).
