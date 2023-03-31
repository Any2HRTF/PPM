import os
import sys
import io
import uuid
import math
from contextlib import redirect_stdout
import shutil
import numpy as np
import cv2
from pyntcloud import PyntCloud
import bpy
import mathutils
os.environ["OPENCV_IO_ENABLE_OPENEXR"]="1"

class Bone():
    r"""Bone class.
    
    Args:
        name (str): Name of the bone.
        blender_object : blender object.
    """

    def __init__(self, name, blender_object):

        self.name = name
        blender_object.bones.append(self)
        blender_object.bones_lookup[self.name] = self


    def rotation(self, point, axis, val):
        r"""Rotate bone."""

        if axis == 'W':
            axis_idx = 0
        elif axis == 'X':
            axis_idx = 1
        elif axis == 'Y':
            axis_idx = 2
        elif axis == 'Z':
            axis_idx = 3
        else:
            axis_idx = "error"

        bpy.data.objects["Armature"].pose.bones[self.name + \
            "-" + point].rotation_quaternion[axis_idx] = float(val)

    def location(self, point, axis, val):
        r"""Move bone."""

        if axis == 'X':
            axis_idx = 0
        elif axis == 'Y':
            axis_idx = 1
        elif axis == 'Z':
            axis_idx = 2
        else:
            axis_idx = "error"

        bpy.data.objects["Armature"].pose.bones[self.name + \
            "-" + point].location[axis_idx] = float(val)

    def scaling(self, point, axis, val):
        r"""Scale bone."""

        if axis == 'X':
            axis_idx = 0
        elif axis == 'Y':
            axis_idx = 1
        elif axis == 'Z':
            axis_idx = 2
        else:
            axis_idx = "error"

        bpy.data.objects["Armature"].pose.bones[self.name \
            + "-" + point].scale[axis_idx] = float(val)

class BaseBlenderObject():
    r"""BaseBlenderObject class.

    Args:
        name (str): Name of the BaseBlenderObject instance.
    """

    def __init__(self, blender_tmp_dir, name="default") -> None:

        self.name = name

        self.blender_tmp_dir = blender_tmp_dir

        if not os.path.exists(self.blender_tmp_dir):
            os.makedirs(self.blender_tmp_dir)


        self.old = os.dup(sys.stdout.fileno())

        self.logfile = self.blender_tmp_dir + '/blender_render.log'
        with open(self.logfile, 'w', encoding="utf8") as _:
            pass

        self.log_file_d = None


    def __del__(self):
        if os.path.exists(self.blender_tmp_dir):
            shutil.rmtree(self.blender_tmp_dir)

    def _load_blender_file(self, path_to_file, selection):

        self.old = os.dup(sys.stdout.fileno())
        sys.stdout.flush()
        os.close(sys.stdout.fileno())
        self.log_file_d = os.open(self.logfile, os.O_WRONLY)

        bpy.ops.wm.open_mainfile(filepath=path_to_file)
        
        bpy.ops.object.select_all(action='DESELECT')
        for obj in bpy.data.objects:
            obj.hide_render = True
        bpy.data.objects[selection].hide_render = False
        bpy.data.objects[selection].select_set(True)

        # disable output redirection
        os.close(self.log_file_d)
        os.dup(self.old)
        os.close(self.old)

    def _modifiers(self, selection:str, state: bool):
        """Enable or disable modifiers"""

        bpy.data.objects[selection].modifiers["DataTransfer"].show_render = state
        bpy.data.objects[selection].modifiers["DataTransfer"].show_viewport = state
        bpy.data.objects[selection].modifiers["DataTransfer"].show_in_editmode = state
        bpy.data.objects[selection].modifiers["DataTransfer"].show_on_cage = state
        bpy.data.objects[selection].modifiers["Decimate"].show_render = state
        bpy.data.objects[selection].modifiers["Decimate"].show_viewport = state
    
    def __select(self, label, action):
        """Select object in blender"""
        if action:
            bpy.ops.object.select_all(action='DESELECT')
            for obj in bpy.data.objects:
                obj.hide_render = True
            bpy.data.objects[label].hide_render = False
            bpy.data.objects["Area"].hide_render = False
            bpy.data.objects["Armature"].hide_render = False
            bpy.data.objects[label].select_set(True)
            bpy.context.view_layer.objects.active = bpy.data.objects[label]
        else:
            bpy.data.objects[label].select_set(False)
            bpy.ops.object.select_all(action='DESELECT')


    def _get_pc(self, selection: str) -> np.ndarray:
        """Get point cloud from blender"""

        cloud = PyntCloud.from_file(self._export_pc(selection))
        cloud = cloud.points.values


        return cloud.astype(np.float32)

    def _export_pc(self, selection: str, target_file_ply=None):
        """Export point cloud from blender"""

        if target_file_ply is None:
            target_file_ply = self.blender_tmp_dir + f'/pc_{str(uuid.uuid4())}.ply'
        self.__select(selection, True)
        with redirect_stdout(io.StringIO()):
            bpy.ops.export_mesh.ply(
                filepath=target_file_ply,
                use_selection=True,
                use_normals=False,
                use_uv_coords=False,
                use_colors=False
            )
        self.__select(selection, False)

        return target_file_ply

    def _export_mesh(self, selection: str, target_file_stl=None):
        r"""Export mesh from blender"""

        if target_file_stl is None:
            target_file_stl = self.blender_tmp_dir + f'/mesh_{str(uuid.uuid4())}.stl'
        self.__select(selection, True)
        with redirect_stdout(io.StringIO()):
            bpy.ops.export_mesh.stl(
                filepath=target_file_stl,
                use_selection=True,
                use_scene_unit=True
            )
        self.__select(selection, False)

        return target_file_stl

    def _get_image(self, path_to_img, img_size=256):
        r"""Get image"""

        # read in using cv2
        img = cv2.imread(path_to_img, 0)

        img = cv2.normalize(img, None, 0, 255, cv2.NORM_MINMAX, cv2.CV_8U)
        img = cv2.resize(img, (img_size, img_size))

        return img

    def _get_depth(self, path_to_depth, img_size=256):
        r"""Get depth image"""

        depth = cv2.imread(path_to_depth, cv2.IMREAD_ANYCOLOR | cv2.IMREAD_ANYDEPTH)

        # Convert to 8-bit and grayscale
        depth = cv2.normalize(depth, None, 0, 255, cv2.NORM_MINMAX, dtype=cv2.CV_8U)
        depth = cv2.resize(depth, (img_size, img_size))
        depth = cv2.cvtColor(depth, cv2.COLOR_BGR2GRAY)

        return depth

    def _render(
        self, resolution: int=256, depth: bool=True,
        shade_smooth: bool=True, image_comp: int=0,
        image_col_dep='8', cam_loc:tuple=(-10,200,5),
        cam_rot:tuple=(90, 0, 180), cam_loc_ref:tuple=None,
        depth_farthest=0,depth_nearest='cam_loc',
        depth_codec_exr='NONE', depth_col_dep_exr='16',
        depth_comp_exr=8) -> tuple:
        """Render image from blender"""
        render_id = f'{str(uuid.uuid4())}'

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
        bpy.context.scene.render.filepath = self.blender_tmp_dir + f'/img_{render_id}'

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
            file_output_exr_depth.base_path = self.blender_tmp_dir
            file_output_exr_depth.format.file_format = "OPEN_EXR"
            file_output_exr_depth.file_slots[0].path = f"depth_{render_id}." +\
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
        file_output_png.base_path = self.blender_tmp_dir
        file_output_png.format.file_format = "PNG"
        file_output_png.file_slots[0].path = f'/img_{render_id}'
        file_output_png.format.color_depth = image_col_dep
        file_output_png.format.compression = int(image_comp)

        # Link denoise-node output with compositor-output node (png)
        links.new(denoise.outputs['Image'], file_output_png.inputs['Image'])



        self.old = os.dup(sys.stdout.fileno())
        sys.stdout.flush()
        os.close(sys.stdout.fileno())
        self.log_file_d = os.open(self.logfile, os.O_WRONLY)


        # Render!
        bpy.ops.render.render()


        # disable output redirection
        os.close(self.log_file_d)
        os.dup(self.old)
        os.close(self.old)


        # rename current files by removing automatically appended frame index
        if depth:

            for file in os.listdir(self.blender_tmp_dir ):
                if file.startswith(f'depth_{render_id}'):
                    os.rename(self.blender_tmp_dir + f'/{file}', \
                        self.blender_tmp_dir + f'/depth_{render_id}.exr')
                    break

        for file in os.listdir(self.blender_tmp_dir ):
            if file.startswith(f'img_{render_id}'):
                os.rename(self.blender_tmp_dir + f'/{file}', \
                    self.blender_tmp_dir + f'/img_{render_id}.png')
                break

        bpy.context.scene.render.use_compositing = False

        if depth:
            return self.blender_tmp_dir + f'/img_{render_id}.png', \
                self.blender_tmp_dir + f'/depth_{render_id}.exr'
        else:
            return self.blender_tmp_dir + f'/img_{render_id}.png', None
