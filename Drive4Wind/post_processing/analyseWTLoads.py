#%% imports
import numpy as np
import scipy.io as sio
from scipy.stats import weibull_min
import os
import matplotlib.pyplot as plt

#%% ========== loads incl MS, Blade Root and Tower Base ==========
def func_loadULS_mat2dict( loc_ULS_loads_mat_wBldRootTwrBs ):
    """
    Inputs:
    -------
    loc_FLS_loads_mat_file : str
        path to ULS loads .mat file
    
    Outputs:
    -------
    Snew : dict
        with keys = ['Fx', 'Fy', 'Fz', 'Mx', 'My', 'Mz']
        and values= np.array of shape (720000,10)
        &
        with keys = ['Fx_max','Fy_max','Fz_mean', 'Mx_max','My_max','Mz_max']
        and values= float

    Internal Progress:
    -----------------
    - DONE : implementation
    """
    # init
    print(f' --- Loading: mainshaft ULS loads from {loc_ULS_loads_mat_wBldRootTwrBs}')

    try:
        S_ULS = sio.loadmat(loc_ULS_loads_mat_wBldRootTwrBs)
    except Exception as e:
        raise RuntimeError(f'Could not load ULS .mat files: {e}')
    # Merge both into unified structure (SI units: N, Nm)
    S = {
        'Fx_max': S_ULS['S_ULS']['Fx_max'][0, 0].item(),
        'Fy_max': S_ULS['S_ULS']['Fy_max'][0, 0].item(),
        'Fz_mean': S_ULS['S_ULS']['Fz_mean'][0, 0].item(), #TODO: "_mean" alongisde "_max"! why?! + automate with openFAST outputs
        'Mx_max': S_ULS['S_ULS']['Mx_max'][0, 0].item(),
        'My_max': S_ULS['S_ULS']['My_max'][0, 0].item(),
        'Mz_max': S_ULS['S_ULS']['Mz_max'][0, 0].item(),
        'RootMxb_max': S_ULS['S_ULS']['RootMxb_max'][0, 0].item(),
        'RootMyb_max': S_ULS['S_ULS']['RootMyb_max'][0, 0].item(),
        'TwrBsMyt_max': S_ULS['S_ULS']['TwrBsMyt_max'][0, 0].item(),
        'TwrBsMxt_max': S_ULS['S_ULS']['TwrBsMxt_max'][0, 0].item()
    }
    print(' --- Success: loaded FLS and ULS load data.')
    print(' --- Success: converted .mat loads to dict (returning).\n')
    return S

#%%
def plot_ms_load_statistics( S, clr_F=None, clr_M=None, figsize=(15,15), loc_save_plot=None ):
    """
    Plot mean and standard deviation of main-shaft loads vs. wind speed.

    Parameters
    ----------
    S : dict
        Dictionary containing load arrays with keys:
        `Fx, Fy, Fz, Mx, My, Mz`
        Each array shape: (time_steps, n_wind_speeds)

        Must also contain:
        `mean_wind_speed` (length n_wind_speeds)
    """

    if "mean_wind_speed" in S.keys():
        wind = S["mean_wind_speed"][0] # shape = (1,11)
    elif "ws" in S.keys():
        wind = S["ws"][0] # shape = (1,11)

    # n_ws = wind.shape[1]

    loads = {
        "F": ["Fx", "Fy", "Fz"],
        "M": ["Mx", "My", "Mz"]
    }

    clrs = [ clr_F, clr_M ]

    fig, axes = plt.subplots(3, 2, figsize=figsize)

    for col, load_type in enumerate(["F", "M"]):

        for row, comp in enumerate(loads[load_type]):

            data = S[comp] / 1e6

            mean_val = np.mean(data, axis=0)
            std_val = np.std(data, axis=0)

            ax = axes[row, col]

            ax.errorbar(
                wind,
                mean_val,
                yerr=std_val,
                fmt='o-',
                capsize=4,
                color=clrs[col],
                linewidth=3,
                markersize=12
            )

            ax.grid(True)
            ax.set_xticks(wind)

    # title
    axes[0,0].set_title(r'$ \mathbf{F}~ [MN] $')
    axes[0,1].set_title(r'$ \mathbf{M}~ [MNm] $')
    # ws label
    axes[2,0].set_xlabel("Wind speed [m/s]")
    axes[2,1].set_xlabel("Wind speed [m/s]")
    # x,y,z label
    axes[0,0].set_ylabel(r"$x$")
    axes[1,0].set_ylabel(r"$y$")
    axes[2,0].set_ylabel(r"$z$")
    # 

    plt.tight_layout()
    if loc_save_plot is not None:
        plt.savefig(loc_save_plot)
    plt.show()

#%%
# ===== Plot Blade Root and Tower Base loads (iea15mw vs. made4wind) =====
if __name__ == "__main__":
    script_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))))
    dir_loads = "outputs_mainshaft_loads"
    file_loads = "mainshaft_loads_ULS_wBldRoot&TwBs.mat"
    loc_ULS_loads_mat_wBldRootTwrBs = os.path.join(script_dir, dir_loads, file_loads)

    S = func_loadULS_mat2dict( loc_ULS_loads_mat_wBldRootTwrBs )

    # DONE: iea15mw loads (cf. semi-sub report, fig.23, top fig.)
    # --- with same units as our loads (cf. units dict below)
    # --- include in plot alongside m4w loads (cf. bar plot docs: https://matplotlib.org/stable/gallery/lines_bars_and_markers/barchart.html)
    Siea15 = {
        'RootMyb_max':  90*1e6,     # monopile: 90, semi-sub: 90
        'RootMxb_max':  30*1e6,     # monopile: 40, semi-sub: 30
        'TwrBsMxt_max': 525*1e6,    # monopile: 410, semi-sub: 525
        'TwrBsMyt_max': 640*1e6     # monopile: 400, semi-sub: 640
    }

    # ==============================
    # _____ post-processing _____
    # ==============================

    # main colors
    from color_schemes import read_color_scheme, loc_clr_scheme_m4w
    clrs_m4w = read_color_scheme(loc_clr_scheme_m4w)

    # ===== Select loads and labels
    load_keys = [
        'RootMyb_max', 
        'RootMxb_max', 
        'TwrBsMxt_max',
        'TwrBsMyt_max' 
    ]

    units = [
        'Nm', 'Nm', 'Nm', 'Nm' # DONE checked with Felix; all in N, Nm
    ]

    labels = [
        'Blade Root\nMoment,\nFlapwise',
        'Blade Root\nMoment,\nEdgewise',
        'Tower Base\nMoment,\nSide-Side',
        'Tower Base\nMoment,\nFore-Aft'
    ]

    colors_m4w = [
        clrs_m4w["Turquoise"],
        clrs_m4w["Turquoise"],
        clrs_m4w["Green"],
        clrs_m4w["Green"]
    ]
    colors_iea = [
        clrs_m4w["Light_Turquoise"],
        clrs_m4w["Light_Turquoise"],
        clrs_m4w["Light_Green"],
        clrs_m4w["Light_Green"]
    ]

    # Convert to MN-m
    values = []
    values_iea = []
    for key, unit in zip(load_keys, units):
        val = S[key]
        val_iea = Siea15[key]
        # convert to MN-m
        if unit == 'kNm':
            val /= 1e3
            val_iea /= 1e3
        elif unit == 'Nm':
            val /= 1e6
            val_iea /= 1e6
        values.append( val )
        values_iea.append( val_iea )
    # =====

    # -------------------------
    # options: Journal polish
    # plot rc params
    params_plot_rc = {
            "font.size": 24,
            "axes.labelsize": 24,
            "legend.fontsize": 24, # 16 for pdf of `var_with_iter` plot
            "lines.linewidth": 2,
            "lines.markersize": 6,
        }
    plt.rcParams.update( params_plot_rc )
    # --------------------------

    # ===== Grouped bar plot
    x = np.arange(len(labels))  # label locations
    width = 0.35                # bar width

    fig, ax = plt.subplots(figsize=(16, 10))

    rects2 = ax.bar(x - width/2, values_iea,
        width, label='IEA 15MW', color=clrs_m4w['Light_Green'])
    rects1 = ax.bar(x + width/2, values,
        width, label='Made4Wind 15MW', color=clrs_m4w['Aqua'])

    # Formatting
    ax.set_ylabel('Moments [M-Nm]')
    ax.set_xticks(x)
    ax.set_xticklabels(labels)
    ax.legend()
    ax.grid(axis='y', linestyle='--', alpha=0.6)
    plt.xticks(rotation=0)
    plt.yticks(np.arange(0, max(values)*1.1, 1e2)) # set y-ticks with some margin above max value

    plt.tight_layout()

    plot_path = os.path.join(script_dir, dir_loads,
            "loads_compr_BldRoot&TwrBs.pdf")
    # plt.savefig(plot_path) # NOTE: saved, so don't change now 

    plt.show()

    # =====
# ====================
# %%
if __name__ == "__main__":
    # IEA 15MW DD hub loads (cf. M:\Vasudev_Gupta\WISDEM\examples\06_drivetrain\drivetrain_direct.py)
    S["IEA"] = {}
    S["IEA"]["Fx_max"] = 2517580.0 # F
    S["IEA"]["Fy_max"] = -27669.0
    S["IEA"]["Fz_mean"] = 3204.0
    S["IEA"]["Mx_max"] = 21030561.0 # M
    S["IEA"]["My_max"] = 7414045.0
    S["IEA"]["Mz_max"] = 1450946.0

    # ===== Common settings
    width = 0.35

    # Use GridSpec to control layout
    fig = plt.figure(figsize=(16, 12))
    gs = fig.add_gridspec(2, 2)

    # Top row (same as before)
    ax1 = fig.add_subplot(gs[0, 0])
    ax2 = fig.add_subplot(gs[0, 1])

    # Bottom row: span BOTH columns
    ax3 = fig.add_subplot(gs[1, :])

    # ===== Plot 1: Hub Forces
    labels_f = ['Fx_max', 'Fy_max', 'Fz_mean']
    values_iea_f = [S['IEA'][k]/ 1e6 for k in labels_f] # convert to MN
    values_m4w_f = [S[k]/ 1e6 for k in labels_f] # convert to MN

    x = np.arange(len(labels_f))

    ax1.bar(x - width/2, values_iea_f, width, label='IEA 15MW',
            color=clrs_m4w['Light_Green'])
    ax1.bar(x + width/2, values_m4w_f, width, label='Made4Wind 15MW',
            color=clrs_m4w['Aqua'])

    ax1.set_title('Hub Forces ' + r'$\mathbf{F}~[MN]$')
    # ax1.set_ylabel('Forces [N]')
    ax1.set_xticks(x)
    ax1.set_xticklabels( [r'$x$', r'$y$', r'$z$'] )
    ax1.grid(axis='y', linestyle='--', alpha=0.6)
    # ax1.legend()

    # ===== Plot 2: Hub Moments
    labels_m = ['Mx_max', 'My_max', 'Mz_max']
    values_iea_m = [S['IEA'][k]/ 1e6 for k in labels_m] # convert to MN-m
    values_m4w_m = [S[k]/ 1e6 for k in labels_m] # convert to MN-m

    x = np.arange(len(labels_m))

    ax2.bar(x - width/2, values_iea_m, width, label='IEA 15MW',
            color=clrs_m4w['Light_Green'])
    ax2.bar(x + width/2, values_m4w_m, width, label='Made4Wind 15MW',
            color=clrs_m4w['Aqua'])

    ax2.set_title('Hub Moments ' + r'$\mathbf{M}~[MNm]$')
    # ax2.set_ylabel('Moments [M-Nm]')
    ax2.set_xticks(x)
    ax2.set_xticklabels( [r'$x$', r'$y$', r'$z$'] )
    ax2.grid(axis='y', linestyle='--', alpha=0.6)
    # ax2.legend()

    # ===== Plot 3: Present Loads (merged across bottom)
    x = np.arange(len(labels))

    ax3.bar(x - width/2, values_iea, width, label='IEA 15MW',
            color=clrs_m4w['Light_Green'])
    ax3.bar(x + width/2, values, width, label='Made4Wind 15MW',
            color=clrs_m4w['Aqua'])

    ax3.set_title('Turbine Loads Comparison '+ r'$[MNm]$')
    # ax3.set_ylabel('Moments [M-Nm]')
    ax3.set_xticks(x)
    ax3.set_xticklabels(labels)
    ax3.grid(axis='y', linestyle='--', alpha=0.6)
    ax3.legend()

    # ===== Final layout
    plt.tight_layout()
    plot_path = os.path.join(script_dir, dir_loads,
                "loads_compr_Hub_Bld_Twr.png")
    # plt.savefig(plot_path) # NOTE: saved, so don't change now 
    plt.show()

# %%
