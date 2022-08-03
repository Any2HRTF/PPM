function hd = hausdorff_dist(P,Q)
%hausdorff_dist - Calculate the Hausdorff distance between two sets of points 
% P and Q in Euclidian space [1, 2]. Function adapted from [3].
%
%   Usage: 
%
%     hd = hausdorff_dist(P,Q)
%
%   Input parameters:
%
%     P  : Set of points P.
%     Q  : Set of points Q. 
%
%   Output parameters:
%
%     hd : Hausdorff distance between the two sets of points P and Q.
%
% [1] Pompeiu, D., Sur la continuité des fonctions de variables complexes 
%     (These), Gauthier-Villars, Paris, 1905; Ann.Fac.Sci.de Toulouse, 7 
%     (1905), 264–315.
% [2] Hausdorff, F., Set Theory, Chelsea Publishing Company, New York, 1957
% [3] Zachary Danziger (2022). Hausdorff Distance 
%     (https://www.mathworks.com/matlabcentral/fileexchange/26738-hausdorff-distance), 
%     MATLAB Central File Exchange. Retrieved February 18, 2022. 

% #Author: Mantas Tamulionis (2021)
% Modifications by Florian Pausch (2022)   

dist = zeros(size(P,1),1);
for p = 1:size(P,1)
    % Calculate the minimum distance from points in P to Q
    minP = min(sum(bsxfun(@minus,P(p,:),Q).^2, 2));
    dist(p,1) = minP;
end

hd = sqrt(dist);