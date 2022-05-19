%% MATLAB script to demonstrate the functionality of the interface to the 
% parametric pinna model (PPM), including bi-directional communication with 
% Blender via Python scripts
%
% The PPM was developed at Austrian Research Institute (ARI), cf. [1-4].
%
% Dependencies:
% MATLAB (tested with version 9.11.0.1769968, R2021b) 
% MATLAB Computer Vision Toolbox (tested with version 10.1, R2021b)
% MATLAB class `quaternion` (version 1.8.0.0 by Mark Tincknell, downloaded on the fly 
%                            from File Exchange)
% Python (tested with version 3.9.12, March 23, 2022)
% Blender (tested with version: 3.1.2, branch: master, 
%          commit date: 2022-03-31 17:40, hash: cc66d1020c3b, type: release
%          build date: 2022-03-31, 23:39:57)
% Blender model ARI_PPM_v1 (armature and object definitions)
%
% Related functions : ppm_initialize, ppm_get_values, ppm_set_values, 
%                     ppm_evaluate
%
% [1] Pollack K.; Majdak P.; Brinkmann F.; Kreuzer W. (2021) Von Fotos zu 
%     personalisierter räumlicher Audiowiedergabe. e & i Elektrotechnik und 
%     Informationstechnik.
% [2] Pollack K.; Majdak P.; Furtado H. (2021) Evaluation of Pinna Point 
%     Cloud Alignment by Means of Non-Rigid registration Algorithms. Audio 
%     Engineering Society (AES) 150th convention.
% [3] Pollack K.; Majdak P. (2021) Evaluation of a Parametric Pinna Model 
%     for the Calculation of Head-Related Transfer Functions. Immersive and 
%     3D Audio (I3DA) conference.
% [4] Pollack K.; Majdak P.; Furtado H. (2020) A Parametric Pinna Model for 
%     the Calculations of Head-Related Transfer Functions. Proceedings of 
%     Forum Acusticum 2020, Lyon. S. 1357-1360.

% Versions and contributors:
% 0.8 and above: Florian Pausch (2022)
% 0.7 and below: Mantas Tamulionis (2021)
%
% Current release version: 1.1.0

clear; close all; clc

%% initialize ppm
name_blender_file = 'PPM_modified_v1.blend';

ppm = ppm_initialize(...
    'path_blender_file',fullfile(pwd,'result'),...
    'name_blender_file',name_blender_file,...
    'verbose_level',2,...
    'auto_delete',true);

%% get parameter values from specified Blender file and export mesh
[ppm,val] = ppm_get_values(ppm,...
    'type','Rotation',...
    'name','Size-Bendy',...
    'axis',[]);

% display the selected parameter subset
if ppm.ini.verbose_level>0
    disp(val)
end

%% set and apply parameter value to specified Blender file
% type 'ppm.parameters' to get a list of all parameters
% type 'help ppm_set_values' to obtain information about parameter limits 
ppm = ppm_set_values(ppm,...
    'type','Rotation',...
    'name','Size-Bendy',...
    'axis','X',... 
    'val',5,...
    'range',4,...
    'itr',1,...
    'instruction_mode','abs', ...
    'rotation_mode','XYZ',...
    'image',true,...
    'mesh',true,...
    'set_cam',true,...
    'cam_loc',[-10, 200, 5],...
    'cam_rot',[90, 0, 180]);

%% compare the resulting mesh to the specified target mesh
%  and evaluate its fit based on the Hausdorff distance, plot result
name_mesh_target = 'PPM_default_v1.ply';

ppm = ppm_evaluate(ppm,...
    'path_mesh_target',ppm.ini.path.data,...
    'name_mesh_target',name_mesh_target,...
    'caxis_min',0,...
    'caxis_max',5);



