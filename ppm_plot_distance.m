function ppm_plot_distance(ppm,varargin)
%ppm_plot_distance - Plot a target point cloud and contrast it with the result point 
%          cloud, i.e the PPM instance with modified parameters. The latter point cloud
%          is color-coded in terms of the corresponding directed pointwise 
%          minimum-distance values ppm.evaluate.dist_dir1 (with the lowest mean 
%          minimum directed pointwise distance if ppm.modify.itr > 1). 
%
% Usage: 
%
%   plot_distance(ppm)
%
% Input parameters:
%
%   ppm : PPM structure array [struct]. Initialized as per ppm_initialize.
%
% Note: Only the distances d(P,Q) are plotted even when the supremum is  
%       larger in d(Q,P).
%
%
% Related functions: hausdorff_dist

% #Author: Florian Pausch (2023)

%% Parse input arguments
p = inputParser;

addOptional(p,'caxis_min',[]);
addOptional(p,'caxis_max',[]);

parse(p,varargin{:});

caxis_min = p.Results.caxis_min;
caxis_max = p.Results.caxis_max;

if ~isfield(ppm,'modify')
    itr = 1; % set itr=1 if ppm_set_values was not executed
else
    itr = ppm.modify.itr;
end

if itr>1
    dist_dir_mean_min_itr = ppm.evaluate.dist_dir_mean_min_itr;
else
    dist_dir_mean_min_itr = 1;
end

%% Select directed pointwise minimum distances for the direction with larger supremum
distance_val = ppm.evaluate.dist_dir1(:,dist_dir_mean_min_itr);

%% Clip distance values below/above caxis_min/caxis_max for plot
if isempty(p.Results.caxis_min)
    caxis_min = min(distance_val);
else
    distance_val(distance_val<=caxis_min) = caxis_min;
end

if isempty(p.Results.caxis_max)
    caxis_max = max(distance_val);
else
    distance_val(distance_val>=caxis_max) = caxis_max;
end

distance_c = round(distance_val/max(distance_val)*256);  % Convert distance values to range [1 256]

clr = colormap(turbo); % Create a matrix with colormap hue codes
cmatrix = zeros(size(distance_val,1),3); % create a matrix to store color codes corresponding to distance values

if ~all(isnan(distance_c))
    % Fill the matrix with hue codes corresponding to distance values
    for idx=1:size(distance_val,1)
        if distance_c(idx) ~= 0
            cmatrix(idx,:) = clr(distance_c(idx),:);
        else % intercept potential index error
            cmatrix(idx,:) = clr(1,:);
        end
    end
else
   distance_c = 0.8*ones(size(cmatrix));
end

%% Plot color-coded result point cloud and overlay it with target point cloud in grey color
nexttile
ptCloud_target = pointCloud(ppm.evaluate.pc_target, ...
    'Color',0.8*ones(size(ppm.evaluate.pc_target)));
pcshow(ptCloud_target,'MarkerSize', 10);
filename = strsplit(ppm.ini.blender_file,'\');
title(filename{end}(1:end-1),'Interpreter','none')
hold on

% Create new ptCloud with color-coded directed pointwise minimum distances and plot
ptCloud_result = pointCloud(ppm.evaluate.pc_result(:,:,dist_dir_mean_min_itr), ...
    'Color',cmatrix);
pcshow(ptCloud_result,'MarkerSize', 20);

hl = legend('Target ear','PPM instance');
set(hl,'color','white','location','southwestoutside');

if ~all(range(distance_c)==0)
    c=colorbar;
end
c.Label.String = 'Directed pointwise minimum distance (mm)';
c.FontSize = 16;
set(gcf,'color','w');
set(gca,'color','w');

if ~all(range(distance_c)==0)
    caxis([caxis_min, caxis_max])
end
view([180 0])
set(gca,'fontsize',14)


%% Plot histogram of directed pointwise minimum-distance values
nexttile
histogram(distance_val,'EdgeColor','black','FaceColor',[.5 .5 .5]);
xlabel('Directed pointwise minimum distance (mm)')
ylabel('Count')
axis square
grid on
set(gca,'fontsize',14)

title(['$\mu\pm\sigma=', ...
    num2str(round(mean(distance_val)*100)/100),'\pm',...
    num2str(round(std(distance_val)*100)/100),'$, Mdn $=', ...
    num2str(round(median(distance_val)*100)/100),'$'], ...
    'interpreter','latex')