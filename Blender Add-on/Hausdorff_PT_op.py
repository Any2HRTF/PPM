import bpy
import numpy as np
import time
import ctypes as cts
import sys



class VisualizeDistance(bpy.types.Operator):
    """
    A class used to visualize either the pointwise minimal distance
    or the dice index
    ...

    Methods
    -------
    poll(cls, context)
        Bouncer function which decides whether the execute function is called
    execute(self, context)
        calculates the chosen distance, stores the relevant statistical measurements
        and visualizes the data
    
    """

    bl_idname = "object.visualize_distance"
    bl_label = "Distance Visualization"
    bl_description = "Calculate and visualize the chosen distance to/from a reference object"



    @classmethod
    def poll(cls, context):
        obj = context.object
        if obj is not None and obj.mode == "OBJECT":
            return True
        else:
            return False
    

    def execute(self, context):
        
        obj1 = context.view_layer.objects.active

        check_if_nomats(obj1)
        set_use_nodes_False(obj1)
        check_if_nocols(obj1)


        obj2= context.scene.objects[context.scene.Reference]         #setting up reference object
        color_map = obj1.data.vertex_colors.active.data
        MW2 = obj2.matrix_world
        MW1 = obj1.matrix_world
        P= np.array([MW1 @ vert.co for vert in obj1.data.vertices ])
        Q= np.array([MW2 @ vert.co for vert in obj2.data.vertices ])



        # P -> Q
        #calculate Hausdorff Distance
        hausdorff, dealloc_array  = hausdorff_distance(P,Q)
            


        #store statisctical measurements
        bpy.ops.object.mode_set(mode='VERTEX_PAINT')
        hausdorff_item = context.scene.distances.add()
        hausdorff_item.mean_PQ = np.round(np.mean(hausdorff), decimals=2)
        print("Mean: ", hausdorff_item.mean_PQ)
        hausdorff_item.median_PQ = np.round(np.median(hausdorff), decimals=2)
        print("Median: ", hausdorff_item.median_PQ)
        hausdorff_item.max_PQ = np.round(np.max(hausdorff), decimals=2)
        print("Maximum: ", hausdorff_item.max_PQ)
        hausdorff_item.min_PQ = np.round(np.min(hausdorff), decimals=2)
        print("Minimum: ", hausdorff_item.min_PQ)

        hausdorff_trans=list((hausdorff - np.mean(hausdorff))*(1/(np.mean(hausdorff)+0.1))+1)
        #free memory
        dealloc_array(hausdorff)


        # Q -> P
        #calculate Hausdorff Distance
        hausdorff, dealloc_array  = hausdorff_distance(Q,P)
        
        #store statisctical measurements
        hausdorff_item.mean_QP = np.round(np.mean(hausdorff), decimals=2)
        print("Mean: ", hausdorff_item.mean_QP)
        hausdorff_item.median_QP = np.round(np.median(hausdorff), decimals=2)
        print("Median: ", hausdorff_item.median_QP)
        hausdorff_item.max_QP = np.round(np.max(hausdorff), decimals=2)
        print("Maximum: ", hausdorff_item.max_QP)
        hausdorff_item.min_QP = np.round(np.min(hausdorff), decimals=2)
        print("Minimum: ", hausdorff_item.min_QP)
        #free memory
        dealloc_array(hausdorff)





        # setting up color array
        color_array = np.zeros(len(obj1.data.vertices) * 4, dtype=np.float32)
        color_array.shape = (len(obj1.data.vertices), 4)
    

        # iterating through vertices and setting colors
        for i, vert in enumerate(obj1.data.vertices):
            if hausdorff_trans[i] <= 1:

                color_array[i] = [0, 0, 1, 1]

            elif hausdorff_trans[i] > 1 and hausdorff_trans[i]<=2:

                color_array[i] = [0, 1, 3, 1]

            elif hausdorff_trans[i] > 2 and hausdorff_trans[i]<=4:

                color_array[i] = [0, 1, 0, 1]

            elif hausdorff_trans[i] > 4:

                color_array[i] = [1, 0, 0, 1]

        

        # setting colors for the object

        for loop in obj1.data.loops:

            color_map[loop.index].color=list(color_array[loop.vertex_index])


        obj1.select_set(True)

        bpy.context.view_layer.objects.active = obj1


        return {'FINISHED'}

    
class DistanceProperty(bpy.types.PropertyGroup):
    """
    A class used to init the relevant statistical distances
    ...

    Attributes
    -------
    mean_PQ   : float
        the mean distance to Reference
    median_PQ : float
        the median distance to Reference
    max_PQ    : float
        the max distance to Reference
    min_PQ    : float
        the min distance to Reference
    mean_QP   : float
        the mean distance from Reference
    median_QP : float
        the median distance from Reference
    max_QP    : float
        the max distance from Reference
    min_QP    : float
        the min distance from Reference
  
    """
        
    mean_PQ: bpy.props.FloatProperty(name="Mean_PQ", default =0.0)
    median_PQ: bpy.props.FloatProperty(name="Median_PQ",default =0.0 )
    max_PQ: bpy.props.FloatProperty(name="Maximum_PQ",default =0.0 )
    min_PQ: bpy.props.FloatProperty(name="Minimum_PQ",default =0.0 )
    
    mean_QP: bpy.props.FloatProperty(name="Mean_QP", default =0.0)
    median_QP: bpy.props.FloatProperty(name="Median_QP",default =0.0 )
    max_QP: bpy.props.FloatProperty(name="Maximum_QP",default =0.0 )
    min_QP: bpy.props.FloatProperty(name="Minimum_QP",default =0.0 )


def np_mat_type(rows, cols, element_type=float):
    return np.ctypeslib.ndpointer(dtype=element_type, shape=(rows, cols), flags="C_CONTIGUOUS")
def hausdorff_distance(P,Q):
    
    DLL_NAME = "C:/Program Files/Blender Foundation/Blender 3.6/3.6/scripts/addons\Hausdorff/haus_40.{:s}".format("dll" if sys.platform[:3].lower() == "win" else "so")

    rows0,cols0 = P.shape
    rows1,cols1 = Q.shape
    dll = cts.CDLL(DLL_NAME)
    matrix_func = dll.matrixFunc
    matrix_func.argtypes = (
        np_mat_type(rows0, cols0), cts.c_size_t, cts.c_size_t,
        np_mat_type(rows1, cols1), cts.c_size_t, cts.c_size_t)
    matrix_func.restype = np_mat_type(rows0, 1)
    dealloc_array = dll.deallocArray
    dealloc_array.argtypes = (np_mat_type(rows0, 1),)
    dealloc_array.restype = None


    start = time.time()
    hausdorff = matrix_func(P, rows0, cols0, Q, rows1, cols1)
    end = time.time()
    print(f"Time for Hausdorff: {end - start}")
    return hausdorff, dealloc_array


def check_if_nomats(obj):

    

    if len(obj.data.materials)==0:
        print("LEN OF DATA IS ZERO")
        new_mat=bpy.data.materials.new('NewMaterial')

        obj.data.materials.append(new_mat)

    

    return {'FINISHED'}
def set_use_nodes_False(obj):

    for mats in obj.data.materials:

        mats.use_nodes=False
def check_if_nocols(obj):

    if obj.data.vertex_colors.active == None:

        obj.data.vertex_colors.new()    
