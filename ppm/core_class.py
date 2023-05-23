import os
import io
import csv
import numpy as np
from contextlib import redirect_stdout


import bpy
import bmesh

CURRENT_DIR = os.path.dirname(os.path.realpath(__file__))


class PPM():
    """PPM class

    Parameters:
    -----------
        from_blender_file (str): Path to a blender file to load the PPM from; if None, the standard PPM is loaded
        from_csv_file (str): Path to a csv file to load the PPM parameters from; if None, the standard PPM is loaded
    """
    def __init__(self, from_blender_file=None, from_csv_file=None, backend='blender'):

        if from_blender_file is not None and from_csv_file is not None:
            raise Exception('Either load from blender file or from csv file.')

        self.backend = backend

        # load init parameters
        self.__parameters = self.__load_parameters_from_csv()

        if self.backend is 'blender':
            if from_blender_file is not None:
                if self.backend is not 'blender':
                    raise Exception('Blender backend not selected.')
                bpy.ops.wm.open_mainfile(filepath=from_blender_file)
            else:
                bpy.ops.wm.open_mainfile(filepath=f'{CURRENT_DIR}/resources/PPM_modified_v1.blend')
            self.__get_parameters_from_blender()
        
        # rerun fct to load parameters from csv file
        if from_csv_file is not None:
            self.__parameters = self.__load_parameters_from_csv(from_csv_file)

    def __load_parameters_from_csv(self, csv_file=None) -> dict:

        if csv_file is None:
            csv_file = f'{CURRENT_DIR}/resources/PPM_params_default_v1.csv'

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
                    if 'Size' in row[0]:
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
                if point is not None:
                    if point not in parameters[name]:
                        parameters[name][point] = {}
                    if axis is not None:
                        if type not in parameters[name][point]:
                            parameters[name][point][type] = {}
                        parameters[name][point][type][axis] = value
                    else:
                        parameters[name][point][type] = value
                else:
                    if axis is not None:
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
        obj = bpy.data.objects["Armature"]

        for parameter_name, parameter in self.__parameters.items():
            # shape keys
            if 'Shape_key' in parameter.keys():
                bpy.data.shape_keys['Key.002'].key_blocks[parameter_name].value = self.__parameters[parameter_name]['Shape_key']
            else:
                for point_name, point in parameter.items():
                    # scale
                    if 'Scale' in point.keys():
                        if 'Size' in parameter_name:
                            for axis, axis_value in point['Scale'].items():
                                obj.pose.bones[parameter_name + "-" + point_name].scale[
                                        0 if axis == 'X' else 
                                        1 if axis == 'Y' else 
                                        2 if axis == 'Z' else 
                                        None] = axis_value
                                    
                        else:
                            obj.pose.bones[parameter_name + "-" + point_name].scale[0] = self.__parameters[parameter_name][point_name]['Scale']
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
                self.__parameters[parameter_name]['Shape_key'] = bpy.data.shape_keys['Key.002'].key_blocks[parameter_name].value
            else:
                for point_name, point in parameter.items():
                    # scale
                    if 'Scale' in point.keys():
                        if 'Size' in parameter_name:
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

    def __export_ply_blender(self, file_path):

        bpy.ops.object.select_all(action='DESELECT')
        bpy.data.objects['ARI_PPM_v1'].select_set(True)
        # bpy.context.view_layer.objects.active = bpy.data.objects['ARI_PPM_v1']

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
        if self.backend == 'blender':
            self.__set_parameters_in_blender()
            self.__export_ply_blender(file_path)
        else:
            raise NotImplementedError

    def __export_stl_blender(self, file_path):

        bpy.ops.object.select_all(action='DESELECT')
        bpy.data.objects['ARI_PPM_v1'].select_set(True)

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
        if self.backend == 'blender':
            self.__set_parameters_in_blender()
            self.__export_stl_blender(file_path)
        else:
            raise NotImplementedError
        
    def export_csv(self, file_path):
        """Exports the PPM as a CSV file.

        Parameters
        ----------
        file_path : str
            Path to the CSV file.
        """

        self.__set_parameters_in_blender()

        export_dict = {}

        for parameter_name, parameter in self.__parameters.items():
            # shape keys
            if 'Shape_key' in parameter.keys():
                export_dict[f'Shape_key_{parameter_name}'] = self.__parameters[parameter_name]['Shape_key']
            else:
                for point_name, point in parameter.items():
                    # scale
                    if 'Scale' in point.keys():
                        if 'Size' in parameter_name:
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
        
        with open(file_path, 'w', newline='') as csvfile:
            for key, value in export_dict.items():
                csvfile.write(f'{key},{value}\n')
