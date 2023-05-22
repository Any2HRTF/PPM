import os
import numpy as np

from .math_helpers import euler_to_quaternion


class PPM():
    """PPM class

    Parameters:
    -----------
        from_blender_file (str): Path to a blender file to load the PPM from; if None, the standard PPM is loaded
        from_csv_file (str): Path to a csv file to load the PPM parameters from; if None, the standard PPM is loaded
    """
    def __init__(self, from_blender_file=None, from_csv_file=None, from_parameter_dict=None, backend='blender'):

        self.backend = backend
        if self.backend == 'blender':
            import bpy
            import bmesh


    def __set_parameters_in_blender(self):
        pass

    def __get_parameters_from_blender(self):
        pass

    def __get_point_cloud_blender(self):
        obj = bpy.data.objects['ARI_PPM_v1']
        
        if bpy.ops.object.mode_set.poll():
            bpy.ops.object.mode_set(mode='OBJECT')

        depsgraph = bpy.context.evaluated_depsgraph_get()
        obj_eval = obj.evaluated_get(depsgraph)
        bm = bmesh.new()
        me = obj_eval.to_mesh()
        me.transform(obj.matrix_world)
        bm.from_mesh(me)
        obj.to_mesh_clear()

        verts = [v.co for v in bm.verts]

        bm.free()

        return np.array(verts)

    def get_point_cloud(self):
        """Returns the point cloud of the PPM.

        Returns
        -------
        np.array
            Point cloud of the PPM.
        """
        if self.backend == 'blender':
            self.__set_parameters_in_blender()
            return self.__get_point_cloud_blender()
        else:
            raise NotImplementedError

