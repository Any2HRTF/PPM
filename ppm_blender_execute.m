function ppm_blender_execute(ppm,varargin)
%ppm_blender_execute - Send the parameter values to be modified to Blender 
%                      and update the parametric pinna model (PPM) as specified 
%                      in the PPM structure array.
%
% Usage: 
%   ppm = ppm_blender_execute(ppm,varargin)
%
% Input parameters:
%
%   Required
%     ppm      : PPM structure array, initialized as per ppm_initialize(), 
%                with parameters set via ppm_set_values(). 
%
%   Optional (key/value pairs):
%     'mesh'      : Export updated Blender mesh [logical], default: true 
%     'remesh'    : Disable/enable modififiers in Blender [logical], default: true
%     'image'     : Export image [logical], default: false
%     'image_res' : Image resolution (image_res x image_res) of the
%                   exported image [int], default: 1024
%
% Note: This function is called within ppm_set_values().

% #Author: Florian Pausch (2022)

%% parse input arguments

p = inputParser;

addOptional(p,'mesh',true);
addOptional(p,'remesh',false);
addOptional(p,'image',false);
addOptional(p,'image_res',1024);
addOptional(p,'set_cam',false);

parse(p,varargin{:});

% convert 1 and 0 to TRUE and FALSE, respectively (for Python scripts)
parsePool = [p.Results.mesh,p.Results.remesh,p.Results.image,p.Results.set_cam];
parsePoolString = {'TRUE','FALSE'};
parsedStrings = parsePoolString((parsePool==0)+1);

%% execute Blender via Python scripts
switch ppm.ini.verbose_level
    
    case 0
        args = [ppm.ini.path.blender_exe, ' ', ppm.ini.blender_file...
            ' -b -P ' fullfile(ppm.ini.path.python,'set_values_and_export_mesh_v1_3.py'),' -- ', ...
            ppm.ini.path.result, ' ',...
            parsedStrings{1}, ' ',...
            parsedStrings{2}, ' ',...
            parsedStrings{3},' ',...
            num2str(p.Results.image_res),' ',...
            parsedStrings{4},...
            ' -a > nul 2>&1', ];
        
        stat = system(args);
        if stat
            error('Mesh manipulations were not successful. Aborted.')
        else
            if ppm.ini.verbose_level>0
                disp([mfilename,': Mesh manipulations were successful.'])
            end
        end
        
    case 1
        disp([mfilename,': Sending modified parameter values to blender. Manipulating mesh...'])
        args = [ppm.ini.path.blender_exe, ' ', ppm.ini.blender_file...
            ' -b -P ' fullfile(ppm.ini.path.python,'set_values_and_export_mesh_v1_3.py'),' -- ', ...
            ppm.ini.path.result, ' ',...
            parsedStrings{1}, ' ',...
            parsedStrings{2}, ' ',...
            parsedStrings{3},' ',...
            num2str(p.Results.image_res),' ',...
            parsedStrings{4},...
            ' -a > nul 2>&1'];
        
        stat = system(args);
        if stat
            error('Mesh manipulations were not successful. Aborted.')
        else
            if ppm.ini.verbose_level>0
                disp([mfilename,': Mesh manipulations were successful.'])
            end
        end
        
        
    case 2
        disp([mfilename,': Sending modified parameter values to blender. Manipulating mesh...'])
        args = [ppm.ini.path.blender_exe, ' ', ppm.ini.blender_file...
            ' -b -P ' fullfile(ppm.ini.path.python,'set_values_and_export_mesh_v1_3.py'),' -- ', ...
            ppm.ini.path.result, ' ',...
            parsedStrings{1}, ' ',...
            parsedStrings{2}, ' ',...
            parsedStrings{3},' ',...
            num2str(p.Results.image_res),' ',...
            parsedStrings{4},...
            ' '];
        
        stat = system(args);
        if stat
            error('Mesh manipulation were not successful. Aborted.')
        else
            if ppm.ini.verbose_level>0
                disp([mfilename,': Mesh manipulations were successful.'])
            end
        end
        
end
   
% delete(fullfile(ppm.ini.path.result,'blender_render.log'));