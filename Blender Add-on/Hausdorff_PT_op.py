import bpy
import bmesh

import numpy as np

def get_points_from_obj(obj: bpy.types.Object) -> np.array:

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

def hausdorff_distance(P: np.array, Q:np.array) -> np.array:

    dist = np.zeros((P.shape[0], 1))
    for p in range(P.shape[0]):
        dist[p, 0] = np.min(np.sum((P[p, :] - Q)**2, axis=1))

    return np.sqrt(dist)


class VisualizeHausdorff(bpy.types.Operator):

    bl_idname = "object.visualize_hausdorff"
    bl_label = "Hausdorff Visualization"
    bl_description = "Calculate and visualize the Hausdorff distance to a reference object"


    @classmethod

    def poll(cls, context):

        obj = context.object

        if obj is not None:

            if obj.mode == "OBJECT":

                return True

        return False

    

    def execute(self, context):



        obj1 = context.view_layer.objects.active

        obj2= context.scene.objects[context.scene.theReferenceObject]         #setting up reference object

        P = get_points_from_obj(obj1)
        Q = get_points_from_obj(obj2)


        hausdorff_direction_1 = hausdorff_distance(P, Q)


        print("Hausdorff distance Direction 1: ")
        print("Maximum: %0.2f" % np.max(hausdorff_direction_1))
        print("Mean:    %0.2f" % np.mean(hausdorff_direction_1))
        print("Std:     %0.2f" % np.std(hausdorff_direction_1))
        print("Median:  %0.2f" % np.median(hausdorff_direction_1))




        hausdorff_direction_2 = hausdorff_distance(Q, P)
        
        print("Hausdorff distance Direction 2: ")
        print("Maximum: %0.2f" % np.max(hausdorff_direction_2))
        print("Mean:    %0.2f" % np.mean(hausdorff_direction_2))
        print("Std:     %0.2f" % np.std(hausdorff_direction_2))
        print("Median:  %0.2f" % np.median(hausdorff_direction_2))



        return {'FINISHED'}
