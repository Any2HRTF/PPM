from ppm import PPM
from ppm.math_helpers import minimal_distances
import time
from pyntcloud import PyntCloud
import numpy as np

from ppm.plotting_helpers import plot_distances

ppm = PPM()
ppm2 = PPM(from_blender_file='/Users/felixperfler/Downloads/NH1061.blend')
ppm2_target = PyntCloud.from_file('/Users/felixperfler/Downloads/NH1061_target.ply').xyz


start = time.time()

# ppm.export_stl('/Users/felixperfler/Downloads/test.stl')
# ppm2.export_stl('/Users/felixperfler/Downloads/test2.stl')

# ppm2.export_csv('/Users/felixperfler/Downloads/test2.csv')

# ppm2 = PPM(from_csv_file='/Users/felixperfler/Downloads/test2.csv')

# ppm2.export_stl('/Users/felixperfler/Downloads/test2_varify.stl')

# print(ppm.parameters)

p = ppm2.parameters

# ppm.parameters = p

# plot_distances(ppm2, ppm2_target)

# check if both point clouds are the same
# print(np.allclose(ppm.points, ppm2.points))

ppm.render(file_path='/Users/felixperfler/Downloads', filename='image')

end = time.time()
print('Time: %0.2fs' % (end - start))