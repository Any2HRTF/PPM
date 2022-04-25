import bpy
import sys
import os
import io
import glob
from contextlib import redirect_stdout

stdout = io.StringIO()

argv = sys.argv

arg_path = argv[argv.index("--") + 1]

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

def export(self, name):

    target_file = setDir(self.path, name, "ply")
    select('ARI_PPM_v1', True)
    with redirect_stdout(stdout):
        bpy.ops.export_mesh.ply(filepath=target_file, use_selection=True, use_normals=False, use_uv_coords=False, use_colors=False)
    select('ARI_PPM_v1', False)

txtr = open(arg_path + '1.txt', 'r')
txtw = open(arg_path + 'blender_bones_data.txt', 'w')
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
        # self.bones = []
        # self.bonesLookup = {}

    def export(self,name):
        target_file = setDir(self.path, name, "ply")
        select('ARI_PPM_v1', True)
        with redirect_stdout(stdout):
            bpy.ops.export_mesh.ply(filepath=target_file, use_selection=True, use_normals=False, use_uv_coords=False, use_colors=False)
        select('ARI_PPM_v1', False)

    def export_mesh(self):
        os.chdir(self.path)
        for file in glob.glob("*.txt"):
            name = file.split('.')[0]
            self.export(name)

Ear = Ear("Ear")

Ear.export_mesh()