import numpy as np

def _get_point_cloud(P) -> np.ndarray:
    """ Returns the point cloud of P.
    
    Parameters
    ----------
    P : PPM or np.ndarray
    
    Returns
    -------
    np.ndarray
        Point cloud of P.
    """

    if P.__class__.__name__ == 'PPM':
        return np.array(P.points, dtype=np.float32)
    elif P.__class__.__name__ == 'ndarray':
        return np.array(P, dtype=np.float32)
    else:
        raise TypeError('P must be of type PPM or np.ndarray')

def dice_coefficient(P, Q, resolution_x=None, resolution_y=None, resolution_z=None) -> np.float32:
    """ Computes the Dice coefficient between two point clouds P and Q.
    
    Parameters
    ----------
    P : PPM or np.ndarray
    Q : PPM or np.ndarray
    
    Returns
    -------
    np.float32
        Dice coefficient between P and Q. (0 <= D <= 1)
    """

    jaccard = jaccard_similarity(P, Q, resolution_x, resolution_y, resolution_z)
    return 2 * jaccard / (1 + jaccard)

def jaccard_similarity(P, Q, resolution_x=None, resolution_y=None, resolution_z=None) -> np.float32:
    """ Computes the Jaccard similarity between two point clouds P and Q.
    
    Parameters
    ----------
    P : PPM or np.ndarray
    Q : PPM or np.ndarray
    
    Returns
    np.float32
        Jaccard similarity between P and Q. (0 <= J <= 1)
    """

    P_points = _get_point_cloud(P)
    Q_points = _get_point_cloud(Q)

    x_min = min(min(P_points[:, 0]), min(Q_points[:, 0])); x_max = max(max(P_points[:, 0]), max(Q_points[:, 0]))
    y_min = min(min(P_points[:, 1]), min(Q_points[:, 1])); y_max = max(max(P_points[:, 1]), max(Q_points[:, 1]))
    z_min = min(min(P_points[:, 2]), min(Q_points[:, 2])); z_max = max(max(P_points[:, 2]), max(Q_points[:, 2]))

    resolution_xx = int(x_max - x_min) if resolution_x is None else resolution_x
    resolution_yy = int(y_max - y_min) if resolution_y is None else resolution_y
    resolution_zz = int(z_max - z_min) if resolution_z is None else resolution_z

    xx = np.linspace(x_min+.25, x_max-.25, resolution_xx) 
    yy = np.linspace(y_min+.25, y_max-.25, resolution_yy)
    zz = np.linspace(z_min+.25, z_max-.25, resolution_zz)

    grid_points = np.zeros((resolution_xx*resolution_yy*resolution_zz, 11))
    offset = 0

    for z_idx in range(len(zz)):
        for y_idx in range(len(yy)):
            for x_idx in range(len(xx)):
                grid_points[x_idx+offset,...] = np.array([xx[x_idx], yy[y_idx], zz[z_idx],  0, 1, 0, 0, 0, 1, 0, 0])
            offset += len(xx)

    for i in range(len(grid_points)):
        dist_to_nearest_p = np.sqrt(np.min(np.sum( (grid_points[i,:3] - P_points)**2, axis=1)))
        dist_to_nearest_q = np.sqrt(np.min(np.sum( (grid_points[i,:3] - Q_points)**2, axis=1)))

        if dist_to_nearest_p <= 0.6:
            grid_points[i, 3:7] = np.array([1, 0, 1, 0])

        if dist_to_nearest_q <= 0.6:
            grid_points[i, 7:] = np.array([1, 0, 1, 0])

    return np.sum(np.logical_and(grid_points[:, 3], grid_points[:, 7])) / (np.sum(np.logical_or(grid_points[:, 3], grid_points[:, 7])) + np.finfo(np.float32).eps)



def minimal_distances(P, Q) -> np.array:
    """ Computes the minimal distances between two point clouds P and Q.
    P and Q can be of type PPM or np.ndarray.

    Parameters
    ----------
    P : PPM or np.ndarray
    Q : PPM or np.ndarray

    Returns
    -------
    np.array
        Minimal distances between P and Q.
    """

    P_points = _get_point_cloud(P)
    Q_points = _get_point_cloud(Q)

    dist = np.zeros(P_points.shape[0], dtype=np.float32)
    for idx_pred in range(dist.shape[0]):
        dist[idx_pred] = np.min(np.sum((P_points[idx_pred, :] - Q_points)**2, axis=1))

    return np.sqrt(dist)

def hausdorff_distance(P, Q) -> np.float32:
    """ Computes the Hausdorff distance between two point clouds P and Q.
    P and Q can be of type PPM or np.ndarray.

    Parameters
    ----------
    P : PPM or np.ndarray
    Q : PPM or np.ndarray

    Returns
    -------
    np.float32
        Hausdorff distance between P and Q.
    """

    minmal_distance = minimal_distances(P, Q)

    return np.max(minmal_distance)