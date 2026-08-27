#%%
"""
plot_tower_data.py

Created by Vasudev Gupta on 2026-06-22. Dept. of Marine Technology, NTNU. All rights reserved.
"""

import yaml
import numpy as np
import matplotlib.pyplot as plt
import pandas as pd
import os
import wisdem.inputs as sch
from wisdem.commonse.fileIO import var_df2dict
from Drive4Wind.post_processing.color_schemes import loc_clr_scheme_m4w, read_color_scheme

clrs_m4w = read_color_scheme( loc_clr_scheme_m4w )

#%%
def parse_bowt_data_from_yaml( yaml_file, towerORmonopile='tower' ):
    # ========================
    # Load YAML
    # ========================
    data = sch.load_yaml( yaml_file )

    tower = data['components'][towerORmonopile]

    # ========================
    # Extract data
    # ========================
    # Height (z coordinates)
    z = np.array(
        tower['reference_axis']['z']['values']
    )

    # Outer diameter
    d = np.array(
        tower['outer_shape']['outer_diameter']['values']
    )

    # Thickness (multiple layers → sum them)
    layers = tower['structure']['layers']

    t_list = []
    for layer in layers:
        t_list.append(np.array(layer['thickness']['values']))

    t_total = np.sum(np.vstack(t_list), axis=0)  # [m]
    t_mm = t_total * 1000  # convert to mm

    return z, d, t_mm

def plot_tower_geo_comparison( m4w_yaml, iea15_yaml, only_tower=True,
                              m4w_label='Made4Wind', iea_label='IEA 15MW',
                              loc_save_img=None, clrs=clrs_m4w ):
    # ========================
    # Load YAMLs
    # ========================
    # 1. tower
    z_m4w, d_m4w, t_m4w = parse_bowt_data_from_yaml( m4w_yaml )
    z_iea, d_iea, t_iea = parse_bowt_data_from_yaml( iea15_yaml )
    # ---- Reference lines ---- 
    waterline = 0.0 # always?
    transition = z_iea[0] # 15.0
    # 2. monopile
    if not only_tower:
        z_m4w_mp, d_m4w_mp, t_m4w_mp = parse_bowt_data_from_yaml( m4w_yaml, towerORmonopile='monopile' )
        z_iea_mp, d_iea_mp, t_iea_mp = parse_bowt_data_from_yaml( iea15_yaml, towerORmonopile='monopile' )
        # ---- Reference lines ---- 
        mudline = z_iea_mp[1] # -30.0

    # ========================
    # stack d and t for tower+monopile
    # ========================
    if not only_tower:
        # 1. M4W
        z_m4w = np.hstack( (z_m4w_mp, z_m4w) )
        d_m4w = np.hstack( (d_m4w_mp, d_m4w) )
        t_m4w = np.hstack( (t_m4w_mp, t_m4w) )
        # 2. IEA
        z_iea = np.hstack( (z_iea_mp, z_iea) )
        d_iea = np.hstack( (d_iea_mp, d_iea) )
        t_iea = np.hstack( (t_iea_mp, t_iea) )

    # ========================
    # Update plot settings
    # ========================
    plot_rcParams_update = {
        "font.size": 16,
        "axes.labelsize": 16,
        "legend.fontsize": 16, # 16 for pdf of `var_with_iter` plot
        "lines.linewidth": 3,
        "lines.markersize": 6,
    }
    plt.rcParams.update( plot_rcParams_update )

    # ========================
    # Plot
    # ========================
    if only_tower: figsize = (10,6)
    else: figsize = (10,10)
    fig, axs = plt.subplots(1, 2, figsize=figsize, sharey=True)

    for ax in axs:
        ax.axhline(transition, linestyle='--',color=clrs['Dark_Green'])
        if not only_tower:
            ax.axhline(waterline, linestyle='--',color=clrs['Dark_Blue'])
            ax.axhline(mudline, linestyle='--',color=clrs['Dark_Red'])

    # Labels only once (left plot)
    axs[0].text(d_iea.min(), transition + 2, 'Tower transition')
    if not only_tower:
        axs[0].text(d_iea.min(), waterline + 2, 'Water line')
        axs[0].text(d_iea.min(), mudline + 2, 'Mud line')

    # ---- Outer Diameter ----
    axs[0].plot(d_iea, z_iea,
        label=iea_label, color=clrs['Light_Turquoise'], linewidth=2)
    axs[0].plot(d_m4w, z_m4w,
        label=m4w_label, color=clrs['Aqua'], linewidth=2)
    axs[0].set_xlabel('Outer Diameter [m]')
    axs[0].set_yticks( z_iea )
    axs[0].set_ylabel('Tower Height [m]')
    axs[0].grid(True)

    # ---- Thickness (step plot) ----
    # NOTE: 'mid'=avg. btw x-pos (thickness) <- consistent with internal wisdem tower vector
    axs[1].step(t_iea, z_iea,
        where='mid', color=clrs['Light_Turquoise'], linewidth=2)
    axs[1].step(t_m4w, z_m4w,
        where='mid', color=clrs['Aqua'], linewidth=2)
    axs[1].set_xlabel('Wall Thickness [mm]')
    axs[1].grid(True)

    axs[0].legend(loc='upper right')
    
    plt.tight_layout()
    if loc_save_img: plt.savefig(loc_save_img)
    plt.show()
# ========================

#%%
# Run & plot
if __name__ == "__main__":
    mydir = os.path.dirname(os.path.dirname(__file__))
    dir_wisdem = os.path.join( mydir, os.path.pardir, os.path.pardir,
                              os.path.pardir, "WISDEM" )
    dirTowerEg = dir_wisdem+(
        os.sep+"examples"+os.sep+"05_tower_monopile")
    dir_m4w_run = dirTowerEg + os.sep + "M4W_01_semisubTower_only"
    # Geometry YAML files
    # 1. base IEA 15-MW
    iea_yaml = dir_m4w_run +os.sep+ "iea15mw_tower_semisub_report.yaml"
    # 2. Made4Wind
    m4w_yaml = dir_m4w_run +os.sep+ "outputs" + os.sep+ "test_m4w.yaml"
    plot_tower_geo_comparison( m4w_yaml, iea_yaml )
# =======================================================================

# %%[markdown]
# ### Plotting loading conditions at tower-top from `modelling_option` files
#%%
# ======================================================
# 1. READ FUNCTION
# ======================================================
def parse_Loading_modelYAML2dict(yaml_file, flag_yamlFromDrivetrain=False):
    """
    Inputs
    _______
    flag_yamlFromDrivetrain : Boolen 
        if the `yaml_file` was created using the `utilities_drivetrain/write_yaml_of_drivetrain_properties.py` function,
        originally from an input .csv file of the drivetrain or wind turbine,
        then set this flag to `True`.
    """
    data = sch.load_yaml( yaml_file )

    if flag_yamlFromDrivetrain: 
        loading = data['modeling_options']['Loading']
    else:
        loading = data['WISDEM']['Loading']

    out = {}

    # Scalars
    out['mass'] = loading['mass']

    # COM
    out['com'] = np.array(loading['center_of_mass'])

    # Inertia (take principal components only)
    moi = np.array(loading['moment_of_inertia'])
    out['I'] = moi[:3]       # keep if still used elsewhere
    out['I_full'] = moi      # full 6 components



    # Loads (first entry)
    loads = loading['loads'][0]
    out['F'] = np.array(loads['force'])
    out['M'] = np.array(loads['moment'])

    return out


# ======================================================
# 2. PLOTTING FUNCTION
# ======================================================
def plot_loads_TT_comparison(
        m4w_dict, iea_dict,
        m4w_label='Made4Wind', iea_label='IEA 15MW',
        clrs=clrs_m4w, loc_save_img=None, figsize=(12,8)
        ):

    labels = [iea_label, m4w_label]
    colors = [clrs['Light_Green'], clrs['Aqua']]

    fig, axs = plt.subplots(2, 2, figsize=figsize)

    width = 0.35


    # --------------------------------------------------
    # Helper function for percentage labels
    # --------------------------------------------------
    def add_percentage_labels(ax, x, reference, comparison, offset):

        for i, (ref, val) in enumerate(zip(reference, comparison)):

            if ref != 0:
                diff = (val - ref) / ref * 100
            else:
                diff = np.nan

            # Position label above positive bars and below negative bars
            if val >= 0:
                y = val + offset
                va = 'bottom'
            else:
                y = val - offset
                va = 'top'

            if np.isfinite(diff):
                ax.text(
                    x[i] + width/2,
                    y,
                    f'{diff:+.1f}%',
                    ha='center',
                    va=va,
                    # fontsize=10
                )


    # --------------------------------------------------
    # (1) Mass
    # --------------------------------------------------
    ax = axs[0, 0]

    categories = [r'$m_{RNA}$']

    m4w_vals = np.array([
        m4w_dict['mass']/1e6,
    ])

    iea_vals = np.array([
        iea_dict['mass']/1e6,
    ])

    x = np.arange(len(categories))

    ax.bar(
        x - width/2,
        iea_vals,
        width,
        color=colors[0],
        label=labels[0]
    )

    ax.bar(
        x + width/2,
        m4w_vals,
        width,
        color=colors[1],
        label=labels[1]
    )

    # Percentage difference
    add_percentage_labels(
        ax, x, iea_vals, m4w_vals,
        offset=0.02 * max(abs(m4w_vals))
    )

    ax.set_xticks(x)
    ax.set_xticklabels(categories)
    ax.set_ylabel('Mass ' + r'$[10^3 ~t]$')
    ax.set_title('RNA Mass Comparison')
    ax.grid(True)


    # --------------------------------------------------
    # (2) Full Moment of Inertia (6 components)
    # --------------------------------------------------
    ax = axs[0, 1]

    labels_I = [
        r'$I_{xx}$',
        r'$I_{yy}$',
        r'$I_{zz}$',
        r'$I_{xy}$',
        r'$I_{xz}$',
        r'$I_{yz}$'
    ]

    m4w_I = np.asarray(m4w_dict['I_full']) / 1e6
    iea_I = np.asarray(iea_dict['I_full']) / 1e6

    x = np.arange(len(labels_I))

    ax.bar(
        x - width/2,
        iea_I,
        width,
        color=colors[0],
        label=labels[0]
    )

    ax.bar(
        x + width/2,
        m4w_I,
        width,
        color=colors[1],
        label=labels[1]
    )

    # Percentage difference
    add_percentage_labels(
        ax, x, iea_I, m4w_I,
        offset=0.02 * max(abs(m4w_I))
    )

    ax.set_xticks(x)
    ax.set_xticklabels(labels_I)
    ax.set_ylabel('MoI ' + r'$[10^6 ~kg \cdot m^2]$')
    ax.set_title('Full Inertia Tensor Comparison')
    ax.legend()
    ax.grid(True)


    # --------------------------------------------------
    # (3) Forces
    # --------------------------------------------------
    ax = axs[1, 0]

    labels_F = [
        r'$F_x$',
        r'$F_y$',
        r'$F_z$'
    ]

    x = np.arange(3)

    iea_F = np.asarray(iea_dict['F']) / 1e6
    m4w_F = np.asarray(m4w_dict['F']) / 1e6

    ax.bar(
        x - width/2,
        iea_F,
        width,
        color=colors[0]
    )

    ax.bar(
        x + width/2,
        m4w_F,
        width,
        color=colors[1]
    )

    # Percentage difference
    add_percentage_labels(
        ax, x, iea_F, m4w_F,
        offset=0.02 * max(abs(m4w_F))
    )

    ax.set_xticks(x)
    ax.set_xticklabels(labels_F)
    ax.set_ylabel('Force ' + r'$[MN]$')
    ax.set_title('Forces Comparison')
    ax.grid(True)


    # --------------------------------------------------
    # (4) Moments
    # --------------------------------------------------
    ax = axs[1, 1]

    labels_M = [
        r'$M_x$',
        r'$M_y$',
        r'$M_z$'
    ]

    x = np.arange(3)

    iea_M = np.asarray(iea_dict['M']) / 1e6
    m4w_M = np.asarray(m4w_dict['M']) / 1e6

    ax.bar(
        x - width/2,
        iea_M,
        width,
        color=colors[0]
    )

    ax.bar(
        x + width/2,
        m4w_M,
        width,
        color=colors[1]
    )

    # Percentage difference
    add_percentage_labels(
        ax, x, iea_M, m4w_M,
        offset=0.02 * max(abs(m4w_M))
    )

    ax.set_xticks(x)
    ax.set_xticklabels(labels_M)
    ax.set_ylabel('Moment ' + r'$[MNm]$')
    ax.set_title('Moments Comparison')
    ax.grid(True)


    # --------------------------------------------------
    # Final formatting
    # --------------------------------------------------
    plt.tight_layout()

    if loc_save_img:
        plt.savefig(loc_save_img, bbox_inches='tight')

    plt.show()

#%%
# ======================================================
# 3. MAIN
# ======================================================
if __name__ == "__main__":
    dir_m4w_runs_main = dirTowerEg +os.sep+ "M4W_production_runs"
    # model yaml files
    file_m4w = dir_m4w_runs_main +os.sep+ "modeling_options_m4w_monopile_only.yaml"
    file_iea = dir_m4w_runs_main +os.sep+ "modeling_options_iea15_monopile_only_wisdemV3.yaml"
    # parse
    m4w = parse_Loading_modelYAML2dict(file_m4w)
    iea = parse_Loading_modelYAML2dict(file_iea)
    # loc_save_img
    loc_save_img = dir_m4w_runs_main +os.sep+ "outputs" +os.sep+ (
            "compr_RNAprops_iea&m4w.pdf"
        )
    # plot
    plot_loads_TT_comparison(m4w, iea)

# %%[markdown]
# ### Comparing loading conditions at tower-base and plotting
# %%
def get_towerBaseLoads_from_csv( loc_csv ):
    df = pd.read_csv(loc_csv)
    dict = var_df2dict(df)
    towerBaseLoads_dict = {
        "F": np.array(eval(dict["towerse.tower.turbine_F"])).reshape(3,),
        "M": np.array(eval(dict["towerse.tower.turbine_M"])).reshape(3,)
        }
    return towerBaseLoads_dict

#%%
def plot_compr_towerBaseLoads_from_dict( m4w_dict, iea_dict,
        m4w_label="Made4Wind", iea_label="IEA 15MW", figsize=(12,8),
        clrs=clrs_m4w, loc_save_img=None ):

    colors = [ clrs['Light_Green'], clrs['Aqua'] ]

    fig, axs = plt.subplots(1,2, figsize=figsize)
    plt.suptitle("Tower-base loads comparison",y=0.9)

    width = 0.35

    # --------------------------------------------------
    # (3) Forces
    # --------------------------------------------------
    ax = axs[0]

    labels_F = [r'$F_x$', r'$F_y$', r'$F_z$']
    x = np.arange(3)

    iea_F = iea_dict['F'] / 1e6
    m4w_F = m4w_dict['F'] / 1e6

    ax.bar(
        x - width/2, iea_F,
        width,
        color=colors[0],
        label=iea_label
    )

    ax.bar(
        x + width/2, m4w_F,
        width,
        color=colors[1],
        label=m4w_label
    )

    # Percentage difference: (second - first) / first
    diff_F = (m4w_F - iea_F) / iea_F * 100

    # Add percentage labels on second bar
    for i, (value, diff) in enumerate(zip(m4w_F, diff_F)):

        # Offset above/below bar depending on sign
        offset = 0.3 if value >= 0 else -0.3
        va = 'bottom' if value >= 0 else 'top'

        ax.text(
            x[i] + width/2,
            value + offset,
            f'{diff:+.0f}%',
            ha='center',
            va=va,
            # fontsize=12
        )

    ax.set_xticks(x)
    ax.set_xticklabels(labels_F)
    ax.set_ylabel('Force ' + r'$[MN]$')
    ax.legend()
    ax.grid(True)

    # --------------------------------------------------
    # (4) Moments
    # --------------------------------------------------
    ax = axs[1]

    labels_M = [r'$M_x$', r'$M_y$', r'$M_z$']
    x = np.arange(3)

    iea_M = iea_dict['M'] / 1e6
    m4w_M = m4w_dict['M'] / 1e6

    ax.bar(
        x - width/2, iea_M,
        width,
        color=colors[0]
    )

    ax.bar(
        x + width/2, m4w_M,
        width,
        color=colors[1]
    )

    # Percentage difference
    diff_M = (m4w_M - iea_M) / iea_M * 100

    # Add percentage labels on second bar
    for i, (value, diff) in enumerate(zip(m4w_M, diff_M)):

        offset = 10 if value >= 0 else -10
        va = 'bottom' if value >= 0 else 'top'

        ax.text(
            x[i] + width/2,
            value + offset,
            f'{diff:+.0f}%',
            ha='center',
            va=va,
            # fontsize=12
        )

    ax.set_xticks(x)
    ax.set_xticklabels(labels_M)
    ax.set_ylabel('Moment ' + r'$[MNm]$')
    ax.grid(True)

    plt.tight_layout()

    if loc_save_img:
        plt.savefig(loc_save_img)

    plt.show()
# %%
