def jaccard_similarity(P_points, Q_points, resolution_xx, resolution_yy, resolution_zz) -> np.float32:

    x_min = min(min(P_points[:, 0]), min(Q_points[:, 0])); x_max = max(max(P_points[:, 0]), max(Q_points[:, 0]))
    y_min = min(min(P_points[:, 1]), min(Q_points[:, 1])); y_max = max(max(P_points[:, 1]), max(Q_points[:, 1]))
    z_min = min(min(P_points[:, 2]), min(Q_points[:, 2])); z_max = max(max(P_points[:, 2]), max(Q_points[:, 2]))

    xx = np.linspace(x_min+.25, x_max-.25, resolution_xx) 
    yy = np.linspace(y_min+.25, y_max-.25, resolution_yy)
    zz = np.linspace(z_min+.25, z_max-.25, resolution_zz)

    grid_points = np.zeros((resolution_xx*resolution_yy*resolution_zz, 11))
    offset = 0

    for z_idx in range(len(zz)):
        for y_idx in range(len(yy)):
            for x_idx in range(len(xx)):
                grid_points[x_idx+offset,...] = np.array([xx[x_idx], yy[y_idx], zz[z_idx],  0, 1, 0, 0, 0, 1, 0, 0])
            offset += len(xx)

    for i in range(len(grid_points)):
        dist_to_nearest_p = np.sqrt(np.min(np.sum( (grid_points[i,:3] - P_points)**2, axis=1)))
        dist_to_nearest_q = np.sqrt(np.min(np.sum( (grid_points[i,:3] - Q_points)**2, axis=1)))

        if dist_to_nearest_p <= 0.6:
            grid_points[i, 3:7] = np.array([1, 0, 1, 0])

        if dist_to_nearest_q <= 0.6:
            grid_points[i, 7:] = np.array([1, 0, 1, 0])

    return np.sum(np.logical_and(grid_points[:, 3], grid_points[:, 7])) / (np.sum(np.logical_or(grid_points[:, 3], grid_points[:, 7])) + np.finfo(np.float32).eps)


jaccard = jaccard_similarity(ground_truth_point_cloud, prediction_point_cloud, resolution_x, resolution_y, resolution_z)

jaccard_similarity_list_of_dict = {
    'id': file_id,
    'path': path,
    'jaccard_similarity': jaccard
}

dice_coefficient_list_of_dict = {
    'id': file_id,
    'path': path,
    'dice_coefficient': 2 * jaccard / (1 + jaccard)
}