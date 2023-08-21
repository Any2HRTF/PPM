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

    if P.__class__.__name__ == 'BezierPPM':
        return np.array(P.points, dtype=np.float32)
    elif P.__class__.__name__ == 'ndarray':
        return np.array(P, dtype=np.float32)
    else:
        raise TypeError('P must be of type PPM or np.ndarray')

def minimal_distances(P, Q,) -> np.ndarray:
    """ Computes the minimal distances between two point clouds P and Q.
    P and Q can be of type PPM or np.ndarray.

    Parameters
    ----------
    P : PPM or np.ndarray
    Q : PPM or np.ndarray

    Returns
    -------
    np.ndarray
        Minimal distances between P and Q.
    """

    P_points = _get_point_cloud(P)
    Q_points = _get_point_cloud(Q)

    min_distances = np.zeros(P_points.shape[0], dtype=np.float32)
    for idx_pred in range(min_distances.shape[0]):
        min_distances[idx_pred] = np.sqrt(np.min(np.sum((P_points[idx_pred, :] - Q_points)**2, axis=1)))

    return min_distances

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

def point_wise_distances(P, Q) -> np.float32:
    """ Computes the pointwise distance for two point clouds P and Q.

     Parameters
    ----------
    P: BezierPPM or np.ndarray
    Q: BezierPPM or np.ndarray

    Returns
    -------
    np.ndarray
        point wide distances
    """
    P_points = _get_point_cloud(P)
    Q_points = _get_point_cloud(Q)

    if P_points.shape[0] != Q_points.shape[0]:
        raise Exception("The number of points needs to be the same")

    return np.sqrt(np.sum((P_points-Q_points)**2, axis=1))

def rmse_distance(P, Q) -> np.float32:
    """ Computes the pointwise distance for two point clouds P and Q.

    Parameters
    ----------
    P: BezierPPM or np.ndarray
    Q: BezierPPM or np.ndarray

    Returns
    -------
    np.ndarray
        point wide distances
    """
    P_points = _get_point_cloud(P)
    Q_points = _get_point_cloud(Q)
    
    if P_points.shape[0] == Q_points.shape[0]:
        rmse = np.mean(point_wise_distances(P_points, Q_points))
    else:
        rmse = np.max([np.mean(minimal_distances(P_points, Q_points)), np.mean(minimal_distances(Q_points, P_points))])

    return rmse
