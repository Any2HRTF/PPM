# Installation instructions

1) Go to the [Release](https://github.com/Any2HRTF/PPM/releases) page and download the latest release (Blender_Add-on_X.x).
2) In Blender, go to Edit -> Preferences  -> Add-ons. Click on the "Install..." button, select the previously downloaded zip file, click on "Install Add-on", and enable the "PointCloudCompare" Add-on by activating the checkbox.
3) The Add-on panel "PointCloudCompare" is now accessible from the UI below the 'Tools' and 'View' panels in the top right corner of the viewport window.   

# Usage
## General
Open a BLEND file containing the PPM to be manually aligned with a target mesh. Use the PointCloudCompare Add-on to interactively validate the current geometric registration error. To do so, follow the steps below:
1) Under "Reference", select the target mesh.
2) Select PPM by clicking on the corresponding object.
3) Under Metric select the desired distance/error measurement.
4) Click on "Calculate" to perform the operation.

## Metrics
### Minimal pointwise distance to Ref
This distance is defined by the minimal pointwise distance from each data point of the PPM to the reference mesh. Therefore for each point in the PPM the distances to all the points of the ground truth mesh are calculated and the minimum is stored. As a result, this calculation returns N values, where in is the length of the PPM array. The PPM object gets then colored according to the individual distances. The color scheme is as follows:
<center>
<img src="colorbar_test1.jpg" width="800" />
</center>

### Minimal pointwise distance from Ref
Since this metric doesn't lead to the same result, when calculating from A to B and from B to A, there is the option of calculating the minimal pointwise distance from the ground truth mesh to the PPM. The result is an array of length M, where M is the length of the ground truth mesh. <br>  <br>
Comparing these two measurements can provide information on outliers.
Several different statistics are then displayed on the add-on, including the minimum, maximum (Hausdorff distance), median and mean of the result array.


### Jaccard/Dice Index
In general the Jaccard index of two discrete sets A and B is defined as: <br>
<center> <p> $J(A,B) = \dfrac{A \cap B}{A \cup B}$ </p> </center>
The dice coefficient is strongly related to the jaccard index: <br>
<center> <p>$DSC = \dfrac{2 \cdot J(A,B)}{J(A,B) + 1}$ </p> </center>
To obtain a discrete set from the three dimensional point cloud a voxelisation was performed. The spanned space from the two meshes was subdivided into small cubes. Each cube can be seen as a boolean placeholder, which is True when an data point lies within the cube and false outerwise. This is down for each of the two meshes. The obtained binary masks are then treated as a discrete sets (this is possible because both voxelised meshes share the same grid). The intersection operation (logical and) is hence the number of "true assigned cubes" which occur in both sets. The union operation (logical or) is defined as the total number of different "true assigned cubes" in both sets. The Voxelisation can be seen as rounding each of the 3 coordinates to a given grid and if points from both data sets get discretized to the same point, they count as "intersection". <br>
The "resolution" paramater in the add on specifies the grid resolution for the voxelisation process. The "resolution" itself is half the length of each cube. The "resolution" value can be interpreted as: The minimum distance at which differences between the target mesh and the PPM are detected. <br>
To gain intuition: If you compute the Jaccard from A to A, or you choose the resolution wider than the boundary box of the data, the result is 1. So the higher the Jaccard/Dice, the more similar the two meshes are. <br>
Since the Voxelisation is highly depended on the location of the data point relative to the grid, there is also an averaging performed. This is done by shifting the grid in each direction from - gridlength/2 to + gridlength/2 in 10 steps. For each shift the jaccard similarity is calculated. After doing this for every possible shift the mean is calculated and displayed at "Avg Jaccard". The used function for obtaining the array of all different jaccard similarities is called

```python
shift_grid_average_jaccard()
```

#### Visualize Grid Cube
In order to get an visual feedback of what is happening in the background, there is a checkbox "visualize grid cube". Once this checkbox is ticked, the option selected in the "Type" menu gets displayed. The options are: "Visualize the whole grid", "Visualize just intersection/union","Visualize the 2 quantized meshes".
When "Visualize the whole grid" is chosen, every single voxel is displayed. This can be used to check if the boundary box is ok or the gain intuition about the amount of voxels in the grid. The voxel contributing to the Union get colored red, and those contributing to the intersection get colored green. When "Visualize just intersection/union" is chosen, only active voxels are displayed (The get colored like before). This might be helpful to detect problematic regions, where the fitting is not good yet. The last option "Visualize the 2 quantized meshes" creates two new object where each representes the quantized mesh of one layer. The reference gets colored green and the active object gets colored red. 

## Tips and Workarounds
1) The "Calculation" button is only visible in the OBJECT Mode. Furthermore an Object must be selected.
2) If changes are made to the script, the scripts can be reloaded by clicking on the blender icon (top left) -> System -> Reload scripts.
3) The colored visualisation for the "Minimal pointwise distance to Ref" can only be seen in the VERTEX Mode.
4) Go to Window -> Toggle System Console to open a terminal showing Python print commands.
5) Do not store data on the layers "Grid_visualization", "Grid_object1","Grid_object2", because these layers get created by the plugin itself and might get overwritten!


# Code and functions
The overall add on consists of 3 Python Files, one init file, one for the panel and one for all the calculation. <br>
In addition to the .py files, there are also compiled executables (.dll and .so) which are used to speed up the min point distance calculation. The .py files try to load the compiled files, if that fails a pyhton implemenation is loaded, which is a little bit slower.
If this case happens on your machine, please feel free to open an issue in this repository with your operating system and your architecture. In this compiled C file there is also a function called
```python
binaryMaskGenerator()
```
, which can be used to calculate the Jaccard index for non-regular grids.
(eg. using a grid with more grid points around more important areas could be used, which results in a sort of "weighting". eg more points near the cavum conchae, less near the lobulus). For further interest, there is a template function 
```python
map_points_to_grid()
```
in the "PointCloudCompare_PT_op.py".
For adding more Jaccard resolution, go to the "JaccardResolutionSelector" class and add another element to the items list. <br>
For implementing another metric, start by adding a new option in the DistanceSelector class and implementing the algorithmn in the execute method of the "VisualizeDistance" class (You will find if-switch cases with all the options). However in order to visualize the results on the panel, open the "PointCloudCompare_PT_pnl.py" file, go to the draw method of the INTERFACE_PT_panel class
and again you will find "if" cases with the selected option.
If your new metric stores different statistics, they can be added by creating a new Attribute in the "DistanceProperty" class. A new set of statistics can be created by
```python
stats_distance = context.scene.distances.add()
```
Afterwards you can access the stored values in "stats_distance" from the "PointCloudCompare_PT_pnl.py" in the draw method and print the values to the addon.


## Documentation for relevant Helper functions
### Minimal pointwise distance  
Minimal pointwise distance calulation based on the C compiled file
```python
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
```
Minimal pointwise distance calulation fallback based on numpy
```python
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
```
  ### Jaccard/Dice
```python
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
```
### Visualize the Voxelisation grid
```python
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
```
