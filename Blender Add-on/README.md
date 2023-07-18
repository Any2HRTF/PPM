# Installation instructions

1) Go to the [releases](https://github.com/Any2HRTF/PPM/releases) page and download the latest release (Blender_Add-on_X.x).
2) In Blender, go to Edit -> Preferences, click the button "Install...", select the previously downloaded zip file, click "Install Add-on", and enable the Add-on "Hausdorff distance" by activating the check box.
3) The Add-on panel "Hausdorff" is now accessible via the UI below the 'Tools' and 'View' panels in the top right corner of the viewport window.   

# Usage

Open a BLEND file containing the PPM to be manually aligned with a target mesh. Use the Hausdorff Add-on for intermediate validation of the current geometric registration error. To do so, follow the steps below:
1) Under "theReferenceObject", select the target mesh.
2) Select the PPM.
3) Click on "Distance visualization" to calculate and visualise the pointwise minimum distances between the PPM and the target mesh. Note that the calculated minimum-distance values and the visualisation correspond to the evaluation direction (PPM vs. target mesh or target mesh vs. PPM) resulting in the greater maximum distance value.
4) After a few seconds, the pointwise minimum distances are calculated, and displayed in Blender's Vertex-Paint mode.
5) Switch back to "Pose mode" and continue with your manual registration.
6) Repeat steps 3-5 until the geometric error is below the requirements.
