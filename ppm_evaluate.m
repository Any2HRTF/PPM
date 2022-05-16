function ppm = ppm_evaluate(ppm,varargin)
%ppm_evaluate - Evaluate the mesh obtained from the parametric pinna model
%               (PPM) against a target mesh in terms of the Hausdorff distance
%
% Usage: 
%   ppm = ppm_evaluate(ppm,varargin)
%
% Input parameters:
%
%   Required
%     ppm                : PPM structure array, initialized as per 
%                          ppm_initialize() and optionally modified via 
%                          ppm_set_values. Type 'help ppm_initialize' to 
%                          obtain further information [struct].                          
%     'path_mesh_target' : Path to target mesh [string]
%     'name_mesh_target' : File name of target mesh [string]
%
%   Optional
%     .path_mesh_result  : Path to result mesh [string], default: ppm.ini.path.result
%     .name_mesh_result  : File name of result mesh [string], default: '1.ply'
%     'caxis_min'        : lower limit of colorbar [double], default: min(hd)
%     'caxis_max'        : upper limit of colorbar [double], default: max(hd)
%
% Output parameters:
%
%   ppm : PPM structure array extended by
%         .evaluate
%             .val             : if ppm.modify > 1 the parameter value is 
%                                set to the one resulting in the minimum mean
%                                minimum Hausdorff distance across iterations
%             .mesh_target     : target mesh [double]
%             .mesh_result     : resulting mesh after modifications of PPM 
%                                parameters [double]
%             .hd              : minimum Hausdorff distance per point 
%                                of the result mesh [double]
%             .hd_mean         : average minimum Hausdorff distance 
%                                across the entire result mesh per 
%                                iteration (if ppm.modify.itr > 1) [double]
%             .hd_std          : standard deviation of minimum Hausdorff distance 
%                                across the entire result mesh per 
%                                iteration (if ppm.modify.itr > 1) [double]
%             .hd_median       : median of minimum Hausdorff distance 
%                                across the entire result mesh per 
%                                iteration (if ppm.modify.itr > 1) [double]
%             .hd_mean_min     : minimum average minimum Hausdorff distance 
%                                across all iterations mesh (if 
%                                ppm.modify.itr > 1) [double]
%             .hd_mean_min_itr : index of iteration that yielded the 
%                                minimum average minimum Hausdorff distance 
%                                (only relevant if ppm.modify.itr > 1) [double]
%
% Related functions : ppm_initialize, ppm_get_values, ppm_set_values, 
%                     
% Dependencies      : Computer Vision Toolbox

% #Author: Florian Pausch (2022)

%% parse input arguments
p = inputParser;

addOptional(p,'path_mesh_result',ppm.ini.path.result);
addOptional(p,'name_mesh_result','1.ply');
addOptional(p,'path_mesh_target',[]);
addOptional(p,'name_mesh_target',[]);
addOptional(p,'caxis_min',[]);
addOptional(p,'caxis_max',[]);

parse(p,varargin{:});

if (isempty(p.Results.path_mesh_target) || isempty(p.Results.name_mesh_target))
    error('ppm_evaluate: Input error. Please specify ''path_mesh_target'' and ''name_mesh_target''.')
end

if ~isfield(ppm,'modify')
    itr = 1; % set itr=1 if ppm_set_values was not executed
else
    itr = ppm.modify.itr;
end

%% load first result mesh and specified target mesh
mesh_result_temp = pcread(fullfile(p.Results.path_mesh_result,p.Results.name_mesh_result));
ppm.evaluate.mesh_result = mesh_result_temp.Location;

mesh_target_temp = pcread(fullfile(p.Results.path_mesh_target, p.Results.name_mesh_target));
ppm.evaluate.mesh_target = mesh_target_temp.Location;

%% load remaining result meshes obtained in the corresponding iterations
if itr>1
    mesh_result_mtx = zeros(size(ppm.evaluate.mesh_result,1),...
        size(ppm.evaluate.mesh_result,2),itr); 
    mesh_result_mtx(:,:,1) = ppm.evaluate.mesh_result;
    for idx=2:itr
        mesh_result_temp = pcread(fullfile(ppm.ini.path.result,[num2str(idx),'.ply']));
        mesh_result_mtx(:,:,idx) = mesh_result_temp.Location;
    end
    ppm.evaluate.mesh_result = mesh_result_mtx;
end

%% calculate Hausdorff distance and visualize result
if itr==1
    
    % compare result and target meshes
    ppm.evaluate.hd = hausdorff_dist(ppm.evaluate.mesh_result,ppm.evaluate.mesh_target);

    if ppm.ini.verbose_level>0
       
        if isequal(ppm.evaluate.mesh_result,ppm.evaluate.mesh_target)
            warning([mfilename,': Result mesh and target mesh are identical.'])
        end

        figure('units','normalized','outerposition',[0 0 1 1])
        tiledlayout(1,2)

        % plot result mesh with color-coded Hausdorff distance
        ppm_plot_hd(ppm,...
            'caxis_min',p.Results.caxis_min,...
            'caxis_max',p.Results.caxis_max);

        disp([mfilename,': Average Hausdorff distance of the entire mesh (mu+/-sigma, Mdn): ', ...
            [num2str(mean(ppm.evaluate.hd)),'+/-',num2str(std(ppm.evaluate.hd)), ', ', ...
            num2str(median(ppm.evaluate.hd))]]);
    
    end
    
else % itr > 1
    
    % create a matrix to store HDs given by different parameter values
    ppm.evaluate.hd = zeros(size(ppm.evaluate.mesh_result,1),itr);
    
    % Read all the meshes and calculate HDs
    if ppm.ini.verbose_level>0
        wb = waitbar(0,'ppm\_multiple\_hausdorff\_dist: Calculating HD for all iterations...');
    end
    
    for idx = 1:itr
        ppm.evaluate.hd(:,idx) = hausdorff_dist(squeeze(ppm.evaluate.mesh_result(:,:,idx)), ...
            ppm.evaluate.mesh_target);
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
        tiledlayout(2,2)

        % plot HD means over the different parameter values tested
        nexttile
        plot(ppm.modify.val_vec, ppm.evaluate.hd_mean,'o-');
        hold on
        plot(ppm.modify.val_vec(ppm.evaluate.hd_mean_min_itr), ...
            min(ppm.evaluate.hd_mean),'r.','markersize',20);
        set(gca,'xtick',round(ppm.modify.val_vec*1000)/1000)
        xlabel('Parameter value per iteration')
        ylabel ('Mean minimum Hausdorff distance')
        grid minor
        axis square
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

        % Create a graph showing HDs using the parameter value that gives the smallest mean
        nexttile      
        ppm_plot_hd(ppm,...
            'caxis_min',p.Results.caxis_min,...
            'caxis_max',p.Results.caxis_max);

        delete(nexttile(2))

        disp([mfilename,': Average Hausdorff distance of the entire mesh (mu+/-sigma, Mdn): ', ...
            [num2str(mean(ppm.evaluate.hd(:,ppm.evaluate.hd_mean_min_itr))),'+/-', ...
            num2str(std(ppm.evaluate.hd(:,ppm.evaluate.hd_mean_min_itr))), ', ', ...
            num2str(median(ppm.evaluate.hd(:,ppm.evaluate.hd_mean_min_itr)))]]);
    end
   
    if isequal(squeeze(ppm.evaluate.mesh_result(:,:,ppm.evaluate.hd_mean_min_itr)), ...
            ppm.evaluate.mesh_target)
        warning([mfilename,': Result mesh and target mesh are identical.'])
    end

end

