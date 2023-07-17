# Installation instructions

1) Go to the [releases](https://github.com/Any2HRTF/PPM/releases) page and download the latest release (Blender_Add-on_X.x).
2) In Blender, go to Edit -> Preferences  -> Add-ons. Click the button "Install...", select the previously downloaded zip file, click "Install Add-on", and enable the Add-on "PointCloudCompare" by activating the check box.
3) The Add-on panel "PointCloudCompare" is now accessible via the UI below the 'Tools' and 'View' panels in the top right corner of the viewport window.   

# Usage
## General
Open a BLEND file containing the PPM to be manually aligned with a target mesh. Use the PointCloudCompare Add-on for intermediate validation of the current geometric registration error. To do so, follow the steps below:
1) Under "Reference", select the target mesh.
2) Select PPM by clicking on the corresponding object.
3) Under Metric select the desired distance/error measurement.
4) Click on "Calculate" to perform the operation.

## Metrics
### Minimal pointwise distance to Ref
This distance is defined by the minimal pointwise distance from each data point of the PPM to the reference mesh. Therefore for each point in the PPM the distances to all the points of the ground truth mesh are calculated and the minimum is stored. As a result, this calculation returns N values, where in is the length of the PPM array. The PPM object gets then colored accoring to the individual distances. The color scheme is as follows:
<center>
<img src="colorbar_test1.jpg" width="800" />
</center>

### Minimal pointwise distance from Ref
Since this metric doesn't lead to the same result, when calculating from A to B and from B to A, there is the option of calculating the minimal pointwise distance from the ground truth mesh to the PPM. The result is an array of length M, where M is the length of the ground truth mesh. <br>  <br>
Comparing these two measurements can provide information on outliers.
Several different statistics are then displayed on the add-on, containing the minimum, maximum (hausdorff distance), median and mean of the result array.


### Jaccard/Dice Index
In general the jaccard index of two discrete sets A and B is defined as: <br>
<center> <p> $J(A,B) = \dfrac{A \cap B}{A \cup B}$ </p> </center>
The dice coefficient is strongly related to the jaccard index: <br>
<center> <p>$DSC = \dfrac{2 \cdot J(A,B)}{J(A,B) + 1}$ </p> </center>
To obtain a discrete set from the three dimensional point cloud a voxelisation was performed. The spanned space from the two meshes was subdivided into small cubes. Each cube can be seen as a boolean placeholder, which is True when an data point lies within the cube and false outerwise. This is down for each of the two meshes. The obtained binary masks are then treated as a discrete sets (this is possible because both voxelised meshes share the same grid). The intersection operation (logical and) is hence the number of "true cubes" which occur in both sets. The union operation (logical or) is defined as the total number of different "true cubes" in both sets. <br>
The "resolution" paramater in the add on specifies the grid resolution for the voxelisation process. The "resolution" itself is the half length of each cube. The "resolution" value can be interpreted as: The minimum distance at which differences between the target mesh and the PPM are detected. <br>
To gain intuition: If one computes the jaccard from A to A or chooses the resolution wider than the boundary box of the data, the result is 1. Therefore the higher the jaccard/dice the more similar are the two meshes.

## Tips and Workarounds
1) The "Calculation" Button is only visible in the OBJECT Mode. Furthermore an Object must be selected.
2) If changes in the script are performed, the scripts can be reloaded by clicking on the blender icon (top left) -> System -> Reload scripts.
3) The colored visualisation for the "Minimal pointwise distance to Ref" can only be seen in the VERTEX Mode.
4) Under Window -> Toggle System Console a terminal can be opened, which shows Python print commands.
