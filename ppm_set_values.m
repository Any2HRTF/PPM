function ppm = ppm_set_values(ppm,varargin)
%ppm_set_values - Set the parameters values of the parametric pinna model (PPM)  
%                 in the Blender file specified in the PPM structure array
%
% Usage: 
%   ppm = ppm_set_values(ppm,varargin)
%
% Input parameters:
%
%   Required
%     ppm    : PPM structure array, initialized as per ppm_initialize()
%     'type' : Parameter type [string]
%     'name' : Parameter name [string]
%     'axis' : Displacement/rotation axis [string], '
%              'W' (only for type 'Rotation')/'X'/'Y'/'Z' (default: []) 
%              (only required if parameter is not of type 'Shape_key', 
%              otherwise optional)
%     'val'  : Value to be assigned to the selected parameter [double].
%              For parameter type 'Rotation', 'val' sets the values of
%              the orientation quaternion, or the Euler-angle component in deg 
%              as per ppm.modify.rotation_mode. The general behavior depends on 
%              ppm.modify.instruction_mode. 
%
%   Optional (key/value pairs):
%     'rotation_mode'    : Rotation mode [string]. Possible rotation modes include 
%                          'quaternion': W,X,Y,Z (default)
%                          'XYZ': XYZ Euler rotation (order: Z -> Y -> X)
%                          'XZY': XZY Euler rotation (order: Y -> Z -> X)
%                          'YXZ': YXZ Euler rotation (order: Z -> X -> Y)
%                          'YZX': YZX Euler rotation (order: X -> Z -> Y)
%                          'ZXY': ZXY Euler rotation (order: Y -> X -> Z)
%                          'ZYX': ZYX Euler rotation (order: X -> Y -> Z)
%
%                          NOTE: Manipulations of Euler-angle components will 
%                                result in a correspondingly updated normalized
%                                quaternion.
%
%     'instruction_mode' : Instruction mode [string]
%                           'rel': val is added to val_orig and subsequently 
%                                  assigned to the parameter (default)
%                           'abs': val is directly assigned to the parameter
%     'itr'              : Number of iterations. Test itr neigboring values in steps 
%                          of range/itr, symmetrically around val [double] 
%                          (default: 1). 
%     'range'            : Range of values to be tested, in a range of 
%                          (+/-range/2) symmetric around val [double] 
%                          (default: 1).
%     'cam_loc'          : Location vector of the camera [double] 
%                          (default: [-10, 200, 5])
%     'cam_rot'          : Rotation vector of the camera, containing 
%                          XYZ Euler angles in deg [double] 
%                          (default: [90, 0, 180])
%     'cam_loc_ref'      : Reference position to which the camera is to be 
%                          pointed [double] (default: [])
%                          NOTE: If 'cam_loc_ref' is set the values for 
%                                'cam_rot' will be overwritten.
%
%   For ppm_blender_execute()
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
% Output parameters:
%
%   ppm : PPM structure array [struct] extended by
%         .modify
%             .type [string]
%             .name [string]
%             .axis [string]
%             .val / .val_vec : parameter value after modification / 
%                               (itr>1) vector of parameter values after
%                               modification [double] 
%             .itr [double]
%             .range [double]
%             .instruction_mode [string]
%             .rotation_mode [string]
%             .cam_loc [double]
%             .cam_rot [double]
%             .cam_loc_ref [double]
%             .set_cam [logical]
%             .mesh [logical]
%             .remesh [logical]
%             .image [logical]
%             .image_res [logical]
%             .image_col_dep [double]
%             .image_comp [double]
%             .depth [logical]
%             .depth_col_dep_exr [double]
%             .depth_comp_exr [double]
%             .depth_codec_exr [string]
%             .depth_col_dep_png [double]
%             .depth_comp_png [double]
%             .idx [double]   : row in ppm.parameters [double]
%             .val_orig       : original parameter value before modification [double]
%             .stp            : step size between parameter values (if itr>1) [double]
%
% Definition of parameter limits and conventions in ppm.parameters:
% (Row)   .type     .name           .axis    (Limits)        (Description) 
%       1 Location  Size-Bendy      X        [-inf +inf]     Displacement in global X-axis direction
%       2 Location  Size-Bendy      Y        [-inf +inf]     Displacement in global Y-axis direction
%       3 Location  Size-Bendy      Z        [-inf +inf]     Displacement in global Z-axis direction
%
%       4 Rotation  Size-Bendy      W        [-inf +inf]     Scalar part of rotation quaternion (real number)
%       5 Rotation  Size-Bendy      X        [-inf +inf]     Vector part of rotation quaternion (real number of the i-th basic quaternion)
%       6 Rotation  Size-Bendy      Y        [-inf +inf]     Vector part of rotation quaternion (real number of the j-th basic quaternion)
%       7 Rotation  Size-Bendy      Z        [-inf +inf]     Vector part of rotation quaternion (real number of the k-th basic quaternion)
%
%       7 Scale     Size-Bendy      X        [0 +2]          Scaling in global X-axis direction
%       8 Scale     Size-Bendy      Y        [0 +2]          Scaling in global Y-axis direction
%       9 Scale     Size-Bendy      Z        [0 +2]          Scaling in global Z-axis direction
%
%   10-27 Shape_key                 n/a      cf. ppm.ini.shape_key_limits
%
%  28-135 Location  Control_points  X/Y/Z                    Displacement in global X/Y/Z-axis direction
%         Rotation  Control_points  W/X/Y/Z                  Rotation as per rotation quaternion
%
% 136-162 Scale     Bendy_bones     X/Y/Z    [0 +2]          Scaling in global X/Y/Z-axis direction
%
% NOTE: All changes of parameter values are non-destructive and only
%       contained in the exported meshes. The Blender file itself, specified  
%       in ppm_initialize, is not modified.
%
% Related functions : ppm_initialize, ppm_get_values, ppm_evaluate

% #Author: Florian Pausch (2022)

%% parse input arguments
p = inputParser;

addOptional(p,'type',[]);
addOptional(p,'name',[]);
addOptional(p,'axis',[]);
addOptional(p,'val',[]);
addOptional(p,'itr',1);
addOptional(p,'range',1);
addOptional(p,'instruction_mode','rel');
addOptional(p,'rotation_mode','quaternion');
addOptional(p,'cam_loc',[-10, 200, 5]);
addOptional(p,'cam_rot',[90, 0, 180]);
addOptional(p,'cam_loc_ref',[]);

% input arguments for ppm_blender_execute()
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

%% check for input errors
if ~sum(strcmp(p.Results.type,ppm.parameters(:,1)))
    error('Input error. Unknown parameter type.')
end

if ~sum(strcmp(p.Results.name,ppm.parameters(:,2)))
    error('Input error. Unknown parameter name.')
end

if ~sum(strcmp(p.Results.axis,ppm.parameters(:,3))) && ~strcmp(p.Results.type,'Shape_key')
    error('Input error. Unknown displacement/rotation axis. Must be one of ''X'', ''Y'', or ''Z''.')
end

if strcmp(p.Results.type,'Location') && strcmp(p.Results.axis,'W')
    error('Input error. Axis does not exist for type ''Location''.')
end

if strcmp(p.Results.type,'Rotation') && ~strcmp(p.Results.rotation_mode,'quaternion') && strcmp(p.Results.axis,'W')
    error('Input error. W-component is not relevant for manipulation of Euler angle components.')
end

if (isempty(p.Results.type) || isempty(p.Results.name) || isempty(p.Results.val))
    error('Not enough input arguments. Please specify ''type'', ''name'', and ''val''.')
end

if ~strcmp(p.Results.type,'Shape_key') && isempty(p.Results.axis)
    error('Not enough input arguments. Please specify ''axis''.')
end

if ~sum(strcmp(p.Results.type,ppm.parameters(:,1)) & strcmp(p.Results.name,ppm.parameters(:,2)))
    error('Input error. Unknown combination of parameter ''type'' and ''name''.')
end

if p.Results.itr>1 && isempty(p.Results.range) 
    error('Not enough input arguments. Please specify ''range''.')
end

if ~ismember(p.Results.instruction_mode,{'rel','abs'})
    error('Instruction mode must be either ''rel'' or ''abs''.')
end

if ~ismember(p.Results.rotation_mode,{'quaternion','XYZ','XZY','YXZ','YZX','ZXY','ZYX'})
    error('Rotation mode must be either ''quaternion'',''XYZ'',''XZY'',''YXZ'',''YZX'',''ZXY'', or ''ZYX''.')
end

%% assign input arguments to ppm struct
ppm.modify.type  = p.Results.type;
ppm.modify.name  = p.Results.name;
ppm.modify.axis  = p.Results.axis;
ppm.modify.val   = p.Results.val;
ppm.modify.itr   = p.Results.itr;
ppm.modify.range = p.Results.range;
ppm.modify.instruction_mode  = p.Results.instruction_mode;
ppm.modify.rotation_mode     = p.Results.rotation_mode;
ppm.modify.cam_loc           = p.Results.cam_loc;
ppm.modify.cam_rot           = p.Results.cam_rot;
ppm.modify.cam_loc_ref       = p.Results.cam_loc_ref;
ppm.modify.set_cam           = p.Results.set_cam;
ppm.modify.mesh              = p.Results.mesh;
ppm.modify.remesh            = p.Results.remesh;
ppm.modify.image             = p.Results.image;
ppm.modify.image_res         = p.Results.image_res;
ppm.modify.image_col_dep     = p.Results.image_col_dep;
ppm.modify.image_comp        = p.Results.image_comp;
ppm.modify.depth             = p.Results.depth;
ppm.modify.depth_col_dep_exr = p.Results.depth_col_dep_exr;
ppm.modify.depth_comp_exr    = p.Results.depth_comp_exr;
ppm.modify.depth_codec_exr   = p.Results.depth_codec_exr;
ppm.modify.depth_col_dep_png = p.Results.depth_col_dep_png;
ppm.modify.depth_comp_png    = p.Results.depth_comp_png;

%% assign the specified values to the selected parameter
ppm = ppm_modify_parameter_values(ppm);

%% export modified mesh
ppm_blender_execute(ppm,...
    'mesh',p.Results.mesh,...
    'remesh',p.Results.remesh,...
    'image',p.Results.image,...
    'image_res',p.Results.image_res,...
    'image_col_dep',p.Results.image_col_dep,...
    'image_comp',p.Results.image_comp,...
    'set_cam',p.Results.set_cam,...
    'depth',p.Results.depth,...
    'depth_col_dep_exr',p.Results.depth_col_dep_exr,...
    'depth_comp_exr',p.Results.depth_comp_exr,...
    'depth_codec_exr',p.Results.depth_codec_exr,...
    'depth_col_dep_png',p.Results.depth_col_dep_png,...
    'depth_comp_png',p.Results.depth_comp_png)

end
