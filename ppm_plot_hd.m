function ppm_plot_hd(ppm,varargin)
%ppm_plot_hd - Plot a target point cloud and contrast it with the result point 
%          cloud after modifying parameters of the PPM. The latter point cloud
%          is color-coded in terms of the corresponding Hausdorff-distance values. 
%
% Usage: 
%
%   plot_hd(ppm)
%
% Input parameters:
%
%   ppm : PPM structure array [struct]. Initialized as per ppm_initialize.
% 
% Related functions: hausdorff_dist

% #Author: Florian Pausch (2022)
% Initial version by Mantas Tamulionis (2021)    

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
    hd_mean_min_itr = ppm.evaluate.hd_mean_min_itr;
else
    hd_mean_min_itr = 1;
end

%% Select point cloud with lowest mean HD
hd_plot = ppm.evaluate.hd(:,hd_mean_min_itr);

%% Clip HD values below/above caxis_min/caxis_max for plot
if isempty(p.Results.caxis_min)
    caxis_min = min(ppm.evaluate.hd(:,hd_mean_min_itr));
else
    hd_plot(hd_plot<=caxis_min) = caxis_min;
end

if isempty(p.Results.caxis_max)
    caxis_max = max(ppm.evaluate.hd(:,hd_mean_min_itr));
else
    hd_plot(hd_plot>=caxis_max) = caxis_max;
end

hd_c = round(hd_plot/max(hd_plot)*256);  % Convert HD values to range [1 256]

clr = colormap(turbo); % Create a matrix with colormap hue codes
cmatrix = zeros(size(ppm.evaluate.hd,1),3); % create a matrix to store color codes corresponding to HD values

if ~all(isnan(hd_c))
    % Fill the matrix with hue codes corresponding to HD values
    for idx=1:size(ppm.evaluate.hd,1)
        if hd_c(idx) ~= 0
            cmatrix(idx,:) = clr(hd_c(idx),:);
        else % intercept potential index error
            cmatrix(idx,:) = clr(1,:);
        end
    end
else
   hd_c = 0.8*ones(size(cmatrix));
end

%% Plot point cloud and overlay it with target point cloud in grey color
nexttile
ptCloud_target = pointCloud(ppm.evaluate.pc_target, ...
    'Color',0.8*ones(size(ppm.evaluate.pc_target)));
pcshow(ptCloud_target,'MarkerSize', 10);
filename = strsplit(ppm.ini.blender_file,'\');
title(filename{end},'Interpreter','none')
hold on

% Create new ptCloud with HD-dependent color codes and plot
ptCloud_result = pointCloud(ppm.evaluate.pc_result(:,:,hd_mean_min_itr), ...
    'Color',cmatrix);
pcshow(ptCloud_result,'MarkerSize', 20);

hl = legend('Target point cloud','Modelled point cloud');
set(hl,'color','white','location','southwestoutside');

if ~all(range(hd_c)==0)
    c=colorbar;
end
c.Label.String = 'Pointwise minimum distance (mm)';
c.FontSize = 16;
set(gcf,'color','w');
set(gca,'color','w');

if ~all(range(hd_c)==0)
    caxis([caxis_min, caxis_max])
end
view([180 0])
set(gca,'fontsize',14)


%% Plot histogram of HD values
nexttile
histogram(ppm.evaluate.hd(:,hd_mean_min_itr),'EdgeColor','black','FaceColor',[.5 .5 .5]);
xlabel('Pointwise minimum distance (mm)')
ylabel('Count')
axis square
grid on
set(gca,'fontsize',14)

title(['$\mu\pm\sigma=', ...
    num2str(round(mean(ppm.evaluate.hd(:,hd_mean_min_itr))*100)/100),'\pm',...
    num2str(round(std(ppm.evaluate.hd(:,hd_mean_min_itr))*100)/100),'$, Mdn $=', ...
    num2str(round(median(ppm.evaluate.hd(:,hd_mean_min_itr))*100)/100),'$'], ...
    'interpreter','latex')