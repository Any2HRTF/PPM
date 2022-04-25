print("Blender Loaded")
#print("Initialising Scripts... ", end="", flush=True)
import bpy
import os
import glob
import sys
import io
from contextlib import redirect_stdout

stdout = io.StringIO()

argv = sys.argv

arg_path = argv[argv.index("--") + 1]
arg_mesh = argv[argv.index("--") + 2]
arg_remesh = argv[argv.index("--") + 3]
arg_image = argv[argv.index("--") + 4]
arg_res = argv[argv.index("--") + 5]

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
            #bpy.data.objects["ARI_PPM_v1"].modifiers["Decimate"].show_render = state
            #bpy.data.objects["ARI_PPM_v1"].modifiers["Decimate"].show_viewport = state

    def shapeKey(self, name, val):
        bpy.data.shape_keys["Key.002"].key_blocks[name].value = float(val)

    def export(self, name):

        target_file = setDir(self.path, name, "ply")
        select('ARI_PPM_v1', True)
        with redirect_stdout(stdout):
            bpy.ops.export_mesh.ply(filepath=target_file, use_selection=True, use_normals=False, use_uv_coords=False, use_colors=False)
        select('ARI_PPM_v1', False)

    def render(self, name):

        bpy.data.scenes["Scene"].render.resolution_x = int(arg_res)
        bpy.data.scenes["Scene"].render.resolution_y = int(arg_res)
        target_file = setDir(self.path, name, "png")
        bpy.context.scene.render.filepath = target_file
        bpy.ops.render.render(write_still=True)

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

            self.load(name)
            if arg_mesh == 'TRUE' or arg_image == 'TRUE':
                self.modifiers(True)
                if arg_mesh == 'TRUE':
                    self.export(name)
                if arg_image == 'TRUE':
                    self.render(name)
                self.modifiers(False)
            self.reset(name)

            os.close(1)
            os.dup(old)
            os.close(old)
            #print("Done")

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

#print("Done")

Ear.loadAll()

#print("Task Complete")