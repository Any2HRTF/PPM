%% MATLAB script to demonstrate the functionality of the interface to the 
% parametric pinna model (PPM), including bi-directional communication with 
% blender via Python scripts
%
% The PPM was developed at Austrian Research Institute (ARI), cf. [1-4].
%
% Dependencies:
% blender (tested with version: 3.1.2, branch: master, 
%          commit date: 2022-03-31 17:40, hash: cc66d1020c3b, type: release
%          build date: 2022-03-31, 23:39:57)
% blender model ARI_PPM_v1 (armature and object definitions)
% Python  (tested with version: 3.10.2 (main, Jan 27 2022, 08:34:43) 
%          [MSC v.1928 64 bit (AMD64)])
% MATLAB Computer Vision Toolbox (tested with Version 10.1, R2021b)
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
% Current release version: 1.1.0 (see release_notes.txt)

clear; close all; clc

%% initialize ppm
name_blender_file = 'PPM_modified_v1.blend';

ppm = ppm_initialize(...
    'path_blender_file',fullfile(pwd,'result'),...
    'name_blender_file',name_blender_file,...
    'verbose_level',1,...
    'auto_delete',false);

%% get parameter values from specified blender file and export mesh
[ppm,val] = ppm_get_values(ppm,...
    'type','Location',...
    'name','Size-Bendy',...
    'axis',[]);

% display the selected parameter subset
if ppm.ini.verbose_level>0
    disp(val)
end

%% set and apply parameter value to specified blender file
% type 'ppm.parameters' to get a list of all available parameters
% type 'help ppm_set_values' to obtain information about parameter limits 
ppm = ppm_set_values(ppm,...
    'type','Location',...
    'name','Size-Bendy',...
    'axis','X',... 
    'val',2,...
    'range',10,...
    'itr',1,...
    'instruction_mode','abs');

%% compare the resulting mesh to the specified target mesh
%  and evaluate its fit based on the Hausdorff distance, plot result
name_mesh_target = 'PPM_default_v1.ply';

ppm = ppm_evaluate(ppm,...
    'path_mesh_target',ppm.ini.path.data,...
    'name_mesh_target',name_mesh_target,...
    'caxis_min',0,...
    'caxis_max',5);



