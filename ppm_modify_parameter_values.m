function ppm = ppm_modify_parameter_values(ppm)
%ppm_modify_parameter_values - Change the value of the parameter to be modified. 
%                    Depending on the instruction mode, the specified value 
%                    is either added to the existing value of, or directly assigned 
%                    to the selected parameter. The parametric pinna model 
%                    (PPM) structure array is updated accordingly.
%
% Usage: 
%   ppm = ppm_modify_parameter_values(ppm)
%
% Input parameters:
%
%   ppm : PPM structure array [struct]. Initialized as per ppm_initialize().
%
% Output parameters:
%
%   ppm : updated PPM structure array [struct]
%
% Note: This function is called within ppm_set_values().

% #Author: Florian Pausch (2022)

%% determine ppm.modify.idx
if iscell(ppm.modify.type) || iscell(ppm.modify.name) || iscell(ppm.modify.axis)
    ppm.modify.idx = zeros(size(ppm.modify.type,1),1);
    for idx=1:size(ppm.modify.type,1)
        ppm.modify.idx(idx) = find( strcmp(ppm.modify.type{idx},ppm.parameters(:,1)) & ...
            strcmp(ppm.modify.name{idx},ppm.parameters(:,2)) & ...
            strcmp(ppm.modify.axis{idx},ppm.parameters(:,3)) );
    end
else
    if strcmp(ppm.modify.type,'Shape_key')
        ppm.modify.idx = find(strcmp(ppm.modify.type,ppm.parameters(:,1)) & ...
            strcmp(ppm.modify.name,ppm.parameters(:,2)));
    else % additionally check axis
        ppm.modify.idx = find(strcmp(ppm.modify.type,ppm.parameters(:,1)) & ...
            strcmp(ppm.modify.name,ppm.parameters(:,2)) & ...
            strcmp(ppm.modify.axis,ppm.parameters(:,3)));
    end
end

%% store original parameter value before modifications
if iscell(ppm.modify.type) || iscell(ppm.modify.name) || iscell(ppm.modify.axis)
    ppm.modify.val_orig = cell2mat(ppm.parameters(ppm.modify.idx,4));
else
    ppm.modify.val_orig = ppm.parameters{ppm.modify.idx,4};
end

%% check if set shape-key value/s is/are within limits
if iscell(ppm.modify.type) || iscell(ppm.modify.name) || iscell(ppm.modify.axis)

    if any( ismember(ppm.modify.type,'Shape_key') )

        shape_key_idx_local = find(strcmp('Shape_key',ppm.modify.type));
        shape_key_idx_all = find(strcmp('Shape_key',ppm.parameters(:,1)));
        [~,shape_key_idx_global] = ismember( ppm.modify.name(ismember( ppm.modify.name, ppm.parameters(shape_key_idx_all,2))), ...
            ppm.parameters(:,2) );
        shape_key_idx = shape_key_idx_global-10;

        lim_low = cell2mat( ppm.ini.shape_key_limits(shape_key_idx,2) );
        lim_up = cell2mat( ppm.ini.shape_key_limits(shape_key_idx,3) );

        if any(ppm.modify.val(shape_key_idx_local) > lim_up)
            if ppm.ini.verbose_level>0
                warning([mfilename,': The value/s of the shape-key parameter/s selected exceed/s the upper limit/s. Upper limit/s was/were assigned as value/s.']);
            end
            ppm.modify.val(shape_key_idx_local) = lim_up;
        end

        if any(ppm.modify.val(shape_key_idx_local) < lim_low)
            if ppm.ini.verbose_level>0
                warning([mfilename,': The value/s of the shape-key parameter/s selected exceed/s the lower limit/s. Lower limit/s was/were assigned as value/s.']);
            end
            ppm.modify.val(shape_key_idx_local) = lim_low;
        end

    end

else

    if strcmp(ppm.modify.type,"Shape_key")

        lim_low = ppm.ini.shape_key_limits{ppm.modify.idx-10,2};
        lim_up = ppm.ini.shape_key_limits{ppm.modify.idx-10,3};
        if ppm.modify.val > lim_up
            if ppm.ini.verbose_level>0
                warning([mfilename,': The value of the Shape_key parameter you selected exceeds the upper limit of ',...
                    num2str(lim_up),'. Upper limit was assigned to the value.']);
            end
            ppm.modify.val = lim_up;
        end

        if  ppm.modify.val < lim_low
            if ppm.ini.verbose_level>0
                warning([mfilename,': The value of the Shape_key parameter you selected exceeds the lower limit of ',...
                    num2str(lim_low),'. Lower limit was assigned to the value.']);
            end
            ppm.modify.val = lim_low;
        end
    end

end

%% modify the instruction file
% itr=1
if ppm.modify.itr == 1

    ppm = ppm_add_or_assign(ppm);
    writecell(ppm.parameters, fullfile(ppm.ini.path.result, 'parameters', ...
        [num2str(ppm.modify.sample_start_idx),'.txt']));

    if ppm.modify.set_cam && ppm.modify.image
        % save camera perspective as txt-file to be loaded by set_values_and_export_mesh.py
        cam_pose = [ppm.modify.cam_loc; ppm.modify.cam_rot; ppm.modify.cam_loc_ref];

        if ~exist(fullfile(ppm.ini.path.result,'cam'),'dir')
            mkdir(fullfile(ppm.ini.path.result,'cam'))
        end
        writematrix(cam_pose,fullfile(ppm.ini.path.result,'cam',...
            [num2str(ppm.modify.sample_start_idx),'_cam.txt']))
    end

else % ppm.modify.itr > 1

    ppm.modify.stp = ppm.modify.range/(ppm.modify.itr-1); % calculate step size for the parameter values to be modified
    ppm.modify.val_vec = zeros(numel(ppm.modify.val), ...
        numel((ppm.modify.val+ppm.modify.val_orig)-ppm.modify.range/2:...
        ppm.modify.stp:...
        (ppm.modify.val+ppm.modify.val_orig)+ppm.modify.range/2));

    if strcmp(ppm.modify.instruction_mode,'rel')
        for idx=1:size(ppm.modify.val,1)
            ppm.modify.val_vec(idx,:) = ((ppm.modify.val(idx)+ppm.modify.val_orig(idx))-ppm.modify.range/2:...
                ppm.modify.stp:...
                (ppm.modify.val(idx)+ppm.modify.val_orig(idx))+ppm.modify.range/2); % create a vector of values to be modified
        end
    else
        for idx=1:size(ppm.modify.val,1)
            ppm.modify.val_vec(idx,:) = (ppm.modify.val(idx)-ppm.modify.range/2:...
                ppm.modify.stp:...
                ppm.modify.val(idx)+ppm.modify.range/2); % create a vector of values to be modified
        end
    end

    % set limits of .val_vec according to ppm.ini.name_limit_file
    % cell-array input
    if iscell(ppm.modify.type) || iscell(ppm.modify.name) || iscell(ppm.modify.axis)

        if any(strcmp(ppm.modify.type,"Shape_key"))
            for idx=1:ppm.modify.itr
                if ppm.ini.verbose_level>0 && ( ...
                        any( ppm.modify.val_vec(shape_key_idx_local,idx)<lim_low ) || ...
                        any( ppm.modify.val_vec(shape_key_idx_local,idx)>lim_up ) )
                    warning([mfilename,': Range of values of the selected shape-key parameter exceeds the limits. Affected parameter values were set according to the corresponding limits.'])
                    
                    idx_min_vio = shape_key_idx_local(ppm.modify.val_vec(shape_key_idx_local,idx)<lim_low);
                    if ~isempty(idx_min_vio)
                        ppm.modify.val_vec(idx_min_vio, idx) = lim_low(idx_min_vio-min(idx_min_vio)+1);
                    end

                    idx_max_vio = shape_key_idx_local(ppm.modify.val_vec(shape_key_idx_local,idx)>lim_up);                 
                    if ~isempty(idx_max_vio)
                        ppm.modify.val_vec(idx_max_vio, idx) = lim_up(idx_max_vio-min(idx_max_vio)+1);
                    end

                end
            end     
        end

    else % single input

        if strcmp(ppm.modify.type,"Shape_key")
            if ppm.ini.verbose_level>0 && (any(ppm.modify.val_vec(ppm.modify.val_vec<lim_low)) || ...
                    any(ppm.modify.val_vec(ppm.modify.val_vec>lim_up)))
                warning([mfilename,': Range of values of the selected shape-key parameter exceeds the limits. ',...
                    'Select a value between ', num2str(lim_low), ' and ',num2str(lim_up),...
                    ' (set was limited as per parameter limits).']);
                ppm.modify.val_vec(ppm.modify.val_vec<lim_low) = lim_low;
                ppm.modify.val_vec(ppm.modify.val_vec>lim_up) = lim_up;
            end
        end

    end

    % create different blender instruction files that contain the range of
    % values to be tested
    for idx = ppm.modify.sample_start_idx:ppm.modify.sample_start_idx+ppm.modify.itr-1
        ppm.modify.val = ppm.modify.val_vec(:,idx-ppm.modify.sample_start_idx+1);

        ppm = ppm_add_or_assign(ppm);
        writecell(ppm.parameters, fullfile(ppm.ini.path.result,'parameters',...
            [num2str(idx), '.txt']));

        if ppm.modify.set_cam && ppm.modify.image
            if ~exist(fullfile(ppm.ini.path.result,'cam'),'dir')
                mkdir(fullfile(ppm.ini.path.result,'cam'))
            end

            % save camera perspective as txt-file to be loaded by set_values_and_export_mesh.py
            cam_pose = [ppm.modify.cam_loc; ppm.modify.cam_rot; ppm.modify.cam_loc_ref];
            writematrix(cam_pose,fullfile(ppm.ini.path.result,'cam',[num2str(idx),'_cam.txt']))
        end

    end
end

end

%% add or assign value/s to parameter/s depending on ppm.modify.instruction_mode
function ppm = ppm_add_or_assign(ppm)

% transform quaternions to Euler angles as per ppm.modify.rotation_mode and
% reconstruct quaternion from modified Euler angle component
if any( ~strcmp(ppm.modify.rotation_mode,'quaternion') & strcmp(ppm.modify.type,'Rotation') )
    
    if iscell(ppm.modify.type) || iscell(ppm.modify.name) || ...
            iscell(ppm.modify.axis) || iscell(ppm.modify.val)

        rotation_idx_local = find(strcmp(ppm.modify.type,'Rotation'));
        rotation_idx = zeros(numel(rotation_idx_local),1);
        for idx=rotation_idx_local'
            [~,rotation_idx(idx)] = max( ...
                strcmp(ppm.modify.type{idx},ppm.parameters(:,1)) & ...
                strcmp(ppm.modify.name{idx},ppm.parameters(:,2)) & ...
                strcmp(ppm.modify.axis{idx},ppm.parameters(:,3)) );
        end
        rotation_idx(rotation_idx==0) = [];

        % select corresponding quaternion-rotation entries
        rotation_idx_quat = zeros(numel(rotation_idx)+numel(rotation_idx)/3,1);
        rotation_idx_quat(1:4:end) = rotation_idx(1:3:end)-1;
        rotation_idx_quat(rotation_idx_quat==0) = rotation_idx;
        if length(rotation_idx_quat)>4
            val_orig = cell2mat( reshape(ppm.parameters(rotation_idx_quat,4),...
                numel(rotation_idx_quat)/3, numel(rotation_idx)/3) );
        else
            val_orig = cell2mat( ppm.parameters(rotation_idx_quat,4) );
        end

    else
        
        [~,rotation_idx] = max( ...
            strcmp(ppm.modify.type,ppm.parameters(:,1)) & ...
            strcmp(ppm.modify.name,ppm.parameters(:,2)) & ...
            strcmp(ppm.modify.axis,ppm.parameters(:,3)) );

        % select corresponding quaternion-rotation entries
        rotation_idx_quat = find( ...
            strcmp(ppm.modify.type,ppm.parameters(:,1)) & ...
            strcmp(ppm.modify.name,ppm.parameters(:,2)) );
        [~, rotation_idx_local] = max(rotation_idx==rotation_idx_quat);
        rotation_idx_local = rotation_idx_local-1;
        val_orig = cell2mat(ppm.parameters(rotation_idx_quat,4));
        
    end

    q = quaternion(val_orig);
    angles_Eul = EulerAngles(q,lower(ppm.modify.rotation_mode));

    % execute depending on specified instruction mode
    switch ppm.modify.instruction_mode
        case 'rel'
            if length(ppm.modify.val)>1
                angles_Eul = angles_Eul + ...
                    reshape( deg2rad(ppm.modify.val(rotation_idx_local)), size(angles_Eul));
            else
                angles_Eul(rotation_idx_local) = angles_Eul(rotation_idx_local) + deg2rad(ppm.modify.val);
            end
        case 'abs'
            if length(ppm.modify.val)>1
                angles_Eul = reshape( deg2rad(ppm.modify.val(rotation_idx_local)),...
                    size(angles_Eul) );
            else
                angles_Eul(rotation_idx_local) = deg2rad(ppm.modify.val);
            end
    end

    % reconstruct quaternion from modified Euler angles
    q_rec = quaternion.eulerangles(lower(ppm.modify.rotation_mode),angles_Eul);
    q_rec_double = squeeze(q_rec.double);
    ppm.parameters(rotation_idx_quat,4) = num2cell(q_rec_double(:));

    % change remaining values depending on specified instruction mode
    switch ppm.modify.instruction_mode
        case 'rel'
            ppm.parameters(ppm.modify.idx(setdiff(ppm.modify.idx,rotation_idx_quat)),4) = ...
                num2cell(ppm.modify.val_orig(setdiff(ppm.modify.idx,rotation_idx_quat)) + ...
                         ppm.modify.val(setdiff(ppm.modify.idx,rotation_idx_quat)));
        case 'abs'
            ppm.parameters(setdiff(ppm.modify.idx,rotation_idx_quat),4) = ...
                num2cell(ppm.modify.val(setdiff(ppm.modify.idx,rotation_idx_quat)));
    end

else

    % execute depending on specified instruction mode
    switch ppm.modify.instruction_mode
        case 'rel'
            ppm.parameters(ppm.modify.idx,4) = ...
                num2cell(ppm.modify.val_orig + ppm.modify.val);

        case 'abs'
            ppm.parameters(ppm.modify.idx,4) = ...
                num2cell(ppm.modify.val);
    end

end

% apply shape-key limits to ppm.parameters (if instruction mode 'rel' resulted 
% in further violations of the shape-key limits)
shape_key_idx_all = find(strcmp('Shape_key',ppm.parameters(:,1)));

sk_min_val = cell2mat(ppm.ini.shape_key_limits(:,2));
sk_min_vio_idx = cell2mat(ppm.parameters(shape_key_idx_all,4)) < sk_min_val;

sk_max_val = cell2mat(ppm.ini.shape_key_limits(:,3));
sk_max_vio_idx = cell2mat(ppm.parameters(shape_key_idx_all,4)) > sk_max_val;

ppm.parameters(shape_key_idx_all(sk_min_vio_idx),4) = num2cell(sk_min_val(sk_min_vio_idx));
ppm.parameters(shape_key_idx_all(sk_max_vio_idx),4) = num2cell(sk_max_val(sk_max_vio_idx));

end