from bezierppm.plotting_helpers import plot_distances
from bezierppm import BezierPPM
from pyntcloud import PyntCloud
import numpy as np

target = PyntCloud.from_file('/Users/felixperfler/Documents/ISF/2023/Mesh2PPM Overview Paper/Manual Registration Challenge/Meshes/NH5_target_KP.ply').xyz
registered = PyntCloud.from_file('/Users/felixperfler/Documents/ISF/2023/Mesh2PPM Overview Paper/Manual Registration Challenge/Meshes/NH5_registered_KP.ply').xyz

# target = BezierPPM().points
# registered = BezierPPM()
# registered.set_parameter('Lobulus', 'Location', [0.005,0.005,0.005], 'Start', 'ZYX')

plot_distances(registered, target)
