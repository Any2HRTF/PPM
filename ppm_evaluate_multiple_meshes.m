%% MATLAB script to evaluate multiple PPM template meshes against the
%  corresponding target meshes in terms of the Hausdorff distance
%
% Related functions : ppm_initialize, ppm_get_values, ppm_evaluate

% #Author: Florian Pausch (2022)

clear; close all; clc

%% Define meshes/files to be compared
mesh_ppm = {
    'SOU_BK_mergeHeadEars_Pois_12_7_Smooth_BEMReady_left_ear_adapt_ppm_v1.blend',...
    'SOU_CV_left_ear_adapt_ppm_v1.blend',...
    'SOU_LS_KU100_left_ear_adapt_ppm_v1.blend'};

mesh_target = {
    'SOU_BK_mergeHeadEars_Pois_12_7_Smooth_BEMReady_left_ear.ply',...
    'SOU_CV_left_ear.ply',...
    'SOU_LS_KU100_left_ear.ply'};

sel = 1:3; % select meshes to be evaluated

wb = waitbar(0,sprintf('Evaluating mesh %s/%s...',...
    num2str(1),num2str(numel(sel))));
idx_wb = 1;

for idx=sel

    %% Initialize ppm
    ppm = ppm_initialize(...
        'path_blender_file',fullfile(pwd,'result'),...
        'name_blender_file',mesh_ppm{idx},...
        'verbose_level',0,...
        'auto_delete',true);

    %% Get parameter values from the specified blender file
    [ppm,val] = ppm_get_values(ppm);

    %% Compare the resulting mesh to the specified target mesh
    %  and evaluate its fit based on Hausdorff distances, plot result
    ppm = ppm_evaluate(ppm,...
        'path_mesh_target',ppm.ini.path.data,...
        'name_mesh_target',mesh_target{idx});

    % Plot result mesh with color-coded Hausdorff distance
    if idx==sel(1)
        figure('units','normalized','outerposition',[0.19,0.05,0.62,0.91])
        tiledlayout(numel(sel),2)
    end
    ppm_plot_hd(ppm,...
        'caxis_min',0,...
        'caxis_max',5);

    disp([mfilename,': Average Hausdorff distance of the entire mesh (mu+/-sigma, Mdn): ', ...
        [num2str(mean(ppm.evaluate.hd)),'+/-',num2str(std(ppm.evaluate.hd)), ', ', ...
        num2str(median(ppm.evaluate.hd))]]);

    if idx_wb<numel(sel)
        waitbar(idx_wb/numel(sel),wb,sprintf('Evaluating mesh %s/%s...',...
            num2str(idx_wb+1),num2str(numel(sel))));
        idx_wb = idx_wb+1;
    end

end
close(wb)
