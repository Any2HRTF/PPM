import bpy
import numpy as np

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
        obj1_copy = create_mesh_copy(obj1)

        check_if_nomats(obj1_copy)
        set_use_nodes_False(obj1_copy)
        check_if_nocols(obj1_copy)

        obj2= context.scene.objects[context.scene.theReferenceObject]         #setting up reference object
        obj2_copy = create_mesh_copy(obj2)
        color_map = obj1_copy.data.vertex_colors.active.data

        MW2 = obj2_copy.matrix_world
        MW1 = obj1_copy.matrix_world

        #setting up P and Q
        P= np.array([MW1 @ vert.co for vert in obj1_copy.data.vertices ])
        Q= np.array([MW2 @ vert.co for vert in obj2_copy.data.vertices ])

        #calculating hausdorff distance of each point
        hausdorff=hausdorff_distance(P,Q)

        #hausdorff_l=list(hausdorff)
        hausdorff_trans=list((hausdorff - np.mean(hausdorff))*(1/np.mean(hausdorff))+1)
        # print("Hausdorf calculated")

        print("Maximum: ", max(hausdorff))
        print("Minimum: ", min(hausdorff))
        print("Mean: ", np.mean(hausdorff))
        print("Median: ", np.median(hausdorff))

        hausdorff_trans=list((hausdorff - np.mean(hausdorff))*(1/np.mean(hausdorff))+1)

        # setting up color array
        color_array = np.zeros(len(obj1_copy.data.vertices) * 4, dtype=np.float32)
        color_array.shape = (len(obj1_copy.data.vertices), 4)

        # iterating through vertices and setting colors
        for i, vert in enumerate(obj1_copy.data.vertices):
            if hausdorff_trans[i] <= 1:
                color_array[i] = [0, 0, 1, 1]
            elif hausdorff_trans[i] > 1 and hausdorff_trans[i]<=2:
                color_array[i] = [0, 1, 3, 1]
            elif hausdorff_trans[i] > 2 and hausdorff_trans[i]<=4:
                color_array[i] = [0, 1, 0, 1]
            elif hausdorff_trans[i] > 4:
                color_array[i] = [1, 0, 0, 1]

        # setting colors for the object

        for loop in obj1_copy.data.loops:
            color_map[loop.index].color=list(color_array[loop.vertex_index])

        bpy.data.objects.remove(obj2_copy, do_unlink=True)
        obj1_copy.select_set(True)
        bpy.context.view_layer.objects.active = obj1_copy
        bpy.ops.object.mode_set(mode='VERTEX_PAINT')
        hausdorff_item = context.scene.hausdorff.add()
        hausdorff_item.mean = np.round(np.mean(hausdorff), decimals=2)
        hausdorff_item.median = np.round(np.median(hausdorff), decimals=2)
        hausdorff_item.max = np.round(np.max(hausdorff), decimals=2)
        hausdorff_item.min = np.round(np.min(hausdorff), decimals=2)

        return {'FINISHED'}

    
class HausdorffProperty(bpy.types.PropertyGroup):
    mean: bpy.props.FloatProperty(name="Mean", default =0.0)
    median: bpy.props.FloatProperty(name="Median",default =0.0 )
    max: bpy.props.FloatProperty(name="Maximum",default =0.0 )
    min: bpy.props.FloatProperty(name="Minimum",default =0.0 )


class ResetColors(bpy.types.Operator):

    bl_idname = "object.reset_colors"
    bl_label = "Reset colors"
    bl_description = "Resets colors after visualizing the Hausdorff distance"

    @classmethod
    def poll(cls, context):
        obj = context.object
        if obj is not None:
            if obj.mode == "OBJECT":
                return True

        return False

    def execute(self, context):
        obj1 = context.view_layer.objects.active
        color_map=obj1.data.vertex_colors.active.data

        for index in range(len(color_map)):
            color_map[index].color=[1,1,1,8]

        return {'FINISHED'}

    
class OutputHausdorff(bpy.types.Operator):
    bl_idname = "object.output_hausdorff"
    bl_label = "Output Hausdorff Distance"
    bl_description = "Output the mean and max Hausdorff distance"



    @classmethod
    def poll(cls, context):
        obj = context.object
        if obj is not None:
            if obj.mode == "OBJECT":
                return True

        return False

    

    def execute(self, context):

        obj1 = context.view_layer.objects.active
        obj2= context.scene.objects[context.scene.theReferenceObject] 
        
        # creating the meshes
        obj1_copy = create_mesh_copy(obj1)
        obj2_copy = create_mesh_copy(obj2)

        # world matrices
        MW2 = obj2_copy.matrix_world
        MW1 = obj1_copy.matrix_world

        # setting up P and Q

        P= np.array([MW1 @ vert.co for vert in obj1_copy.data.vertices ])
        Q= np.array([MW2 @ vert.co for vert in obj2_copy.data.vertices ])

        # calculation bi-directional hausdorff distance
        hausdorff_direction_1 = hausdorff_distance(P, Q)
        hausdorff_direction_2 = hausdorff_distance(Q, P)

        # We should do this to get the generalized Hausdorff distance as we are interested in the worst case
        if hausdorff_direction_1.max() > hausdorff_direction_2.max():
            hausdorff = hausdorff_direction_1

        else:
           hausdorff = hausdorff_direction_2

        #printing the results:
        print("Maximum: ", max(hausdorff))
        print("Minimum: ", min(hausdorff))
        print("Mean: ", np.mean(hausdorff))
        print("Median: ", np.median(hausdorff))

        #updating the hausdorff property in the panel
        hausdorff_item = context.scene.hausdorff.add()
        hausdorff_item.mean = np.round(np.mean(hausdorff), decimals=2)
        hausdorff_item.median = np.round(np.median(hausdorff), decimals=2)
        hausdorff_item.max = np.round(np.max(hausdorff), decimals=2)
        hausdorff_item.min = np.round(np.min(hausdorff), decimals=2)
    

        #deleting the meshes
        bpy.data.objects.remove(obj2_copy, do_unlink=True)
        bpy.data.objects.remove(obj1_copy, do_unlink=True)

        return {'FINISHED'}

def hausdorff_distance(P,Q):

    #inputs P and Q are arrays of vert coordinates
    dist = np.zeros((P.shape[0], 1))
    for p in range(P.shape[0]):
        # Calculate the minimum distance from points in P to Q
        dist[p, 0] = np.min(np.sum((P[p, :] - Q)**2, axis=1))

    return np.sqrt(dist)

def check_if_nomats(obj):
    if len(obj.data.materials)==0:
        new_mat=bpy.data.materials.new('NewMaterial')
        obj.data.materials.append(new_mat)

    return {'FINISHED'}


def set_use_nodes_False(obj):
    for mats in obj.data.materials:
        mats.use_nodes=False


def check_if_nocols(obj):
    if obj.data.vertex_colors.active == None:
        obj.data.vertex_colors.new()

    
def create_mesh_copy(obj1):
    obj1_copy = obj1.copy()
    obj1_copy.data = obj1.data.copy()
    bpy.context.collection.objects.link(obj1_copy)
    obj1.select_set(False)
    obj1_copy.select_set(True)
    bpy.context.view_layer.objects.active = obj1_copy
    bpy.ops.object.convert(target='MESH')

    return obj1_copy