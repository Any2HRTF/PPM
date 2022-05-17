function ppm = ppm_modify_parameter_values_v1_2(ppm)
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
if strcmp(ppm.modify.type,"Shape_key")
    ppm.modify.idx = find(strcmp(ppm.modify.type,ppm.parameters(:,1)) & ...
        strcmp(ppm.modify.name,ppm.parameters(:,2)));
else % additionally check axis
    ppm.modify.idx = find(strcmp(ppm.modify.type,ppm.parameters(:,1)) & ...
        strcmp(ppm.modify.name,ppm.parameters(:,2)) & ...
        strcmp(ppm.modify.axis,ppm.parameters(:,3)));
end

%% store original parameter value before modifications
ppm.modify.val_orig = ppm.parameters{ppm.modify.idx,4};

%% check if set value is within limits
if strcmp(ppm.modify.type,"Shape_key")
    
    lim_low = ppm.ini.shape_key_limits{ppm.modify.idx-9,2};
    lim_up = ppm.ini.shape_key_limits{ppm.modify.idx-9,3};
    if ppm.modify.val > lim_up

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
if ppm.modify.itr == 1
    
    ppm = ppm_add_or_assign(ppm);
    writecell(ppm.parameters, fullfile(ppm.ini.path.result, '1.txt'));

    if ppm.modify.set_cam
        % save camera perspective as txt-file to be loaded by set_values_and_export_mesh.py
        cam_pose = [ppm.modify.cam_loc; ppm.modify.cam_rot];
        writematrix(cam_pose,fullfile(ppm.ini.path.result,'1_cam.txt'))
    end
    
else % ppm.modify.itr > 1
    
    ppm.modify.stp = ppm.modify.range/(ppm.modify.itr-1); % calculate step size for the parameter values to be tested
    
    if strcmp(ppm.modify.instruction_mode,'rel')
        ppm.modify.val_vec = ((ppm.modify.val+ppm.modify.val_orig)-ppm.modify.range/2:...
            ppm.modify.stp:...
            (ppm.modify.val+ppm.modify.val_orig)+ppm.modify.range/2); % create a vector of values to be tested
    else
        ppm.modify.val_vec = (ppm.modify.val-ppm.modify.range/2:...
            ppm.modify.stp:...
            ppm.modify.val+ppm.modify.range/2); % create a vector of values to be tested
    end

    if strcmp(ppm.modify.type,"Shape_key")
        if ppm.ini.verbose_level>0 && (any(ppm.modify.val_vec(ppm.modify.val_vec<lim_low)) || ...
                any(ppm.modify.val_vec(ppm.modify.val_vec>lim_up)))
            warning([mfilename,': Range of values of the Shape_key parameter selected exceeds the limits. ',...
                'Select a value from ', num2str(lim_low), ' to ',num2str(lim_up),...
                ' (set was limited to parameter limits).']);
            ppm.modify.val_vec(ppm.modify.val_vec<lim_low) = lim_low;
            ppm.modify.val_vec(ppm.modify.val_vec>lim_up) = lim_up;
        end
    end
    
    % create different blender instruction files that contain the range of
    % values to be tested
    for idx = 1:ppm.modify.itr
        ppm.modify.val = ppm.modify.val_vec(idx);
        
        ppm = ppm_add_or_assign(ppm);
        writecell(ppm.parameters, fullfile(ppm.ini.path.result,[num2str(idx), '.txt']));

        if ppm.modify.set_cam
            % save camera perspective as txt-file to be loaded by set_values_and_export_mesh.py
            cam_pose = [ppm.modify.cam_loc; ppm.modify.cam_rot];
            writematrix(cam_pose,fullfile(ppm.ini.path.result,[num2str(idx),'_cam.txt']))
        end

    end
    
end

end

%% add or assign value to parameter depending on ppm.modify.instruction_mode
function ppm = ppm_add_or_assign(ppm)

% transform quaternions to Euler angles as per ppm.modify.rotation_mode and
% reconstruct quaternion from modified Euler angle component
if ~strcmp(ppm.modify.rotation_mode,'quaternion') && strcmp(ppm.modify.type,'Rotation')

    idx = find( strcmp(ppm.modify.type,ppm.parameters(:,1)) & ...
        strcmp(ppm.modify.name,ppm.parameters(:,2)) );
    val_orig = cell2mat( ppm.parameters(idx,4) );

    q = quaternion(val_orig);
    angles_Eul = EulerAngles(q,lower(ppm.modify.rotation_mode));

    str_idx = strfind(ppm.modify.rotation_mode,ppm.modify.axis);

    % execute depending on specified instruction mode
    switch ppm.modify.instruction_mode
        case 'rel'
            angles_Eul(str_idx) = angles_Eul(str_idx) + deg2rad(ppm.modify.val);
        case 'abs'
            angles_Eul(str_idx) = deg2rad(ppm.modify.val);
    end

    % reconstruct quaternion from modified Euler angles
    q_rec = quaternion.eulerangles(lower(ppm.modify.rotation_mode),angles_Eul);
    ppm.parameters(idx,4) = num2cell(q_rec.e);

else

    % execute depending on specified instruction mode
    switch ppm.modify.instruction_mode
        case 'rel'
            ppm.parameters{ppm.modify.idx,4} = ppm.modify.val_orig + ppm.modify.val;
        case 'abs'
            ppm.parameters{ppm.modify.idx,4} = ppm.modify.val;
    end

end

end