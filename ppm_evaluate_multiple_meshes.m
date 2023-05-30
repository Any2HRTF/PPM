%% MATLAB script to evaluate multiple PPM template meshes against the
%  corresponding target meshes in terms of the Hausdorff distance
%
% Related functions : ppm_initialize, ppm_get_values, ppm_evaluate

% #Author: Florian Pausch (2023)

clear; close all; clc

%% Define meshes/files to be compared
ppm_path = 'path to Blender file(s)';
target_path = 'path to corresponding target ply file(s)';

mesh_ppm = {
    'ID1.blend',...
    'ID2.blend',...
    'ID3.blend'
};

mesh_target = {
    'ID1_target.ply',...
    'ID2_target.ply',...
    'ID3_target.ply'
};

sel = 1:6; % select PPMs to be evaluated

wb = waitbar(0,sprintf('Evaluating mesh %s/%s...',...
    num2str(1),num2str(numel(sel))));
idx_wb = 1;

for idx=sel

    %% Initialize ppm
    ppm = ppm_initialize(...
        'path_blender_file',ppm_path,...
        'name_blender_file',mesh_ppm{idx},...
        'verbose_level',0,...
        'auto_delete',true);

    %% Get parameter values from the specified blender file
    [ppm,val] = ppm_get_values(ppm);

    %% Compare the resulting mesh to the specified target mesh
    %  and evaluate its fit based on pointwise minimum distances, plot result
    ppm = ppm_evaluate(ppm,...
        'path_pc_target',target_path,...
        'name_pc_target',mesh_target{idx});

    % Plot result mesh with color-coded directed pointwise minimum distance
    if idx==sel(1)
        figure('units','normalized','outerposition',[0.19,0.05,0.62,0.91])
        tiledlayout(numel(sel),2)
    end
    ppm_plot_distance(ppm,...
        'caxis_min',0,...
        'caxis_max',5);

    fprintf([mfilename,': ', mesh_ppm{idx},'\nMinimum pointwise distances\n'])
    Direction = ["1";"2";"Both"];
    Min = [min(ppm.evaluate.dist_dir1); min(ppm.evaluate.dist_dir2); nan];
    Max = [max(ppm.evaluate.dist_dir1); max(ppm.evaluate.dist_dir2); nan];
    Mean = [mean(ppm.evaluate.dist_dir1); mean(ppm.evaluate.dist_dir2); nan];
    Std = [std(ppm.evaluate.dist_dir1); std(ppm.evaluate.dist_dir2); nan];
    Median = [median(ppm.evaluate.dist_dir1); median(ppm.evaluate.dist_dir2); nan];
    Perc95 = [prctile(ppm.evaluate.dist_dir1,95); prctile(ppm.evaluate.dist_dir2,95); nan];
    Hausdorff = [nan; nan; ppm.evaluate.hd];

    tab = table(Direction,Min,Max,Mean,Std,Median,Perc95,Hausdorff);
    tab = renamevars(tab,"Perc95","95th percentile");
    disp(tab)

    if idx_wb<numel(sel)
        waitbar(idx_wb/numel(sel),wb,sprintf('Evaluating mesh %s/%s...',...
            num2str(idx_wb+1),num2str(numel(sel))));
        idx_wb = idx_wb+1;
    end

end
close(wb)
