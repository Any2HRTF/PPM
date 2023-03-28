import matplotlib.pyplot as plt
import matplotlib.ticker as ticker
from mpl_toolkits.axes_grid1 import ImageGrid
import numpy as np
from .geometric_metrics import _hausdorff_dist

def plot(ppm, return_fig:bool=False, *args, **kwargs) -> plt.figure:


    if 'cam_loc' not in kwargs:
        kwargs['cam_loc'] = np.array([-10,200,5])
    if 'resolution' not in kwargs:
        kwargs['resolution'] = 256
    img, _= ppm.render(*args, **kwargs)

    # calculate the number of rows and columns from shape[0]
    nrows = int(np.ceil(np.sqrt(img.shape[0])))
    ncols = int(np.ceil(img.shape[0] / nrows))

    fig = plt.figure()
    grid = ImageGrid(fig, 111,
                    nrows_ncols=(nrows, ncols),
                    axes_pad=0.2,
                    )

    for i, (ax, im) in enumerate(zip(grid, img)):
        ax.imshow(im, cmap='gray')
        if len(kwargs['cam_loc'].shape) > 1:
            ax.set_title([np.round(loc).astype(int) for loc in kwargs['cam_loc'][:,i]], fontsize=8)
        ax.axis('off')

    for ax in grid[nrows*ncols-img.shape[0]:]:
        ax.axis('off')

    fig.suptitle(ppm.name)

    if return_fig:
        return fig
    plt.show()

def plot_hausdorff(ppm, ppm_target):

    ppm_pts = ppm.get_point_cloud()
    ppm_target_pts = ppm_target.get_point_cloud()

    hs_dist = _hausdorff_dist(ppm_pts, ppm_target_pts, htype='point')

    ax1 = plt.subplot(121)
    ax1.hist(hs_dist,  bins=100, orientation="horizontal", color = "orange", lw=0, histtype='stepfilled'  )
    ax1.set_ylabel('Distance (mm)')
    ax1.set_ylim(0, np.max(hs_dist))
    ax1.xaxis.set_major_locator(ticker.NullLocator())
    ax1.spines['top'].set_visible(False)
    ax1.spines['right'].set_visible(False)
    ax1.spines['left'].set_visible(False)
    ax1.spines['bottom'].set_visible(False)
    ax1.set_yticks([0,1,max(hs_dist)])
    

    ax2 = plt.subplot(122, projection='3d')
    ax2.scatter(ppm_pts[:,0],ppm_pts[:,1],ppm_pts[:,2], color='lightgoldenrodyellow', alpha=0.1)
    ax2.scatter(ppm_target_pts[:,0],ppm_target_pts[:,1],ppm_target_pts[:,2], color='darkolivegreen', alpha=0.01)
    ax2.axis('off')


    plt.show()
