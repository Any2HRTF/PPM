import numpy as np
from scipy.spatial import cKDTree
from .core_class import get_pinna_regions

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
    
def distances_for_pinna_regions(P, Q, skip_input_check=False) -> dict:
    
    if not skip_input_check:
        if P.__class__.__name__ != 'BezierPPM' or Q.__class__.__name__ != 'BezierPPM':
            raise TypeError('P and Q must be of type BezierPPM')
    
    materials = get_pinna_regions()

    out = {}

    for material in materials:
        region_points_p= P.get_vertices_assigned_to_material(material)
        if skip_input_check:
            region_points_q = Q
            out[material] = minimal_distances(region_points_p, region_points_q)
        else:
            region_points_q = Q.get_vertices_assigned_to_material(material)
            out[material] = point_wise_distances(region_points_p, region_points_q)

    return out

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

    # min_distances = np.zeros(P_points.shape[0], dtype=np.float32)
    # for idx_pred in range(min_distances.shape[0]):
    #     min_distances[idx_pred] = np.sqrt(np.min(np.sum((P_points[idx_pred, :] - Q_points)**2, axis=1)))

    tree = cKDTree(Q_points)
    min_distances = tree.query(P_points, workers=-1)[0]

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
        rmse = np.sqrt(np.mean(point_wise_distances(P_points, Q_points)**2))
    else:
        rmse = np.sqrt(np.mean(minimal_distances(P_points, Q_points)**2))

    return rmse
    
def completeness(P, Q, threshhold=1.) -> np.float32:
    """ Computes the completeness for two point clouds P and Q.

    Parameters
    ----------
    P: BezierPPM or np.ndarray
    Q: BezierPPM or np.ndarray
    threshhold: threshhold in mm

    Returns
    -------
    np.ndarray
        completeness in percent
    """

    P_points = _get_point_cloud(P)
    Q_points = _get_point_cloud(Q)
    
    if P_points.shape[0] == Q_points.shape[0]:
        distances = point_wise_distances(P_points, Q_points)
    else:
        distances = minimal_distances(P_points, Q_points)
        
    return 1 - distances[distances > threshhold].shape[0] / distances.shape[0]
        
def chamger_distance(P, Q) -> np.float32:
    """ Computes the chamfer distance given two point clouds P and Q.

    Parameters
    ----------
    P: BezierPPM or np.ndarray
    Q: BezierPPM or np.ndarray

    Returns
    -------
    np.ndarray
        chamfer distance
    """

    P_points = _get_point_cloud(P)
    Q_points = _get_point_cloud(Q)
    
    distances_direction1 = minimal_distances(P, Q)
    distances_direction2 = minimal_distances(Q, P)

    return np.mean(distances_direction1) + np.mean(distances_direction2)
