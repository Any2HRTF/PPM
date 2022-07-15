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
%     'mesh'              : Render updated PPM mesh [logical], default: true 
%     'remesh'            : Disable/enable modififiers in blender [logical], default: false
%     'image'             : Render PPM mesh as PNG [logical], default: false
%     'image_res'         : Resolution (image_res x image_res) of the
%                           rendered PNG image [double], default: 1024
%     'image_col_dep'     : Set color depth of PNG file in bit [double], 
%                           {8, 10, 12, 16, 32}, default: 16
%     'image_comp'        : Set amount of compression in rendered PNG file [double], 
%                           [0, 100] = [none, maximum lossless compression], 
%                           default: 15
%     'set_cam'           : Set camera position and rotation as per cam_loc, cam_rot 
%                           and/or cam_loc_ref [logical], default: false
%     'depth'             : Export image-depth data (z buffer) as EXR and PNG
%                           files, normalised to values between 1 (black) 
%                           and (0) white [logical], default: false
%     'depth_col_dep_exr' : Set color-depth of depth data (z buffer) in OpenEXR file
%                           [double], {16, 32}, default: 16
%     'depth_comp_exr'    : Set amount of compression in OpenEXR file [double], 
%                           [0, 100] = [none, maximum lossless compression], 
%                           default: 15
%     'depth_codec_exr'   : Set codec of rendered OpenEXR file [string], 
%                           {'NONE', 'PXR24', 'ZIP', 'PIZ’, 'RLE’, 'ZIPS’, 
%                           'B44 , 'B44A', 'DWAA', 'DWAB'}, default: 'NONE'
%     'depth_col_dep_png' : Set color-depth of depth data (z buffer) in PNG file
%                           [double], {8, 10, 12, 16, 32}, default: 16
%     'depth_comp_png'    : Set amount of compression in rendered image-depth PNG 
%                           file [double], [0, 100] = [none, maximum lossless compression], 
%                           default: 15
%
% Note: This function is called within ppm_set_values().

% #Author: Florian Pausch (2022)

%% parse input arguments

p = inputParser;

addOptional(p,'mesh',true);
addOptional(p,'remesh',false);
addOptional(p,'image',false);
addOptional(p,'image_res',1024);
addOptional(p,'image_col_dep',16);
addOptional(p,'image_comp',15);
addOptional(p,'set_cam',false);

addOptional(p,'depth',false);
addOptional(p,'depth_col_dep_exr',16);
addOptional(p,'depth_comp_exr',15);
addOptional(p,'depth_codec_exr','NONE');
addOptional(p,'depth_col_dep_png',16);
addOptional(p,'depth_comp_png',15);

parse(p,varargin{:});

% convert 1 and 0 to TRUE and FALSE, respectively (for Python scripts)
parsePool = [p.Results.mesh,p.Results.remesh,p.Results.image,p.Results.set_cam,...
    p.Results.depth];
parsePoolString = {'TRUE','FALSE'};
parsedStrings = parsePoolString((parsePool==0)+1);

%% execute Blender via Python scripts
switch ppm.ini.verbose_level
    
    case 0
        args = [ppm.ini.path.blender_exe, ' ', ppm.ini.blender_file...
            ' -b -P ' fullfile(ppm.ini.path.python,'set_values_and_export_mesh_v1_3_0.py'),' -- ', ...
            ppm.ini.path.result, ' ',...
            parsedStrings{1}, ' ',...
            parsedStrings{2}, ' ',...
            parsedStrings{3},' ',...
            num2str(p.Results.image_res),' ',...
            num2str(p.Results.image_col_dep),' ',...
            num2str(p.Results.image_comp),' ',...
            parsedStrings{4},' ',...
            parsedStrings{5},' ',...
            num2str(p.Results.depth_col_dep_exr),' ',...
            num2str(p.Results.depth_comp_exr),' ',...
            p.Results.depth_codec_exr,' ',...
            num2str(p.Results.depth_col_dep_png),' ',...
            num2str(p.Results.depth_comp_png),...
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
            ' -b -P ' fullfile(ppm.ini.path.python,'set_values_and_export_mesh_v1_3_0.py'),' -- ', ...
            ppm.ini.path.result, ' ',...
            parsedStrings{1}, ' ',...
            parsedStrings{2}, ' ',...
            parsedStrings{3},' ',...
            num2str(p.Results.image_res),' ',...
            num2str(p.Results.image_col_dep),' ',...
            num2str(p.Results.image_comp),' ',...
            parsedStrings{4},' ',...
            parsedStrings{5},' ',...
            num2str(p.Results.depth_col_dep_exr),' ',...
            num2str(p.Results.depth_comp_exr),' ',...
            p.Results.depth_codec_exr,' ',...
            num2str(p.Results.depth_col_dep_png),' ',...
            num2str(p.Results.depth_comp_png),...
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
            ' -b -P ' fullfile(ppm.ini.path.python,'set_values_and_export_mesh_v1_3_0.py'),' -- ', ...
            ppm.ini.path.result, ' ',...
            parsedStrings{1}, ' ',...
            parsedStrings{2}, ' ',...
            parsedStrings{3},' ',...
            num2str(p.Results.image_res),' ',...
            num2str(p.Results.image_col_dep),' ',...
            num2str(p.Results.image_comp),' ',...
            parsedStrings{4},' ',...
            parsedStrings{5},' ',...
            num2str(p.Results.depth_col_dep_exr),' ',...
            num2str(p.Results.depth_comp_exr),' ',...
            p.Results.depth_codec_exr,' ',...
            num2str(p.Results.depth_col_dep_png),' ',...
            num2str(p.Results.depth_comp_png),...
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