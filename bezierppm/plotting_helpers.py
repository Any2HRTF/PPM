import matplotlib as mpl
import matplotlib.pyplot as plt
import matplotlib.ticker as ticker
import matplotlib.cm as cm
from mpl_toolkits import mplot3d
from matplotlib.colors import Normalize
import numpy as np
from .math_helpers import minimal_distances

def normalize_pc(points):
	points -= np.mean(points, axis=0)
	points /= np.max(np.sqrt(np.sum(abs(points)**2,axis=-1)))
	return points

def plot_distances(P, Q, vmin=None, vmax=None, filename=None):
    """Plot the hausdorff distance between two point clouds

    Parameters:
    -----------
        P: PPM
            PPM object
        Q: PPM
            PPM object
    """
    if P.__class__.__name__ == 'BezierPPM':
        P_points = P.get_point_cloud()
    elif P.__class__.__name__ == 'ndarray':
        P_points = P
    else:
        raise TypeError('P must be of type BezierPPM or np.ndarray')

    if Q.__class__.__name__ == 'BezierPPM':
        Q_points = Q.get_point_cloud()
    elif Q.__class__.__name__ == 'ndarray':
        Q_points = Q
    else:
        raise TypeError('Q must be of type BezierPPM or np.ndarray')

    hs_dist = minimal_distances(P_points, Q_points)
    vmin = 0 if vmin == None else vmin
    vmax = np.max(hs_dist) if vmax == None else vmax
    
    fig, (ax1, ax2) = plt.subplots(1,2,width_ratios=[1, 3.5])
    ax1.hist(hs_dist,  bins=100, orientation="horizontal", color = "gray", lw=0, histtype='stepfilled', range=(vmin, vmax))
    ax1.set_ylabel('Distances (mm)')
    ax1.set_ylim(vmin, vmax)
    ax1.xaxis.set_major_locator(ticker.NullLocator())
    ax1.spines['top'].set_visible(False)
    ax1.spines['right'].set_visible(False)
    ax1.spines['left'].set_visible(False)
    ax1.spines['bottom'].set_visible(False)
    ax1.set_yticks([vmin,1,max(hs_dist), vmax])

    Q_points = normalize_pc(Q_points)
    P_points = normalize_pc(P_points)

    ax2 = plt.subplot(122, projection='3d')
    Q_plot = mplot3d.art3d.Poly3DCollection([Q_points], facecolor='black', alpha=0.1)
    ax2.add_collection3d(Q_plot)

    ax2.scatter(P_points[:,0], P_points[:,1], P_points[:,2], c=hs_dist, cmap='hot', s=1, alpha=0.5, vmin=vmin, vmax=vmax)
    plt.colorbar(cm.ScalarMappable(norm=Normalize(vmin=vmin, vmax=vmax, clip=False), cmap='hot'), ax=ax2, shrink=0.9)
    scale = P_points.flatten()
    ax2.auto_scale_xyz(scale, scale, scale)
    ax2.axis('off')
    ax2.view_init(elev=0., azim=0., roll=0.)

    if filename is not None:
        plt.savefig(filename)
    else:
        plt.show()