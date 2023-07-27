import bpy
import os
import numpy as np
import time
import ctypes as cts
import sys
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
    


    def validate_active_layer(self,obj1,stats_distance):
        """
        A function to check if the active layer is on of the helper layers of the addon
        ...

        Parameters
        -------
        obj1: bpy_types.Object
            the instance of the object to be validated
        stats_distance: DistanceProperty
            an instance of the DistanceProperty class
        Return: bool
            whether the object is valid of not
        
        """
        if obj1.name == 'Grid_visualization':
            self.report({'WARNING'},"PointCloudCompare: You still have selected the Gid_visualization layer!")
            #stats_distance = context.scene.distances.add()
            stats_distance.ERROR = "You still have selected the Gid_visualization layer!"
            return False
        elif obj1.name == 'Grid_object1':
            self.report({'WARNING'},"PointCloudCompare: You still have selected the Grid_object1 layer!")
            #stats_distance = context.scene.distances.add()
            stats_distance.ERROR = "You still have selected the Grid_object1 layer!"
            return False
        elif obj1.name == 'Grid_object2':
            self.report({'WARNING'},"PointCloudCompare: You still have selected the Grid_object2 layer!")
            #stats_distance = context.scene.distances.add()
            stats_distance.ERROR = "You still have selected the Grid_object2 layer!"
            return False
        else:
            return True

    def execute(self, context):
        
        
        #Object 1
        obj1 = context.view_layer.objects.active
        stats_distance = context.scene.distances.add()
        if not self.validate_active_layer(obj1,stats_distance):
            print(f"PointCloudCompare: {stats_distance.ERROR}")
            return {'CANCELLED'}
        
        #fetch data for P
        P = fetch_data_array(obj1)
        
        #fetch data for Q
        try:
            obj2 = context.scene.objects[context.scene.Reference]
        except:
            self.report({'WARNING'},"PointCloudCompare: Please select a reference object!")
            stats_distance = context.scene.distances.add()
            stats_distance.ERROR = "Please select a reference object!"
            return {'CANCELLED'}
        Q = fetch_data_array(obj2)


        #ERROR HANDLING
        if np.isnan(Q).all() or np.isnan(P).all():
            self.report({'WARNING'},"PointCloudCompare: Both objects must contain geometry data!")
            stats_distance = context.scene.distances.add()
            stats_distance.ERROR = "Both objects must contain geometry data!"
            return {'CANCELLED'}
        

        #select distance type from drop down menu
        dist_type = context.scene.distance_selector.selector


        #if jaccard/dice is selected, fetch specified grid resolution       
        if dist_type == "jaccard_dice":
            jaccard_res = context.scene.jaccard_resolution.selector
         
        #minimal pontwise distance to Ref 
        # P -> Q
        if dist_type == "min_p_dist_to":
            distance_values, dealloc_array  = distance_calulation_min_pointwise(P,Q)
            
            #fallback numpy implementation
            if distance_values is None:
                distance_values = distance_calulation_min_pointwise_np(P,Q)

            #store statistics
            stats_distance = context.scene.distances.add()  
            stats_distance.mean_pmin = np.round(np.mean(distance_values), decimals=2)
            stats_distance.median_pmin = np.round(np.median(distance_values), decimals=2)
            stats_distance.max_pmin = np.round(np.max(distance_values), decimals=2)
            stats_distance.min_pmin = np.round(np.min(distance_values), decimals=2)
    

        #minimal pontwise distance from Ref 
        # Q -> P   
        elif dist_type == "min_p_dist_from":
            distance_values, dealloc_array  = distance_calulation_min_pointwise(Q,P)
            
            #fallback numpy implementation
            if distance_values is None:
                distance_values = distance_calulation_min_pointwise_np(P,Q)

            #store statistics
            stats_distance = context.scene.distances.add()  
            stats_distance.mean_pmin = np.round(np.mean(distance_values), decimals=2)
            stats_distance.median_pmin = np.round(np.median(distance_values), decimals=2)
            stats_distance.max_pmin = np.round(np.max(distance_values), decimals=2)
            stats_distance.min_pmin = np.round(np.min(distance_values), decimals=2)


        elif dist_type == "jaccard_dice":
            res = float(jaccard_res)
            grid, len_x, len_y, xmin, ymin, zmin = generate_meshgrid(P, Q, res)

            #BETA
            #shift grid and average to gain robustness
            jac_avg = shift_grid_average_jaccard(P, Q, res, len_x, len_y, xmin, ymin, zmin, 10)
            #print(f"Grid resolution: {res}mm")
            #print(f"Minimum: {np.min(jac_avg)}")
            #print(f"Maximum: {np.max(jac_avg)}")
            #print(f"Median: {np.median(jac_avg)}")
            #print(f"Mean: {np.mean(jac_avg)}")            
                    
            #calculate actual jaccard similarity
            bin_grid_p = bin_mask_idx(P, res, len_x, len_y, xmin, ymin, zmin)
            bin_grid_q = bin_mask_idx(Q, res, len_x, len_y, xmin, ymin, zmin)
            jaccard_coef = jaccard_dist(bin_grid_p, bin_grid_q)


            #store statistics
            stats_distance = context.scene.distances.add()  
            stats_distance.jaccard_coef = np.round(jaccard_coef, decimals=2)
            stats_distance.avg_jaccard_coef = np.round(np.mean(jac_avg), decimals=2) #BETA average jaccard
            stats_distance.dice_coef = np.round((2*jaccard_coef)/(jaccard_coef + 1), decimals=2)


            #Visualize the grid
            if context.scene.jaccard_resolution.vis_grid:
                #clear the old visualization layers
                if 'Grid_visualization' in bpy.context.scene.objects.keys():
                    bpy.data.objects.remove(context.scene.objects['Grid_visualization'], do_unlink=True)
                if 'Grid_object1' in bpy.context.scene.objects.keys():
                    bpy.data.objects.remove(context.scene.objects['Grid_object1'], do_unlink=True)
                if 'Grid_object2' in bpy.context.scene.objects.keys():
                    bpy.data.objects.remove(context.scene.objects['Grid_object2'], do_unlink=True)
                
                #visualize the whole grid
                if context.scene.jaccard_resolution.vis_grid_type == "whole_grid":
                    new_mesh = bpy.data.meshes.new('Grid_visualization')
                    vertices, edges, faces = create_grid_mesh(grid,res/10)
                    color_array = color_grid_mesh(bin_grid_p,bin_grid_q,vertices)
                    create_colored_object(new_mesh,vertices, edges, faces,color_array,'Grid_visualization')

                #visualize just the activated voxels
                elif context.scene.jaccard_resolution.vis_grid_type == "inters_union":
                    new_mesh = bpy.data.meshes.new('Grid_visualization')
                    vertices, edges, faces = create_grid_mesh(grid,res)
                    color_array = color_grid_mesh(bin_grid_p,bin_grid_q,vertices)

                    active_voxel_idx = np.unique(np.concatenate([bin_grid_p,bin_grid_q])).astype(int)*6
                    _, _, faces = create_grid_mesh(np.zeros([len(active_voxel_idx),3]),res)
                    active_voxel_idx = np.unique(np.concatenate([bin_grid_p,bin_grid_q])).astype(int)*8
                    active_voxel_idx = generate_consecutive_values(active_voxel_idx,8)
                    vertices = vertices[active_voxel_idx]
                    color_array = color_array[active_voxel_idx]
                    create_colored_object(new_mesh,vertices, edges, faces,color_array,'Grid_visualization')

                #visualize the individual quantized meshes
                elif context.scene.jaccard_resolution.vis_grid_type == "quantized_meshes":
                    new_mesh1 = bpy.data.meshes.new('Grid_object1')
                    new_mesh2 = bpy.data.meshes.new('Grid_object2')
                    vertices, edges, faces = create_grid_mesh(grid,res)

                    #Object 1
                    color_array = color_grid_mesh(bin_grid_p,[],vertices)
                    active_voxel_idx_p = np.unique(np.concatenate([bin_grid_p])).astype(int)*6
                    _, _, faces1 = create_grid_mesh(np.zeros([len(active_voxel_idx_p),3]),res)
                    active_voxel_idx_p = np.unique(np.concatenate([bin_grid_p])).astype(int)*8
                    active_voxel_idx_p = generate_consecutive_values(active_voxel_idx_p,8)
                    vertices1 = vertices[active_voxel_idx_p]
                    color_array1 = color_array[active_voxel_idx_p]
                    create_colored_object(new_mesh1,vertices1, edges, faces1,color_array1,'Grid_object1')

                    #Object 2
                    color_array = color_grid_mesh(bin_grid_q,bin_grid_q,vertices)
                    active_voxel_idx_q = np.unique(np.concatenate([bin_grid_q])).astype(int)*6
                    _, _, faces2 = create_grid_mesh(np.zeros([len(active_voxel_idx_q),3]),res)
                    active_voxel_idx_q = np.unique(np.concatenate([bin_grid_q])).astype(int)*8
                    active_voxel_idx_q = generate_consecutive_values(active_voxel_idx_q,8)
                    vertices2 = vertices[active_voxel_idx_q]
                    color_array2 = color_array[active_voxel_idx_q]
                    create_colored_object(new_mesh2,vertices2, edges, faces2,color_array2,'Grid_object2')


        #painting is only usefull in the first case
        if dist_type == "min_p_dist_to":
            #Color
            if obj1.data.vertex_colors.active == None:
                obj1.data.vertex_colors.new()    
            color_map = obj1.data.vertex_colors.active.data
            bpy.context.view_layer.objects.active = obj1
            
            obj1.hide_set(False)
            #obj1.hide_viewport = obj1.hide_render = True  
            bpy.ops.object.mode_set(mode='VERTEX_PAINT')
            
            # setting up color array
            color_array = np.zeros([len(obj1.data.vertices), 4], dtype=np.float32)
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
        
        
        if dist_type != "jaccard_dice" and dealloc_array is not None:
            #free memory
            dealloc_array(distance_values) 

        stats_distance.dist_type = dist_type
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
    jaccard_coef: bpy.props.FloatProperty
        jaccard distance
    avg_jaccard_coef: bpy.props.FloatProperty
        average jaccard coef
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
    avg_jaccard_coef: bpy.props.FloatProperty(name="jaccard_coef", default =0.0)

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
        items = [("min_p_dist_to",'Minimal pointwise Distance to Ref', ""),
                 ("min_p_dist_from",'Minimal pointwise Distance from Ref', ""),
                 ("jaccard_dice",'Jaccard/Dice Index', "")
        ]
    )


class JaccardResolutionSelector(bpy.types.PropertyGroup):
    """
    A class used to incoorporate the drop down menu for the different
    resolution values and the visualization of the grid
    ...

    Attributes
    ------- 
    selector: bpy.props.EnumProperty
        stores all the resolution choices
    vis_grid: bpy.props.BoolProperty
        a checkbox whether the visualization is applied or not
    vis_grid_type: bpy.props.EnumProperty
        stores all the visualization choices
    
    """
    
    selector: bpy.props.EnumProperty(
        name = "resolution",
        description = "",
        items = [('0.5','0.25mm (very slow)', ""),
                ('1','0.5mm (slow)', ""),
                 ('2','1mm', ""),
                 ('3','1.5mm', ""),
                 ('4','2mm', ""),
                 ('8','4mm', ""),
                 ('20','10mm', ""),
                 ('200','100mm',"")])


    vis_grid: bpy.props.BoolProperty(
    name="Visualize Grid Cube",
    description="Visualize Grid Cube",
    default = False) 


    vis_grid_type: bpy.props.EnumProperty(
        name = "Type",
        description = "",
        items = [('whole_grid','Visualize the whole Grid', ""),
                 ('inters_union','Visualize just Intersection/Union', ""),
                 ('quantized_meshes','Visualize the 2 quantized meshes', "")])






#------------------------------------------------------------General Helper Function
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




#------------------------------------------------------------C Libary Helper Functions
def np_mat_type(rows, cols, element_type = float):
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
        print("PointCloudCompare: Windows Architecture detected")
        DLL_NAME = absolute_path + "/clib_win.dll"
    elif sys.platform[:3].lower() == "lin":
        print("PointCloudCompare: Linux Architecture detected")
        DLL_NAME = absolute_path + "/clib_lin.so"
    elif sys.platform[:3].lower() == "dar":
        print("PointCloudCompare: Mac Architecture detected")
        if "arm" in platform.machine().lower():
            print("PointCloudCompare: ARM Processor detected")
            DLL_NAME = absolute_path + "/clib_mac_arm.so" #arm
        elif "intel" in platform.machine().lower():
            print("PointCloudCompare: Intel Processor detected")
            DLL_NAME = absolute_path + "/clib_mac_arm.so"
            print("PointCloudCompare: THIS case was not tested")
        else:
            print("PointCloudCompare: Unknown Mac Processor")
    else:
        print("PointCloudCompare: The operating system used is not supported for the Clibary")
        return None
    #DLL_NAME = absolute_path + "/haus_46.{:s}".format("dll" if sys.platform[:3].lower() == "win" else "so")


    try:
        c_function = cts.CDLL(DLL_NAME)
        print("PointCloudCompare: C Libary loaded succesfully")
        return c_function
    except:
        print("PointCloudCompare: C Libary cannot be loaded on this machine!")
        return None



#------------------------------------------------------------Minimal pointwise distance Helper Functions
def distance_calulation_min_pointwise(P, Q):
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
        returns an array with each pointwise distance stores
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
    #start = time.time()
    distance_values = min_pointwise_dist(P, rows_p, cols_p, Q, rows_q, cols_q)
    #end = time.time()

    #print(f"Time for Distance calculations: {end - start}")
    return distance_values, dealloc_array


def distance_calulation_min_pointwise_np(P, Q):
    """
    A function used to calculate the specified distance between two objects based on a numpy
    implementation
    ...

    Arguments
    -------
    P: np.array
        An array where each entry stores an x,y,z coordination of the point cloud
    Q: np.array
        An array where each entry stores an x,y,z coordination of the point cloud
    
    Return: np.array/int
        returns an array with each pointwise distance stores
    """
    dist = np.zeros((P.shape[0], 1))

    for p in range(P.shape[0]):
        minP = np.min(np.sum((P[p, :] - Q)**2, axis=1))
        dist[p, 0] = minP

    hd = np.sqrt(dist)
    return hd




#------------------------------------------------------------Jaccard Helper Functions
def generate_meshgrid(P, Q, res):
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
    
    #print(f"Size of grid: {grid.shape}")
    return grid,len_x,len_y,x_min,y_min,z_min


def jaccard_dist(bin_grid_p, bin_grid_q):
    """
    A function to calculate the jaccard similarity, defined as
    intersection/union
    ...

    Arguments
    -------
    bin_grid_p: np.array
        An array where each entry stores an index of an activated voxel of array P
    bin_grid_q: np.array
        An array where each entry stores an index of an activated voxel of array Q
    Return: float
        returns the jaccard similarity between P and Q
    """
    union = len(np.unique(np.append(bin_grid_p,bin_grid_q)))
    intersection = len(np.intersect1d(bin_grid_p,bin_grid_q))
    jaccard_coef = intersection / union
    return jaccard_coef


def bin_mask_idx(P, res, len_x, len_y, start_x, start_y, start_z):
    """
    A function to store the indices of all activated voxels (binary mask)
    ...

    Arguments
    -------
    P: np.array
        An array where each entry stores an x,y,z coordination of the point cloud
    res: float
        a float which specifies the resolution of the grid
    len_x: int
        the length of the grid array in x direction
    len_y: int
        the length of the grid array in y direction
    len_z: int
        the length of the grid array in z direction
    start_x: float
        the start point of the grid array in x direction
    start_y: float
        the start point of the grid array in y direction
    start_z: float
        the start point of the grid array in z direction
    Return: np.array
        returns an array with all the activated voxel indices

    """
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
    #print(f"time for P mask: {end-start}")

    #Binary Mask for Q matrix
    binary_mask_generator.argtypes = (
        np_mat_type(rows_q, cols_q), cts.c_size_t, cts.c_size_t,
        np_mat_type(rows_g, cols_g), cts.c_size_t, cts.c_size_t)
    
    start = time.time()
    int_grid_q_c = binary_mask_generator(Q, rows_q, cols_q, grid, rows_g, cols_g)
    int_grid_q = int_grid_q_c.flatten()
    bool_grid_q = int_grid_q.astype(bool)
    #print(f"time for Q mask: {end-start}")
  
    #TEMPLATE FOR GETTING BOOL AND GRID MASKS FOR ARBITRARY MASKS

    dealloc_array(int_grid_p_c)
    dealloc_array(int_grid_q_c)

    return


#BETA
def shift_grid_average_jaccard(P, Q, res, len_x, len_y, start_x, start_y, start_z, num_of_avg):
    """
    A function for shifting the grid in order to make the jaccard index more robust,
    because the location of the data points doesnt depend that much on their location relative to
    the grid location.
    The grid gets shifted from -res/2 to +res/2 in num_of_avg steps.
    ...

    Arguments
    -------
    P: np.array
        An array where each entry stores an x,y,z coordination of the point cloud
    Q: np.array
        An array where each entry stores an x,y,z coordination of the point cloud
    res: float
        the grid resolution (side length of the grid cubes)
    len_x: int
        the length of the grid array in x direction
    len_y: int
        the length of the grid array in y direction
    len_z: int
        the length of the grid array in z direction
    start_x: float
        the start point of the grid array in x direction
    start_y: float
        the start point of the grid array in y direction
    start_z: float
        the start point of the grid array in z direction
    num_of_avg: int
        how many shift operations are calculated
    Return: np.array
        returns the jaccard similarity for all shifts

    """

    shift_array = np.linspace(-0.5 + np.finfo(np.float64).eps, 0.5 - np.finfo(np.float64).eps, num_of_avg)
    jac_avg = np.zeros([7*num_of_avg, 1])
    counter = 0
    for shift in shift_array:
        shift = res*shift
        bin_grid_p = bin_mask_idx(P, res, len_x, len_y, start_x + shift, start_y, start_z)
        bin_grid_q = bin_mask_idx(Q, res, len_x, len_y, start_x + shift, start_y, start_z)
        jaccard_coef = jaccard_dist(bin_grid_p, bin_grid_q)
        jac_avg[counter] = jaccard_coef
        counter += 1
    for shift in shift_array:
        shift = res*shift
        bin_grid_p = bin_mask_idx(P, res, len_x, len_y, start_x, start_y + shift, start_z)
        bin_grid_q = bin_mask_idx(Q, res, len_x, len_y, start_x, start_y + shift, start_z)
        jaccard_coef = jaccard_dist(bin_grid_p, bin_grid_q)
        jac_avg[counter] = jaccard_coef
        counter += 1
    for shift in shift_array:
        shift = res*shift
        bin_grid_p = bin_mask_idx(P, res, len_x, len_y, start_x, start_y, start_z + shift)
        bin_grid_q = bin_mask_idx(Q, res, len_x, len_y, start_x, start_y, start_z + shift)
        jaccard_coef = jaccard_dist(bin_grid_p,bin_grid_q)
        jac_avg[counter] = jaccard_coef
        counter += 1
    for shift in shift_array:
        shift = res*shift
        bin_grid_p = bin_mask_idx(P, res, len_x, len_y, start_x + shift, start_y + shift, start_z)
        bin_grid_q = bin_mask_idx(Q, res, len_x, len_y, start_x + shift, start_y + shift, start_z)
        jaccard_coef = jaccard_dist(bin_grid_p, bin_grid_q)
        jac_avg[counter] = jaccard_coef
        counter += 1
    for shift in shift_array:
        shift = res*shift
        bin_grid_p = bin_mask_idx(P, res, len_x, len_y, start_x + shift, start_y, start_z + shift)
        bin_grid_q = bin_mask_idx(Q, res, len_x, len_y, start_x + shift, start_y, start_z + shift)
        jaccard_coef = jaccard_dist(bin_grid_p, bin_grid_q)
        jac_avg[counter] = jaccard_coef
        counter += 1
    for shift in shift_array:
        shift = res*shift
        bin_grid_p = bin_mask_idx(P, res, len_x, len_y, start_x, start_y + shift, start_z + shift)
        bin_grid_q = bin_mask_idx(Q, res, len_x, len_y, start_x, start_y + shift, start_z + shift)
        jaccard_coef = jaccard_dist(bin_grid_p, bin_grid_q)
        jac_avg[counter] = jaccard_coef
        counter += 1
    for shift in shift_array:
        shift = res*shift
        bin_grid_p = bin_mask_idx(P, res, len_x, len_y, start_x + shift, start_y + shift, start_z + shift)
        bin_grid_q = bin_mask_idx(Q, res, len_x, len_y, start_x + shift, start_y + shift, start_z + shift)
        jaccard_coef = jaccard_dist(bin_grid_p, bin_grid_q)
        jac_avg[counter] = jaccard_coef
        counter += 1
    return jac_avg




#------------------------------------------------------------Visualize Grid
def color_grid_mesh(bin_grid_p, bin_grid_q, vertices):
    """
    A function for assigning a color to each vertex of the grid based on the activation of the voxels.
    ...

    Arguments
    -------
    bin_grid_p: np.array
        An array where each entry stores an index of an activated voxel of array P
    bin_grid_q: np.array
        An array where each entry stores an index of an activated voxel of array Q
    vertices: np.array
        An array where every entry corresponds to the x,y,z location of a vertex
    Return: np.array
        returns an array where each entry corresponds to the color for a vertex

    """    

    color_array = np.zeros([len(vertices), 4], dtype=np.float32)
    
    union_color = [1,0,0,1] #red
    inters_color = [0,1,0,1] #green
    default_color = [0.6,0.6,0.6,1] #grey

    #assign color to every corner of every cube
    for i in range(len(vertices)):
        color_array[int(i)] = default_color        
    for i in bin_grid_p:
        color_array[int(i)*8:int(i)*8+8] = union_color
    for i in bin_grid_q:
        color_array[int(i)*8:int(i)*8+8] = union_color
    for i in np.intersect1d(bin_grid_p,bin_grid_q):
        color_array[int(i)*8:int(i)*8+8] = inters_color
    
    return color_array


def create_grid_mesh(grid, res):
    """
    A function used to create cubes around every grid point
    ...

    Arguments
    -------
    grid: np.array
        the array which has been used to create the binary mask
    res: float
        the specified resolution of the grid
    
    Return: np.array
        array with all vertices
            np.array
        array with all faces
            np.array
        array with the edges
    """


    vertices = np.zeros([len(grid)*8,3])
    faces = np.zeros([len(grid)*6,4])
    grid_idx = 0
    face_idx = 0
    
    #create a cube around each grid point
    for x,y,z in grid:
        
        #get location for corner points
        vertices[grid_idx + 0] = [x + res, y + res, z - res]
        vertices[grid_idx + 1] = [x + res, y - res, z - res]
        vertices[grid_idx + 2] = [x - res, y - res, z - res]
        vertices[grid_idx + 3] = [x - res, y + res, z - res]
        vertices[grid_idx + 4] = [x + res, y + res, z + res]
        vertices[grid_idx + 5] = [x + res, y - res, z + res]
        vertices[grid_idx + 6] = [x - res, y - res, z + res]
        vertices[grid_idx + 7] = [x - res, y + res, z + res]

        #link corner points to connected faces
        faces[face_idx + 0] = (grid_idx + 0, grid_idx + 1, grid_idx + 2, grid_idx + 3)
        faces[face_idx + 1] = (grid_idx + 4, grid_idx + 7, grid_idx + 6, grid_idx + 5)
        faces[face_idx + 2] = (grid_idx + 0, grid_idx + 4, grid_idx + 5, grid_idx + 1)
        faces[face_idx + 3] = (grid_idx + 1, grid_idx + 5, grid_idx + 6, grid_idx + 2)
        faces[face_idx + 4] = (grid_idx + 2, grid_idx + 6, grid_idx + 7, grid_idx + 3)
        faces[face_idx + 5] = (grid_idx + 4, grid_idx + 0, grid_idx + 3, grid_idx + 7)

        face_idx += 6
        grid_idx += 8

    faces = faces.astype(int)
    edges = []
    return vertices, edges, faces


def generate_consecutive_values(arr, N):
    """
    A function used to generate N consecutive entries for each element in arr
    ...

    Arguments
    -------
    arr: np.array
        an 1D array
    N: int
        the number for how many consecutive entries should be generated
    
    Return: np.array
        array with all consecutive entries
    """

    result = []
    for element in arr:
        for i in range(element, element + N):
            result.append(i)
    return result


def create_colored_object(mesh_obj, vertices, edges, faces, color_array, obj_name):
    """
    A function used to generate an object out of a mesh according to the parameter
    vertices, edges, faces. Afterward the object gets colored according to the color_array.
    The name of the object is stored in obj_name
    ...

    Arguments
    -------
    mesh_obj: ----
        the instance of a mesh
    vertices: np.array
        An array where each entry corresponds to x,y,z location of a vertex
    edges: np.array
        an array with the indices of the edges for the object
    faces: np.array
        an array with the indices of the faces for the object
    color_array: np.array
        an array which specifies the color for every vertex
    obj_name: string
        specifying the name of the object
    Return:
    """
    
    mesh_obj.from_pydata(vertices, edges, faces)
    mesh_obj.update()
    obj = bpy.data.objects.new(name = obj_name, object_data = mesh_obj)
    bpy.context.collection.objects.link(obj)
    bpy.context.view_layer.objects.active = obj
    
    if obj.data.vertex_colors.active == None:
        obj.data.vertex_colors.new()    
        
    color_map = obj.data.vertex_colors.active.data
    bpy.context.view_layer.objects.active = obj
    
    bpy.ops.object.mode_set(mode='VERTEX_PAINT')
    # setting colors for the object
    for loop in obj.data.loops:
        color_map[loop.index].color=list(color_array[loop.vertex_index])
    obj.select_set(True)
    return
