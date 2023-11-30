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

from .render_helpers import render


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

class BezierPPM():
    """PPM class

    Parameters:
    -----------
        from_blender_file (str): Path to a blender file to load the PPM from; if None, the standard PPM is loaded
        from_csv_file (str): Path to a csv file to load the PPM parameters from; if None, the standard PPM is loaded
        from_dict (dict): Dictionary containing the PPM parameters; if None, the standard PPM is loaded
    """
    def __init__(self, 
                 from_csv_file=None,
                 from_dict=None,
                 backend='blender'):

        self.backend = backend

        # load init parameters
        self.__parameters = self.__load_parameters_from_csv()
        
        # rerun fct to load parameters from csv file
        if from_csv_file is not None:
            self.__parameters = self.__load_parameters_from_csv(from_csv_file)
        
        if from_dict is not None:
            self.__parameters = self.__load_parameters_from_dict(from_dict)
        
        self.__reference_point = None

    def __load_blender_file(self, file_path):
        logfile = tempfile.mktemp()
        open(logfile, 'a').close()
        old = os.dup(sys.stdout.fileno())
        sys.stdout.flush()
        os.close(sys.stdout.fileno())
        fd = os.open(logfile, os.O_WRONLY)
        bpy.ops.wm.open_mainfile(filepath=file_path)
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
            raise ValueError('parameter_type must be one of Shape_key, Scale, Rotation, Location')
        
        if point == 'Shape_key':
            if len(value) > 1:
                raise ValueError('value must be a single float value')
            self.__parameters[parameter][parameter_type] = value
        elif parameter_type == 'Scale' and parameter != 'Parent':
            if len(value) > 1:
                raise ValueError('value must be a single float value')
            self.__parameters[parameter]['Bendy'][parameter_type] = value
        else:
            if point not in ['Start', 'End'] and parameter != 'Parent':
                raise ValueError('point must be one of Start, End')
            if parameter == 'Parent':
                point = 'Bendy'

            if len(value) != len(axis):
                raise ValueError('value and axis must have the same number of elements')

            if parameter_type == 'Location':
                for i, val in enumerate(value):
                    self.__parameters[parameter][point][parameter_type][axis[i]] = val
            
            elif parameter_type == 'Rotation':
                # rotation defined in euler angles
                if len(axis) == 3:
                    for a in axis:
                        if a not in ['X', 'Y', 'Z']:
                            raise ValueError('axis must be X, Y, or Z')

                    quaternion = euler_to_quaternion(value, sequence=axis)

                    self.__parameters[parameter][point][parameter_type]['W'] = quaternion[0]
                    self.__parameters[parameter][point][parameter_type]['X'] = quaternion[1]
                    self.__parameters[parameter][point][parameter_type]['Y'] = quaternion[2]
                    self.__parameters[parameter][point][parameter_type]['Z'] = quaternion[3]

                elif len(axis) == 4:
                    if not all(elem in axis for elem in ['W', 'X', 'Y', 'Z']):
                        raise ValueError('axis must contain W, X, Y, Z')

                    for i, a in enumerate(axis):
                        self.__parameters[parameter][point][parameter_type][a] = value[i]

            elif parameter_type == 'Scale':
                for i, a in enumerate(axis):
                    if a not in ['X', 'Y', 'Z']:
                        raise ValueError('axis must be X, Y, Z')
                    self.__parameters[parameter][point][parameter_type][a] = value[i]

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
        self.__load_blender_file(f'{CURRENT_DIR}/resources/PPM.blend')

        if self.__reference_point is not None:
            self.__center_mesh_blender(reference_point=self.__reference_point)

        for parameter_name, parameter in self.__parameters.items():

            obj = bpy.data.objects["Armature"]
            obj.select_set(True)

            if 'Parent' not in parameter_name and 'Shape_key' not in parameter.keys():
                bpy.context.view_layer.objects.active = obj
                if bpy.context.active_object.mode != 'POSE':
                    bpy.ops.object.posemode_toggle()

                pb = obj.pose.bones[parameter_name + "-" + point_name].bone
                pb.select = True

            # shape keys
            if 'Shape_key' in parameter.keys():
                bpy.data.shape_keys['Key'].key_blocks[parameter_name].value = self.__parameters[parameter_name]['Shape_key']
            else:
                for point_name, point in parameter.items():
                    # scale
                    if 'Scale' in point.keys():
                        if 'Parent' in parameter_name:
                            for axis, axis_value in point['Scale'].items():
                                axis_constraint_bool = tuple(True if axis == axis_name else False for axis_name in ['X', 'Y', 'Z'])                          
                                tuple_axis_value = tuple((axis_value,1.0,1.0) if axis == 'X' else
                                                         (1.0,axis_value,1.0) if axis == 'Y' else
                                                         (1.0,1.0,axis_value))

                                bpy.ops.transform.resize(
                                    value=tuple_axis_value,
                                    orient_type='GLOBAL',
                                    orient_matrix=((1, 0, 0), (0, 1, 0), (0, 0, 1)),
                                    orient_matrix_type='GLOBAL', 
                                    constraint_axis=axis_constraint_bool,
                                    use_accurate=True
                                )

                        else:
                            bpy.ops.transform.resize(
                                value=np.array((point['Scale'], point['Scale'], point['Scale'])),
                                orient_type='GLOBAL',
                                orient_matrix=((1, 0, 0), (0, 1, 0), (0, 0, 1)),
                                orient_matrix_type='GLOBAL',
                                use_accurate=True
                            )

                    # rotation
                    if 'Rotation' in point.keys():
                        for axis, axis_value in point['Rotation'].items():

                            self.__parameters[parameter_name][point_name]['Rotation'][axis] = axis_value
                            
                            if axis=='Z':
                                rotation_current = self.__parameters[parameter_name][point_name]['Rotation']
                                rotation_current_quaternion = mathutils.Quaternion(
                                    np.array(
                                        [rotation_current['W'],
                                         rotation_current['X'],
                                         rotation_current['Y'],
                                         rotation_current['Z']]
                                    )
                                )
                                
                                obj.pose.bones[parameter_name + "-" + point_name].rotation_quaternion = rotation_current_quaternion @ \
                                    obj.pose.bones[parameter_name + "-" + point_name].rotation_quaternion
                    # location
                    if 'Location' in point.keys():
                        for axis, axis_value in point['Location'].items():
                            
                            axis_constraint = np.array(tuple(1 if axis == axis_name else 0 for axis_name in ['X', 'Y', 'Z']))
                            axis_constraint_bool = tuple(True if axis == axis_name else False for axis_name in ['X', 'Y', 'Z'])

                            bpy.ops.transform.translate(
                                value=tuple(axis_constraint * axis_value * 1000),
                                orient_type='GLOBAL',
                                orient_matrix=((1, 0, 0), (0, 1, 0), (0, 0, 1)),
                                orient_matrix_type='GLOBAL',
                                constraint_axis=axis_constraint_bool,
                                use_accurate=True
                            )

        obj.select_set(False)
        pb.select = False
        bpy.ops.object.mode_set(mode='OBJECT')

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

    def __export_ply_blender(self, file_path):
        
        bpy.ops.object.select_all(action='DESELECT')
        bpy.data.objects['Mesh'].select_set(True)
        # bpy.context.view_layer.objects.active = bpy.data.objects['Mesh']

        with redirect_stdout(io.StringIO()):
            bpy.ops.export_mesh.ply(
                filepath=file_path,
                use_selection=True
            )

    def export_ply(self, file_path):
        """Exports the PPM as a PLY file.

        Parameters
        ----------
        file_path : str
            Path to the PLY file.
        """
        if file_path[-4:] != '.ply':
            file_path += '.ply'
        if self.backend == 'blender':
            self.__set_parameters_in_blender()
            self.__export_ply_blender(file_path)
        else:
            raise NotImplementedError

    def __export_stl_blender(self, file_path):

        bpy.ops.object.select_all(action='DESELECT')
        bpy.data.objects['Mesh'].select_set(True)

        with redirect_stdout(io.StringIO()):
            bpy.ops.export_mesh.stl(
                filepath=file_path,
                use_selection=True
            )

    def export_stl(self, file_path):
        """Exports the PPM as a STL file.

        Parameters
        ----------
        file_path : str
            Path to the STL file.
        """
        if file_path[-4:] != '.stl':
            file_path += '.stl'
        if self.backend == 'blender':
            self.__set_parameters_in_blender()
            self.__export_stl_blender(file_path)
        else:
            raise NotImplementedError
       
    def __export_blend_blender(self, file_path):

        bpy.ops.wm.save_as_mainfile(filepath=file_path)
     
    def export_csv(self, file_path):
        """Exports the PPM as a CSV file.

        Parameters
        ----------
        file_path : str
            Path to the CSV file.
        """

        export_dict = self.get_parameter_dict()

        with open(file_path, 'w', newline='') as csvfile:
            for key, value in export_dict.items():
                csvfile.write(f'{key},{value:e}\n')


    def render(self, *args, **kwargs):
        """Renders the PPM.

        Parameters
        ----------
        file_path : str
            Path to the rendered image.
        file_name : str
            Name of the rendered image.
        camera_location : list
            Location of the camera. Default: [-10, 170, 5]
            If str not given the unit will be infered from the unit of the PPM.
        camera_rotation : list
            Rotation of the camera. Default: [90, 0, 180]
        camera_location_reference : list or None
            Location of the reference camera.
        light_location : list
            Location of the light source in global coordinates. Default: [-0.01, 0.15, 0.1]
        light_rotation : list
            Rotation of the light source in Euler angles ('XYZ'). Default: [0, 0, 0]
        light_power : float
            Power of the light source in Watts. Default: 200000
        light_type : str
            Type of the light source. Default: 'AREA'. 
            Currently, only 'AREA' is supported.
        light_shape : str
            Shape of the light source. Can be one of 'SQUARE', 'RECTANGLE', 'DISC' or 'ELLIPSE'. Default: 'SQUARE'
        light_size : list
            Dimensions for the SQUARE or RECTANGLE. Default: [0.1, 0.1]
        depth_farthest : float
            Farthest depth value. Default is 1.25 times the radius of the camera.
        depth_nearest : float
            Farthest depth value. Default 0.
        resolution : int
            Resolution of the rendered image. Default: 256
        depth : bool
            Whether to render the depth map. Default: False
        smooth_shading : bool
            Whether to render the image with smooth shading. Default: True
        image_compression : int
            Compression of the rendered image. Default: 0
        image_color_depth : str
            Color depth of the rendered image. Default: '8'
        depth_codec_exr : str
            Codec of the depth map. Default: 'NONE'
        depth_color_depth_exr : str
            Color depth of the depth map. Default: '16'
        depth_compression_exr : int
            Compression of the depth map. Default: 0
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

            if 'camera_location' not in kwargs.keys():
                kwargs['camera_location'] = [-0.010, 0.170, 0.005]

            if 'camera_location_reference' not in kwargs.keys():
                kwargs['camera_location_reference'] = None

            if 'depth_farthest' not in kwargs.keys():
                kwargs['depth_farthest'] = 1.25 * np.sqrt(kwargs['camera_location'][0]**2 + kwargs['camera_location'][1]**2 + kwargs['camera_location'][2]**2)

            if 'depth_nearest' not in kwargs.keys():
                kwargs['depth_nearest'] = 0

            if 'camera_rotation' not in kwargs.keys():
                kwargs['camera_rotation'] = [90, 0, 180]

            if 'light_type' not in kwargs.keys():
                kwargs['light_type'] = 'AREA'

            if kwargs['light_type'] != 'AREA':
                raise NotImplementedError
            
            if 'light_shape' not in kwargs.keys():
                kwargs['light_shape'] = 'SQUARE'

            if 'light_location' not in kwargs.keys():
                kwargs['light_location'] = np.array([-0.01, 0.15, 0.1]) * 1000
            else:
                kwargs['light_location'] = np.array(kwargs['light_location']) * 1000

            if 'light_rotation' not in kwargs.keys():
                kwargs['light_rotation'] = [0, 0, 0]

            if 'light_power' not in kwargs.keys():
                kwargs['light_power'] = 200000

            render(
                file_path = kwargs['file_path'],
                file_name = kwargs['file_name'],
                resolution = kwargs['resolution'] if 'resolution' in kwargs else 256,
                depth = kwargs['depth'] if 'depth' in kwargs else False,
                smooth_shading = kwargs['smooth_shading'] if 'smooth_shading' in kwargs else True,
                image_compression = kwargs['image_compression'] if 'image_compression' in kwargs else 0,
                image_color_depth = kwargs['image_color_depth'] if 'image_color_depth' in kwargs else '8',
                camera_location = kwargs['camera_location'],
                camera_rotation = kwargs['camera_rotation'],
                camera_location_reference = kwargs['camera_location_reference'],
                light_location = kwargs['light_location'],
                light_rotation = kwargs['light_rotation'],
                light_power = kwargs['light_power'],
                light_type = kwargs['light_type'],
                light_shape = kwargs['light_shape'],
                depth_farthest = kwargs['depth_farthest'],
                depth_nearest = kwargs['depth_nearest'] if 'depth_nearest' in kwargs else 'camera_location',
                depth_codec_exr = kwargs['depth_codec_exr'] if 'depth_codec_exr' in kwargs else 'NONE',
                depth_color_depth_exr = kwargs['depth_color_depth_exr'] if 'depth_color_depth_exr' in kwargs else '16',
                depth_compression_exr = kwargs['depth_compression_exr'] if 'depth_compression_exr' in kwargs else 0
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
        local_bounding_box_center = 1/8 * sum((mathutils.Vector(b) for b in obj.bound_box), mathutils.Vector())

        # convert to world coordinates
        center_of_mass = obj.matrix_world @ local_bounding_box_center

        return center_of_mass