function [ppm,val] = ppm_get_values(ppm,varargin)
%ppm_get_values - Get the parameters values from the parametric pinna 
%                 model (PPM) in the Blender file specified in the 
%                 PPM structure array
%
% Usage: 
%   ppm = ppm_get_values(ppm)
%
% Input parameters:
%
%   Required:
%     ppm    : PPM structure array, initialized as per ppm_initialize.
%   
%   Optional:
%     Fetch a subset of the current parameter values (logical conjunction):
%     'type' : Parameter type [string]
%     'name' : Parameter name [string]
%     'axis' : Displacement/rotation axis [string], 
%              'W' (only for rotation)/'X'/'Y'/'Z' (default: []), 
%              (not relevant if parameter is of type "Shape_key")
%
%     Export modelled mesh:
%     'pc'               : Export as point cloud (PLY) [logical], default: true
%     'mesh'             : Export as mesh (STL) [logical], default: false
%     'sample_start_idx' : File-name index. The exported files start at 
%                          this index [double], default: 1
%
% Output parameters:
%
%   ppm  : Updated PPM structure array [struct]
%          .parameters : parameter values as obtained from the
%                       specified Blender file, i.e.
%                       fullfile(path_blender_file,name_blender_file) [cell]
%    val : Subset of queried parameters with current values [cell] 
%
% Related functions : ppm_initialize, ppm_set_values, ppm_evaluate

% #Author: Florian Pausch (2022)

%% Parse input arguments
p = inputParser;

addOptional(p,'type',[]);
addOptional(p,'name',[]);
addOptional(p,'axis',[]);
addOptional(p,'pc',true);
addOptional(p,'mesh',false);
addOptional(p,'sample_start_idx',1);

parse(p,varargin{:});

%% Check for input errors
if ~isempty(p.Results.type)
    if ~ismember(p.Results.type,ppm.parameters(:,1))
        error('Input error: Unknown parameter type.')
    end
end

if ~isempty(p.Results.name)
    if ~ismember(p.Results.name,ppm.parameters(:,2))
        error('Input error: Unknown parameter name.')
    end
end

if strcmp(p.Results.type,'Location') && strcmp(p.Results.axis,'W')
    error('Input error. Axis does not exist for type ''Location''.')
end

if ~isempty(p.Results.axis)
    if ~ismember(p.Results.axis,ppm.parameters(:,3))
        error('Input error: Unknown displacement/rotation axis.')
    end
end

if ~isempty(p.Results.type) && ~isempty(p.Results.name)
    if ~sum(strcmp(p.Results.type,ppm.parameters(:,1)) & strcmp(p.Results.name,ppm.parameters(:,2)))
        error('Input error. Unknown combination of parameter ''type'' and ''name''.')
    end
end

%% Create .txt file containing the current parameter values
if ~exist(fullfile(ppm.ini.path.result,'parameters'),'dir')
    mkdir(fullfile(strrep(ppm.ini.path.result,'"',''),'parameters'))
end

writecell(ppm.parameters, fullfile(strrep(ppm.ini.path.result,'"',''),...
    'parameters','blender_bones_data.txt'));

%% Fetch parameter values from the specified Blender file

% convert 1 and 0 to TRUE and FALSE, respectively (for Python scripts)
parsePool = [p.Results.pc, p.Results.mesh];
parsePoolString = {'TRUE','FALSE'};
parsedStrings = parsePoolString((parsePool==0)+1);

% resolve issues with paths containing spaces
dquotes = '"';
ppm.ini.blender_file = strcat(dquotes, ppm.ini.blender_file, dquotes);
ppm.ini.path.result = strcat(dquotes, ppm.ini.path.result, dquotes);

switch ppm.ini.verbose_level
    case 0
        args = [ppm.ini.path.blender_exe, ' -b ', ppm.ini.blender_file,...
            ' -P ' fullfile(ppm.ini.path.python,'get_values_and_export_mesh_v1_5_0.py'),' -- ',...
            ppm.ini.path.result, ' ',...
            parsedStrings{1}, ' ',...
            parsedStrings{2}, ' ',...
            num2str(p.Results.sample_start_idx), ' ',...
            ' -a > nul 2>&1'];
        stat = system(args);
        if stat
            error('Parameters could not be obtained from Blender file. Check ''args''. Aborted.') 
        end
    case 1
        disp([mfilename,': Obtaining parameter values from specified Blender file...'])
        args = [ppm.ini.path.blender_exe, ' -b ', ppm.ini.blender_file,...
            ' -P ' fullfile(ppm.ini.path.python,'get_values_and_export_mesh_v1_5_0.py'),' -- ',...
            ppm.ini.path.result, ' ',...
            parsedStrings{1}, ' ',...
            parsedStrings{2}, ' ',...
            num2str(p.Results.sample_start_idx), ' ',...
            ' -a > nul 2>&1'];
        stat = system(args); 
        if stat
            error('Parameters could not be obtained from Blender file. Check ''args''. Aborted.')
        else
            disp([mfilename,': Parameter values successfully obtained.'])
        end
    case 2
        disp([mfilename,': Obtaining parameter values from specified Blender file...'])
        args = [ppm.ini.path.blender_exe, ' -b ', ppm.ini.blender_file,...
            ' -P ' fullfile(ppm.ini.path.python,'get_values_and_export_mesh_v1_5_0.py'),' -- ',...
            ppm.ini.path.result, ' ',...
            parsedStrings{1}, ' ',...
            parsedStrings{2}, ' ',...
            num2str(p.Results.sample_start_idx)];
        stat = system(args);
        if stat
            error('Parameters could not be obtained from Blender file. Check ''args''. Aborted.')
        else
            disp([mfilename,': Parameter values successfully obtained.'])
        end
end

parameters = importdata(fullfile(strrep(ppm.ini.path.result,'"',''),'parameters',...
                        [num2str(p.Results.sample_start_idx),'.txt']));
ppm.parameters(:,4) = num2cell(parameters.data);

%% Return selected parameters
if ~isempty(p.Results.type) || ~isempty(p.Results.name) || ~isempty(p.Results.axis)

    if isempty(p.Results.type)
        type = ppm.parameters(:,1);
    else
        type = p.Results.type;
    end

    if isempty(p.Results.name)
        name = ppm.parameters(:,2);
    else
        name = p.Results.name;
    end

    if isempty(p.Results.axis)
        axis = ppm.parameters(:,3);
    else
        if strcmp(p.Results.type,'Shape_key')
            axis = '#';
        else
            axis = p.Results.axis;
        end
    end

    val = ppm.parameters(strcmp(type,ppm.parameters(:,1)) & ...
        strcmp(name,ppm.parameters(:,2)) & ...
        strcmp(axis,ppm.parameters(:,3)),:);

else 

    val = [];

end

delete(fullfile(fullfile(strrep(ppm.ini.path.result,'"',''),...
    'parameters','blender_bones_data.txt')))