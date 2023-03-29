# %%
from ppm import PPM
from ppm.plotting import plot_hausdorff, plot
from ppm.geometric_metrics import hausdorff_distance

ppm = PPM()
ppm_target = PPM()

ppm_target.set_ppm_params(
    {
        'Location_Antitragus-End_X':-10,
        'Location_Antitragus-End_Y':-10,
        'Location_Antitragus-End_Z':-10
    }
)

plot_hausdorff(ppm_target, ppm)

plot(ppm_target)

print(hausdorff_distance(ppm_target, ppm, 'gen'))