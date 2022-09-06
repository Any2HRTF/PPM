function ppm = ppm_set_values(ppm,varargin)
%ppm_set_values - Set the parameters values of the parametric pinna model (PPM)  
%                 in the Blender file specified in the PPM structure array
%
% Usage: 
%
%   ppm = ppm_set_values(ppm,varargin)
%
% Input parameters:
%
%   Required:
%     ppm    : PPM structure array, initialized as per ppm_initialize()
%     'type' : Parameter type [string OR cell array]
%     'name' : Parameter name [string OR cell array]
%     'axis' : Displacement/rotation axis [string OR cell array], 
%              'W' (only for type 'Rotation' and ppm.modify.instruction_mode  
%              set to 'quaternion')/'X'/'Y'/'Z' (default: []) 
%              (only required if parameter is not of type 'Shape_key', 
%              otherwise optional)
%     'val'  : Value to be assigned to the selected parameter [double OR cell array].
%              For parameter type 'Rotation', 'val' sets the values of
%              the orientation quaternion, or the Euler-angle component in deg 
%              as per ppm.modify.rotation_mode. The general behavior depends on 
%              ppm.modify.instruction_mode. 
%
%      NOTE: Provide N x 1 cell arrays for 'type', 'name', 'axis' and 'val' 
%            to change N parameter values simultaneously. Anisotropic scaling 
%            is only possible when `name` is set to 'Size-Bendy'. To scale 
%            Size-Bendy and/or different bendy bones, provide different 
%            and/or identical value triplets, respectively, per corresponding 
%            axis triplets!
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
%                                result in correspondingly updated normalized
%                                quaternions. In rotation modes other than `quaternion`,
%                                provide triplets of X-, Y-, and Z-axis values 
%                                if N parameter values are to be changed
%                                simultaneously!
%
%     'instruction_mode' : Instruction mode [string]
%                           'rel': val is added to val_orig and subsequently 
%                                  assigned to the parameter (default)
%                           'abs': val is directly assigned to the parameter
%     'itr'              : Number of iterations. Test itr neigboring values in steps 
%                          of range/itr, symmetrically around val [double] 
%                          (default: 1) 
%     'range'            : Range of values to be tested, in a range of 
%                          (+/-range/2) symmetric around val [double] 
%                          (default: 1)
%     'sample_start_idx' : File-name index. If itr>1 the exported or
%                          rendered files start at this index and are
%                          incremented [double] (default: 1)
%     'auto_correct'     : (Only relevant for multi-parameter input) 
%                          Automatically unify inadmissable anisotropic scaling
%                          values for bendy bones other than 'Size-Bendy'
%                          using the first value of the corresponding scaling
%                          triplet [logical] (default: false); when changing
%                          a single scale value, the corresponding value
%                          triplet is unified automatically
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
%   For ppm_blender_execute():
%     'pc'                : Export modelled mesh as point cloud (PLY) [logical]
%                           (default: true)
%     'mesh'              : Export modelled mesh as mesh (STL) [logical] 
%                           (default: false) 
%     'remesh'            : Disable/enable reduction of vertex/face count of 
%                           the modelled mesh before exporting [logical]
%                           (default: false)
%     'image'             : Render modelled mesh as PNG [logical] (default: false)
%     'image_res'         : Resolution (image_res x image_res) of the
%                           rendered PNG image [double] (default: 1024)
%     'image_col_dep'     : Set color depth of PNG file in bit [double], 
%                           {8, 16} (default: 16)
%     'image_comp'        : Set amount of compression in rendered PNG file [double], 
%                           [0, 100] = [none, maximum lossless compression] 
%                           (default: 15)
%     'set_cam'           : Set camera position and rotation as per cam_loc, cam_rot 
%                           and/or cam_loc_ref [logical] (default: false)
%     'depth'             : (Requires 'image' set to true) Export image-depth 
%                           data (z buffer) as EXR and PNG files, normalised 
%                           to values between 1 (black, farthest) and 0 
%                           (white, closest) [logical] (default: false)
%     'depth_nearest'     : Nearest distance representing the maximum value
%                           of the normalised image-depth map (white), 
%                           provided in Blender units [double] (default: 
%                           Euclidian distance of the current camera position 
%                           to the origin of the global coordinate system)
%     'depth_farthest'    : Farthest distance representing the minimum value
%                           of the normalised image-depth map (black), 
%                           provided in Blender units [double] (default: 0) 
%                           (origin of the global coordinate system)
%     'depth_col_dep_exr' : Set color-depth of depth data (z buffer) in OpenEXR file
%                           [double], {16, 32} (default: 16)
%     'depth_comp_exr'    : Set amount of compression in OpenEXR file [double], 
%                           [0, 100] = [none, maximum lossless compression] 
%                           (default: 15)
%     'depth_codec_exr'   : Set codec of rendered OpenEXR file [string], 
%                           {'NONE', 'PXR24', 'ZIP', 'PIZ’, 'RLE’, 'ZIPS’, 
%                           'B44 , 'B44A', 'DWAA', 'DWAB'} (default: 'NONE')
%     'depth_col_dep_png' : Set color-depth of depth data (z buffer) in PNG file
%                           [double], {8, 16} (default: 16)
%     'depth_comp_png'    : Set amount of compression in rendered image-depth PNG 
%                           file [double], [0, 100] = [none, maximum lossless 
%                           compression] (default: 15)
%
% Output parameters:
%
%   ppm : PPM structure array [struct] extended by
%         .modify
%             .type [string OR cell array]
%             .name [string OR cell array]
%             .axis [string OR cell array]
%             .val / .val_vec : Parameter value after modification / 
%                               (if itr>1: vector of parameter values after
%                               modification) [double] 
%             .itr [double]
%             .range [double]
%             .sample_start_idx [double]
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
%             .depth_nearest [double]
%             .depth_farthest [double]
%             .depth_col_dep_exr [double]
%             .depth_comp_exr [double]
%             .depth_codec_exr [string]
%             .depth_col_dep_png [double]
%             .depth_comp_png [double]
%             .idx      : Row in ppm.parameters [double]
%             .val_orig : Original parameter value before modification [double]
%             .stp      : Step size between parameter values (if itr>1) [double]
%
% Definition of PPM parameter limits and descriptions of ppm.parameters:
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
%   10-27 Shape_key                 n/a      various, cf. ppm.ini.shape_key_limits
%
%  28-135 Location  Control_points  X/Y/Z                    Displacement in global X/Y/Z-axis direction
%         Rotation  Control_points  W/X/Y/Z                  Rotation as per rotation quaternion
%
% 136-162 Scale     Bendy_bones     X/Y/Z    [0 +2]          Scaling in global X/Y/Z-axis direction
%
% NOTE: All changes of parameter values are non-destructive and only
%       contained in the exported meshes. The Blender file itself, specified  
%       in ppm_initialize(), is not modified.
%
% Related functions : ppm_initialize, ppm_get_values, ppm_evaluate

% #Author: Florian Pausch (2022)

%% Parse input arguments
p = inputParser;

addOptional(p,'type',[]);
addOptional(p,'name',[]);
addOptional(p,'axis',[]);
addOptional(p,'val',[]);
addOptional(p,'itr',1);
addOptional(p,'sample_start_idx',1);
addOptional(p,'auto_correct',false);
addOptional(p,'range',1);
addOptional(p,'instruction_mode','rel');
addOptional(p,'rotation_mode','quaternion');
addOptional(p,'cam_loc',[-10, 200, 5]);
addOptional(p,'cam_rot',[90, 0, 180]);
addOptional(p,'cam_loc_ref',[]); 

% Input arguments for ppm_blender_execute()
addOptional(p,'pc',true);
addOptional(p,'mesh',false);
addOptional(p,'remesh',false);
addOptional(p,'image',false);
addOptional(p,'image_res',1024);
addOptional(p,'image_col_dep',16);
addOptional(p,'image_comp',15);
addOptional(p,'set_cam',false);
addOptional(p,'depth',false);
addOptional(p,'depth_nearest',NaN);
addOptional(p,'depth_farthest',0);
addOptional(p,'depth_col_dep_exr',16);
addOptional(p,'depth_comp_exr',15);
addOptional(p,'depth_codec_exr','NONE');
addOptional(p,'depth_col_dep_png',16);
addOptional(p,'depth_comp_png',15);

parse(p,varargin{:});

%% Check for input errors
% multiple parameter values are to be changed
if iscell(p.Results.type) || iscell(p.Results.name) || ...
        iscell(p.Results.axis) || iscell(p.Results.val)

    if ~isequal( size(p.Results.type), size(p.Results.name), ...
            size(p.Results.axis), size(p.Results.val) )
        error('Input error. Dimensions of ''type'', ''name'' and/or ''axis'' are not consistent.')
    end

    if ~strcmp(p.Results.rotation_mode,'quaternion') && ...
            ( ~isequal( sum(strcmp(p.Results.axis,'X')),...
                     sum(strcmp(p.Results.axis,'Y')),...
                     sum(strcmp(p.Results.axis,'Z')) ) || ...
                     ( mod( sum(strcmp(p.Results.axis,'X'))+...
                      sum(strcmp(p.Results.axis,'Y'))+...
                      sum(strcmp(p.Results.axis,'Z')), 3 ) ) )
        error(['Input error. When using rotation mode ''',...
            p.Results.rotation_mode,...
            ', fully occupied triplets are expected for ''axis'', with corresponding entries for ''type'', ''name'', and ''val''.'])
    end

    if ~all(ismember(p.Results.type,ppm.parameters(:,1)))
        error('Input error. Unknown parameter type.')
    end

    if ~all(ismember(p.Results.name,ppm.parameters(:,2)))
        error('Input error. Unknown parameter name.')
    end

    if ~isempty(p.Results.axis)
        if any( ~ismember(p.Results.axis,ppm.parameters(:,3)) & ~ismember(p.Results.type,'Shape_key') ...
                & ~strcmp(p.Results.rotation_mode,'quaternion') )
            error('Input error. Unknown displacement/rotation axis. Must be one of ''X'', ''Y'', or ''Z''.')
        end

        if any( ~ismember(p.Results.axis,ppm.parameters(:,3)) & ~ismember(p.Results.type,'Shape_key') ...
                & strcmp(p.Results.rotation_mode,'quaternion') )
            error('Input error. Unknown displacement/rotation axis. Must be one of ''W'', ''X'', ''Y'', or ''Z''.')
        end

        if any( ismember(p.Results.type,'Location') & ismember(p.Results.axis,'W') )
            error('Input error. Axis does not exist for type ''Location''.')
        end

        if any( ismember(p.Results.type,'Rotation') & ~strcmp(p.Results.rotation_mode,'quaternion') ...
                & ismember(p.Results.axis,'W') )
            error('Input error. W-component is not relevant for manipulation of Euler angle components.')
        end

        if any( ismember(p.Results.type,'Scale') & ismember(p.Results.axis,'W') )
            error('Input error. Axis does not exist for type ''Scale''.')
        end

        if any(ismember(p.Results.type,'Scale')) && ~all(ismember(p.Results.name,'Size-Bendy')) && ...
                ( ~isequal( sum(strcmp(p.Results.axis,'X')),...
                sum(strcmp(p.Results.axis,'Y')),...
                sum(strcmp(p.Results.axis,'Z')) ) || ...
                ( mod( sum(strcmp(p.Results.axis,'X'))+...
                sum(strcmp(p.Results.axis,'Y'))+...
                sum(strcmp(p.Results.axis,'Z')), 3 ) ) )

            error('Input error. Fully occupied triplets are expected for ''Scale'', with corresponding entries for ''type'' and ''name''. If ''name'' is not set to ''Size-Bendy'' identical triplets for ''val'' are required (isotropic scaling).')
        end

        if any(ismember(p.Results.type,'Scale')) && ~all(ismember(p.Results.name,'Size-Bendy'))

            scale_idx_local = ismember(p.Results.type,'Scale') & ~ismember(p.Results.name,'Size-Bendy');
            scale_reshape = cell2mat(reshape(p.Results.val(scale_idx_local),3,numel(p.Results.val(scale_idx_local))/3));
            
            if ~all(~diff(scale_reshape),'all')
                if p.Results.auto_correct
                    warning([mfilename, ': Anisotropic scaling detected for (several) bendy bones other than ''Size-Bendy''. The affected scaling triplets were unified using the first scaling value(s) of the corresponding scaling triplet(s).'])
                else
                    error('Input error. Only isotropic scaling is possible for bendy bones other than ''Size-Bendy''. Provide identical axis-related values for the corresponding scaling triplets or enable ''auto_correct''.')
                end
            end
        end

    end

    if (isempty(p.Results.type) || isempty(p.Results.name) || isempty(p.Results.val))
        error('Input error. Not enough input arguments. Please specify ''type'', ''name'', and ''val''.')
    end

    if any( ~ismember(p.Results.type,'Shape_key') & ~ismember(p.Results.axis,{'W','X','Y','Z','#'}) )
        error('Input error. Not enough input arguments. Please specify ''axis''.')
    end

    if ~all( ismember(p.Results.type, ppm.parameters(:,1)) & ismember(p.Results.name, ppm.parameters(:,2)) )
        error('Input error. Unknown combination of parameter ''type'' and ''name''.')
    end

else % one parameter value is to be changed

    if ~any(strcmp(p.Results.type,ppm.parameters(:,1)))
        error('Input error. Unknown parameter type.')
    end

    if ~any(strcmp(p.Results.name,ppm.parameters(:,2)))
        error('Input error. Unknown parameter name.')
    end

    if ~any(strcmp(p.Results.axis,ppm.parameters(:,3))) && ~strcmp(p.Results.type,'Shape_key')
        error('Input error. Unknown displacement/rotation axis. Must be one of ''X'', ''Y'', or ''Z''.')
    end

    if strcmp(p.Results.type,'Location') && strcmp(p.Results.axis,'W')
        error('Input error. Axis does not exist for type ''Location''.')
    end

    if strcmp(p.Results.type,'Rotation') && ~strcmp(p.Results.rotation_mode,'quaternion') && strcmp(p.Results.axis,'W')
        error('Input error. W-component is not relevant for manipulation of Euler angle components.')
    end

    if (isempty(p.Results.type) || isempty(p.Results.name) || isempty(p.Results.val))
        error('Input error. Not enough input arguments. Please specify ''type'', ''name'', and ''val''.')
    end

    if ~strcmp(p.Results.type,'Shape_key') && isempty(p.Results.axis)
        error('Input error. Not enough input arguments. Please specify ''axis''.')
    end

    if strcmp(p.Results.type,'Scale') && strcmp(p.Results.axis,'W')
        error('Input error. Axis does not exist for type ''Scale''.')
    end

    if strcmp(p.Results.type,'Scale') && ~strcmp(p.Results.name,'Size-Bendy')
        axes_other = unique( ppm.parameters(~strcmp(p.Results.axis, ppm.parameters(:,3)), 3) );
        axes_other(strcmp(axes_other,'#') | strcmp(axes_other,'W')) = [];
        warning([mfilename,': Only isotropic scaling is possible for bendy bones. Axes ', ...
            char(axes_other(1))', ' and ', char(axes_other(2))', ' were set to the value of ', p.Results.axis, '.'])
    end

    if ~any(strcmp(p.Results.type,ppm.parameters(:,1)) & strcmp(p.Results.name,ppm.parameters(:,2)))
        error('Input error. Unknown combination of parameter ''type'' and ''name''.')
    end

    if ~any(strcmp(p.Results.axis,ppm.parameters(:,3))) && ~strcmp(p.Results.type,'Shape_key') ...
            && strcmp(p.Results.rotation_mode,'quaternion')
        error('Input error. Unknown displacement/rotation axis. Must be one of ''W'', ''X'', ''Y'', or ''Z''.')
    end

    if strcmp(p.Results.type,'Location') && strcmp(p.Results.axis,'W')
        error('Input error. Axis does not exist for type ''Location''.')
    end

    if strcmp(p.Results.type,'Rotation') && ~strcmp(p.Results.rotation_mode,'quaternion') ...
            && strcmp(p.Results.axis,'W')
        error('Input error. W-component is not relevant for manipulation of Euler angle components.')
    end

end

if p.Results.itr>1 && isempty(p.Results.range) 
    error('Input error. Not enough input arguments. Please specify ''range''.')
end

if ~ismember(p.Results.instruction_mode,{'rel','abs'})
    error('Input error. Instruction mode must be either ''rel'' or ''abs''.')
end

if ~ismember(p.Results.rotation_mode,{'quaternion','XYZ','XZY','YXZ','YZX','ZXY','ZYX'})
    error('Input error. Rotation mode must be either ''quaternion'',''XYZ'',''XZY'',''YXZ'',''YZX'',''ZXY'', or ''ZYX''.')
end

%% Fetch parameter values of Blender file if not done yet
if ~exist(fullfile(ppm.ini.path.result,'parameters'),'dir')
    ppm = ppm_get_values(ppm);
end

%% Assign input arguments to ppm.modify
if iscell(p.Results.type) || iscell(p.Results.name) || ...
        iscell(p.Results.axis) || iscell(p.Results.val)

    ppm.modify.type = p.Results.type;
    ppm.modify.name = p.Results.name;
    ppm.modify.axis = p.Results.axis;

    % unify impermissible anisotropic scaling for bendy bones other than Size-Bendy
    if ~all(~diff(scale_reshape),'all') && ~all(ismember(p.Results.name,'Size-Bendy'))...
            && p.Results.auto_correct
        % first non-zero element
        % first_scale_val_row = arrayfun(@(X)  find(scale_reshape(X,:),1,'first'), ...
        %                                1:size(scale_reshape,2));
        val_reshaped = scale_reshape;
        val_reshaped(2:end,:) = repmat(scale_reshape(1,:),2,1);
        val_unified = val_reshaped(:);

        ppm.modify.val = cell2mat(p.Results.val);
        ppm.modify.val(scale_idx_local) = val_unified;
    else
        ppm.modify.val = cell2mat(p.Results.val);
    end

else

    if strcmp(p.Results.type,'Scale') && ~strcmp(p.Results.name,'Size-Bendy')
        % address isotropic scaling of bendy bones
        ppm.modify.type = repmat(cellstr(p.Results.type),3,1);
        ppm.modify.name = repmat(cellstr(p.Results.name),3,1);
        ppm.modify.axis = [cellstr(p.Results.axis); axes_other];
        ppm.modify.val = repmat(p.Results.val,3,1);
    else
        ppm.modify.type = p.Results.type;
        ppm.modify.name = p.Results.name;
        ppm.modify.axis = p.Results.axis;
        ppm.modify.val  = p.Results.val;
    end

end

if ~iscell(p.Results.axis)
    if strcmp(p.Results.axis,'#')
        ppm.modify.axis = [];
    end
end

ppm.modify.itr               = p.Results.itr;
ppm.modify.range             = p.Results.range;
ppm.modify.sample_start_idx  = p.Results.sample_start_idx;
ppm.modify.auto_correct      = p.Results.auto_correct;
ppm.modify.instruction_mode  = p.Results.instruction_mode;
ppm.modify.rotation_mode     = p.Results.rotation_mode;
ppm.modify.cam_loc           = p.Results.cam_loc;
ppm.modify.cam_rot           = p.Results.cam_rot;
ppm.modify.cam_loc_ref       = p.Results.cam_loc_ref;
ppm.modify.set_cam           = p.Results.set_cam;
ppm.modify.pc                = p.Results.pc;
ppm.modify.mesh              = p.Results.mesh;
ppm.modify.remesh            = p.Results.remesh;
ppm.modify.image             = p.Results.image;
ppm.modify.image_res         = p.Results.image_res;
ppm.modify.image_col_dep     = p.Results.image_col_dep;
ppm.modify.image_comp        = p.Results.image_comp;
ppm.modify.depth             = p.Results.depth;
ppm.modify.depth_nearest     = p.Results.depth_nearest;
ppm.modify.depth_farthest    = p.Results.depth_farthest;
ppm.modify.depth_col_dep_exr = p.Results.depth_col_dep_exr;
ppm.modify.depth_comp_exr    = p.Results.depth_comp_exr;
ppm.modify.depth_codec_exr   = p.Results.depth_codec_exr;
ppm.modify.depth_col_dep_png = p.Results.depth_col_dep_png;
ppm.modify.depth_comp_png    = p.Results.depth_comp_png;

if isempty(p.Results.depth_nearest) 
    ppm.modify.depth_nearest = 'cam_loc'; % for set_values_and_export_mesh_vX.py
end

%% Assign the specified values to the selected parameter(s)
ppm = ppm_modify_parameter_values(ppm);

%% Render modified mesh
ppm_blender_execute(ppm)

end
