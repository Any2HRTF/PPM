from scipy.spatial.distance import directed_hausdorff
import numpy as np
from .core_class import PPM

def _hausdorff_dist(
    prediction: np.array,
    target: np.array,
    htype: str='dir') -> np.array:

    r""" Calculates the Hausdorff distance between two point clouds.
    
    A. A. Taha and A. Hanbury, 
    “An efficient algorithm for calculating the exact Hausdorff distance.” 
    IEEE Transactions On Pattern Analysis And Machine Intelligence, vol. 37 pp. 2153-63, 2015.

    Args:
        prediction (np.array): redicted point cloud in Cartesian coordinates XYZ
        target (np.array): target point cloud in Cartesian coordinates XYZ
        htpe (str): Type of the Hausdorff distance to be calculated.
            Can be 'gen' for general (maximum of both directed Hausdorff distances),
            'point' for point-to-point (change order of prediction and target if required)
            or 'point' for point-wise directed Hausdorff distance
            (change order of prediction and target if required).

    Returns:
        dist (np.array): Hausdorff distance between the two point clouds
    
    """

    if htype == 'dir':
        dist = np.asarray(directed_hausdorff(prediction, target)[0], dtype=np.float32)
    elif htype == 'gen':
        dist = np.asarray(max(directed_hausdorff(prediction, target)[0],
                            directed_hausdorff(target, prediction)[0]), dtype=np.float32)
    elif htype == 'point':

        dist = np.zeros(prediction.shape[0], dtype=np.float32)
        for idx_pred in range(dist.shape[0]):
            dist_min = np.linalg.norm(prediction[idx_pred] - target, axis=1)
            dist[idx_pred] = np.min(dist_min)
    else:
        raise NotImplementedError(f'htype {htype} is not implemented!')

    return dist

def hausdorff_distance(ppm: PPM, ppm_target: PPM, htype: str='point') -> np.array:
    """Calculates the Hausdorff distance between two PPMs.
    
    Parameters:
    ----------
        ppm (PPM): PPM object
        ppm_target (PPM): PPM object
        htpe (str): Type of the Hausdorff distance to be calculated.
            Can be 'gen' for general (maximum of both directed Hausdorff distances),
            'point' for point-to-point (change order of prediction and target if required)
            or 'point' for point-wise directed Hausdorff distance
            (change order of prediction and target if required).
    
    Returns:
    -------
        dist (np.array): Hausdorff distance between the two point clouds
    
    """

    prediction = ppm.get_point_cloud()
    target = ppm_target.get_point_cloud()

    return _hausdorff_dist(prediction, target, htype)
