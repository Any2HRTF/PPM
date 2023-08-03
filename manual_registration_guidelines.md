# Guidelines to manually register the PPM to a pinna-only mesh

## Pre-processing steps

1) Open `PPM.blend`, containing the PPM with default parameter values and armature definitions.

2) Import the mesh (e.g., in `stl` or `ply` formats) the PPM needs to be registered to into this file, and hide the PPM. Since the imported mesh likely contains the head and parts of the upper body, we refer to it as pinna-plus-head (PH) mesh below.

3) Center the PH mesh as per the instructions given below:
* *Convention 1*: Rotate and translate the PH mesh so that
	* the center of the interaural axis corresponds to the origin of the world coordinate system
 	* the horizontal plane corresponds to the Frankfurt plane (setting the pitch angle of the head), but with an additional vertical shift applied along the z-axis so that the plane runs through the ear-canal centres,
	* the view vector corresponds to the global positive x-axis (default viewing direction), 
	* the up vector (orthogonal to the view vector) corresponds to the global positive z-axis, and
	* the interaural axis corresponds to the y-axis (increasing positively from the right to the left ear)

4) Save the PH mesh adapted in this way as `blend` file (*_ph_ini.blend).

5) Remove all unneeded parts from the PH mesh, e.g., head and shoulders. Only preserve the left and right pinna-only (PO) meshes. Double-check if all unwanted edges, vertices and faces have been deleted.
* *Convention 2*:
	* Preserve the global rotations and the global offsets in y-direction of the PO meshes.
	* Remove mesh regions of the PO meshes that are not contained in the PPM, e.g., more extended parts at the transition to the removed head mesh. Such mesh parts cannot be properly registered anyway and will likely increase the geometric error when registering the PPM to the PO mesh.
	* Remove the right PO mesh and save the `blend` file (*_left_ear_ini.blend).
 	* Undo the last removal step, remove the left PO mesh instead, and save the `blend` file (*_right_ear_ini.blend). This file is saved for the sake of completeness only as the PPM is currently only implemented for registering left PO meshes.

6) Save another `blend` file for the registration process (*_left_ear_aligned_ppm_v2). Note that "v2" corresponds to the PPM armature definitions as used in version v2.x.x of the [PPM interface](https://github.com/Any2HRTF/PPM/tree/main).

## Blender add-on to visualise the geometric errors

Install the [Blender Add-on](https://github.com/Any2HRTF/PPM/tree/main/Blender%20Add-on) following the installation instructions, and use it as part of the manual registration process described below.

## Manual PPM registration

1) The aim of the manual PPM registration is to modify the global PPM parameters, i.e., the axis-dependent location, rotation and scale, and the local PPM parameters, e.g, the axis-dependent location of Helix_up-Start, so that the resulting PPM instance approximates the target PO mesh with a minimal geometric error (e.g., in terms of a minimum pointwise distance between the modeled and the target point cloud). Note that, apart from the pre-processing steps described in the section above, the target PO mesh is not subjected to any further modifications, i.e., changes of location, rotation and scale. 

2) Since the registration procedure is largely a visual one, it is useful to contrast the color of the PPM against the PO mesh. This can be achieved by selecting the template mesh of the PPM in Blender Object Mode, clicking on the tab “Material Properties” (lower right corner), clicking on “New”, and adding a color under “Viewport Display”.

3) Once the desired part of the armature (green skeleton attached to the PPM) has been selected in Blender Pose Mode, the most important keyboard shortcuts are:
   * “G” to modify the location/translation of start/end points,
   * “R” to rotate start/end points, and
   * “S” to scale the bendy bones.

4) To modify the shape keys, select “Mesh” (under “Armature”), and click on the tab “Object Data Properties”. Under “Shape Keys”, you can change the corresponding value for each shape key within the pre-defined limits.

5) Start the manual alignment process:
	* Start by modifying the global parameter dimensions (i.e., Parent-Bendy: location, rotation, anisotropic scaling),
	* continue with local parameter dimensions (location, rotation, isotropic scaling), and
 	* modify the shape keys for fine-tuning.

*Attention*: Stick to the conventions regarding the available degrees of freedom of PPM parameters as presented by [Pollack et al. (2022)](https://www.researchgate.net/publication/366977010_Parametric_pinna_model_for_a_realistic_representation_of_listener-specific_pinna_geometry).

Example 1: Anisotropic scaling is only allowed for Parent-Bendy.

Example 2: Axis-dependent manipulations of location and rotation parameter dimensions are only allowed for the start and end points of bendy bones, i.e., the control bones. Translating the bendy bones themselves is not allowed!

6) Iteratively check the visualised geometric errors using the [Blender Add-on](https://github.com/Any2HRTF/PPM/tree/main/Blender%20Add-on), and also account for the calculated error metrics (e.g., the mean/median of point-wise minimum distances, the Jaccard index, and the Dice similiarity coefficient).

7) Aim for geometric errors with mean and median pointwise minimum distances below 1 mm, and an error distribution skewed towards 0 (see [Figure 6](https://www.researchgate.net/publication/366977010_Parametric_pinna_model_for_a_realistic_representation_of_listener-specific_pinna_geometry). Try to achieve a particularly low error in the perceptually most relevant pinna regions (i.e., cavum conchae depth, cymba conchae, fossa triangularis), see [Stitt & Katz (2021)](https://asa.scitation.org/doi/full/10.1121/10.0004128).

