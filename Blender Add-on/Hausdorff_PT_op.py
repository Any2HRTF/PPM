import bpy
import os
import numpy as np
import time
import ctypes as cts
import sys
import numpy.matlib


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

        #select distance type from drop down menu
        dist_type = context.scene.distance_selector.selector        
        if dist_type == "OP3":
            jaccard_res = context.scene.jaccard_resolution.selector      
            print(jaccard_res)
         
        #setting up reference object
        obj2= context.scene.objects[context.scene.Reference]         
        color_map = obj1.data.vertex_colors.active.data

        #load data from the two objects
        MW2 = obj2.matrix_world
        MW1 = obj1.matrix_world
        P= np.array([MW1 @ vert.co for vert in obj1.data.vertices ])
        Q= np.array([MW2 @ vert.co for vert in obj2.data.vertices ])


        #calculate the actual distances
        if dist_type == "OP1":
            #minimal pontwise distance to Ref 
            # P -> Q
            distance_values, dealloc_array  = distance_calulation_min_pointwise(P,Q)

            stats_distance = context.scene.distances.add()
            stats_distance.mean_PQ = np.round(np.mean(distance_values), decimals=2)
            print("Mean: ", stats_distance.mean_PQ)
            stats_distance.median_PQ = np.round(np.median(distance_values), decimals=2)
            print("Median: ", stats_distance.median_PQ)
            stats_distance.max_PQ = np.round(np.max(distance_values), decimals=2)
            print("Maximum: ", stats_distance.max_PQ)
            stats_distance.min_PQ = np.round(np.min(distance_values), decimals=2)
            print("Minimum: ", stats_distance.min_PQ)
            
        elif dist_type == "OP2":
            #minimal pontwise distance from Ref 
            # Q -> P      
            distance_values, dealloc_array  = distance_calulation_min_pointwise(Q,P)  

            stats_distance = context.scene.distances.add()
            stats_distance.mean_QP = np.round(np.mean(distance_values), decimals=2)
            print("Mean: ", stats_distance.mean_QP)
            stats_distance.median_QP = np.round(np.median(distance_values), decimals=2)
            print("Median: ", stats_distance.median_QP)
            stats_distance.max_QP = np.round(np.max(distance_values), decimals=2)
            print("Maximum: ", stats_distance.max_QP)
            stats_distance.min_QP = np.round(np.min(distance_values), decimals=2)
            print("Minimum: ", stats_distance.min_QP)

        # elif dist_type == "OP3":
        #     jaccard_bool_coef, jaccard_alt_or_coef, jaccard_pp_coef = distance_calulation_jaccard(P,Q,jaccard_res)

        #     stats_distance = context.scene.distances.add()
        #     stats_distance.jaccard_point_preserve = np.round(jaccard_pp_coef, decimals=2)
        #     print("Point preserve jaccard: ", stats_distance.jaccard_point_preserve)

        #     stats_distance.jaccard_altnerative_or = np.round(jaccard_alt_or_coef, decimals=2)
        #     print("jaccard_altnerative_or: ", stats_distance.jaccard_altnerative_or)

        #     stats_distance.jaccard_bool = np.round(jaccard_bool_coef, decimals=2)
        #     print("jaccard_bool_coef: ", stats_distance.jaccard_bool)
        elif dist_type == "OP3":
            res = float(jaccard_res)
            grid,len_x,len_y,xmin,ymin,zmin = generate_meshgrid(P,Q, res)

            bin_grid_p = bin_mask_idx(P,res,len_x,len_y,xmin,ymin,zmin)
            bin_grid_q = bin_mask_idx(Q,res,len_x,len_y,xmin,ymin,zmin)
            jaccard_coef = jaccard_dist(bin_grid_p,bin_grid_q)

            stats_distance = context.scene.distances.add()
            stats_distance.jaccard_point_preserve = np.round(jaccard_coef, decimals=2)
            print("Point preserve jaccard: ", stats_distance.jaccard_point_preserve)

        stats_distance.dist_type = dist_type
        if dist_type != "OP3":
            #free memory
            dealloc_array(distance_values)


        #painting is only usefull in the first case
        if dist_type == "OP1":
            #COLOR YASEN
            bpy.ops.object.mode_set(mode='VERTEX_PAINT')
            hausdorff_trans=list((distance_values - np.mean(distance_values))*(1/(np.mean(distance_values)+0.1))+1)
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
    dist_type : string
        specifies the used dist_type
    mean_PQ   : bpy.props.FloatProperty
        the mean distance to Reference
    median_PQ : bpy.props.FloatProperty
        the median distance to Reference
    max_PQ    : bpy.props.FloatProperty
        the max distance to Reference
    min_PQ    : bpy.props.FloatProperty
        the min distance to Reference
    mean_QP   : bpy.props.FloatProperty
        the mean distance from Reference
    median_QP : bpy.props.FloatProperty
        the median distance from Reference
    max_QP    : bpy.props.FloatProperty
        the max distance from Reference
    min_QP    : bpy.props.FloatProperty
        the min distance from Reference
    jaccard_point_preserve: bpy.props.FloatProperty
        several jaccards
    jaccard_altnerative_or: bpy.props.FloatProperty
        several jaccards
    jaccard_bool: bpy.props.FloatProperty
        several jaccards
    """ 
    dist_type: bpy.props.StringProperty(name="Dist_type")
    
    #to ref
    mean_PQ: bpy.props.FloatProperty(name="Mean_PQ", default =0.0)
    median_PQ: bpy.props.FloatProperty(name="Median_PQ",default =0.0 )
    max_PQ: bpy.props.FloatProperty(name="Maximum_PQ",default =0.0 )
    min_PQ: bpy.props.FloatProperty(name="Minimum_PQ",default =0.0 )
    
    #from ref
    mean_QP: bpy.props.FloatProperty(name="Mean_QP", default =0.0)
    median_QP: bpy.props.FloatProperty(name="Median_QP",default =0.0 )
    max_QP: bpy.props.FloatProperty(name="Maximum_QP",default =0.0 )
    min_QP: bpy.props.FloatProperty(name="Minimum_QP",default =0.0 )

    #jaccard
    jaccard_point_preserve: bpy.props.FloatProperty(name="jaccard_point_preserve", default =0.0)
    jaccard_altnerative_or: bpy.props.FloatProperty(name="jaccard_altnerative_or",default =0.0 )
    jaccard_bool: bpy.props.FloatProperty(name="jaccard_bool",default =0.0 )



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
                 ('OP3','Dice Index', "")
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
    DLL_NAME = absolute_path + "/haus_46.{:s}".format("dll" if sys.platform[:3].lower() == "win" else "so")
    c_function = cts.CDLL(DLL_NAME)
    return c_function




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
    
    rows_p,cols_p = P.shape
    rows_q,cols_q = Q.shape
    c_func = loadCfile()

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




def distance_calulation_jaccard(P,Q,jaccard_res):
    """
    A function used to calculate several jaccard coefficients between two objects
    ...

    Arguments
    -------
    P: np.array
        An array where each entry stores an x,y,z coordination of the point cloud
    Q: np.array
        An array where each entry stores an x,y,z coordination of the point cloud

    
    Return: np.array
        returns several jaccard versions

    """
    res_x = res_y =res_z = float(jaccard_res)


    c_func = loadCfile()


    grid,len_x,len_y,xmin,ymin,zmin = generate_meshgrid(P, Q, res_x,res_y,res_z)
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
    end = time.time()
    print("nu in grid:")
    print(sum(bool_grid_p))
    print(sum(bool_grid_q))
    print(f"time for Q mask: {end-start}")
    #for i in range(len(bool_grid_q)):
    #    print(int_grid_q[i],int_grid_p[i])


    jaccard_alt_or_coef = jaccard_altnerative_or(int_grid_p,int_grid_q)
    jaccard_bool_coef = jaccard_bool(bool_grid_p,bool_grid_q)
    jaccard_pp_coef = jaccard_point_preserve(int_grid_p,int_grid_q)


    dealloc_array(int_grid_p_c)
    dealloc_array(int_grid_q_c)


    #jaccard_similarity1(P, Q, grid)
    #jaccard_felix = jaccard_similarity(P, Q, grid)
    #jaccard_similarity2(P, Q, grid)

    return jaccard_bool_coef,jaccard_alt_or_coef,jaccard_pp_coef







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
        print("Check if no Cols acitve")
        obj.data.vertex_colors.new()    






def jaccard_bool(bool_grid_p,bool_grid_q) -> np.float32:
    print(sum(np.logical_and(bool_grid_p,bool_grid_q )))
    print(np.sum(np.logical_or(bool_grid_p, bool_grid_q)))

    bool_jaccard = np.sum(np.logical_and(bool_grid_p,bool_grid_q )) / (np.sum(np.logical_or(bool_grid_p, bool_grid_q)) + np.finfo(np.float32).eps)
    #print(f"bool jaccard: {bool_jaccard}")
    return bool_jaccard

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




def jaccard_point_preserve(int_grid_p,int_grid_q) -> np.float32:
    union = int_grid_p + int_grid_q
    intersection = np.minimum(int_grid_p,int_grid_q)
    point_preserve_jaccard = sum(intersection)/(sum(union))
    #print(f"Point preserve jaccard: {point_preserve_jaccard}")
    return point_preserve_jaccard
def jaccard_altnerative_or(int_grid_p,int_grid_q) -> np.float32:
    union_2 = np.maximum(int_grid_p,int_grid_q)
    intersection = np.minimum(int_grid_p,int_grid_q) #gleich
    ver2_jaccard = sum(intersection)/(sum(union_2))    
    #print(f"alternative OR jaccard: {ver2_jaccard}")
    return ver2_jaccard






#def jaccard_similarity2(P, Q, grid) -> np.float32:

    or_val = 0
    min_val = 0
    s=time.time()
    and_val = 0
    max_val = 0
    
    #half distance leads to exactly one point mapping
    
    #diagonal
    #np.sqrt(resolution_xx**2+resolution_yy**2+resolution_zz**2)
    
    #min dist
    #epsilon = min(resolution_xx,resolution_yy,resolution_zz)
    epsilon = 0.5
    for i in range(len(grid)):
        res = [0,0]
        
        dist_to_nearest_p = np.sqrt(np.min(np.sum((grid[i,:] - P)**2, axis=1)))
        
        dist_to_nearest_q = np.sqrt(np.min(np.sum((grid[i,:] - Q)**2, axis=1)))
        min_val += min(dist_to_nearest_p,dist_to_nearest_q)
        if dist_to_nearest_p < epsilon:
            res[0] = 1
        
        max_val += max(dist_to_nearest_p,dist_to_nearest_q)
        if dist_to_nearest_q < epsilon:
            res[1] = 1
        or_val += max(res)
        and_val += min(res)
    print(f"Min/Max value (no mapping): {min_val / max_val}")
    e=time.time()
    print(f"Zeit no mapping: {e-s}")
    return
#def jaccard_similarity(P, Q, grid) -> np.float32:

    s=time.time()
    test = np.array([ 0, 1, 0, 0, 0, 1, 0, 0])
    test_2 = numpy.matlib.repmat(test,len(grid),1)

    grid = np.append(grid, test_2, axis=-1)
    
    for i in range(len(grid)):
        dist_to_nearest_p = np.sqrt(np.min(np.sum( (grid[i,:3] - P)**2, axis=1)))
        dist_to_nearest_q = np.sqrt(np.min(np.sum( (grid[i,:3] - Q)**2, axis=1)))

        if dist_to_nearest_p <= 0.6:
            grid[i, 3:7] = np.array([1, 0, 1, 0])

        if dist_to_nearest_q <= 0.6:
            grid[i, 7:] = np.array([1, 0, 1, 0])

    print(f"Felix : {np.sum(np.logical_and(grid[:, 3], grid[:, 7])) / (np.sum(np.logical_or(grid[:, 3], grid[:, 7])) + np.finfo(np.float32).eps)}")
    e=time.time()
    print(f"Zeit Felix: {e-s}")
    return
#def jaccard_point_preserve(P, Q, grid) -> np.float32:

    or_val = 0
    min_val = 0
    and_val = 0
    max_val = 0
    

    union = int_grid_p + int_grid_q

    
    intersection = np.minimum(int_grid_p,int_grid_q)
    point_preserve_jaccard = sum(intersection)/(sum(union))

    print(f"Point preserve jaccard: {point_preserve_jaccard}")



    union_2 = np.maximum(int_grid_p,int_grid_q)
    intersection = np.minimum(int_grid_p,int_grid_q) #gleich
    ver2_jaccard = sum(intersection)/(sum(union_2))    
    print(f"logisch OR correct jaccard: {ver2_jaccard}")

    bool_jaccard = np.sum(np.logical_and(bool_grid_p,bool_grid_q )) / (np.sum(np.logical_or(bool_grid_p, bool_grid_q)) + np.finfo(np.float32).eps)
    print(f"bool jaccard: {bool_jaccard}")

    e=time.time()
    print(f"johnny time: {e-s}")
    return