%% MATLAB script for comprehensive functionality tests of the interface to the
%  parametric pinna model (PPM), including bi-directional communication with
%  Blender via Python scripts

% #Author: Florian Pausch (2022)

clear; close all;
    
test_get_values          = true;
test_set_values_single   = true;
test_set_values_multiple = true;
test_evaluate            = true;

%% ppm_initialize()

path_blender_file = fullfile(pwd,'result');
name_blender_file = 'PPM_modified_v1.blend';

path_default        = fullfile(pwd,'default');
path_data           = fullfile(pwd,'data');
path_python         = fullfile(pwd,'python');
path_result         = fullfile(pwd,'result');
path_external       = fullfile(pwd,'external');
name_parameter_file = 'parameter_defaults_v1';
name_limit_file     = 'shape_key_limits_v1';
auto_delete         = {true,false};
verbose_level       = {0,1,2};

fprintf('ppm_init(): Testing...\n')

for idx=1:numel(auto_delete)
    for jdx=1:numel(verbose_level)
        try
            ppm = ppm_initialize(...
                'path_blender_file',path_blender_file,...
                'name_blender_file',name_blender_file,...
                'path_default',path_default,...
                'path_data',path_data,...
                'path_python',path_python,...
                'path_result',path_result,...
                'path_external',path_external,...
                'name_parameter_file',name_parameter_file,...
                'name_limit_file',name_limit_file,...
                'auto_delete',auto_delete{idx},...
                'verbose_level',verbose_level{idx});
        catch e
            disp(e)
        end
    end
end

fprintf('ppm_init(): Sucessfully tested.\n\n')

%% ppm_get_values()

ppm.ini.verbose_level = 2;

type = unique(ppm.parameters(:,1));
name = unique(ppm.parameters(:,2));
axis = unique(ppm.parameters(:,3));
axis = strrep(axis,'#','');
axis(cellfun('isempty',axis)) = {[]};
sample_start_idx = [1,14];

if test_get_values
    fprintf('ppm_get_values(): Testing...\n')
    wb = waitbar(0,'ppm_get_values(): Testing...');
    wb.Children.Title.Interpreter = 'none';
    cnt = 0;
    for idx=1:numel(type)
        for jdx=1:numel(name)
            for kdx=1:numel(axis)
                for ldx=1:numel(sample_start_idx)
                    try
                        [ppm,val] = ppm_get_values(ppm,...
                            'type',type{idx},...
                            'name',name{jdx},...
                            'axis',axis{kdx},...
                            'sample_start_idx',sample_start_idx(ldx));
                    catch e
                        disp(e)
                        if contains(e.identifier,'MATLAB')
                            close(wb)
                            error('Unexpected error.')
                        end
                    end
                end
                cnt = cnt+1;
                waitbar(cnt/numel(name)/numel(type)/numel(axis)/numel(sample_start_idx),wb)
            end
        end
    end
    close(wb)
    fprintf('ppm_get_values(): Sucessfully tested.\n\n')
end

%% ppm_set_values()

val = -4.1;
itr_vec = [1,3];
instruction_mode_cell = {'rel','abs'};

%% Change a single parameter value

if test_set_values_single
    fprintf('ppm_set_values(): Testing single input...\n')
    wb = waitbar(0,'ppm_set_values(): Testing single input...');
    wb.Children.Title.Interpreter = 'none';

    cnt = 0;
    for idx=1:numel(type)
        for jdx=1:numel(name)
            for kdx=1:numel(axis)
                for ldx=1:numel(itr_vec)
                    for mdx=1:numel(instruction_mode_cell)
                        for ndx=1:numel(sample_start_idx)
                            try
                                ppm = ppm_set_values(ppm,...
                                    'type',type{idx},...
                                    'name',name{jdx},...
                                    'axis',axis{kdx},...
                                    'val',val,...
                                    'itr',itr_vec(ldx),...
                                    'range',4,...
                                    'instruction_mode',instruction_mode_cell{mdx}, ...
                                    'sample_start_idx',sample_start_idx(ndx),...
                                    'rotation_mode','quaternion');
                            catch e
                                disp(e)
                                if contains(e.identifier,'MATLAB')
                                    close(wb)
                                    error(['Unexpected error for type=',type{idx},', name=',name{jdx},...
                                        ', axis=',axis{kdx},', instruction_mode=',instruction_mode_cell{ldx},...
                                        ', itr=',num2str(itr_vec(ldx)),'. Aborted.'])
                                end
                            end
                            cnt = cnt+1;
                            waitbar(cnt/numel(name)/numel(type)/numel(axis)/...
                                numel(itr_vec)/numel(instruction_mode_cell)/...
                                numel(sample_start_idx),wb)
                        end
                    end
                end
            end
        end
    end
    close(wb)
    fprintf('ppm_set_values(): Sucessfully tested single input.\n\n')
end

%% Change multiple parameter values

selection_cell = {[1:3,5:10,12:14,33:35,40:42];...
                  [1:3,5:10,12:14,33:35,40:41];...
                  1:size(ppm.parameters,1);...
                  [8:10, 155:159];... % incomplete scaling triplets
                  [8:10, 155:160];... % anisotropic scaling triplets for control bones
                  [8:10, 155:160]};   % isotropic/anisotropic triplets for control bones/size bendy
rotation_cell = {'ZYX','quaternion'};
pc = [false, true];
mesh = [false, true];
image = [false, true];
depth = [false, true];

if test_set_values_multiple

    fprintf('ppm_set_values(): Testing multiple input...\n')
    wb = waitbar(0,'ppm_set_values(): Testing multiple input...');
    wb.Children.Title.Interpreter = 'none';

    cnt = 0;

    for kdx=1:numel(selection_cell)
        for jdx=1:numel(rotation_cell)

            type_cell = ppm.parameters(selection_cell{kdx},1);
            name_cell = ppm.parameters(selection_cell{kdx},2);
            axis_cell = ppm.parameters(selection_cell{kdx},3);
            % axis_cell = strrep(axis_cell,'#','');
            % axis_cell(cellfun('isempty',axis_cell)) = {[]};
            
            switch kdx
                case 5
                    if jdx==1
                        val_cell(1) = cellfun(@(x) x-0.3, ppm.parameters(selection_cell{kdx}(1),4),'UniformOutput',0);
                        val_cell(2) = cellfun(@(x) x+0.2, ppm.parameters(selection_cell{kdx}(2),4),'UniformOutput',0);
                        val_cell(3) = cellfun(@(x) x-0.6, ppm.parameters(selection_cell{kdx}(3),4),'UniformOutput',0);
                        val_cell = val_cell';
                        val_cell = repmat(val_cell,3,1);
                    end
                case 6
                    if jdx==1
                        val_cell(1) = cellfun(@(x) x-0.3, ppm.parameters(selection_cell{kdx}(1),4),'UniformOutput',0);
                        val_cell(2) = cellfun(@(x) x+0.2, ppm.parameters(selection_cell{kdx}(2),4),'UniformOutput',0);
                        val_cell(3) = cellfun(@(x) x-0.6, ppm.parameters(selection_cell{kdx}(3),4),'UniformOutput',0);
                        val_cell(4) = cellfun(@(x) x-0.1, ppm.parameters(selection_cell{kdx}(1),4),'UniformOutput',0);
                        val_cell(5) = cellfun(@(x) x-0.1, ppm.parameters(selection_cell{kdx}(2),4),'UniformOutput',0);
                        val_cell(6) = cellfun(@(x) x-0.1, ppm.parameters(selection_cell{kdx}(3),4),'UniformOutput',0);
                        val_cell = val_cell';
                        val_cell = [val_cell; val_cell(4:6)];
                    end
                otherwise
                    val_cell = cellfun(@(x) x-4.1, ppm.parameters(selection_cell{kdx},4),'UniformOutput',0);
            end

            for ldx=1:numel(itr_vec)
                for mdx=1:numel(instruction_mode_cell)
                    for ndx=1:numel(sample_start_idx)
                        for odx=1:numel(pc)
                            for pdx=1:numel(mesh)
                                for qdx=1:numel(image)
                                    for rdx=1:numel(depth)
                                        try
                                            ppm = ppm_set_values(ppm,...
                                                'type',type_cell,...
                                                'name',name_cell,...
                                                'axis',axis_cell,...
                                                'val',val_cell,...
                                                'itr',itr_vec(ldx),...
                                                'range',4,...
                                                'instruction_mode',instruction_mode_cell{mdx}, ...
                                                'rotation_mode',rotation_cell{jdx},...
                                                'sample_start_idx',sample_start_idx(ndx),...
                                                'pc',pc(odx),...
                                                'mesh',mesh(pdx),...
                                                'image',image(qdx),...
                                                'depth',depth(rdx));
                                        catch e
                                            disp(e)
                                            if contains(e.identifier,'MATLAB')
                                                close(wb)
                                                error(['Unexpected error for instruction_mode=',instruction_mode_cell{ldx},...
                                                    ', itr=',num2str(itr_vec(ldx)),'. Aborted.'])
                                            end
                                        end
                                        cnt = cnt+1;
                                        waitbar(cnt/numel(selection_cell)/numel(rotation_cell)/...
                                            numel(itr_vec)/numel(instruction_mode_cell)/...
                                            numel(sample_start_idx)/numel(pc)/numel(mesh)/...
                                            numel(image)/numel(depth),wb)
                                    end
                                end
                            end
                        end
                    end
                end
            end
        end
        clear val_cell
    end
    close(wb)
    fprintf('ppm_set_values(): Sucessfully tested multiple input.\n\n')

end

%% ppm_evaluate()

selection_cell = {3;...
    [1:3,5:10,12:14,33:35,40:42]};

caxis_min = -3;
caxis_max = 7;
name_mesh_target = 'PPM_default_v1.ply';

if test_evaluate

    fprintf('ppm_evaluate(): Testing...\n')
    wb = waitbar(0,'ppm_set_values(): Testing single input...');
    wb.Children.Title.Interpreter = 'none';

    cnt = 0;

    for kdx=1:numel(selection_cell)
        for ldx=1:numel(itr_vec)
            for mdx=1:numel(sample_start_idx)
                if kdx==1
                    type_cell = char(ppm.parameters(selection_cell{kdx},1));
                    name_cell = char(ppm.parameters(selection_cell{kdx},2));
                    axis_cell = char(ppm.parameters(selection_cell{kdx},3));
                    val_cell = cell2mat(cellfun(@(x) x-4.1, ...
                        ppm.parameters(selection_cell{kdx},4),'UniformOutput',0));
                else
                    type_cell = ppm.parameters(selection_cell{kdx},1);
                    name_cell = ppm.parameters(selection_cell{kdx},2);
                    axis_cell = ppm.parameters(selection_cell{kdx},3);
                    val_cell = cellfun(@(x) x-4.1, ppm.parameters(selection_cell{kdx},4),'UniformOutput',0);
                end

                ppm = ppm_set_values(ppm,...
                    'type',type_cell,...
                    'name',name_cell,...
                    'axis',axis_cell,...
                    'val',val_cell,...
                    'itr',itr_vec(ldx),...
                    'range',4,...
                    'instruction_mode','abs', ...
                    'rotation_mode','quaternion',...
                    'sample_start_idx',sample_start_idx(ndx));

                try
                    ppm = ppm_evaluate(ppm,...
                        'path_pc_target',ppm.ini.path.data,...
                        'name_pc_target',name_mesh_target,...
                        'caxis_min',caxis_min,...
                        'caxis_max',caxis_max,...
                        'sample_start_idx',sample_start_idx(ndx));
                catch e
                    disp(e)
                    if contains(e.identifier,'MATLAB')
                        close(wb)
                        error('Unexpected error. Aborted.')
                    end
                end

                cnt = cnt+1;
                waitbar(cnt/numel(selection_cell)/numel(itr_vec),wb)

            end
        end
        clear val_cell

    end

    close(wb)
    fprintf('ppm_evaluate(): Sucessfully tested.\n\n')
end

