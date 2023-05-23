function [dist_dir1, dist_dir2, hd] = hausdorff_dist(P,Q)
%hausdorff_dist - Calculate the directed minimum pointwise distance between  
% two sets of points P and Q in Euclidian space [1, 2]. The Hausdorff
% distance corresponds to the larger supremum of dist_dir1 and dist_dir2. 
% Function adapted from [3].
%
%   Usage: 
%
%     [dist_dir1, dist_dir2, hd] = hausdorff_dist(P,Q)
%
%   Input parameters:
%
%     P : Set of points P [double]
%     Q : Set of points Q [double] 
%
%   Output parameters:
%
%     dist_dir1 : minimum distances between each point in P to Q
%     dist_dir2 : minimum distances between each point in Q to P
%     hd        : Hausdorff distance, i.e. larger supremum of 
%                 dist_dir1 and dist_dir2
%
% [1] Pompeiu, D., Sur la continuité des fonctions de variables complexes 
%     (These), Gauthier-Villars, Paris, 1905; Ann.Fac.Sci.de Toulouse, 7 
%     (1905), 264–315.
% [2] Hausdorff, F., Set Theory, Chelsea Publishing Company, New York, 1957
% [3] Zachary Danziger (2022). Hausdorff Distance 
%     (https://www.mathworks.com/matlabcentral/fileexchange/26738-hausdorff-distance), 
%     MATLAB Central File Exchange. Retrieved February 18, 2022. 

% #Author: Florian Pausch (2022)   

% Calculate the minimum pointwise distance between P and Q
dist_dir1 = zeros(size(P,1),1);
for p = 1:size(P,1)
    dist_dir1(p) = min(sum(bsxfun(@minus,P(p,:),Q).^2, 2));
end
dist_dir1 = sqrt(dist_dir1);

% Calculate the minimum pointwise distance between Q and P
dist_dir2 = zeros(size(Q,1),1);
for q = 1:size(Q,1)
    dist_dir2(q) = min(sum(bsxfun(@minus,Q(q,:),P).^2, 2));
end
dist_dir2 = sqrt(dist_dir2);

% Calculate Pompeiu-Hausdorff distance
hd = max([max(dist_dir1), max(dist_dir2)]);

