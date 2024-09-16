import os
import sys
import itertools
import tempfile
import pickle

import numpy as np
import pandas as pd
import bpy

from core_class import BezierPPM

CURRENT_DIR = os.path.dirname(os.path.realpath(__file__))

def get_vertices_assigned_to_material(material_name="Conchae"):

    BezierPPM().points
    obj = bpy.data.objects.get("Mesh")

    bpy.ops.object.mode_set(mode='EDIT')
    bpy.ops.mesh.select_all(action='DESELECT')

    mesh = obj.data

    material_index = None
    for i, material in enumerate(obj.data.materials):
        if material.name == material_name:
            material_index = i
            break

    if material_index is not None:
        bpy.ops.object.mode_set(mode='OBJECT')
        for face in mesh.polygons:
            if face.material_index == material_index:
                face.select = True

        bpy.ops.object.mode_set(mode='EDIT')
        bpy.ops.mesh.select_mode(type="FACE")
        bpy.ops.object.mode_set(mode='OBJECT')

        indices_selected_vertices = {v for f in mesh.polygons if f.select for v in f.vertices}
        indices_selected_vertices = list(indices_selected_vertices)

        bpy.ops.object.mode_set(mode='EDIT')
    
    return indices_selected_vertices

def get_pinna_regions():     
    # bpy.ops.wm.quit_blender()
    logfile = tempfile.mktemp()
    open(logfile, "a").close()
    old = os.dup(sys.stdout.fileno())
    sys.stdout.flush()
    os.close(sys.stdout.fileno())
    fd = os.open(logfile, os.O_WRONLY)
    bpy.ops.wm.open_mainfile(filepath=f"{CURRENT_DIR}/resources/PPM.blend")
    # disable output redirection
    os.close(fd)
    os.dup(old)
    os.close(old)
    bpy.ops.object.mode_set(mode="OBJECT")

    obj = bpy.data.objects["Mesh"]
    mesh = obj.data
    materials = []

    for f in mesh.polygons:
        slot = obj.material_slots[f.material_index]
        mat = slot.material
        if mat is not None:
            materials.append(mat.name)
    # bpy.ops.wm.quit_blender()
    return list(set(materials))

if __name__ == '__main__':
    regions = get_pinna_regions()
    export = {}

    for region in regions:
        export[region] = get_vertices_assigned_to_material(region)

    with open(CURRENT_DIR+'/resources/pinna_regions.pickle', 'wb') as handle:
        pickle.dump(export, handle, protocol=pickle.HIGHEST_PROTOCOL)
