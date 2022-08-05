# Python script to set the parameters values of the parametric pinna model (PPM)  
# contained in a Blender file
# 
# This script is part of the Matlab/Python PPM interface. Please refer to the respective
# Matlab-function descriptions for further information on its use. 
#
# Related Python function:
# get_values_and_export_mesh_v1_4_0.py
#
# Related Matlab functions:
# ppm_demo, ppm_get_values, ppm_set_values
#
# Versions and contributors:
# PPM interface 0.8 and above: Florian Pausch (2022)
# PPM interface 0.7 and below: Oscar Jones (2021)

print("Blender loaded")

import sys
import os
import glob
import io
from contextlib import redirect_stdout
import bpy
import math
import mathutils
import numpy as np

stdout = io.StringIO()

argv = sys.argv

arg_path = argv[argv.index("--") + 1]
arg_pc = argv[argv.index("--") + 2]
arg_mesh = argv[argv.index("--") + 3]
arg_remesh = argv[argv.index("--") + 4]
arg_image = argv[argv.index("--") + 5]
arg_res = argv[argv.index("--") + 6]
arg_image_col_dep = argv[argv.index("--") + 7]
arg_image_comp = argv[argv.index("--") + 8]
arg_cam = argv[argv.index("--") + 9]

arg_depth = argv[argv.index("--") + 10]
arg_depth_col_dep_exr = argv[argv.index("--") + 11]
arg_depth_comp_exr = argv[argv.index("--") + 12]
arg_depth_codec_exr = argv[argv.index("--") + 13]

arg_depth_col_dep_png = argv[argv.index("--") + 14]
arg_depth_comp_png = argv[argv.index("--") + 15]

arg_depth_nearest = argv[argv.index("--") + 16]
arg_depth_farthest = argv[argv.index("--") + 17]

def select(label, action):
    if action:
        bpy.ops.object.select_all(action='DESELECT')
        bpy.data.objects[label].select_set(True)
        bpy.context.view_layer.objects.active = bpy.data.objects[label]
    else:
        bpy.data.objects[label].select_set(False)
        bpy.ops.object.select_all(action='DESELECT')


def setDir(folder, file, extension):
    target_file = os.path.join(folder, '{}.{}'.format(file, extension))
    return target_file


class Bone():

    def __init__(self, name, ear):

        self.name = name
        ear.bones.append(self)
        ear.bonesLookup[self.name] = self

    def rotation(self, point, axis, val):

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

        bpy.data.objects["Armature"].pose.bones[self.name + "-" + point].rotation_quaternion[axis_idx] = float(val)

    def location(self, point, axis, val):

        if axis == 'X':
            axis_idx = 0
        elif axis == 'Y':
            axis_idx = 1
        elif axis == 'Z':
            axis_idx = 2
        else:
            axis_idx = "error"

        bpy.data.objects["Armature"].pose.bones[self.name + "-" + point].location[axis_idx] = float(val)

    def scaling(self, point, axis, val):

        if axis == 'X':
            axis_idx = 0
        elif axis == 'Y':
            axis_idx = 1
        elif axis == 'Z':
            axis_idx = 2
        else:
            axis_idx = "error"

        bpy.data.objects["Armature"].pose.bones[self.name + "-" + point].scale[axis_idx] = float(val)

          
class Ear():

    def __init__(self, name):

        self.name = name
        self.path = str(arg_path)
        self.bones = []
        self.bonesLookup = {}

    def modifiers(self, state):
        if arg_remesh == 'TRUE':
            bpy.data.objects["ARI_PPM_v1"].modifiers["DataTransfer"].show_render = state
            bpy.data.objects["ARI_PPM_v1"].modifiers["DataTransfer"].show_viewport = state
            bpy.data.objects["ARI_PPM_v1"].modifiers["DataTransfer"].show_in_editmode = state
            bpy.data.objects["ARI_PPM_v1"].modifiers["DataTransfer"].show_on_cage = state
            bpy.data.objects["ARI_PPM_v1"].modifiers["Decimate"].show_render = state
            bpy.data.objects["ARI_PPM_v1"].modifiers["Decimate"].show_viewport = state

    def shapeKey(self, name, val):
        bpy.data.shape_keys["Key.002"].key_blocks[name].value = float(val)

    def export_pc(self, name):

        if name.find('_cam')==(-1) or name!='blender_bones_data':
            target_file_ply = setDir(self.path, name, "ply")
            select('ARI_PPM_v1', True)
            with redirect_stdout(stdout):
                bpy.ops.export_mesh.ply(filepath=target_file_ply, use_selection=True, use_normals=False, use_uv_coords=False, use_colors=False)
            select('ARI_PPM_v1', False)

    def export_mesh(self, name):

        if name.find('_cam')==(-1) or name!='blender_bones_data':
            target_file_stl = setDir(self.path, name, "stl")
            select('ARI_PPM_v1', True)
            with redirect_stdout(stdout):
                bpy.ops.export_mesh.stl(filepath=target_file_stl, use_selection=True, use_scene_unit=True)
            select('ARI_PPM_v1', False)
    
    def render(self, name):

        # Scene-render settings
        bpy.context.scene.render.engine = 'CYCLES' # CYCLES, BLENDER_EEVEE, WORKBENCH
        bpy.context.view_layer.cycles.denoising_store_passes = True

        cam = bpy.data.objects['Camera']
        cam.rotation_mode = 'XYZ'
        bpy.context.scene.camera = cam   

        if arg_cam=='TRUE' and name.find('_cam')==(-1):
      
            cam_file = setDir(self.path, name + '_cam', 'txt')
            with open(cam_file,'r') as cam_pose:
                for idx, line in enumerate(cam_pose):
                    if idx == 0:
                        cam_loc = line
                    elif idx == 1:
                        cam_rot = line
                    else:
                        cam_loc_ref = line
            
            cam_loc = cam_loc.split(',')
            cam_loc[-1] = cam_loc[-1].strip()
            cam_loc = np.asarray(cam_loc)

            cam.location = mathutils.Vector((float(cam_loc[0]),
                                             float(cam_loc[1]),
                                             float(cam_loc[2])))
            bpy.context.view_layer.update()

            if 'cam_loc_ref' not in locals(): # apply custom camera rotation
                cam_rot = cam_rot.split(',')
                cam_rot[-1] = cam_rot[-1].strip()
                cam_rot = np.asarray(cam_rot)

                cam.rotation_euler = mathutils.Euler((math.radians(float(cam_rot[0])),
                                                      math.radians(float(cam_rot[1])),
                                                      math.radians(float(cam_rot[2]))), cam.rotation_mode)
            
            else: # rotate camera to point at cam_loc_ref
                cam_loc_ref = cam_loc_ref.split(',')
                cam_loc_ref[-1] = cam_loc_ref[-1].strip()
                cam_loc_ref = np.asarray(cam_loc_ref)

                cam_loc_mtx = cam.matrix_world.to_translation()
                cam_rot = mathutils.Vector((float(cam_loc_ref[0]),
                                            float(cam_loc_ref[1]),
                                            float(cam_loc_ref[2]))) - cam_loc_mtx

                cam_rot_quat = cam_rot.to_track_quat('-Z','Y')

                cam.rotation_euler = cam_rot_quat.to_euler()
            
        else: # set default camera pose
            cam.location = mathutils.Vector((-10, 200, 5))
            cam.rotation_euler = mathutils.Euler((math.pi/2, 0, math.pi), cam.rotation_mode)

        bpy.context.view_layer.update()

        # render image and depth information, and store as png and exr files
        if arg_depth=='TRUE' or arg_image=='TRUE' and name.find('_cam')==(-1) and name!='blender_bones_data':

            bpy.context.scene.render.use_compositing = True
            bpy.context.scene.render.filepath = setDir(self.path, name, "png")
            
            bpy.data.scenes["Scene"].render.resolution_x = int(arg_res)
            bpy.data.scenes["Scene"].render.resolution_y = int(arg_res)
            bpy.data.scenes["Scene"].render.image_settings.color_depth = arg_image_col_dep
            bpy.data.scenes["Scene"].render.image_settings.compression = int(arg_image_comp)
            
            # Enable nodes
            bpy.context.scene.use_nodes = True

            tree = bpy.context.scene.node_tree
            links = tree.links

            # Clear default nodes
            for n in tree.nodes:
                tree.nodes.remove(n)

            # Create render-layers node
            render_layer = tree.nodes.new(type='CompositorNodeRLayers')

            # Create denoising node
            denoise = tree.nodes.new(type='CompositorNodeDenoise')

            if arg_depth=='TRUE':
                # Create map-range node
                map = tree.nodes.new(type='CompositorNodeMapRange')
                               
                if arg_depth_farthest=='0': #default
                    map.inputs[1].default_value = 0 # map minimum in Blender units
                else:
                    map.inputs[1].default_value = float(arg_depth_farthest) # map minimum in Blender units

                if arg_depth_nearest=='cam_loc': # default
                    # Set map maximum to Euclidian distance of camera to origin
                    cam = bpy.data.objects['Camera']
                    dist_l2 = math.sqrt(cam.location.x**2 + cam.location.y**2 + cam.location.z**2)
                    map.inputs[2].default_value = dist_l2 # map maximum in Blender units
                else:
                    map.inputs[2].default_value = float(arg_depth_nearest) # map maximum in Blender units

                # Map values between 1 (white) and zero (black)
                map.inputs[3].default_value = 1 # map minimum in normalised units (linear steps when using OPEN_EXR)
                map.inputs[4].default_value = 0 # map minimum in normalised units (linear steps when using OPEN_EXR)

                # Link output of render-layers node to input of map node (exr depth)
                links.new(render_layer.outputs['Depth'], map.inputs['Value'])

                # Create a file-output node, set the path, and file format (exr depth)
                fileOutput = tree.nodes.new(type='CompositorNodeOutputFile')
                fileOutput.base_path = self.path
                fileOutput.format.file_format = "OPEN_EXR"
                fileOutput.file_slots[0].path = name + "_depth." + fileOutput.format.file_format # file name with appended frame idx
                fileOutput.format.color_depth = arg_depth_col_dep_exr
                fileOutput.format.compression = int(arg_depth_comp_exr)
                fileOutput.format.exr_codec = arg_depth_codec_exr # [‘NONE’, ‘PXR24’, ‘ZIP’, ‘PIZ’, ‘RLE’, ‘ZIPS’, ‘B44’, ‘B44A’, ‘DWAA’, ‘DWAB’], default ‘NONE’

                # Link output of map node to input of compositor-output node (exr depth)
                links.new(map.outputs['Value'], fileOutput.inputs['Image'])

                # Create a file-output node, set the path, and file format (png depth)
                fileOutput_png_depth = tree.nodes.new(type='CompositorNodeOutputFile')
                fileOutput_png_depth.base_path = self.path
                fileOutput_png_depth.format.file_format = "PNG"
                fileOutput_png_depth.file_slots[0].path = name + "_depth." + fileOutput_png_depth.format.file_format # file name with appended frame idx
                fileOutput_png_depth.format.color_depth = arg_depth_col_dep_png
                fileOutput_png_depth.format.compression = int(arg_depth_comp_png)

                # Link output of map node to input of compositor-output node (png depth)
                links.new(map.outputs['Value'], fileOutput_png_depth.inputs['Image'])

            # Link noisy-image / denoising-normal / denoising-albedo outputs render-layer node 
            # with input of denoising node (png)
            links.new(render_layer.outputs['Image'], denoise.inputs['Image'])
            links.new(render_layer.outputs['Denoising Normal'], denoise.inputs['Normal'])
            links.new(render_layer.outputs['Denoising Albedo'], denoise.inputs['Albedo'])

            # Create a file-output node, set the path, and file format (png)
            fileOutput_png = tree.nodes.new(type='CompositorNodeOutputFile')
            fileOutput_png.base_path = self.path
            fileOutput_png.format.file_format = "PNG"
            fileOutput_png.file_slots[0].path = name + fileOutput_png.format.file_format # file name with appended frame idx
            fileOutput_png.format.color_depth = arg_image_col_dep
            fileOutput_png.format.compression = int(arg_image_comp)

            # Link denoise-node output with compositor-output node (png)
            links.new(denoise.outputs['Image'], fileOutput_png.inputs['Image'])

            # Render!
            bpy.ops.render.render(write_still=True)

            # Remove previous results with same file name and extension
            if arg_depth=='TRUE':
                if (os.path.exists(setDir(self.path, name + "_depth","EXR"))):
                    os.remove(setDir(self.path, name + "_depth", "exr"))

                if (os.path.exists(setDir(self.path, name + "_depth", fileOutput_png_depth.format.file_format))):
                    os.remove(setDir(self.path, name + "_depth", fileOutput_png_depth.format.file_format))

            if (os.path.exists(setDir(self.path, name, fileOutput_png.format.file_format))):
                os.remove(setDir(self.path, name, fileOutput_png.format.file_format))

            # rename current files by removing automatically appended frame index
            if arg_depth=='TRUE':
                if (os.path.exists(setDir(self.path, name + "_depth." + fileOutput.format.file_format 
                    + "0000", "exr"))):
                    os.rename(setDir(self.path, name + "_depth." + fileOutput.format.file_format 
                        + "0000", "exr"), setDir(self.path, name + "_depth", "exr"))

                if (os.path.exists(setDir(self.path, name + "_depth." + fileOutput_png_depth.format.file_format 
                    + "0000", "png"))):
                    os.rename(setDir(self.path, name + "_depth." + fileOutput_png_depth.format.file_format
                        + "0000",fileOutput_png_depth.format.file_format), 
                        setDir(self.path, name + "_depth", "png"))

            if (os.path.exists(setDir(self.path, name + fileOutput_png.format.file_format 
                + "0000", "png"))):
                os.rename(setDir(self.path, name + fileOutput_png.format.file_format
                    + "0000",fileOutput_png.format.file_format), 
                    setDir(self.path, name, "png"))

            bpy.context.scene.render.use_compositing = False


    def reset(self, name):

        target_file = setDir(self.path, name, "txt")
        file = open(target_file, 'r')
        lines = file.readlines()
        lines.reverse()

        for line in lines:
            transform = line.split(',')[0]

            if transform == "Rotation":
                self.bonesLookup[line.split(',')[1].split('-')[0]].rotation(line.split(',')[1].split('-')[1],
                                                                          line.split(',')[2], 0)
            elif transform == "Location":
                self.bonesLookup[line.split(',')[1].split('-')[0]].location(line.split(',')[1].split('-')[1],
                                                                             line.split(',')[2], 0)
            elif transform == "Scale":
                self.bonesLookup[line.split(',')[1].split('-')[0]].scaling(line.split(',')[1].split('-')[1],
                                                                           line.split(',')[2], 0)
            elif transform == "Shape_key":
                self.shapeKey(line.split(',')[1], 0)

            else:
                print("Reset: skipped line")
                pass

    def load(self, name):

        target_file = setDir(self.path, name, "txt")
        file = open(target_file, 'r')
        lines = file.readlines()
        for line in lines:

            transform = line.split(',')[0]

            if transform == "Rotation":
                self.bonesLookup[line.split(',')[1].split('-')[0]].rotation(line.split(',')[1].split('-')[1],
                                                                          line.split(',')[2], line.split(',')[3])
            elif transform == "Location":
                self.bonesLookup[line.split(',')[1].split('-')[0]].location(line.split(',')[1].split('-')[1],
                                                                             line.split(',')[2], line.split(',')[3])
            elif transform == "Scale":
                self.bonesLookup[line.split(',')[1].split('-')[0]].scaling(line.split(',')[1].split('-')[1],
                                                                           line.split(',')[2], line.split(',')[3])
            elif transform == "Shape_key":
                self.shapeKey(line.split(',')[1], line.split(',')[3])
                
            else:
                print("Reset: skipped line")
                pass

    def loadAll(self):
        #print("Locating instructions... ", end="", flush=True)
        os.chdir(self.path)
        #print("Done")
        #print("Loaded Instructions from {}".format(self.path))
        #print("Exporting to {}".format(self.path))
        for file in glob.glob("*.txt"):

            name = file.split('.')[0]
            #print("Ear {}... ".format(name), end="", flush=True)

            logfile = 'blender_render.log'
            open(logfile, 'a').close()
            old = os.dup(1)
            sys.stdout.flush()
            os.close(1)
            os.open(logfile, os.O_WRONLY)

            if name.find('_cam')==(-1) and name!='blender_bones_data':
                self.load(name)
                self.modifiers(True)
                if arg_pc == 'TRUE':
                    self.export_pc(name)
                if arg_mesh == 'TRUE':
                    self.export_mesh(name)
                if arg_image == 'TRUE':
                    self.render(name)
                self.modifiers(False)
                self.reset(name)

            os.close(1)
            os.dup(old)
            os.close(old)

Ear = Ear("Ear")

Lobulus = Bone("Lobulus", Ear)
Helix_low = Bone("Helix_low", Ear)
Helix_middle = Bone("Helix_middle", Ear)
Helix_up = Bone("Helix_up", Ear)
Tragus = Bone("Tragus", Ear)
Antitragus = Bone("Antitragus", Ear)
Antihelix = Bone("Antihelix", Ear)
Crus_inferius_anthelicis = Bone("Crus_inferius_anthelicis", Ear)
Crus_superius_anthelicis = Bone("Crus_superius_anthelicis", Ear)
Size = Bone("Size", Ear)

Ear.loadAll()