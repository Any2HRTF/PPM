import os
import io
import sys
import csv
import math
import tempfile
import numpy as np
from contextlib import redirect_stdout

import bpy
import bmesh
import mathutils


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

CURRENT_DIR = os.path.dirname(os.path.realpath(__file__))

class PPM():
    """PPM class

    Parameters:
    -----------
        from_blender_file (str): Path to a blender file to load the PPM from; if None, the standard PPM is loaded
        from_csv_file (str): Path to a csv file to load the PPM parameters from; if None, the standard PPM is loaded
        from_dict (dict): Dictionary containing the PPM parameters; if None, the standard PPM is loaded
    """
    def __init__(self, 
                 from_blender_file=None,
                 from_csv_file=None,
                 from_dict=None,
                 backend='blender'):

        if from_blender_file != None and from_csv_file != None:
            raise Exception('Either load from blender file or from csv file.')
        
        if backend != 'blender' and from_blender_file != None:
            raise Exception('Blender backend not selected.')

        self.backend = backend

        self.__working_unit = 'mm'
        self.__unit_scale = 1

        # load init parameters
        self.__parameters = self.__load_parameters_from_csv()

        if self.backend == 'blender':
            if from_blender_file != None:
                self.__load_blender_file(from_blender_file)
            else:
                self.__load_blender_file(f'{CURRENT_DIR}/resources/PPM.blend')
            self.__get_parameters_from_blender()
        
        # rerun fct to load parameters from csv file
        if from_csv_file != None:
            self.__parameters = self.__load_parameters_from_csv(from_csv_file)
        
        if from_dict != None:
            self.__parameters = self.__load_parameters_from_dict(from_dict)
        
        bpy.ops.object.mode_set(mode='OBJECT')
        
        self.__reference_point = None

    def __load_blender_file(self, filepath):
        logfile = tempfile.mktemp()
        open(logfile, 'a').close()
        old = os.dup(sys.stdout.fileno())
        sys.stdout.flush()
        os.close(sys.stdout.fileno())
        fd = os.open(logfile, os.O_WRONLY)
        bpy.ops.wm.open_mainfile(filepath=filepath)
        # disable output redirection
        os.close(fd)
        os.dup(old)
        os.close(old)
        bpy.ops.object.mode_set(mode='OBJECT')
    
    @property
    def mesh_reference_point(self):
        return self.__reference_point

    @mesh_reference_point.setter
    def mesh_reference_point(self, reference_point):

        self.center_mesh(reference_point=reference_point)
        
    @property
    def working_unit(self):
        return self.__working_unit
    
    @working_unit.setter
    def working_unit(self, unit):
        if unit == 'm':
            self.__unit_scale = 1000
            self.__working_unit = 'm'
        elif unit == 'cm':
            self.__unit_scale = 10
            self.__working_unit = 'cm'
        elif unit== 'mm':
            self.__unit_scale = 1
            self.__working_unit = 'mm'
        else:
            raise Exception('unit must be one of m, cm, mm')

    @property
    def points(self):
        """The point cloud of the PPM"""
        return self.get_point_cloud()

    @property
    def parameters(self):
        """The parameters of the PPM"""
        return self.__parameters
    
    @parameters.setter
    def parameters(self, parameters):
        for parameter_name, parameter in parameters.items():
            for point_name, point in parameter.items():
                if point_name == 'Shape_key':
                    self.__parameters[parameter_name][point_name] = point
                else:
                    for type_name, type in point.items():
                        if type_name == 'Scale' and parameter_name != 'Parent':
                            self.__parameters[parameter_name][point_name][type_name] = type
                        else:
                            for axis_name, axis in type.items():
                                self.__parameters[parameter_name][point_name][type_name][axis_name] = axis

    def get_parameter_dict(self):
        """Returns the PPM parameters as a dictionary.

        Returns
        -------
        dict
            The PPM parameters.
        """
        export_dict = {}

        for parameter_name, parameter in self.__parameters.items():
            # shape keys
            if 'Shape_key' in parameter.keys():
                export_dict[f'Shape_key_{parameter_name}'] = self.__parameters[parameter_name]['Shape_key']
            else:
                for point_name, point in parameter.items():
                    # scale
                    if 'Scale' in point.keys():
                        if 'Parent' in parameter_name:
                            for axis, axis_value in point['Scale'].items():
                                export_dict[f'Scale_{parameter_name}-{point_name}_{axis}'] = self.__parameters[parameter_name][point_name]['Scale'][axis]
                        else:
                            export_dict[f'Scale_{parameter_name}-{point_name}'] = self.__parameters[parameter_name][point_name]['Scale']
                    # rotation
                    if 'Rotation' in point.keys():
                        for axis, axis_value in point['Rotation'].items():
                            export_dict[f'Rotation_{parameter_name}-{point_name}_{axis}'] = self.__parameters[parameter_name][point_name]['Rotation'][axis]
                    # location
                    if 'Location' in point.keys():
                        for axis, axis_value in point['Location'].items():
                            export_dict[f'Location_{parameter_name}-{point_name}_{axis}'] = self.__parameters[parameter_name][point_name]['Location'][axis]
        

        return export_dict

    def __str__(self):

        string = f'Current PPM parameters:\n'
        for parameter_name, parameter in self.__parameters.items():
            string += f'{parameter_name}:\n'
            for point_name, point in parameter.items():
                string += f'  ∟{point_name}:\n'
                if point_name == 'Shape_key':
                    string += f'    ∟{point}\n'
                else:
                    for type_name, type in point.items():
                        string += f'    ∟{type_name}:\n'
                        if type_name == 'Scale' and parameter_name != 'Parent':
                            string += f'      ∟{type}\n'
                        else:

                            for axis_name, axis in type.items():
                                string += f'      ∟{axis_name}: {axis}\n'

        # remove last \n
        string = string[:-1]
        return string

    def set_parameter(self, parameter:str, parameter_type:str, value:tuple, point=None, axis=None):
        """Set a parameter of the PPM

        Parameters:
        -----------
            parameter (str): The parameter to set
            parameter_type (str): The type of the parameter to set (Shape_key, Scale, Rotation, Location)
            point (str): The point to set the parameter to (Start, End, Shape_key or None)
            axis (str): The axis to set the parameter to (e.g. X, Y, Z, XY, XYZ, WXYZ, ... or None) 
            value (tuple): The value to set the parameter to
        """
        if type(value) is list:
            value = tuple(value)
        elif type(value) is not tuple:
            value = (value,)

        parameter_type = parameter_type.lower().capitalize()
        axis = axis.upper() if axis != None else None
        point = point.lower().capitalize() if point != None else None

        if parameter_type not in ['Shape_key', 'Scale', 'Rotation', 'Location']:
            raise Exception('parameter_type must be one of Shape_key, Scale, Rotation, Location')
        
        if point == 'Shape_key':
            if len(value) > 1:
                raise Exception('value must be a single float value')
            self.__parameters[parameter][parameter_type] = value
        elif parameter_type == 'Scale' and parameter != 'Parent':
            if len(value) > 1:
                raise Exception('value must be a single float value')
            self.__parameters[parameter]['Bendy'][parameter_type] = value
        else:
            if point not in ['Start', 'End'] and parameter != 'Parent':
                raise Exception('point must be one of Start, End')
            elif parameter == 'Parent':
                point = 'Bendy'
            
            if len(value) != len(axis):
                raise Exception('value and axis must have the same number of elements')

            if parameter_type == 'Location':
                for a in axis:
                    if a not in ['X', 'Y', 'Z']:
                        raise Exception('axis must be X, Y, Z')
                for i in range(len(value)):
                    self.__parameters[parameter][point][parameter_type][axis[i]] = self.__unit_scale*value[i]
            
            elif parameter_type == 'Rotation':
                # rotation defined in euler angles
                if len(axis) == 3:
                    for a in axis:
                        if a not in ['X', 'Y', 'Z']:
                            raise Exception('axis must be X, Y, Z')
                    
                    quaternion = euler_to_quaternion(value, sequence=axis)
                    
                    self.__parameters[parameter][point][parameter_type]['W'] = quaternion[0]
                    self.__parameters[parameter][point][parameter_type]['X'] = quaternion[1]
                    self.__parameters[parameter][point][parameter_type]['Y'] = quaternion[2]
                    self.__parameters[parameter][point][parameter_type]['Z'] = quaternion[3]

                elif len(axis) == 4:
                    if not all(elem in axis for elem in ['W', 'X', 'Y', 'Z']):
                        raise Exception('axis must contain W, X, Y, Z')

                    for i in range(len(value)):
                        self.__parameters[parameter][point][parameter_type][axis[i]] = value[i]

    def __load_parameters_from_dict(self, parameter_dict:dict) -> dict:
        parameters = {}
        for key, value in parameter_dict.items():
            if 'Shape_key' in key:
                type = 'Shape_key'
                name = key.replace('Shape_key_', '')
                point = None
                axis = None
            elif 'Scale' in key:
                type = 'Scale'
                name = '_'.join(key.split('-')[0].split('_')[1:])
                point = '_'.join(key.split('-')[1].split('_'))
                if 'Parent' in key:
                    axis = point.split('_')[-1]
                    point = point.split('_')[0]
                else:
                    axis = None
            else:
                type = key.split('_')[0]
                name = '_'.join(key.split('-')[0].split('_')[1:])
                point = '_'.join(key.split('-')[1].split('_')[:-1])
                axis = key.split('_')[-1]
                
            value = float(value)

            if type  == 'Scale':
                pass
            
            if name not in parameters:
                parameters[name] = {}
            if point != None:
                if point not in parameters[name]:
                    parameters[name][point] = {}
                if axis != None:
                    if type not in parameters[name][point]:
                        parameters[name][point][type] = {}
                    parameters[name][point][type][axis] = value
                else:
                    parameters[name][point][type] = value
            else:
                if axis != None:
                    if type not in parameters[name]:
                        parameters[name][type] = {}
                    parameters[name][type][axis] = value
                else:
                    parameters[name][type] = value            

        return parameters


    def __load_parameters_from_csv(self, csv_file=None) -> dict:

        if csv_file is None:
            csv_file = f'{CURRENT_DIR}/resources/PPM_params.csv'

        with open(csv_file, newline='', encoding='utf-8') as csvfile:
            reader = csv.reader(csvfile)
            parameters = {}
            for row in reader:
                if 'Shape_key' in row[0]:
                    type = 'Shape_key'
                    name = row[0].replace('Shape_key_', '')
                    point = None
                    axis = None
                elif 'Scale' in row[0]:
                    type = 'Scale'
                    name = '_'.join(row[0].split('-')[0].split('_')[1:])
                    point = '_'.join(row[0].split('-')[1].split('_'))
                    if 'Parent' in row[0]:
                        axis = point.split('_')[-1]
                        point = point.split('_')[0]
                    else:
                        axis = None
                else:
                    type = row[0].split('_')[0]
                    name = '_'.join(row[0].split('-')[0].split('_')[1:])
                    point = '_'.join(row[0].split('-')[1].split('_')[:-1])
                    axis = row[0].split('_')[-1]
                    
                value = float(row[1])

                if type  == 'Scale':
                    pass
                
                if name not in parameters:
                    parameters[name] = {}
                if point != None:
                    if point not in parameters[name]:
                        parameters[name][point] = {}
                    if axis != None:
                        if type not in parameters[name][point]:
                            parameters[name][point][type] = {}
                        parameters[name][point][type][axis] = value
                    else:
                        parameters[name][point][type] = value
                else:
                    if axis != None:
                        if type not in parameters[name]:
                            parameters[name][type] = {}
                        parameters[name][type][axis] = value
                    else:
                        parameters[name][type] = value            

        return parameters
            
    def reset_parameters(self):
        """Resets the PPM parameters to the default parameters.
        """
        self.__parameters = self.__load_parameters_from_csv()

    def __set_parameters_in_blender(self):
        if self.__reference_point is not None:
            self.__center_mesh_blender(reference_point=self.__reference_point)

        obj = bpy.data.objects["Armature"]

        for parameter_name, parameter in self.__parameters.items():
            # shape keys
            if 'Shape_key' in parameter.keys():
                bpy.data.shape_keys['Key.001'].key_blocks[parameter_name].value = self.__parameters[parameter_name]['Shape_key']
            else:
                for point_name, point in parameter.items():
                    # scale
                    if 'Scale' in point.keys():
                        if 'Parent' in parameter_name:
                            for axis, axis_value in point['Scale'].items():
                                obj.pose.bones[parameter_name + "-" + point_name].scale[
                                        0 if axis == 'X' else 
                                        1 if axis == 'Y' else 
                                        2 if axis == 'Z' else 
                                        None] = axis_value
                                    
                        else:
                            obj.pose.bones[parameter_name + "-" + point_name].scale[0] = self.__parameters[parameter_name][point_name]['Scale']
                            obj.pose.bones[parameter_name + "-" + point_name].scale[1] = self.__parameters[parameter_name][point_name]['Scale']
                            obj.pose.bones[parameter_name + "-" + point_name].scale[2] = self.__parameters[parameter_name][point_name]['Scale']
                    # rotation
                    if 'Rotation' in point.keys():
                        for axis, axis_value in point['Rotation'].items():
                            obj.pose.bones[parameter_name + "-" + point_name].rotation_quaternion[
                                    0 if axis == 'W' else
                                    1 if axis == 'X' else
                                    2 if axis == 'Y' else
                                    3 if axis == 'Z' else
                                    None] = axis_value
                    # location
                    if 'Location' in point.keys():
                        for axis, axis_value in point['Location'].items():
                            obj.pose.bones[parameter_name + "-" + point_name].location[
                                    0 if axis == 'X' else
                                    1 if axis == 'Y' else
                                    2 if axis == 'Z' else
                                    None] = axis_value

    def __get_parameters_from_blender(self):

        obj = bpy.data.objects["Armature"]

        for parameter_name, parameter in self.__parameters.items():
            # shape keys
            if 'Shape_key' in parameter.keys():
                self.__parameters[parameter_name]['Shape_key'] = bpy.data.shape_keys['Key.001'].key_blocks[parameter_name].value
            else:
                for point_name, point in parameter.items():
                    # scale
                    if 'Scale' in point.keys():
                        if 'Parent' in parameter_name:
                            for axis, axis_value in point['Scale'].items():
                                self.__parameters[parameter_name][point_name]['Scale'][axis] = \
                                    obj.pose.bones[parameter_name + "-" + point_name].scale[
                                        0 if axis == 'X' else 
                                        1 if axis == 'Y' else 
                                        2 if axis == 'Z' else 
                                        None]
                        else:
                            self.__parameters[parameter_name][point_name]['Scale'] = obj.pose.bones[parameter_name + "-" + point_name].scale[0]
                    # rotation
                    if 'Rotation' in point.keys():
                        for axis, axis_value in point['Rotation'].items():
                            self.__parameters[parameter_name][point_name]['Rotation'][axis] = \
                                obj.pose.bones[parameter_name + "-" + point_name].rotation_quaternion[
                                    0 if axis == 'W' else
                                    1 if axis == 'X' else
                                    2 if axis == 'Y' else
                                    3 if axis == 'Z' else
                                    None]
                    # location
                    if 'Location' in point.keys():
                        for axis, axis_value in point['Location'].items():
                            self.__parameters[parameter_name][point_name]['Location'][axis] = \
                                obj.pose.bones[parameter_name + "-" + point_name].location[
                                    0 if axis == 'X' else
                                    1 if axis == 'Y' else
                                    2 if axis == 'Z' else
                                    None]

    def __get_point_cloud_blender(self):

        obj = bpy.data.objects['Mesh']
        
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

        return np.array(verts)

    def get_point_cloud(self) -> np.array:
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

    def __export_ply_blender(self, filepath):
        
        bpy.ops.object.select_all(action='DESELECT')
        bpy.data.objects['Mesh'].select_set(True)
        # bpy.context.view_layer.objects.active = bpy.data.objects['Mesh']

        with redirect_stdout(io.StringIO()):
            bpy.ops.export_mesh.ply(
                filepath=filepath,
                use_selection=True
            )

    def export_ply(self, filepath):
        """Exports the PPM as a PLY file.

        Parameters
        ----------
        filepath : str
            Path to the PLY file.
        """
        if filepath[-4:] != '.ply':
            filepath += '.ply'
        if self.backend == 'blender':
            self.__set_parameters_in_blender()
            self.__export_ply_blender(filepath)
        else:
            raise NotImplementedError

    def __export_stl_blender(self, filepath):

        bpy.ops.object.select_all(action='DESELECT')
        bpy.data.objects['Mesh'].select_set(True)

        with redirect_stdout(io.StringIO()):
            bpy.ops.export_mesh.stl(
                filepath=filepath,
                use_selection=True
            )

    def export_stl(self, filepath):
        """Exports the PPM as a STL file.

        Parameters
        ----------
        filepath : str
            Path to the STL file.
        """
        if filepath[-4:] != '.stl':
            filepath += '.stl'
        if self.backend == 'blender':
            self.__set_parameters_in_blender()
            self.__export_stl_blender(filepath)
        else:
            raise NotImplementedError
       
    def __export_blend_blender(self, filepath):

        bpy.ops.wm.save_as_mainfile(filepath=filepath)

    def export_blend(self, filepath:str):
        """Exports the PPM as a blend file.

        Parameters
        ----------
        filepath : str
            Path to the blend file.(NOTE: has to be an absolute path)
        """

        if self.backend != 'blender':
            raise NotImplementedError

        self.__set_parameters_in_blender()
        self.__export_blend_blender(filepath=filepath)

     
    def export_csv(self, filepath):
        """Exports the PPM as a CSV file.

        Parameters
        ----------
        filepath : str
            Path to the CSV file.
        """

        export_dict = self.get_parameter_dict()

        with open(filepath, 'w', newline='') as csvfile:
            for key, value in export_dict.items():
                csvfile.write(f'{key},{value}\n')

    def __render_blender(self,
                         file_path,
                         filename,
                         resolution,
                         depth,
                         shade_smooth,
                         image_comp,
                         image_col_dep,
                         cam_loc,
                         cam_rot,
                         cam_loc_ref,
                         depth_farthest,
                         depth_nearest,
                         depth_codec_exr,
                         depth_col_dep_exr,
                         depth_comp_exr):

        # Scene-render settings
        bpy.context.scene.render.engine = 'CYCLES' # CYCLES, BLENDER_EEVEE, WORKBENCH
        bpy.context.view_layer.cycles.denoising_store_passes = True

        cam = bpy.data.objects['Camera']
        cam.rotation_mode = 'XYZ'
        bpy.context.scene.camera = cam

        # Optionally smooth mesh faces for more pleasing rendering results
        if shade_smooth:
            mesh = bpy.context.object.data
            for polygon in mesh.polygons:
                polygon.use_smooth = True

        cam.location = mathutils.Vector((float(cam_loc[0]),
                                            float(cam_loc[1]),
                                            float(cam_loc[2])))
        bpy.context.view_layer.update()

        cam.rotation_euler = mathutils.Euler((
                                    math.radians(float(cam_rot[0])),
                                    math.radians(float(cam_rot[1])),
                                    math.radians(float(cam_rot[2]))),
                                    cam.rotation_mode
                                )

        if cam_loc_ref is not None:

            cam_loc_mtx = cam.matrix_world.to_translation()
            cam_rot = mathutils.Vector((float(cam_loc_ref[0]),
                                        float(cam_loc_ref[1]),
                                        float(cam_loc_ref[2]))) - cam_loc_mtx

            cam_rot_quat = cam_rot.to_track_quat('-Z','Y')

            cam.rotation_euler = cam_rot_quat.to_euler()

        bpy.context.view_layer.update()

        # render image and depth information, and store as png and exr files

        bpy.context.scene.render.use_compositing = True
        bpy.context.scene.render.filepath = file_path + '/' + filename 

        bpy.data.scenes["Scene"].render.resolution_x = resolution
        bpy.data.scenes["Scene"].render.resolution_y = resolution
        bpy.data.scenes["Scene"].render.image_settings.color_depth = image_col_dep
        bpy.data.scenes["Scene"].render.image_settings.compression = image_comp
        bpy.data.scenes["Scene"].render.image_settings.color_mode = 'BW'

        # Enable nodes
        bpy.context.scene.use_nodes = True

        tree = bpy.context.scene.node_tree
        links = tree.links

        # Clear default nodes
        for node in tree.nodes:
            tree.nodes.remove(node)

        # Create render-layers node
        render_layer = tree.nodes.new(type='CompositorNodeRLayers')

        # Create denoising node
        denoise = tree.nodes.new(type='CompositorNodeDenoise')

        if depth:
            # Create map-range node
            tree_map = tree.nodes.new(type='CompositorNodeMapRange')

            # set map minimum in Blender units
            if depth_farthest=='0': #default
                tree_map.inputs[1].default_value = 0
            else:
                tree_map.inputs[1].default_value = float(depth_farthest)
            if depth_nearest=='cam_loc': # default
                # Set map maximum to Euclidian distance of camera to origin
                cam = bpy.data.objects['Camera']
                dist_l2 = math.sqrt(cam.location.x**2 + cam.location.y**2 + cam.location.z**2)
                # map maximum in Blender units
                tree_map.inputs[2].default_value = dist_l2
            else:
                # map maximum in Blender units
                tree_map.inputs[2].default_value = float(depth_nearest)

            # Map values between 1 (white) and zero (black)
            # map minimum in normalised units (linear steps when using OPEN_EXR)
            tree_map.inputs[3].default_value = 1
            # map minimum in normalised units (linear steps when using OPEN_EXR)
            tree_map.inputs[4].default_value = 0

            # Link output of render-layers node to input of map node (exr depth)
            links.new(render_layer.outputs['Depth'], tree_map.inputs['Value'])

            # Create a file-output node, set the path, and file format (exr depth)
            file_output_exr_depth = tree.nodes.new(type='CompositorNodeOutputFile')
            file_output_exr_depth.base_path = file_path
            file_output_exr_depth.format.file_format = "OPEN_EXR"
            file_output_exr_depth.file_slots[0].path = filename +\
                file_output_exr_depth.format.file_format # file name with appended frame idx
            file_output_exr_depth.format.color_depth = depth_col_dep_exr
            file_output_exr_depth.format.compression = depth_comp_exr
            file_output_exr_depth.format.exr_codec = depth_codec_exr

            # Link output of map node to input of compositor-output node (exr depth)
            links.new(tree_map.outputs['Value'], file_output_exr_depth.inputs['Image'])

        links.new(render_layer.outputs['Image'], denoise.inputs['Image'])
        links.new(render_layer.outputs['Denoising Normal'], denoise.inputs['Normal'])
        links.new(render_layer.outputs['Denoising Albedo'], denoise.inputs['Albedo'])

        # Create a file-output node, set the path, and file format (png)
        file_output_png = tree.nodes.new(type='CompositorNodeOutputFile')
        file_output_png.base_path = file_path
        file_output_png.format.file_format = "PNG"
        file_output_png.file_slots[0].path = filename
        file_output_png.format.color_depth = image_col_dep
        file_output_png.format.compression = int(image_comp)

        # Link denoise-node output with compositor-output node (png)
        links.new(denoise.outputs['Image'], file_output_png.inputs['Image'])

        # Render!
        bpy.ops.render.render()


        if depth:
            for file in os.listdir(file_path):
                if file.startswith(filename) and file.endswith('.exr'):
                    os.rename(file_path + f'/{file}', \
                        file_path + f'/{filename}.exr')
                    break
        
        for file in os.listdir(file_path):
            if file.startswith(filename) and file.endswith('.png'):
                os.rename(file_path + f'/{file}', \
                    file_path+ f'/{filename}.png')
                break


    def render(self, *args, **kwargs):
        """Renders the PPM.

        Parameters
        ----------
        filepath : str
            Path to the rendered image.
        filename : str
            Name of the rendered image.
        cam_loc : list
            Location of the camera.
        cam_rot : list
            Rotation of the camera.
        cam_loc_ref : list
            Location of the reference camera.
        depth_farthest : float
            Farthest depth value.
        depth_nearest : str
            Nearest depth value. Default: 'cam_loc'
        resolution : int
            Resolution of the rendered image. Default: 256
        depth : bool
            Whether to render the depth map. Default: False
        shade_smooth : bool
            Whether to render the image with smooth shading. Default: True
        image_comp : int
            Compression of the rendered image. Default: 0
        image_col_dep : str
            Color depth of the rendered image. Default: '8'
        depth_codec_exr : str
            Codec of the depth map. Default: 'NONE'
        depth_col_dep_exr : str
            Color depth of the depth map. Default: '16'
        depth_comp_exr : str
            Compression of the depth map. Default: 8
        """
        if self.backend == 'blender':
            self.__set_parameters_in_blender()
            # redirect output to temporary file
            logfile = tempfile.mktemp()
            open(logfile, 'a').close()
            old = os.dup(sys.stdout.fileno())
            sys.stdout.flush()
            os.close(sys.stdout.fileno())
            fd = os.open(logfile, os.O_WRONLY)

            kwargs['cam_loc'] = self.__unit_scale*np.array(kwargs['cam_loc'])
            kwargs['cam_loc_ref'] = self.__unit_scale*np.array(kwargs['cam_loc_ref'])
            kwargs['depth_farthest'] = self.__unit_scale*kwargs['depth_farthest']

            self.__render_blender(
                file_path=kwargs['filepath'],
                filename=kwargs['filename'],
                resolution=kwargs['resolution'] if 'resolution' in kwargs else 256,
                depth=kwargs['depth'] if 'depth' in kwargs else False,
                shade_smooth=kwargs['shade_smooth'] if 'shade_smooth' in kwargs else True,
                image_comp=kwargs['image_comp'] if 'image_comp' in kwargs else 0,
                image_col_dep=kwargs['image_col_dep'] if 'image_col_dep' in kwargs else '8',
                cam_loc=kwargs['cam_loc'],
                cam_rot=kwargs['cam_rot'] if 'cam_rot' in kwargs else [0, 0, 0],
                cam_loc_ref=kwargs['cam_loc_ref'],
                depth_farthest=kwargs['depth_farthest'],
                depth_nearest=kwargs['depth_nearest'] if 'depth_nearest' in kwargs else 'cam_loc',
                depth_codec_exr=kwargs['depth_codec_exr'] if 'depth_codec_exr' in kwargs else 'NONE',
                depth_col_dep_exr=kwargs['depth_col_dep_exr'] if 'depth_col_dep_exr' in kwargs else '16',
                depth_comp_exr=kwargs['depth_comp_exr'] if 'depth_comp_exr' in kwargs else 8
            )

            # disable output redirection
            os.close(fd)
            os.dup(old)
            os.close(old)
        else:
            raise NotImplementedError
        
    def center_mesh(self, reference_point='ear_canal_entrance'):

        self.__reference_point = reference_point

    def __center_mesh_blender(self, reference_point):
        # get reference point
        if reference_point == 'ear_canal_entrance':
            reference_point = self.__get_ear_canal_entrance_blender()
        elif reference_point == 'center_of_mass':
            reference_point = self.__get_center_of_mass_blender()
        else:
            raise ValueError("reference_point must be either 'ear_canal_entrance' or 'center_of_mass'.")
        
        # move object so that the reference point coincides with the center of the global coordinate system
        obj = bpy.data.objects['Armature']
        obj.matrix_world = mathutils.Matrix.Translation(-reference_point) @ obj.matrix_world
        
    def __get_ear_canal_entrance_blender(self):
        
        vs = [vert for vert in bpy.context.object.data.vertices if bpy.context.object.vertex_groups['Ear_canal_entrance_center'].index in [i.group for i in vert.groups]]
        local_ear_canal_entrance = vs[0].co

        obj = bpy.data.objects['Mesh']
        ear_canal_entrance = obj.matrix_world @ local_ear_canal_entrance

        return ear_canal_entrance

    def __get_center_of_mass_blender(self):

        # get center of mass of PPM template mesh bounding box
        obj = bpy.data.objects['Mesh']
        local_bbox_center = 1/8 * sum((mathutils.Vector(b) for b in obj.bound_box), mathutils.Vector())

        # convert to world coordinates
        center_of_mass = obj.matrix_world @ local_bbox_center

        return center_of_mass