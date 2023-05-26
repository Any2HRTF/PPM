import matplotlib.pyplot as plt
import matplotlib.ticker as ticker
from mpl_toolkits.axes_grid1 import ImageGrid
import numpy as np
from .math_helpers import minimal_distances


def plot_distances(P, Q):
    """Plot the hausdorff distance between two point clouds 

    Parameters:
    -----------
        P: PPM
            PPM object
        Q: PPM
            PPM object
    """
    if P.__class__.__name__ == 'PPM':
        P_points = P.get_point_cloud()
    elif P.__class__.__name__ == 'ndarray':
        P_points = P
    else:
        raise TypeError('P must be of type PPM or np.ndarray')
    
    if Q.__class__.__name__ == 'PPM':
        Q_points = Q.get_point_cloud()
    elif Q.__class__.__name__ == 'ndarray':
        Q_points = Q
    else:
        raise TypeError('Q must be of type PPM or np.ndarray')
    
    hs_dist_exact = minimal_distances(P_points, Q_points)

    # reduce number of points to 5000
    if P_points.shape[0] > 5000:
        P_points = P_points[np.random.choice(P_points.shape[0], 5000, replace=False), :]
    if Q_points.shape[0] > 5000:
        Q_points = Q_points[np.random.choice(Q_points.shape[0], 5000, replace=False), :]

    hs_dist = minimal_distances(P_points, Q_points)

    ax1 = plt.subplot(121)
    ax1.hist(hs_dist_exact,  bins=100, orientation="horizontal", color = "orange", lw=0, histtype='stepfilled'  )
    ax1.set_ylabel('Distance (mm)')
    ax1.set_ylim(0, np.max(hs_dist))
    ax1.xaxis.set_major_locator(ticker.NullLocator())
    ax1.spines['top'].set_visible(False)
    ax1.spines['right'].set_visible(False)
    ax1.spines['left'].set_visible(False)
    ax1.spines['bottom'].set_visible(False)
    ax1.set_yticks([0,1,max(hs_dist)])

    C = 255 - np.round((hs_dist - np.min(hs_dist)) / (np.max(hs_dist) - np.min(hs_dist)) * 255).astype(int)

    ax2 = plt.subplot(122, projection='3d')
    ax2.scatter(P_points[:,0],P_points[:,1],P_points[:,2], c=C, cmap='gist_heat', alpha=0.1)
    ax2.scatter(Q_points[:,0],Q_points[:,1],Q_points[:,2], color='black', alpha=0.05)
    ax2.axis('off')

    # add title to show mean, variance and median in LaTeX
    plt.suptitle(r'$\mu=%.2f,\ \sigma=%.2f,\ \mathrm{median}=%.2f$' %(np.mean(hs_dist_exact), np.std(hs_dist_exact), np.median(hs_dist_exact)))

    plt.show()