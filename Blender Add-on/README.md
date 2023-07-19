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
To gain intuition: If you compute the Jaccard from A to A, or you choose the resolution wider than the boundary box of the data, the result is 1. So the higher the Jaccard/Dice, the more similar the two meshes are.

## Tips and Workarounds
1) The "Calculation" button is only visible in the OBJECT Mode. Furthermore an Object must be selected.
2) If changes are made to the script, the scripts can be reloaded by clicking on the blender icon (top left) -> System -> Reload scripts.
3) The colored visualisation for the "Minimal pointwise distance to Ref" can only be seen in the VERTEX Mode.
4) Go to Window -> Toggle System Console to open a terminal showing Python print commands.


# Code and functions
The overall add on consists of 3 Python Files, one init file, one for the panel and one for all the calculation.
