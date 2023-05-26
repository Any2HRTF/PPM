# PPM interface #

MATLAB-Python-Blender interface for bi-directional communication with the 
    parametric pinna model (PPM) in Matlab via Python scripts (module `bpy`) 

## Main Matlab scripts and functions ##
- `ppm_demo.m`
- `ppm_initialize()`
- `ppm_get_values()`
- `ppm_set_values()`
- `ppm_evaluate()`

## Python scripts ##
- `get_values_and_export_mesh_v1.X.X.py` 
- `set_values_and_export_mesh_v1.X.X.py` 

## Dependencies ##
- MATLAB (tested with version 9.11.0.1769968, R2021b) 
- MATLAB Computer Vision Toolbox (tested with version 10.1, R2021b; only used in `ppm_evaluate()`)
- MATLAB class `quaternion` (version 1.8.0.0 by Mark Tincknell, downloaded 
                           on the fly from [MATLAB File Exchange]([url](https://www.mathworks.com/matlabcentral/fileexchange/33341-quaternion)))
- Blender (tested with version: [3.1.2](https://www.blender.org/download/releases/3-1/), branch: master, 
         commit date: 2022-03-31 17:40, hash: cc66d1020c3b, type: release
         build date: 2022-03-31, 23:39:57)
- Blender model ARI_PPM_v1 (armature and object definitions)

The PPM was developed at the Acoustics Research Institute (ARI) of the 
Austrian Academy of Sciences, Vienna, Austria [1-4].

1.  Pollack K.; Pausch F.; Majdak P. (2022) Parametric pinna model for a 
    realistic representation of listener-specific pinna geometry, 
    Proceedings: A21, Virtual Acoustics, ICA 2022 (International Congress 
    on Acoustics); Gyeongju, S. 168-178. 
 2. Pollack K.; Majdak P.; Brinkmann F.; Kreuzer W. (2021) Von Fotos zu 
    personalisierter räumlicher Audiowiedergabe. e & i Elektrotechnik und 
    Informationstechnik.
 3. Pollack K.; Majdak P.; Furtado H. (2021) Evaluation of Pinna Point 
    Cloud Alignment by Means of Non-Rigid registration Algorithms. 150th 
    Convention of the Audio Engineering Society.
 4. Pollack K.; Majdak P. (2021) Evaluation of a Parametric Pinna Model 
    for the Calculation of Head-Related Transfer Functions. Immersive and 
    3D Audio (I3DA) conference.
 5. Pollack K.; Majdak P.; Furtado H. (2020) A Parametric Pinna Model for 
    the Calculations of Head-Related Transfer Functions. Proceedings of 
    Forum Acusticum 2020, Lyon. S. 1357-1360.

The latest release version can be downloaded from the [releases page](https://github.com/Any2HRTF/PPM/releases).
