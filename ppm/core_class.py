import os
import io
import csv
import numpy as np
from contextlib import redirect_stdout

import bpy
import bmesh
import mathutils
import math

CURRENT_DIR = os.path.dirname(os.path.realpath(__file__))

class PPM():
    """PPM class

    Parameters:
    -----------
        from_blender_file (str): Path to a blender file to load the PPM from; if None, the standard PPM is loaded
        from_csv_file (str): Path to a csv file to load the PPM parameters from; if None, the standard PPM is loaded
    """
    def __init__(self, from_blender_file=None, from_csv_file=None, backend='blender'):

        if from_blender_file != None and from_csv_file != None:
            raise Exception('Either load from blender file or from csv file.')
        
        if backend != 'blender' and from_blender_file != None:
            raise Exception('Blender backend not selected.')

        self.backend = backend

        # load init parameters
        self.__parameters = self.__load_parameters_from_csv()

        if self.backend == 'blender':
            if from_blender_file != None:
                with redirect_stdout(io.StringIO()):
                    bpy.ops.wm.open_mainfile(filepath=from_blender_file)
            else:
                with redirect_stdout(io.StringIO()):
                    bpy.ops.wm.open_mainfile(filepath=f'{CURRENT_DIR}/resources/PPM_modified_v1.blend')
            self.__get_parameters_from_blender()
        
        # rerun fct to load parameters from csv file
        if from_csv_file != None:
            self.__parameters = self.__load_parameters_from_csv(from_csv_file)

    @property
    def points(self):
        return self.get_point_cloud()

    @property
    def parameters(self):
        return self.__parameters
    
    @parameters.setter
    def parameters(self, parameters):
        for parameter_name, parameter in parameters.items():
            for point_name, point in parameter.items():
                if point_name == 'Shape_key':
                    self.__parameters[parameter_name][point_name] = point
                else:
                    for type_name, type in point.items():
                        if type_name == 'Scale' and parameter_name != 'Size':
                            self.__parameters[parameter_name][point_name][type_name] = type
                        else:
                            for axis_name, axis in type.items():
                                self.__parameters[parameter_name][point_name][type_name][axis_name] = axis

    def set_parameter(self, parameter, point, type, axis, value):
        if point == 'Shape_key':
            self.__parameters[parameter][point] = value
        elif type == 'Scale' and parameter != 'Size':
            self.__parameters[parameter][point][type] = value
        else:
            self.__parameters[parameter][point][type][axis] = value

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

    def __render_blender(self,
                         file_path,
                         filename,
                         resolution: int=256,
                         depth: bool=True,
                         shade_smooth: bool=True,
                         image_comp: int=0,
                         image_col_dep='8',
                         cam_loc:tuple=(-10,200,5),
                         cam_rot:tuple=(90, 0, 180),
                         cam_loc_ref:tuple=None,
                         depth_farthest=0,
                         depth_nearest='cam_loc',
                         depth_codec_exr='NONE',
                         depth_col_dep_exr='16',
                         depth_comp_exr=8):

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
        with redirect_stdout(io.StringIO()):
            bpy.ops.render.render()


    def render(self, file_path, filename):
        """Renders the PPM.

        Parameters
        ----------
        file_path : str
            Path to the rendered image.
        """
        if self.backend == 'blender':
            self.__set_parameters_in_blender()
            self.__render_blender(file_path, filename)
        else:
            raise NotImplementedError
