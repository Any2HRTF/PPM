# Python script to get the parameters values of the parametric pinna model (PPM)  
# contained in a Blender file
# 
# This script is part of the Matlab/Python PPM interface. Please refer to the respective
# Matlab-function descriptions for further information on its use. 
#
# Related Python function:
# set_values_and_export_mesh_v1_5_0.py
#
# Related Matlab functions:
# ppm_demo, ppm_get_values, ppm_set_values
#
# Versions and contributors:
# PPM interface 0.8 and above: Florian Pausch (2022)
# PPM interface 0.7 and below: Oscar Jones (2021)

import bpy
import sys
import os
import io
import glob
from contextlib import redirect_stdout

stdout = io.StringIO()

argv = sys.argv
arg_path = argv[argv.index("--") + 1]
arg_pc = argv[argv.index("--") + 2]
arg_mesh = argv[argv.index("--") + 3]
arg_sample_start_idx = argv[argv.index("--") + 4]

def select(label, action):
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


def setDir(folder, file, extension):
    target_file = os.path.join(folder, '{}.{}'.format(file, extension))
    return target_file

txtr = open(os.path.join(arg_path, 'parameters', 'blender_bones_data.txt'), 'r')
txtw = open(os.path.join(arg_path, 'parameters', arg_sample_start_idx + '.txt'), 'w')
lines = txtr.readlines()
for line in lines:
    transform = line.split(',')[0]
    if transform == "Rotation":
        nm = line.split(',')[1].split('-')[0]
        pnt = line.split(',')[1].split('-')[1]
        ax = line.split(',')[2]
        obj = bpy.data.objects["Armature"].pose.bones[nm + "-" + pnt]
        txtw.write('Rotation,' + nm + '-' + pnt + ',')
        if ax == 'W':
            txtw.write(ax + ',' + str(obj.rotation_quaternion.w)+'\n')
        elif ax == 'X':
            txtw.write(ax + ',' + str(obj.rotation_quaternion.x)+'\n')
        elif ax == 'Y':
            txtw.write(ax + ',' + str(obj.rotation_quaternion.y)+'\n')
        elif ax == 'Z':
            txtw.write(ax + ',' + str(obj.rotation_quaternion.z)+'\n')
        else:
            pass

    elif transform == "Location":
        nm = line.split(',')[1].split('-')[0]
        pnt = line.split(',')[1].split('-')[1]
        ax = line.split(',')[2]
        obj = bpy.data.objects["Armature"].pose.bones[nm + "-" + pnt]
        txtw.write('Location,' + nm + '-' + pnt + ',')
        if ax == 'X':
            txtw.write(ax + ',' + str(obj.location.x) + '\n')
        elif ax == 'Y':
            txtw.write(ax + ',' + str(obj.location.y) + '\n')
        elif ax == 'Z':
            txtw.write(ax + ',' + str(obj.location.z) + '\n')
        else:
            pass

    elif transform == "Scale":
        nm = line.split(',')[1].split('-')[0]
        pnt = line.split(',')[1].split('-')[1]
        ax = line.split(',')[2]
        obj = bpy.data.objects["Armature"].pose.bones[nm + "-" + pnt]
        txtw.write('Scale,' + nm + '-' + pnt + ',')
        if ax == 'X':
            txtw.write(ax + ',' + str(obj.scale.x) + '\n')
        elif ax == 'Y':
            txtw.write(ax + ',' + str(obj.scale.y) + '\n')
        elif ax == 'Z':
            txtw.write(ax + ',' + str(obj.scale.z) + '\n')
        else:
            pass

    elif transform == "Shape_key":
        nm = line.split(',')[1]
        obj = bpy.data.shape_keys["Key.002"].key_blocks[nm]
        txtw.write('Shape_key,' + obj.name)
        txtw.write(',#,' + str(obj.value) + '\n')

    else:
        print("Reset: skipped line")
        pass

txtw.close()

class Ear():
    def __init__(self, name):
        self.name = name
        self.path = str(arg_path)

    def export(self, name):

        select('ARI_PPM_v1', True)

        if arg_pc == 'TRUE':   
            if not os.path.exists(os.path.join(self.path,'pc')):
                os.makedirs(os.path.join(self.path,'pc'))      
            
            target_file_ply = setDir(os.path.join(self.path,'pc'), name, "ply")
            with redirect_stdout(stdout):
                bpy.ops.export_mesh.ply(filepath=target_file_ply, 
                                        use_selection=True, 
                                        use_normals=False, 
                                        use_uv_coords=False, 
                                        use_colors=False)

        if arg_mesh == 'TRUE':
            if not os.path.exists(os.path.join(self.path,'mesh')):
                os.makedirs(os.path.join(self.path,'mesh'))   

            target_file_stl = setDir(os.path.join(self.path,'mesh'), name, "stl")
            with redirect_stdout(stdout):
                bpy.ops.export_mesh.stl(filepath=target_file_stl, 
                                        use_selection=True, 
                                        use_scene_unit=True)

        select('ARI_PPM_v1', False)

    def loadAll(self):
        os.chdir(os.path.join(self.path,'parameters'))

        for file in glob.glob("*.txt"):

            name = file.split('.')[0]

            if name!='blender_bones_data':
                if arg_pc == 'TRUE' or arg_mesh == 'TRUE':
                    self.export(name)
  
Ear = Ear("Ear")
Ear.loadAll()