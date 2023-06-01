import numpy as np
from .core_class import PPM

def minimal_distances(P, Q) -> np.array:
    """ Computes the minimal distances between two point clouds P and Q.
    P and Q can be of type PPM or np.ndarray.

    Parameters
    ----------
    P : PPM or np.ndarray
        Point cloud P.
    Q : PPM or np.ndarray
        Point cloud Q.

    Returns
    -------
    np.array
        Minimal distances between P and Q.
    """

    if Q.__class__.__name__ == 'PPM':
        Q_points = Q.get_point_cloud()
    elif Q.__class__.__name__ == 'ndarray':
        Q_points = Q
    else:
        raise TypeError('Q must be of type PPM or np.ndarray')
    
    if P.__class__.__name__ == 'PPM':
        P_points = P.get_point_cloud()
    elif P.__class__.__name__ == 'ndarray':
        P_points = P
    else:
        raise TypeError('P must be of type PPM or np.ndarray')

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
        Point cloud P.
    Q : PPM or np.ndarray
        Point cloud Q.

    Returns
    -------
    np.float32
        Hausdorff distance between P and Q.
    """

    minmal_distance = minimal_distances(P, Q)

    return np.max(minmal_distance)