function ppm = ppm_initialize(varargin)
%ppm_initialize - Initialize the parametric pinna model (PPM) structure
%                 array
%
% Usage: 
%   ppm = ppm_initialize(varargin)
%
% Input parameters (key/value pairs):
%
%   Required
%     'path_blender_file'   : Path to Blender file to be modified [string]
%     'name_blender_file'   : Name of Blender file to be modified [string] 
%
%   Optional
%     'path_default'        : Path to default folder [string]
%                             (default: fullfile(pwd,'default')) 
%     'path_data'           : Path to data folder [string]
%                             (default: fullfile(pwd,'data')) 
%     'path_python'         : Path to folder containing Python scripts [string]
%                             (default: fullfile(pwd,'python')) 
%     'path_result'         : Path to result folder [string]
%                             (default: fullfile(pwd,'result')) 
%     'path_external'       : Path to folder containing external
%                             classes, functions, scripts etc. [string]
%     'name_parameter_file' : Name of file containing default parameter definitions 
%                             in default folder [string] 
%                             (default: 'parameter_defaults_v1')
%     'name_limit_file'     : Name of file containing shape key parameter limits 
%                             in default folder [string] 
%                             (default: 'shape_key_limits_v1')
%     'auto_delete'         : Automatically delete previous results in result 
%                             folder [logical], (default: false)
%     'verbose_level'       : Verbosity level [double] 
%                             0: quiet (errors only)
%                             1: info (default) 
%                             2: debug
%
% Output parameters:
%
%   ppm : initialized PPM structure array [struct]
%         .ini
%             .blender_file     : fullfile(path_blender_file, ...
%                                          name_blender_file) [string]
%             .verbose_level
%             .path             : paths to default, data, python, result,
%                                 and external folders, and blender_exe [string]
%             .sysarch          : automatically determined system [string]
%                                 architecture (e.g. win64)
%             .shape_key_limits : limits of PPM parameters of type 
%                                 'Shape_key' [cell]
%         .parameters           : initial parameter values as per 
%                                 fullfile(ppm.ini.path.default,...
%                                       'parameter_defaults_v1.mat') [cell]
%
% ATTENTION: The Blender file to be modified needs to be saved in "Object Mode"
%            in Blender with visible armature and object definitions
%            in viewport.
%
% Related functions : ppm_get_values, ppm_set_values, ppm_evaluate

% #Author: Florian Pausch (2022)

%% parse input arguments
p = inputParser;

addOptional(p,'path_blender_file',[]);
addOptional(p,'name_blender_file',[]);
addOptional(p,'path_default',fullfile(pwd,'default'));
addOptional(p,'path_data',fullfile(pwd,'data'));
addOptional(p,'path_python',fullfile(pwd,'python'));
addOptional(p,'path_result',fullfile(pwd,'result'));
addOptional(p,'path_external',fullfile(pwd,'external'));
addOptional(p,'auto_delete',false);
addOptional(p,'verbose_level',1);
addOptional(p,'name_limit_file','shape_key_limits_v1');
addOptional(p,'name_parameter_file','parameter_defaults_v1');

parse(p,varargin{:});

%% check for input errors
if (isempty(p.Results.path_blender_file) || isempty(p.Results.name_blender_file))
    error([mfilename, ': Input error. Please specify ''path_blender_file'' and ''name_blender_file''.'])
end

if ~((p.Results.verbose_level>=0) && (p.Results.verbose_level<=2))
    error(mfilename, ': Input error. ''verbose_level'' must be between 0 and 2.')
end

%% assign default parameters to ppm
% set Blender project to be modified

ppm.ini.blender_file  = fullfile(p.Results.path_blender_file,...
                                 p.Results.name_blender_file);
ppm.ini.verbose_level = p.Results.verbose_level; 
ppm.ini.path.python   = p.Results.path_python; 
ppm.ini.path.default  = p.Results.path_default; 
ppm.ini.path.data     = p.Results.path_data; 
ppm.ini.path.result   = p.Results.path_result;
ppm.ini.path.external = p.Results.path_external;
if ~exist(ppm.ini.path.result,'dir'); mkdir(ppm.ini.path.result); end
if ~exist(ppm.ini.path.external,'dir'); mkdir(ppm.ini.path.external); end
addpath(genpath(ppm.ini.path.external))

%% download quaternion class from MATLAB File Exchange
if ~exist(fullfile(ppm.ini.path.external,'quaternion'),'dir')
    mkdir(fullfile(ppm.ini.path.external,'quaternion'))
    disp([mfilename,': Downloading required class `quaternion` from MATLAB File Exchange...'])
    websave(fullfile(ppm.ini.path.external,'quaternion','quaternion.zip'),'https://de.mathworks.com/matlabcentral/mlc-downloads/downloads/submissions/33341/versions/9/download/zip');
    unzip(fullfile(ppm.ini.path.external,'quaternion','quaternion.zip'),fullfile(ppm.ini.path.external,'quaternion'))
    delete(fullfile(ppm.ini.path.external,'quaternion','quaternion.zip'))
    disp([mfilename,': Finished downloading required class `quaternion` from MATLAB File Exchange.'])
end

%% optionally delete all existing txt/ply files in result folder
filelist = dir(fullfile(ppm.ini.path.result,'*.ply'));
if ~isempty(filelist) && p.Results.auto_delete==1
    if ppm.ini.verbose_level>0
        warning([mfilename,': Specified result folder contains previous results, which will be deleted.'])
    end
    for idx=1:numel(filelist)-1
        delete(fullfile(p.Results.path_result,filelist(idx).name))
        delete(fullfile(p.Results.path_result,[filelist(idx).name(1:end-4),'.txt']))
    end
    delete(fullfile(p.Results.path_result,'blender_bones_data.txt'))
    delete(fullfile(p.Results.path_result,'blender_bones_data.ply'))
    if exist(fullfile(p.Results.path_result,'blender_render.log'),'file')
        delete(fullfile(p.Results.path_result,'blender_render.log'))
    end
elseif ~isempty(filelist) && p.Results.auto_delete==0
    answer = questdlg([mfilename,': Specified result folder contains previous results, which will be deleted. Proceed?'],'Yes','No');
    if strcmp(answer,'Yes')
        for idx=1:numel(filelist)-1
            delete(fullfile(filelist(idx).folder,filelist(idx).name))
            delete(fullfile(filelist(idx).folder,[filelist(idx).name(1:end-4),'.txt']))
        end
        delete(fullfile(filelist(idx).folder,'blender_bones_data.txt'))
        delete(fullfile(filelist(idx).folder,'blender_bones_data.ply'))
        if exist(fullfile(p.Results.path_result,'blender_render.log'),'file')
            delete(fullfile(p.Results.path_result,'blender_render.log'))
        end
    else
        error('Aborted by user.')
    end
end

%% determine Blender location depending on system architecture
ppm.ini.sysarch = computer('arch'); % determines system architecture
switch ppm.ini.sysarch
    case 'win64'
        [~, temp] = system('WHERE /F /R "C:\Program Files\Blender Foundation" blender.exe');
        temp2 = regexp(temp, '[\f\n\r]', 'split'); % remove unwanted line break added by system command
        ppm.ini.path.blender_exe = temp2{1};
    case 'glnxa64'
        ppm.ini.path.blender = '';
        error('Please manually set path to Blender.')
    otherwise % 'MACI64'
        ppm.ini.path.blender_exe = ''; %'/Users/<user name>/BlenderApp/blender/blender.app/Contents/MacOS/Blender';
        error('Please manually set path to Blender.')
end

% load default transformation matrix
load(fullfile(ppm.ini.path.default,[p.Results.name_parameter_file,'.mat']),'parameter_defaults_v1');
ppm.parameters = parameter_defaults_v1;

% load default ppm parameter limits
load(fullfile(ppm.ini.path.default,[p.Results.name_limit_file,'.mat']),'shape_key_limits_v1');
ppm.ini.shape_key_limits = shape_key_limits_v1;