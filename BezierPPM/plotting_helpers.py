import matplotlib as mpl
import matplotlib.pyplot as plt
import matplotlib.ticker as ticker
from mpl_toolkits import mplot3d
import numpy as np
from .math_helpers import minimal_distances

def normalize_pc(points):
	centroid = np.mean(points, axis=0)
	points -= centroid
	furthest_distance = np.max(np.sqrt(np.sum(abs(points)**2,axis=-1)))
	points /= furthest_distance

	return points

def plot_distances(P, Q, y_toleranz=0, max_distance=None, filename=None):
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

    hs_dist_with_nans = minimal_distances(P_points, Q_points, y_toleranz, max_distance)
    hs_dist = hs_dist_with_nans[~np.isnan(hs_dist_with_nans)]
    hs_normalized = (hs_dist - np.min(hs_dist)) / (np.max(hs_dist) - np.min(hs_dist))

    ax1 = plt.subplot(121)
    ax1.hist(hs_dist,  bins=100, orientation="horizontal", color = "orange", lw=0, histtype='stepfilled'  )
    ax1.set_ylabel('Distance (mm)')
    ax1.set_ylim(0, np.max(hs_dist))
    ax1.xaxis.set_major_locator(ticker.NullLocator())
    ax1.spines['top'].set_visible(False)
    ax1.spines['right'].set_visible(False)
    ax1.spines['left'].set_visible(False)
    ax1.spines['bottom'].set_visible(False)
    ax1.set_yticks([0,1,max(hs_dist)])

    Q_points = normalize_pc(Q_points)
    P_points = normalize_pc(P_points)

    ax2 = plt.subplot(122, projection='3d')
    Q_plot = mplot3d.art3d.Poly3DCollection([Q_points], facecolor='black', alpha=0.1)
    ax2.add_collection3d(Q_plot)

    # P_plot = mplot3d.art3d.Poly3DCollection([P_points], facecolor='red', alpha=0.1)
    # ax2.add_collection3d(P_plot)

    hs_dist_with_nans[~np.isnan(hs_dist_with_nans)] = hs_normalized
    hs_dist_with_nans[np.isnan(hs_dist_with_nans)] = 1000

    ax2.scatter(P_points[:,0], P_points[:,1], P_points[:,2], c=hs_dist_with_nans, cmap='jet', s=1, alpha=0.5)

    scale = P_points.flatten()
    ax2.auto_scale_xyz(scale, scale, scale)
    ax2.axis('off')


    plt.suptitle(r'$\mu=%.2f,\ \sigma=%.2f,\ \mathrm{median}=%.2f$' %(np.mean(hs_dist), np.std(hs_dist), np.median(hs_dist)))

    if filename is not None:
        ax2.view_init(elev=0., azim=0.)
        plt.savefig(filename)
    else:
        plt.show()