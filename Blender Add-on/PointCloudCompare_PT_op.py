import bpy
import os
import numpy as np
import time
import ctypes as cts
import sys
import numpy.matlib
import platform
import bmesh

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
        
        #fetch data for P
        obj1 = context.view_layer.objects.active
        P = fetch_data_array(obj1)

        #fetch data for Q
        obj2 = context.scene.objects[context.scene.Reference]
        Q = fetch_data_array(obj2)


        #ERROR HANDLING
        if np.isnan(Q).all() or np.isnan(P).all():
            #self.report({'ERROR'},"Both objects must contain geometry data!")
            self.report({'WARNING'},"Both objects must contain geometry data!")
            stats_distance = context.scene.distances.add()
            stats_distance.ERROR = "Both objects must contain geometry data!"
            return {'CANCELLED'}
        

        #select distance type from drop down menu
        dist_type = context.scene.distance_selector.selector        
        if dist_type == "OP3":
            jaccard_res = context.scene.jaccard_resolution.selector
         


        #calculate the actual distances
        if dist_type == "OP1":
            #minimal pontwise distance to Ref 
            # P -> Q
            distance_values, dealloc_array  = distance_calulation_min_pointwise(P,Q)
            if distance_values is None:
                distance_values = distance_calulation_min_pointwise_np(P,Q)

            stats_distance = context.scene.distances.add()  
            stats_distance.mean_pmin = np.round(np.mean(distance_values), decimals=2)
            print("Mean: ", stats_distance.mean_pmin)
            stats_distance.median_pmin = np.round(np.median(distance_values), decimals=2)
            print("Median: ", stats_distance.median_pmin)
            stats_distance.max_pmin = np.round(np.max(distance_values), decimals=2)
            print("Maximum: ", stats_distance.max_pmin)
            stats_distance.min_pmin = np.round(np.min(distance_values), decimals=2)
            print("Minimum: ", stats_distance.min_pmin)
            
        elif dist_type == "OP2":
            #minimal pontwise distance from Ref 
            # Q -> P   
            distance_values, dealloc_array  = distance_calulation_min_pointwise(Q,P)
            if distance_values is None:
                distance_values = distance_calulation_min_pointwise_np(P,Q)

            stats_distance = context.scene.distances.add()  
            stats_distance.mean_pmin = np.round(np.mean(distance_values), decimals=2)
            print("Mean: ", stats_distance.mean_pmin)
            stats_distance.median_pmin = np.round(np.median(distance_values), decimals=2)
            print("Median: ", stats_distance.median_pmin)
            stats_distance.max_pmin = np.round(np.max(distance_values), decimals=2)
            print("Maximum: ", stats_distance.max_pmin)
            stats_distance.min_pmin = np.round(np.min(distance_values), decimals=2)
            print("Minimum: ", stats_distance.min_pmin)

        elif dist_type == "OP3":
            res = float(jaccard_res)
            grid,len_x,len_y,xmin,ymin,zmin = generate_meshgrid(P,Q, res)

            bin_grid_p = bin_mask_idx(P,res,len_x,len_y,xmin,ymin,zmin)
            bin_grid_q = bin_mask_idx(Q,res,len_x,len_y,xmin,ymin,zmin)
            jaccard_coef = jaccard_dist(bin_grid_p,bin_grid_q)

            stats_distance = context.scene.distances.add()  
            stats_distance.jaccard_coef = np.round(jaccard_coef, decimals=2)
            print("jaccard coefficient: ", stats_distance.jaccard_coef)

            stats_distance.dice_coef = np.round((2*jaccard_coef)/(jaccard_coef + 1), decimals=2)
            print("dice coefficient: ", stats_distance.dice_coef)

        stats_distance.dist_type = dist_type
        if dist_type != "OP3" and dealloc_array is not None:
            #free memory
            dealloc_array(distance_values)


        #painting is only usefull in the first case
        if dist_type == "OP1":
            
            #Color
            if obj1.data.vertex_colors.active == None:
                obj1.data.vertex_colors.new()    
            color_map = obj1.data.vertex_colors.active.data
            bpy.context.view_layer.objects.active = obj1
            
            obj1.hide_set(False)
            #obj1.hide_viewport = obj1.hide_render = True  
            bpy.ops.object.mode_set(mode='VERTEX_PAINT')
            
            # setting up color array
            color_array = np.zeros(len(obj1.data.vertices) * 4, dtype=np.float32)
            color_array.shape = (len(obj1.data.vertices), 4)
            # iterating through vertices and setting colors
            for i, vert in enumerate(obj1.data.vertices):

                if distance_values[i] <= 1:
                    color_array[i] = [0, 0, 1, 1] #blue
                elif distance_values[i] > 1 and distance_values[i]<=1.5:
                    color_array[i] = [0, 1, 3, 1] #türkis
                elif distance_values[i] > 1.5 and distance_values[i]<=2:
                    color_array[i] = [0, 1, 0, 1] #green
                elif distance_values[i] > 2 and distance_values[i]<=3:
                    color_array[i] = [3, 0.8, 0, 1] #yellow/orange
                elif distance_values[i] > 3 and distance_values[i] <= 5:
                    color_array[i] = [3, 0.5, 0, 1] #orange
                elif distance_values[i] > 5:
                    color_array[i] = [1, 0, 0, 1] #red

            # setting colors for the object
            for loop in obj1.data.loops:
                color_map[loop.index].color=list(color_array[loop.vertex_index])
            obj1.select_set(True)
            
        return {'FINISHED'}

    
class DistanceProperty(bpy.types.PropertyGroup):
    """
    A class used to init the relevant statistical distances
    ...

    Attributes
    -------
    dist_type : string
        specifies the used dist_type
    mean_pmin   : bpy.props.FloatProperty
        the mean distance to Reference
    median_pmin : bpy.props.FloatProperty
        the median distance to Reference
    max_pmin    : bpy.props.FloatProperty
        the max distance to Reference
    min_pmin    : bpy.props.FloatProperty
        the min distance to Reference
    jaccard_coef bpy.props.FloatProperty
        jaccard distance
    ERROR: string
        an string object to display potential errors
    """ 
    dist_type: bpy.props.StringProperty(name="Dist_type")
    
    #to ref
    mean_pmin: bpy.props.FloatProperty(name="Mean_PQ", default =0.0)
    median_pmin: bpy.props.FloatProperty(name="Median_PQ",default =0.0 )
    max_pmin: bpy.props.FloatProperty(name="Maximum_PQ",default =0.0 )
    min_pmin: bpy.props.FloatProperty(name="Minimum_PQ",default =0.0 )
    

    #jaccard
    jaccard_coef: bpy.props.FloatProperty(name="jaccard_coef", default =0.0)

    #dice
    dice_coef: bpy.props.FloatProperty(name="dice_coef", default =0.0)

    #ERROR
    ERROR: bpy.props.StringProperty(name="ERROR", default ="")


class DistanceSelector(bpy.types.PropertyGroup):
    """
    A class used to incoorporate the drop down menu for the different
    measurement types
    ...

    Attributes
    -------
    selector: bpy.props.EnumProperty
        stores all the distacne choices
    
    """
    selector: bpy.props.EnumProperty(
        name = "Metric",
        description = "",
        items = [('OP1','Minimal pointwise Distance to Ref', ""),
                 ('OP2','Minimal pointwise Distance from Ref', ""),
                 ('OP3','Jaccard/Dice Index', "")
        ]
    )


class JaccardResolutionSelector(bpy.types.PropertyGroup):
    """
    A class used to incoorporate the drop down menu for the different
    resolution values
    ...

    Attributes
    ------- 
    selector: bpy.props.EnumProperty
        stores all the resolution choices
    
    """
    selector: bpy.props.EnumProperty(
        name = "resolution",
        description = "",
        items = [('1','0.5mm', ""),
                 ('2','1mm', ""),
                 ('3','1.5mm', ""),
                 ('4','2mm', ""),
                 ('8','4mm', ""),
                 ('20','10mm', ""),
                 ('200','100mm',"")
        ]
    )




#General Helper Function
def fetch_data_array(obj):
    """
    A function used to fetch point cloud arrays from objects
    ...

    Arguments
    -------
    obj: bpy_types.Object
        the object from which the data should be fetched
    
    Return: np.array
        array with x,y,z of the point cloud
    """

    #check_if_nomats(obj)
    #set_use_nodes_False(obj)
    #check_if_nocols(obj)
    if bpy.ops.object.mode_set.poll():
        bpy.ops.object.mode_set(mode='OBJECT')
    depsgraph = bpy.context.evaluated_depsgraph_get()
    obj_eval = obj.evaluated_get(depsgraph)
    bm = bmesh.new()
    try:
        me = obj_eval.to_mesh()
    except:
        return np.array([[np.nan]])
        
    me.transform(obj.matrix_world)
    bm.from_mesh(me)
    obj.to_mesh_clear()
    verts = [v.co for v in bm.verts]
    bm.free()
    return np.array(verts)

def np_mat_type(rows, cols, element_type=float):
    """
    A function used to cast arrays between python and C
    ...

    Arguments
    -------
    rows: int
        Specifies the amount of rows in the matrix
    cols: int
        Specifies the amount of columns in the matrix
    element_type: float
        specifies the data type of the elements of the matrix
    
    Return: np.ctypeslib.ndpointer
        a C pointer
    """
    return np.ctypeslib.ndpointer(dtype=element_type, shape=(rows, cols), flags="C_CONTIGUOUS")

def loadCfile():
    """
    A function used to load the compiled C file for fast calculation
    ...

    Arguments
    -------
    filename: string
        filename of file to the .dll or .so file (must be in the same directory as this file)

    Return: class 'ctypes.CDLL'
        an instance of a class where the compiled function are stored
    """

    #get path of compiled C file
    absolute_path = os.path.dirname(__file__)
    if sys.platform[:3].lower() == "win":
        print("Windows Architecture detected")
        DLL_NAME = absolute_path + "/clib_win.dll"
    elif sys.platform[:3].lower() == "lin":
        print("Linux Architecture detected")
        DLL_NAME = absolute_path + "/clib_lin.so"
    elif sys.platform[:3].lower() == "dar":
        print("Mac Architecture detected")
        if "arm" in platform.machine().lower():
            print("ARM Processor detected")
            DLL_NAME = absolute_path + "/clib_mac_arm.so" #arm
        elif "intel" in platform.machine().lower():
            print("Intel Processor detected")
            DLL_NAME = absolute_path + "/clib_mac_arm.so"
            print("THIS case was not tested")
        else:
            print("Unknown Mac Processor")
    else:
        print("The operating system used is not supported for the Clibary")
        return None
    #DLL_NAME = absolute_path + "/haus_46.{:s}".format("dll" if sys.platform[:3].lower() == "win" else "so")


    try:
        c_function = cts.CDLL(DLL_NAME)
        print("C Libary loaded succesfully")
        return c_function
    except:
        print("C Libary cannot be loaded on this machine!")
        return None

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


def distance_calulation_min_pointwise_np(P,Q):

    #inputs P and Q are arrays of vert coordinates

    dist = np.zeros((P.shape[0], 1))

    for p in range(P.shape[0]):

        # Calculate the minimum distance from points in P to Q

        minP = np.min(np.sum((P[p, :] - Q)**2, axis=1))

        dist[p, 0] = minP



    hd = np.sqrt(dist)

    return hd


#Minimal pointwise distance Helper Functions
def distance_calulation_min_pointwise(P,Q):
    """
    A function used to calculate the specified distance between two objects
    ...

    Arguments
    -------
    P: np.array
        An array where each entry stores an x,y,z coordination of the point cloud
    Q: np.array
        An array where each entry stores an x,y,z coordination of the point cloud
    
    Return: np.array/int
        returns either the dice coefficient or an array with each pointwise distance stores
    Return: function_handler
        returns the used function for freeing memory of the returned array
    """

    c_func = loadCfile()
    if c_func is None:
        return None,None
    
    rows_p,cols_p = P.shape
    rows_q,cols_q = Q.shape
    P = np.ascontiguousarray(P.astype(cts.c_double))
    Q = np.ascontiguousarray(Q.astype(cts.c_double))

    

    #consider freeing memory
    dealloc_array = c_func.deallocArray
    dealloc_array.argtypes = (np_mat_type(rows_p, 1),)
    dealloc_array.restype = None


    min_pointwise_dist = c_func.pointwiseDistance

    min_pointwise_dist.argtypes = (
        np_mat_type(rows_p, cols_p), cts.c_size_t, cts.c_size_t,
        np_mat_type(rows_q, cols_q), cts.c_size_t, cts.c_size_t)
    min_pointwise_dist.restype = np_mat_type(rows_p, 1)
    start = time.time()
    distance_values = min_pointwise_dist(P, rows_p, cols_p, Q, rows_q, cols_q)
    end = time.time()

    print(f"Time for Distance calculations: {end - start}")
    return distance_values, dealloc_array



#Jaccard Helper Functions
def generate_meshgrid(P,Q, res):
    """
    A function used to generate a meshgrid over two arrays given a resolution
    ...

    Arguments
    -------
    P: np.array
        An array where each entry stores an x,y,z coordination of the point cloud
    Q: np.array
        An array where each entry stores an x,y,z coordination of the point cloud
    res: float
        given the resolution/stepsize of each voxel

    Return: np.array/int
        returns an array of the grid mesh points
    """
        

    #get boundaries of grid
    x_min = min(min(P[:, 0]), min(Q[:, 0])); x_max = max(max(P[:, 0]), max(Q[:, 0]))
    y_min = min(min(P[:, 1]), min(Q[:, 1])); y_max = max(max(P[:, 1]), max(Q[:, 1]))
    z_min = min(min(P[:, 2]), min(Q[:, 2])); z_max = max(max(P[:, 2]), max(Q[:, 2]))
    print(f"X: {x_min} - {x_max} : {x_max-x_min}")

    print(f"Y: {y_min} - {y_max} : {y_max-y_min}")
    print(f"Z: {z_min} - {z_max} : {z_max-z_min}")


    #apply grid resolution
    xx = np.arange(x_min, x_max+res/2+np.finfo(np.float64).eps, res)
    yy = np.arange(y_min, y_max+res/2+np.finfo(np.float64).eps, res)
    zz = np.arange(z_min, z_max+res/2+np.finfo(np.float64).eps, res)
    
    len_x = len(xx)
    len_y = len(yy)

    #generate grid
    xx,yy,zz = np.meshgrid(yy,zz,xx)
    grid = np.array([zz.ravel(),xx.ravel(),yy.ravel()]).T

    #output:
    # - x     increases
    # - - y   inceases
    # - - - z increases
    
    print(f"Size of grid: {grid.shape}")
    return grid,len_x,len_y,x_min,y_min,z_min

def jaccard_dist(bin_grid_p,bin_grid_q):
    union = len(np.unique(np.append(bin_grid_p,bin_grid_q)))

    #val,idx = np.unique(bin_grid_p,return_index=True)
    intersection = len(np.intersect1d(bin_grid_p,bin_grid_q))
    jaccard_coef = intersection / union
    return jaccard_coef

def bin_mask_idx(P,res,len_x,len_y,start_x,start_y,start_z):
    discret_x = np.round((P[:,0]-start_x)/res)
    discret_y = np.round((P[:,1]-start_y)/res)
    discret_z = np.round((P[:,2]-start_z)/res)
    
    # get index of grid element
    bin_mask_idx = discret_x + discret_y*len_x + discret_z * len_x*len_y
    return bin_mask_idx

def map_points_to_grid(P,Q, grid = None,jaccard_res = 1):
    """
    A template function for mapping data points on an an arbitrary grid
    ...

    Arguments
    -------
    P: np.array
        An array where each entry stores an x,y,z coordination of the point cloud
    Q: np.array
        An array where each entry stores an x,y,z coordination of the point cloud
    grid: np.array
        An array where each grid point is stored.
        Default: None (an regularly spaced grid with resolution jaccard_res is calculated)
    jaccard_res: float
        Resolution for the grid (if grid parameter is set as default (None))
        Default: 1
    Return: np.array
        returns several jaccard versions

    """
    
    c_func = loadCfile()

    if grid is None:
        res_x = res_y =res_z = float(jaccard_res)
        grid,len_x,len_y,xmin,ymin,zmin = generate_meshgrid(P, Q, res_x,res_y,res_z)
        grid = np.ascontiguousarray(grid)
    else:
        grid = np.ascontiguousarray(grid)

        
    rows_p, cols_p = P.shape
    rows_q, cols_q = Q.shape
    rows_g, cols_g = grid.shape


    binary_mask_generator = c_func.binaryMaskGenerator
    binary_mask_generator.restype = np_mat_type(rows_g, 1,element_type=int)
    
    dealloc_array = c_func.deallocArray
    dealloc_array.argtypes = (np_mat_type(rows_g, 1,element_type=int),)
    dealloc_array.restype = None

    #Binary Mask for P matrix
    binary_mask_generator.argtypes = (
        np_mat_type(rows_p, cols_p), cts.c_size_t, cts.c_size_t,
        np_mat_type(rows_g, cols_g), cts.c_size_t, cts.c_size_t)
    
    start = time.time()
    int_grid_p_c = binary_mask_generator(P, rows_p, cols_p, grid, rows_g, cols_g)
    int_grid_p = int_grid_p_c.flatten()
    bool_grid_p = int_grid_p.astype(bool)
    end = time.time()
    print(f"time for P mask: {end-start}")

    #Binary Mask for Q matrix
    binary_mask_generator.argtypes = (
        np_mat_type(rows_q, cols_q), cts.c_size_t, cts.c_size_t,
        np_mat_type(rows_g, cols_g), cts.c_size_t, cts.c_size_t)
    
    start = time.time()
    int_grid_q_c = binary_mask_generator(Q, rows_q, cols_q, grid, rows_g, cols_g)
    int_grid_q = int_grid_q_c.flatten()
    bool_grid_q = int_grid_q.astype(bool)
    print(f"time for Q mask: {end-start}")
  
    #TEMPLATE FOR GETTING BOOL AND GRID MASKS FOR ARBITRARY MASKS

    dealloc_array(int_grid_p_c)
    dealloc_array(int_grid_q_c)

    return





