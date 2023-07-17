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

## Metric
### Minimal pointwise distance to Ref
This distance is defined by the minimal pointwise distance from each data point of the PPM to the reference mesh. Therefore for each point in the PPM the distances to all the points of the ground truth mesh are calculated and the minimum is stored. As a result, this calculation returns N values, where in is the length of the PPM array. The PPM object gets then colored accoring to the individual distances. The color scheme is as follows:<br>
<img src="colorbar_test1.jpg" width="828" align="center"/>
