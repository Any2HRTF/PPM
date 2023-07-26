1) Import the target mesh (*.stl, *.ply) into Blender (which already contains the default PPM v1 with armature definitions: PPM_default_v1.blend) and hide the PPM

2) Center the pinna-plus-head (PH) mesh: for example, the horizontal plane corresponds to the Frankfurt plane (preferably, use a vertical shift so that horizontal plane runs through the ear-canal centre)
-> Convention 1: Rotate the PH mesh so that
- the view vector corresponds to the global +x-axis (default viewing 				direction), 
- the up vector corresponds to the global +z-axis,
- the interaural axis corresponds to the y-axis (increasing positively from left to right ear)

3) Save the PH mesh as blender file (*_ph_ini.blend)

4) Remove head mesh, preserve left and right pinna-only meshes
-> Convention 2: Preserve ear offsets in y-direction
-> Remove mesh regions of the pinna that are superfluous with respect to the PPM template mesh (such superfluous mesh parts will only increase the geometric error at a later evaluation stage)
-> Save each pinna-related file separately (*_left_ear_ini.blend, *_right_ear_ini.blend), although the PPM is currently implemented for the left ear only

5) Save another Blender file for the aligned PPM (*_left_ear_aligned_ppm_v1) -> v1 corresponds to the PPM armature definitions in the current PPM-interface version

6) Start the manual alignment process:
		a) Start with the alignment of global parameters (i.e. Size-Bendy: Location, 			Rotation, anisotropic scaling)
		b) Continue with local parameters

Attention: Stick to the parameter conventions and their available degrees of freedom as presented in our latest ICA publication (https://www.researchgate.net/publication/366977010_Parametric_pinna_model_for_a_realistic_representation_of_listener-specific_pinna_geometry).

Example 1: Anisotropic scaling is only allowed for Size-Bendy.
Example 2: Axis-dependent manipulation of location and rotation is only 	´			allowed for the start and end points of bendy bones. 				Translation of the bendy bones themselves is not allowed!
c) Fine-tune your model by modifying the shape-key parameters.

7) Iteratively check the geometric error (pointwise Hausdorff distance) by running the PPM-interface functions ppm_evaluate(), which is part of ppm_demo.m, or ppm_evaluate_multiple_meshes().

8) Try to obtain a mean geometric error in terms of the pointwise Hausdorff distance below 1 mm with an error distribution that is skewed towards 0 (see Figure 6 in the publication above). Be especially careful when fitting the perceptually most relevant pinna regions (i.e. cavum-conchae depth, cymba-conchae depth, fossa triangularis), see https://asa.scitation.org/doi/full/10.1121/10.0004128!

Things to mention: 
    1. Since it is mostly a visual manual alignment procedure, it is useful to contrast the color of the PPM against the targest mesh. This can be achieved by selecting the PPM mesh in Blender Object Mode, clicking on the “Material Properties” tab (lower right corner, ), click on “New”, and add a color under “Viewport Display”.
    2. Once the desired part of the armature (green skeleton attached to the PPM) has been selected in Blender Pose Mode, the most important keyboard short cuts are: “G” to modify the location/translation of start/end points, “R” to rotate start/end points, and “S” to scale bendy bones.
    3. To modify the shape keys, select “R_mean_v13” under “ARI_PPM_v1” (), and click on the tab “Object Data Properties” (). Under “Shape Keys” you can now change the corresponding value for each shape key, limited as defined in the file shape_key_limits_v1.mat in the PPM Matlab-Blender interface in the folder “default”.

