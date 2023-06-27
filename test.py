from ppm import PPM

# p = PPM()

# print(p)
# # # p.ear_canal_closed = True
# # p.ear_canal_closed = True
# # p.mesh_reference_point = 'center_of_mass'
# # p.set_parameter('Lobulus', 'Location', (10,10,10), 'Start', 'YZX')

# # # p.export_blend('/Users/felixperfler/Documents/ISF/PyPPM/test.blend')

# # p2 = PPM()
# # p2.mesh_reference_point = 'center_of_mass'

# # from ppm.plotting_helpers import plot_distances

# # plot_distances(p,p2)

from pyntcloud import PyntCloud

cloud = PyntCloud.from_file("/Users/felixperfler/Downloads/NH131_registered.ply").xyz
# cloud = PyntCloud.from_file("/Users/felixperfler/Downloads/NH5_target.ply").xyz
target_cloud = PyntCloud.from_file("/Users/felixperfler/Downloads/NH131_target.ply").xyz

from ppm.math_helpers import jaccard_similarity
import numpy as np



import time

time_start = time.time()
print(jaccard_similarity(cloud,target_cloud))
time_end = time.time()

print(time_end-time_start)

P = PPM()
Q = PPM()
Q.set_parameter('Lobulus', 'Location', (10,10,10), 'Start', 'YZX')


time_start = time.time()
print(jaccard_similarity(P,Q))
time_end = time.time()
print(time_end-time_start)