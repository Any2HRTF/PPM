import numpy as np

def euler_to_quaternion(euler_matrix:np.array, sequence:str='ZYX') -> np.array:
    """Transforms a rotation matrix into a quaternion.

    Parameters
    ----------
    euler_matrix : np.array
        Rotation matrix.
    sequence : str
        Rotation sequence. 
        "ZYX" (default) | "ZYZ" | "ZXY" | "ZXZ" | "YXY" | "YZX" | "YXZ" | "YZY" | "XYX" | "XYZ" | "XZX" | "XZY"

    Returns
    -------
    np.array
        Quaternion.
    """
    quaternion = np.zeros((4,))

    if sequence.lower() == 'zyx':
        c_1 = np.cos(euler_matrix[0]*0.5)
        s_1 = np.sin(euler_matrix[0]*0.5)
        c_2 = np.cos(euler_matrix[1]*0.5)
        s_2 = np.sin(euler_matrix[1]*0.5)
        c_3 = np.cos(euler_matrix[2]*0.5)
        s_3 = np.sin(euler_matrix[2]*0.5)

        quaternion[0] = c_1*c_2*c_3 + s_1*s_2*s_3
        quaternion[1] = c_1*c_2*s_3 - s_1*s_2*c_3
        quaternion[2] = c_1*s_2*c_3 + s_1*c_2*s_3
        quaternion[3] = s_1*c_2*c_3 - c_1*s_2*s_3

    elif sequence.lower() == 'zyz':
        t_1 = euler_matrix[0]*0.5
        t_2 = euler_matrix[1]*0.5
        t_3 = euler_matrix[2]*0.5

        quaternion[0] = np.cos(t_2)*np.cos( t_1 + t_3)
        quaternion[1] = np.sin(t_2)*np.sin(-t_1 + t_3)
        quaternion[2] = np.sin(t_2)*np.cos(-t_1 + t_3)
        quaternion[3] = np.cos(t_2)*np.sin( t_1 + t_3)

    elif sequence.lower() == 'zxy':
        # TODO
        raise NotImplementedError("Sequence 'ZXY' not implemented yet.")

    elif sequence.lower() == 'zxz':
        # TODO
        raise NotImplementedError("Sequence 'ZXZ' not implemented yet.")

    elif sequence.lower() == 'yxy':
        # TODO
        raise NotImplementedError("Sequence 'YXY' not implemented yet.")
    
    elif sequence.lower() == 'yzx':
        # TODO
        raise NotImplementedError("Sequence 'YZX' not implemented yet.")
    
    elif sequence.lower() == 'yxz':
        # TODO
        raise NotImplementedError("Sequence 'YXZ' not implemented yet.")
    
    elif sequence.lower() == 'yzy':
        # TODO
        raise NotImplementedError("Sequence 'YZY' not implemented yet.")
    
    elif sequence.lower() == 'xyx':
        # TODO
        raise NotImplementedError("Sequence 'XYX' not implemented yet.")
    
    elif sequence.lower() == 'xyz':
        # TODO
        raise NotImplementedError("Sequence 'XYZ' not implemented yet.")
    
    elif sequence.lower() == 'xzx':
        # TODO
        raise NotImplementedError("Sequence 'XZX' not implemented yet.")
    
    elif sequence.lower() == 'xzy':
        # TODO
        raise NotImplementedError("Sequence 'XZY' not implemented yet.")

    else:
        raise ValueError(f"Sequence '{sequence}' not supported.")

    return quaternion
