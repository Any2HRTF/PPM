function ppm = ppm_evaluate(ppm,varargin)
%ppm_evaluate - Evaluate the parametric-pinna-model (PPM) point cloud against a 
%               target point cloud in terms of the Hausdorff distance
%
% Usage: 
%
%   ppm = ppm_evaluate(ppm,varargin)
%
% Input parameters:
%
%   Required
%     ppm                : PPM structure array, initialized as per 
%                          ppm_initialize() and optionally modified via 
%                          ppm_set_values() [struct]                          
%     'path_pc_target'   : Path to target point cloud [string]
%     'name_pc_target'   : File name of target point cloud [string]
%
%   Optional
%     'sample_start_idx' : File-name index. If itr>1 the exported PLY files 
%                          start at this index and are incremented [double], 
%                          default: 1
%     'caxis_min'        : Lower limit of colorbar [double], default: min(hd)
%     'caxis_max'        : Upper limit of colorbar [double], default: max(hd)
%
% Output parameters:
%
%   ppm : PPM structure array extended by
%         .evaluate
%             .val             : If ppm.modify > 1 the parameter value is 
%                                set to the one resulting in the minimum mean
%                                minimum Hausdorff distance across iterations
%             .pc_target       : Target point cloud [double]
%             .pc_result       : Resulting point cloud after modifications of PPM 
%                                parameters [double]
%             .sample_start_idx [double]
%             .hd              : Minimum Hausdorff distance per point 
%                                of the result point cloud [double]
%             .hd_mean         : Average minimum Hausdorff distance 
%                                across the entire result point cloud per 
%                                iteration (if ppm.modify.itr > 1) [double]
%             .hd_std          : Standard deviation of minimum Hausdorff distance 
%                                across the entire result point cloud per 
%                                iteration (if ppm.modify.itr > 1) [double]
%             .hd_median       : Median of minimum Hausdorff distance 
%                                across the entire result point cloud per 
%                                iteration (if ppm.modify.itr > 1) [double]
%             .hd_mean_min     : Minimum average minimum Hausdorff distance 
%                                across all iterations point cloud (if 
%                                ppm.modify.itr > 1) [double]
%             .hd_mean_min_itr : Index of iteration that yielded the 
%                                minimum average minimum Hausdorff distance 
%                                (only relevant if ppm.modify.itr > 1) [double]
%
% Related functions : ppm_initialize, ppm_get_values, ppm_set_values, 
%                     
% Dependencies      : Computer Vision Toolbox

% #Author: Florian Pausch (2022)

%% Parse input arguments
p = inputParser;

addOptional(p,'path_pc_target',[]);
addOptional(p,'name_pc_target',[]);
addOptional(p,'sample_start_idx',1);
addOptional(p,'caxis_min',[]);
addOptional(p,'caxis_max',[]);

parse(p,varargin{:});

if (isempty(p.Results.path_pc_target) || isempty(p.Results.name_pc_target))
    error('ppm_evaluate: Input error. Please specify ''path_pc_target'' and ''name_pc_target''.')
end

if ~isfield(ppm,'modify')
    itr = 1; % set itr=1 if ppm_set_values was not executed
else
    itr = ppm.modify.itr;
end

%% Set default MATLAB renderer
set(0, 'DefaultFigureRenderer', 'opengl');

%% Load specified target point cloud
if ~exist(fullfile(p.Results.path_pc_target, ...
    p.Results.name_pc_target),'file')
    error('Path error: File ''name_pc_target'' does not exist in ''path_pc_target''.')
end
pc_target_temp = pcread(fullfile(p.Results.path_pc_target, ...
    p.Results.name_pc_target));
ppm.evaluate.pc_target = double(pc_target_temp.Location);

%% Load result point clouds exported in the corresponding iterations
pc_result = dir(fullfile(strrep(ppm.ini.path.result,'"',''),'pc'));
pc_result_name = {pc_result(3:end).name};

if itr==1
    try
        pc_result_temp = pcread(fullfile(fullfile(strrep(ppm.ini.path.result,'"',''),'pc'), ...
            [num2str(p.Results.sample_start_idx),'.ply']));
    catch
        error(['Input error. Result point cloud ', ...
            fullfile(fullfile(strrep(ppm.ini.path.result,'"',''),'ply'), [num2str(p.Results.sample_start_idx),'.ply']),...
            ' does not exist. Consider specifying ''sample_start_idx''.'])
    end
    ppm.evaluate.pc_result = pc_result_temp.Location;
else % itr>1
    try
        pc_result_temp = pcread(fullfile(fullfile(strrep(ppm.ini.path.result,'"',''),'pc'), ...
            [num2str(p.Results.sample_start_idx),'.ply']));
    catch
        error(['Input error. Result point cloud ', ...
            fullfile(fullfile(strrep(ppm.ini.path.result,'"',''),'ply'), [num2str(p.Results.sample_start_idx),'.ply']),...
            ' does not exist. Consider specifying ''sample_start_idx''.'])
    end
    ppm.evaluate.pc_result = pc_result_temp.Location;

    pc_result_mtx = zeros(size(ppm.evaluate.pc_result,1),...
        size(ppm.evaluate.pc_result,2),itr); 
    pc_result_mtx(:,:,1) = ppm.evaluate.pc_result;
    for idx=p.Results.sample_start_idx+1:p.Results.sample_start_idx+itr-1
        pc_result_temp = pcread(fullfile(fullfile(strrep(ppm.ini.path.result,'"',''),'pc'),...
            pc_result_name{idx-p.Results.sample_start_idx+1}));
        pc_result_mtx(:,:,idx-p.Results.sample_start_idx+1) = pc_result_temp.Location;
    end
    ppm.evaluate.pc_result = pc_result_mtx;
end

%% Calculate Hausdorff distance and visualize result
if itr==1
    
    % Compare result and target point clouds
    ppm.evaluate.hd = hausdorff_dist(ppm.evaluate.pc_result,ppm.evaluate.pc_target);

    if ppm.ini.verbose_level>0
       
        if isequal(ppm.evaluate.pc_result,ppm.evaluate.pc_target)
            warning([mfilename,': Result point cloud and target point cloud are identical.'])
        end

        figure('units','normalized','outerposition',[0 0 1 1])
        tiledlayout(1,2)

        % Plot result point cloud with color-coded Hausdorff distance
        ppm_plot_hd(ppm,...
            'caxis_min',p.Results.caxis_min,...
            'caxis_max',p.Results.caxis_max);

        disp([mfilename,': Average minimum pointwise distance (mu+/-sigma, Mdn): ', ...
            [num2str(mean(ppm.evaluate.hd)),'+/-',num2str(std(ppm.evaluate.hd)), ', ', ...
            num2str(median(ppm.evaluate.hd))]]);
    
    end
    
else % itr > 1
    
    % Create a matrix to store HDs given by different parameter values
    ppm.evaluate.hd = zeros(size(ppm.evaluate.pc_result,1),itr);
    
    % Read all the point clouds and calculate HDs
    if ppm.ini.verbose_level>0
        wb = waitbar(0,'ppm\_multiple\_hausdorff\_dist: Calculating HD for all iterations...');
    end
    
    for idx = 1:itr
        ppm.evaluate.hd(:,idx) = hausdorff_dist(squeeze(ppm.evaluate.pc_result(:,:,idx)), ...
            ppm.evaluate.pc_target);
        if ppm.ini.verbose_level>0
            waitbar(idx/itr,wb)
        end
    end
    
    if ppm.ini.verbose_level>0
        close(wb)
    end
    
    ppm.evaluate.hd_mean   = mean(ppm.evaluate.hd); % calculate means of minimum HDs
    ppm.evaluate.hd_std    = std(ppm.evaluate.hd); % calculate standard deviation of minimum HDs
    ppm.evaluate.hd_median = median(ppm.evaluate.hd); % calculate median of minimum HDs
    [ppm.evaluate.hd_mean_min,ppm.evaluate.hd_mean_min_itr] = min(ppm.evaluate.hd_mean); % find the smallest mean of minimum HDs
    ppm.modify.val = ppm.modify.val_vec(ppm.evaluate.hd_mean_min_itr); % assign parameter value with lowest HD to parameter

    if ppm.ini.verbose_level>0
        figure('units','normalized','outerposition',[0 0 1 1])
        
        if size(ppm.modify.val_vec,1)>1
            tiledlayout(1,2)
        else
            tiledlayout(2,2)

            % Plot HD means over the different parameter values tested
            nexttile
            plot(ppm.modify.val_vec, ppm.evaluate.hd_mean,'o-');
            hold on
            plot(ppm.modify.val_vec(ppm.evaluate.hd_mean_min_itr), ...
                min(ppm.evaluate.hd_mean),'r.','markersize',20);
            set(gca,'xtick',round(ppm.modify.val_vec*1000)/1000)
            xlabel('Parameter value per iteration')
            ylabel ('Mean minimum pointwise distance')
            grid minor
            axis square
            axis vis3d
            if strcmp(ppm.modify.type,'Shape key')
                title(sprintf('Parameter Nr. %d: %s, %s',ppm.modify.idx,...
                    ppm.modify.type,...
                    ppm.modify.name))
            else
                title(sprintf('Parameter Nr. %d: %s, %s (%s)',ppm.modify.idx,...
                    ppm.modify.type,...
                    ppm.modify.name,...
                    ppm.modify.axis))
            end
        end

        % Create a graph showing HDs using the parameter value that gives the smallest mean
        if size(ppm.modify.val_vec,1)==1
            nexttile
        end
        ppm_plot_hd(ppm,...
            'caxis_min',p.Results.caxis_min,...
            'caxis_max',p.Results.caxis_max);

        if size(ppm.modify.val_vec,1)==1
            delete(nexttile(2))
        end

        disp([mfilename,': Average minimum pointwise distance (mu+/-sigma, Mdn): ', ...
            [num2str(mean(ppm.evaluate.hd(:,ppm.evaluate.hd_mean_min_itr))),'+/-', ...
            num2str(std(ppm.evaluate.hd(:,ppm.evaluate.hd_mean_min_itr))), ', ', ...
            num2str(median(ppm.evaluate.hd(:,ppm.evaluate.hd_mean_min_itr)))]]);
    end
   
    if isequal(squeeze(ppm.evaluate.pc_result(:,:,ppm.evaluate.hd_mean_min_itr)), ...
            ppm.evaluate.pc_target)
        warning([mfilename,': Result point cloud and target point cloud are identical.'])
    end

end