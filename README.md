# PPM interface #

MATLAB-Python-Blender interface for bi-directional communication with the 
    parametric pinna model (PPM) via Python scripts (module `bpy`) using Matlab  

## Main Matlab scripts and functions ##

Get to know the functionality of the PPM interface by exploring `ppm_demo.m`, which calls the main functions listed below:
- `ppm_initialize()`
- `ppm_get_values()`
- `ppm_set_values()`
- `ppm_evaluate()`

## Python scripts ##
The following Python scripts are called within `ppm_get_values()`, and `ppm_set_values()` -> `ppm_blender_execute()`, respectively: 

- `get_values_and_export_mesh_v1.X.X.py` 
- `set_values_and_export_mesh_v1.X.X.py` 

## Dependencies ##
- MATLAB (tested with version 9.11.0.1769968, R2021b) 
- MATLAB Computer Vision Toolbox (tested with version 10.1, R2021b; only used in `ppm_evaluate()`)
- Custom MATLAB class `quaternion` (version [1.8.0.0](https://www.mathworks.com/matlabcentral/fileexchange/33341-quaternion) by Mark Tincknell, downloaded 
                           on the fly)
- Blender (tested with version: [3.1.2](https://www.blender.org/download/releases/3-1/), branch: master, 
         commit date: 2022-03-31 17:40, hash: cc66d1020c3b, type: release
         build date: 2022-03-31, 23:39:57, containing the Blender Python API)
- Blender model ARI_PPM_v1 (armature and object definitions)

## Releases ##
The latest release version can be downloaded from the [releases page](https://github.com/Any2HRTF/PPM/releases). Please note that the development of the MATLAB-Python-Blender interface is stopped after release version 1.6.0, and continued only for the Python-Blender PPM interface. Bug fixes for the MATLAB-Python-Blender PPM interface will be available on the branch "matlab".

## References ##
The PPM was developed at the Acoustics Research Institute (ARI) of the 
Austrian Academy of Sciences, Vienna, Austria [1-4].

1.  Pollack K.; Pausch F.; Majdak P. (2022) [Parametric pinna model for a 
    realistic representation of listener-specific pinna geometry](https://www.researchgate.net/profile/Florian-Pausch/publication/366977010_Parametric_pinna_model_for_a_realistic_representation_of_listener-specific_pinna_geometry/links/63bc77a1097c7832caa1ffd2/Parametric-pinna-model-for-a-realistic-representation-of-listener-specific-pinna-geometry.pdf?origin=publicationDetail&_sg%5B0%5D=CFr20BsHvQ3k0OmR_gN-XEXvU_IUp2yohXbvrqEzLIKyydtYST3pOQd_ec4Hj_7Dla8Ma5PNwHlp8t0OFyNlXw.vRk-HUSZsPec5Y3v5TJ0n8X0UTQrsWDRO85zyvQJrrni5DtuPXpOFj5yNTsWR3OUDbtwXTIp2qGWwbMbu2O6-w&_sg%5B1%5D=FAr7AoGW3im4MzlZvfT29nywMswK_uXAxcn-6CSJoTZF5IvSbVCKGgdSYxp7jwb1phk1ZGDndKDpqXh0qo_V0F-m2QqukrE0L_4AwshB1m5k.vRk-HUSZsPec5Y3v5TJ0n8X0UTQrsWDRO85zyvQJrrni5DtuPXpOFj5yNTsWR3OUDbtwXTIp2qGWwbMbu2O6-w&_iepl=&_rtd=eyJjb250ZW50SW50ZW50IjoibWFpbkl0ZW0ifQ%3D%3D), 
    Proceedings: A21, Virtual Acoustics, ICA 2022 (International Congress 
    on Acoustics); Gyeongju, S. 168-178. 
 2. Pollack K.; Majdak P.; Brinkmann F.; Kreuzer W. (2021) [Von Fotos zu 
    personalisierter räumlicher Audiowiedergabe](https://link.springer.com/article/10.1007/s00502-021-00891-4). e & i Elektrotechnik und 
    Informationstechnik, S. 250-255.
 3. Pollack K.; Majdak P. (2021) [Evaluation of a Parametric Pinna Model 
    for the Calculation of Head-Related Transfer Functions](https://ieeexplore.ieee.org/abstract/document/9610885). Immersive and 
    3D Audio (I3DA) conference.
 4. Pollack K.; Majdak P.; Furtado H. (2020) [A Parametric Pinna Model for 
    the Calculations of Head-Related Transfer Functions](https://hal.science/hal-03235345/document). Proceedings of 
    Forum Acusticum 2020, Lyon. S. 1357-1360.
