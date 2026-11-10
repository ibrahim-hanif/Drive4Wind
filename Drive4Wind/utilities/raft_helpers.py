#%%
# IMPORTS

import os
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import ast
import math
from wisdem.commonse.fileIO import var_df2dict

#%%
# PROCESS RESULTS FROM CSVs FOR USER DEFINED VARIABLES

# list of variables to extract from weis csv results
lst_variables=[
    "drivese.F_aero_hub",
    "drivese.M_aero_hub",

    "drivese.nacelle_mass",
    "drivese.nacelle_cm",

    "drivese.base_F",
    "drivese.base_M",

    "towerse.tower.turbine_F",
    "towerse.tower.turbine_M",

    "floatingse.f1",
    "floatingse.f2",

    "raft.rigid_body_periods",

    "raft.Max_Offset",
    "raft.heave_avg",
    "raft.Max_PtfmPitch",
    "raft.max_nac_accel",
    "raft.max_tower_base",

    "raft.stats_surge_max",
    "raft.stats_Mbase_max",
    "raft.stats_Tmoor_max",
    "raft.stats_AxRNA_max"
]

def parse_variables_from_csv_to_dict(
        lst_csv_outputs,
        lst_variables,
        tendon_index = 0,
    ):
    """
    Inputs
    _____
    lst_csv_outputs: list of strings

        each string is the full path of the csv output
    
    tendon_index: int

        index of the tendon to analyse


    Outputs
    _____
    outputs_df: pandas DataFrame
    
    outputs_dict: dict
    """

    # -- Tendon-1 anchor tensions
    str_max_Tmoor_anchor = f"raft.max_Tmoor_{tendon_index+1}_anchor"

    # output init
    outputs_dict = {}
    outputs_dict["name"] = []
    outputs_dict[ str_max_Tmoor_anchor ] = []

    # loop over each output csv
    for i, csv_dir in enumerate(lst_csv_outputs):
        csv_file = os.path.join( csv_dir )

        df = pd.read_csv(csv_file)

        dict_vals = var_df2dict( df )

        # NOTE: add first column as 'name' with names of each design 'iea15_UN_*'
        outputs_dict["name"].append( csv_dir.split("\\")[-2] )

        # loop each variable in this csv
        for iv, var in enumerate(lst_variables):
            if var not in outputs_dict.keys(): outputs_dict[ var ] = []
            outputs_dict[ var ].append( dict_vals[ var ] )

            # Tendon-tension
            # = given tendon_index's anchor
            # = extr DLC 6.1 vals
            # = 0 deg yaw misalign
            if "Tmoor" in var:
                stats_Tmoor_max = np.asarray( eval(
                        str( dict_vals[ var ] )
                        ), dtype=float
                    )
                val_Tmoor_tendon_dlc61 = float(
                    stats_Tmoor_max[-2,tendon_index]
                )   
                outputs_dict[ str_max_Tmoor_anchor ].append(val_Tmoor_tendon_dlc61)

    outputs_df = pd.DataFrame( outputs_dict )

    return outputs_df, outputs_dict

# %%[markdown]
# ### Plot drivetrain-base & tower base loads comparison
#%%
def plot_bars_force_moment_loads(
        path_csv_of_all_outputs,
        var_force="drivese.base_F",
        var_moment="drivese.base_M",
        name_col="name",
        design_labels=None,
        colors=None,
        figsize=(14, 6),
        show_percent=False,
        reference_index=0,
        percent_decimals=1,
        title="Tower-Top Loads Comparison"):
    """
    Plot tower-base force and moment components for multiple designs.

    Expected CSV structure
    ----------------------
    Each row represents one design.

    Required columns:
        name
        either:
        - `drivese.base_F` and `drivese.base_M` = drivetrain-base or tower-top force.
        or
        - `towerse.tower.turbine_F` and `towerse.tower.turbine_M` = tower-base or floater-top.

    `drivese.base_F` expected as:
        [[Fx], [Fy], [Fz]]

    `drivese.base_M` expected as:
        [[Mx], [My], [Mz]]

    Parameters
    ----------
    path_csv_of_all_outputs : str
        Path to comparison CSV.

    design_labels : list[str] or None
        Optional custom labels.
        If None, values from `name_col` are used.

    colors : list or None
        Colors corresponding to each design.

    show_percent : bool
        If True, add percentage difference relative
        to design at `reference_index`.

    reference_index : int
        Row/design used as reference for percentage differences.

    loc_save_img : str or None
        Optional path for saving figure.

    Returns
    -------
    fig, axs
    F, M
        F and M have shape (n_designs, 3), in MN and MNm.
    """
    percent_decimals = int(percent_decimals)

    # ============================================================
    # Read CSV
    # ============================================================

    df = pd.read_csv(path_csv_of_all_outputs)

    n_designs = len(df)

    if n_designs < 1:
        raise ValueError("CSV contains no designs.")

    # ============================================================
    # Helper for parsing [[x], [y], [z]]
    # ============================================================

    def parse_vector(value):

        arr = np.asarray(
            ast.literal_eval(str(value)),
            dtype=float
        ).squeeze()

        arr = arr.flatten()

        if len(arr) != 3:
            raise ValueError(
                "Expected a 3-component vector, "
                f"but received shape {arr.shape}"
            )

        return arr

    # ============================================================
    # Extract data
    # ============================================================

    F = np.vstack([
        parse_vector(value)
        for value in df[var_force]
    ])

    M = np.vstack([
        parse_vector(value)
        for value in df[var_moment]
    ])

    # N -> MN
    F = F / 1e6

    # Nm -> MNm
    M = M / 1e6

    # ============================================================
    # Labels
    # ============================================================

    if design_labels is None:

        if name_col in df.columns:
            design_labels = df[name_col].astype(str).tolist()
        else:
            design_labels = [
                f"Design {i+1}"
                for i in range(n_designs)
            ]

    if len(design_labels) != n_designs:
        raise ValueError(
            "Number of design_labels must match "
            "number of rows in CSV."
        )

    # ============================================================
    # Colors
    # ============================================================

    if colors is None:
        cmap = plt.get_cmap("tab10")

        colors = [
            cmap(i % 10)
            for i in range(n_designs)
        ]

    # ============================================================
    # Figure
    # ============================================================

    fig, axs = plt.subplots(
        1,
        2,
        figsize=figsize
    )

    ax_F, ax_M = axs

    x = np.arange(3)

    # Keep full group width reasonably constant
    group_width = 0.8
    bar_width = group_width / n_designs

    # Center all bars around Fx/Fy/Fz or Mx/My/Mz
    offsets = (
        np.arange(n_designs)
        - (n_designs - 1) / 2
    ) * bar_width

    # ============================================================
    # Plot each design
    # ============================================================

    for i in range(n_designs):

        ax_F.bar(
            x + offsets[i],
            F[i],
            width=bar_width,
            color=colors[i],
            label=design_labels[i]
        )

        ax_M.bar(
            x + offsets[i],
            M[i],
            width=bar_width,
            color=colors[i],
            label=design_labels[i]
        )

    # ============================================================
    # Percentage differences
    # ============================================================

    def calculate_difference_percent(
            comparison, reference, percent_decimals ):
        diff =  ((comparison - reference) / reference) * 100
        diff = np.round(diff, percent_decimals)
        return diff


    if show_percent:

        F_ref = F[reference_index]
        M_ref = M[reference_index]

        for i in range(n_designs):

            if i == reference_index:
                continue

            with np.errstate(
                    divide="ignore",
                    invalid="ignore"):

                F_diff = calculate_difference_percent(
                    F[i], F_ref, percent_decimals
                )
                M_diff = calculate_difference_percent(
                    M[i], M_ref, percent_decimals
                )

            # Force labels
            for j in range(3):

                if np.isfinite(F_diff[j]) and not (
                    np.isclose( F_diff[j], 0.0 )
                ):

                    offset_y = (
                        0.04
                        * max(
                            abs(F[j]).max(),
                            1e-12
                        )
                    )

                    if F[i, j] >= 0:
                        y = F[i, j] + offset_y
                        va = "bottom"
                    else:
                        y = F[i, j] - offset_y
                        va = "top"

                    ax_F.text(
                        x[j] + offsets[i],
                        y,
                        f"{ F_diff[j] } %",
                        ha="center",
                        va=va
                    )

            # Moment labels
            for j in range(3):

                if np.isfinite(M_diff[j]) and not (
                    np.isclose( M_diff[j], 0.0 )
                ):

                    offset_y = (
                        0.04
                        * max(
                            abs(M[j]).max(),
                            1e-12
                        )
                    )

                    if M[i, j] >= 0:
                        y = M[i, j] + offset_y
                        va = "bottom"
                    else:
                        y = M[i, j] - offset_y
                        va = "top"

                    ax_M.text(
                        x[j] + offsets[i],
                        y,
                        f"{ M_diff[j] } %",
                        ha="center",
                        va=va
                    )

    # ============================================================
    # Force subplot
    # ============================================================

    ax_F.set_xticks(x)

    ax_F.set_xticklabels([
        r"$F_x$",
        r"$F_y$",
        r"$F_z$"
    ])

    ax_F.set_ylabel("Force [MN]")

    ax_F.axhline(
        0,
        color="black",
        linewidth=0.8
    )

    ax_F.grid(
        True,
        axis="y",
        alpha=0.4
    )

    ax_F.set_axisbelow(True)

    ax_F.legend(loc="lower left")

    # ============================================================
    # Moment subplot
    # ============================================================

    ax_M.set_xticks(x)

    ax_M.set_xticklabels([
        r"$M_x$",
        r"$M_y$",
        r"$M_z$"
    ])

    ax_M.set_ylabel("Moment [MNm]")

    ax_M.axhline(
        0,
        color="black",
        linewidth=0.8
    )

    ax_M.grid(
        True,
        axis="y",
        alpha=0.4
    )

    ax_M.set_axisbelow(True)

    # ============================================================
    # Overall figure
    # ============================================================

    if title is not None:
        fig.suptitle(title)

    fig.tight_layout()

    return fig, axs, F, M

#%%[markdown]
# ### Plot scalar variables for multiple designs
#%%
def plot_comparison_bar_plot_of_float_vars_from_csv(
        csv_path,
        lst_vars,
        name_col="name",
        design_labels=None,
        colors=None,
        ncols=3,
        figsize=None,
        show_percent=True,
        reference_index=0,
        percent_decimals=1,
        title="Maximum Results Comparison",
        idx_axis_show_legend=0):
    """
    Compare scalar/float variables between an arbitrary number
    of designs stored as rows of a CSV.

    Parameters
    ----------
    csv_path : str
        Path to comparison CSV.

    lst_vars : list of tuples
        Each tuple must have the form:

            (variable_name, plot_label, unit)

        Example:
            ("raft.Max_Offset", r"$x_{max}$", "[m]")

    name_col : str
        CSV column containing the design names.

    design_labels : list[str] or None
        Optional custom labels for each CSV row/design.
        If None, labels are taken from `name_col`.

    colors : list or None
        Optional list of colors, one per design.
        If None, colors are generated automatically.

    ncols : int
        Maximum number of subplot columns.

    figsize : tuple or None
        Figure size. If None, automatically determined.

    show_percent : bool
        If True, write percentage differences above/below
        non-reference bars.

    reference_index : int
        Design/row treated as the reference for percentage
        differences.

    percent_decimals : int
        Number of decimal places shown in percentage values.

    title : str or None
        Figure title.

    loc_save_img : str or None
        Optional path for saving the figure.

    Returns
    -------
    fig : matplotlib.figure.Figure

    axs : ndarray
        Flat array containing only the active subplot axes.

    values : ndarray
        Shape:
            (n_designs, n_variables)

        values[i, j] is variable j for design i.

    differences : ndarray
        Percentage differences relative to reference_index.
        Same shape as values.
    """

    # ========================================================
    # Read CSV
    # ========================================================

    df = pd.read_csv(csv_path)

    n_designs = len(df)
    nvars = len(lst_vars)

    if n_designs < 1:
        raise ValueError("CSV contains no design rows.")

    if nvars < 1:
        raise ValueError("lst_vars contains no variables.")

    if not 0 <= reference_index < n_designs:
        raise ValueError(
            f"reference_index={reference_index} is invalid for "
            f"{n_designs} designs."
        )

    # ========================================================
    # Check requested variables
    # ========================================================

    missing_vars = [
        var
        for var, _, _ in lst_vars
        if var not in df.columns
    ]

    if missing_vars:
        raise KeyError(
            "The following variables are missing from the CSV:\n"
            + "\n".join(missing_vars)
        )

    # ========================================================
    # Variable labels / units
    # ========================================================

    labels = [
        label
        for _, label, _ in lst_vars
    ]

    units = [
        unit
        for _, _, unit in lst_vars
    ]

    # ========================================================
    # Extract values
    #
    # Shape:
    #     n_designs x nvars
    # ========================================================

    values = np.array(
        [
            [
                float(row[var])
                for var, _, _ in lst_vars
            ]
            for _, row in df.iterrows()
        ],
        dtype=float
    )

    # ========================================================
    # Design labels
    # ========================================================

    if design_labels is None:

        if name_col in df.columns:

            design_labels = (
                df[name_col]
                .astype(str)
                .tolist()
            )

        else:

            design_labels = [
                f"Design {i + 1}"
                for i in range(n_designs)
            ]

    if len(design_labels) != n_designs:
        raise ValueError(
            "Number of design_labels must equal the "
            "number of designs/rows in the CSV."
        )

    # ========================================================
    # Colors
    # ========================================================

    if colors is None:

        cmap = plt.get_cmap("tab10")

        colors = [
            cmap(i % 10)
            for i in range(n_designs)
        ]

    elif len(colors) < n_designs:

        raise ValueError(
            f"{n_designs} designs were found, but only "
            f"{len(colors)} colors were provided."
        )

    # ========================================================
    # Percentage differences relative to reference
    # ========================================================

    ref_values = values[reference_index]

    with np.errstate(
            divide="ignore",
            invalid="ignore"):

        differences = (
            (values - ref_values)
            / ref_values
            * 100.0
        )

    # Reference is exactly zero difference
    differences[reference_index, :] = 0.0

    # ========================================================
    # Subplot arrangement
    # ========================================================

    # Do not create more columns than variables
    ncols_plot = min(ncols, nvars)

    nrows = math.ceil(
        nvars / ncols_plot
    )

    if figsize is None:

        figsize = (
            5.5 * ncols_plot,
            4.5 * nrows
        )

    fig, axs = plt.subplots(
        nrows,
        ncols_plot,
        figsize=figsize,
        squeeze=False
    )

    axs = axs.flatten()

    # ========================================================
    # Adaptive bar positioning
    # ========================================================

    # Total width occupied by one group of bars
    group_width = 0.80

    bar_width = (
        group_width
        / n_designs
    )

    offsets = (
        np.arange(n_designs)
        - (n_designs - 1) / 2
    ) * bar_width

    # ========================================================
    # Plot each variable
    # ========================================================

    for j, ax in enumerate(axs[:nvars]):

        variable_values = values[:, j]

        # ----------------------------------------------------
        # Bars
        # ----------------------------------------------------

        for i in range(n_designs):

            ax.bar(
                offsets[i],
                variable_values[i],
                width=bar_width,
                color=colors[i],
                label=design_labels[i]
            )

        # ----------------------------------------------------
        # Percentage annotations
        # ----------------------------------------------------

        if show_percent:

            scale = max(
                np.max(
                    np.abs(variable_values)
                ),
                1e-12
            )

            text_offset = 0.04 * scale

            for i in range(n_designs):

                # Don't display +0% on reference
                if i == reference_index:
                    continue

                diff = differences[i, j]
                value = variable_values[i]

                if not np.isfinite(diff):
                    continue

                if value >= 0:

                    y = value + text_offset
                    va = "bottom"

                else:

                    y = value - text_offset
                    va = "top"

                ax.text(
                    offsets[i],
                    y,
                    f"{diff:+.{percent_decimals}f}%",
                    ha="center",
                    va=va
                )

        # ----------------------------------------------------
        # Axis formatting
        # ----------------------------------------------------

        ax.set_xticks([0])

        ax.set_xticklabels(
            [labels[j]]
        )

        ax.set_ylabel(
            units[j]
        )

        ax.grid(
            True,
            axis="y",
            alpha=0.4
        )

        ax.set_axisbelow(True)

        ax.axhline(
            0.0,
            color="black",
            # linewidth=0.8
        )

        # Additional space for annotations
        ymin, ymax = ax.get_ylim()

        yrange = ymax - ymin

        if yrange > 0:

            ax.set_ylim(
                ymin - 0.04 * yrange,
                ymax + 0.12 * yrange
            )

    # ========================================================
    # Remove unused subplots
    # ========================================================

    for ax in axs[nvars:]:
        ax.remove()

    # Keep only actually used axes in return
    axs_active = axs[:nvars]

    # ========================================================
    # Legend
    # ========================================================

    axs_active[ idx_axis_show_legend ].legend()

    # ========================================================
    # Figure title
    # ========================================================

    if title is not None:
        fig.suptitle(title)

    fig.tight_layout()

    # Note:
    # intentionally no plt.show() here.
    # This lets you modify fig/axs afterwards.

    return (
        fig,
        axs_active,
        values,
        differences
    )

#%%[markdown]
# ### Plot changes in rigid body periods
#%%
RBM_NAMES_SYMB_DICT = {
    "surge": r"$(x)$",
    "sway ": r"$(y)$",
    "heave ": r"$(z)$",
    "roll ": r"$(\phi)$",
    "pitch ": r"$(\theta)$",
    "yaw ": r"$(\psi)$",
}

def plot_comparison_bar_plot_of_1Darray_from_csv(
        csv_path,
        lst_vars,
        name_col="name",
        design_labels=None,
        colors=None,
        figsize=(10, 9),
        show_percent=True,
        reference_index=0,
        percent_decimals=1,
        title=None,
    ):

    # ========================================================
    # Read CSV
    # ========================================================

    df = pd.read_csv(csv_path)

    n_designs = len(df)

    if n_designs < 1:
        raise ValueError("CSV contains no design rows.")

    if not 0 <= reference_index < n_designs:
        raise ValueError(
            f"reference_index={reference_index} is invalid "
            f"for {n_designs} designs."
        )

    # ========================================================
    # Design labels
    # ========================================================

    if design_labels is None:

        if name_col in df.columns:
            design_labels = df[name_col].astype(str).tolist()

        else:
            design_labels = [
                f"Design {i + 1}"
                for i in range(n_designs)
            ]

    if len(design_labels) != n_designs:
        raise ValueError(
            "Number of design_labels must equal "
            "number of CSV rows/designs."
        )

    # ========================================================
    # Colors
    # ========================================================

    if colors is None:

        cmap = plt.get_cmap("tab10")

        colors = [
            cmap(i % 10)
            for i in range(n_designs)
        ]

    elif len(colors) < n_designs:

        raise ValueError(
            f"{n_designs} designs found but only "
            f"{len(colors)} colors supplied."
        )

    # ========================================================
    # Parse CSV array
    # ========================================================

    def parse_array(value):

        arr = np.asarray(
            ast.literal_eval(str(value)),
            dtype=float
        )

        return arr.squeeze().flatten()

    # ========================================================
    # Figure
    # ========================================================

    fig, axs = plt.subplots(
        2,
        1,
        figsize=figsize
    )

    all_values = {}
    all_differences = {}

    # Rigid-body modes
    mode_labels = [key + " " + val for key, val in RBM_NAMES_SYMB_DICT.items()]

    # ========================================================
    # Process variables
    # ========================================================

    for var, label, unit in lst_vars:

        if var not in df.columns:
            raise KeyError(
                f"Variable '{var}' not found in CSV."
            )

        arrays = [
            parse_array(df.iloc[i][var])
            for i in range(n_designs)
        ]

        lengths = [len(arr) for arr in arrays]

        if len(set(lengths)) != 1:
            raise ValueError(
                f"Different array lengths found for "
                f"'{var}': {lengths}"
            )

        n = lengths[0]

        if n != 6:
            raise ValueError(
                f"{var} has {n} elements. "
                "This layout expects the 6 rigid-body modes."
            )

        values = np.vstack(arrays)

        all_values[var] = values

        # ====================================================
        # Percentage differences
        # ====================================================

        ref_values = values[reference_index]

        with np.errstate(
                divide="ignore",
                invalid="ignore"):

            differences = (
                (values - ref_values)
                / ref_values
                * 100.0
            )

        differences[reference_index, :] = 0.0

        all_differences[var] = differences

        # ====================================================
        # Plot groups
        # ====================================================

        groups = [
            (
                axs[0],
                np.array([0, 1, 2]),
                mode_labels[:3]
            ),
            (
                axs[1],
                np.array([3, 4, 5]),
                mode_labels[3:]
            )
        ]

        for ax, indices, labels in groups:

            x = np.arange(len(indices))

            group_width = 0.80

            bar_width = (
                group_width
                / n_designs
            )

            offsets = (
                np.arange(n_designs)
                - (n_designs - 1) / 2
            ) * bar_width

            # ================================================
            # Plot designs
            # ================================================

            for i in range(n_designs):

                ax.bar(
                    x + offsets[i],
                    values[i, indices],
                    width=bar_width,
                    color=colors[i],
                    label=design_labels[i]
                )

            # ================================================
            # Percentage annotations
            # ================================================

            if show_percent:

                subset_values = values[:, indices]

                scale = max(
                    np.max(np.abs(subset_values)),
                    1e-12
                )

                text_offset = 0.025 * scale

                for i in range(n_designs):

                    if i == reference_index:
                        continue

                    for j, idx in enumerate(indices):

                        diff = differences[i, idx]
                        value = values[i, idx]

                        if not np.isfinite(diff):
                            continue

                        if value >= 0:
                            y = value + text_offset
                            va = "bottom"

                        else:
                            y = value - text_offset
                            va = "top"

                        ax.text(
                            x[j] + offsets[i],
                            y,
                            f"{diff:+.{percent_decimals}f}%",
                            ha="center",
                            va=va
                        )

            # ================================================
            # Formatting
            # ================================================

            ax.set_xticks(x)

            ax.set_xticklabels(labels)

            ax.set_ylabel(unit)

            ax.grid(
                True,
                axis="y",
                alpha=0.3
            )

            ax.set_axisbelow(True)

            ax.axhline(
                0.0,
                color="black",
                linewidth=0.8
            )

            # Give % labels additional space
            ymin, ymax = ax.get_ylim()

            yrange = ymax - ymin

            if yrange > 0:

                ax.set_ylim(
                    ymin - 0.03 * yrange,
                    ymax + 0.12 * yrange
                )

    # ========================================================
    # Axis titles
    # ========================================================

    axs[0].set_title( "Translational Modes" )

    axs[1].set_title( "Rotational Modes" )

    # only one legend required
    handles, labels = axs[0].get_legend_handles_labels()

    # avoid duplicate entries if lst_vars has >1 variable
    unique = dict(zip(labels, handles))

    axs[0].legend(
        unique.values(),
        unique.keys()
    )

    # ========================================================
    # Figure title
    # ========================================================

    if title is not None:
        fig.suptitle(title)

    fig.tight_layout()

    # ========================================================
    return (
        fig,
        axs,
        all_values,
        all_differences
    )
#%%[markdown]
# ### Plot spectra of excitation (1P, 3P), RBMs, tower bending modes (1.,2.)
#%%
from Drive4Wind.utilities.spectrums import spectrum_jonswap, spectrum_kaimal
#%%
def plot_frequency_placement_with_metocean(
        csv_path,
        modeling_options_yaml,
        hub_height,
        rpm_min,
        rpm_rated,
        design_labels,
        colors,
        markers,
        figsize=(16, 6),
        title="Wind, Wave, Excitation and Structural Frequency Comparison",
        wind_speed_indices=None):
    
    import yaml
    from matplotlib.patches import Patch
    from matplotlib.lines import Line2D

    # ==================================================
    # Load CSV and metocean data
    # ==================================================

    df = pd.read_csv(csv_path)

    with open(modeling_options_yaml, "r") as fp:
        modeling_options = yaml.safe_load(fp)

    metocean = modeling_options["DLC_driver"]["metocean_conditions"]

    wind_speeds = np.asarray(metocean["wind_speed"], dtype=float)
    Hs_all = np.asarray(metocean["wave_height_NSS"], dtype=float)
    Tp_all = np.asarray(metocean["wave_period_NSS"], dtype=float)

    if wind_speed_indices is None:
        wind_speed_indices = [0, 4, 8, len(wind_speeds) - 1]

    # ==================================================
    # Frequency grid [Hz]
    # ==================================================

    f = np.linspace(0.001, 0.7, 200)

    fig, ax = plt.subplots(figsize=figsize)

    # ==================================================
    # Wave spectra (selected metocean conditions)
    # ==================================================

    clr_wave_spec = "aqua"

    for idx in wind_speed_indices:
        Hs, Tp = Hs_all[idx], Tp_all[idx]

        S = spectrum_jonswap(f, Hs, Tp, gamma=None)
        S /= max(np.max(S), np.finfo(float).eps)

        ax.plot(
            f, S,
            color=clr_wave_spec,
            alpha=0.7,
            label=f"Wave: Hs={Hs:.1f} m, Tp={Tp:.1f} s"
        )

    # ==================================================
    # Wind spectra
    # ==================================================

    clr_wind_spec = "blue"

    for idx in wind_speed_indices:
        U = wind_speeds[idx]

        S = spectrum_kaimal(f, U, Hhub=hub_height)
        S /= max(np.max(S), np.finfo(float).eps)

        ax.plot(
            f, S,
            color=clr_wind_spec,
            alpha=0.7,
            label=f"Wind: U={U:.0f} m/s"
        )

    # ==================================================
    # 1P / 3P frequency bands [Hz]
    # ==================================================

    f_1P = np.sort(np.array([rpm_min, rpm_rated], dtype=float) / 60.0)
    f_3P = 3.0 * f_1P

    margin_1P, margin_3P = 0.02, 0.05
    # TODO: use function `calculate_2_std_of_rotor_speed_samples`

    # ========== 1P ==========
    clr_1p = "0.7"

    ax.axvspan(
        max(0.0, f_1P[0] - margin_1P),
        f_1P[1] + margin_1P,
        color=clr_1p, zorder=0
    )
    ax.axvspan(
        f_1P[0], f_1P[1],
        facecolor="none", hatch="//",
        edgecolor="black", linewidth=0.8, zorder=1
    )

    # ========== 3P ==========
    clr_3p = "0.8"

    ax.axvspan(
        max(0.0, f_3P[0] - margin_3P),
        f_3P[1] + margin_3P,
        color=clr_3p, zorder=0
    )
    ax.axvspan(
        f_3P[0], f_3P[1],
        facecolor="none", hatch="\\\\",
        edgecolor="black", linewidth=0.8, zorder=1
    )

    # ==================================================
    # Structural frequencies for all designs
    # ==================================================

    rbm_names = [name for name in RBM_NAMES_SYMB_DICT.values()]

    rbm_text_pos = np.linspace(0.6,0.98,6)

    rbm_periods = {}
    tower_periods = {}

    for i, design in enumerate(design_labels):

        if design not in df.index:
            # Design labels are plot labels, not necessarily CSV index values.
            # Use the row at the same position as a fallback.
            row = df.iloc[i]
        else:
            row = df.loc[design]

        color = colors[i]
        marker = markers[i]

        # --------------------------------------------------
        # Rigid-body modes: raft.rigid_body_periods [s]
        # --------------------------------------------------

        periods = np.asarray(
            ast.literal_eval(str(row["raft.rigid_body_periods"])),
            dtype=float
        ).ravel()

        if len(periods) != 6:
            raise ValueError(
                f"Design {design}: expected 6 RBM periods, got {len(periods)}."
            )

        rbm_periods[design] = periods

        for mode, period, tpos in zip(rbm_names, periods, rbm_text_pos):
            if not np.isfinite(period) or period <= 0:
                continue

            ff = 1.0 / period

            ax.axvline(
                ff,
                color=color,
                linestyle="-.",
                # linewidth=1.4,
                # alpha=0.85,
                zorder=3,
                label=mode
            )

            ax.plot(
                ff,
                0.45,
                marker=marker,
                color=color,
                markersize=14,
                transform=ax.get_xaxis_transform(),
                clip_on=False
            )

            ax.text(
                ff,
                tpos,
                mode,
                rotation=0,
                va="top",
                ha="center",
                backgroundcolor="white",
                zorder=10
            )

        # --------------------------------------------------
        # Tower modes: floatingse.f1 and floatingse.f2 [Hz]
        # --------------------------------------------------

        f1 = float(row["floatingse.f1"])
        f2 = float(row["floatingse.f2"])

        tower_periods[design] = {
            "tower_T1": 1.0 / f1 if f1 > 0 else np.nan,
            "tower_T2": 1.0 / f2 if f2 > 0 else np.nan,
        }

        if i == 0:
            ax.text(
                f1,
                0.98,
                f"Tower (FA, SS)",
                rotation=0,
                va="top",
                ha="center",
                backgroundcolor="white",
                zorder=10
            )

        for ff in (f1, f2):
            if not np.isfinite(ff) or ff <= 0:
                continue

            ax.axvline(
                ff,
                color=color,
                linestyle="--",
                # linewidth=1.8,
                # alpha=0.9,
                zorder=4,
                label=mode
            )

            ax.plot(
                ff,
                0.45,
                marker=marker,
                color=color,
                markersize=14,
                transform=ax.get_xaxis_transform(),
                clip_on=False
            )

    # ==================================================
    # Formatting
    # ==================================================

    ax.set_xlabel("Frequency [Hz]")
    ax.set_ylabel("Normalized Power Spectrum")
    ax.set_xlim(0, f.max())
    ax.set_ylim(0, 1.05)
    ax.set_title(title)
    ax.grid(True, which="both", alpha=0.25)

    # Legend handles
    handles = [
        Patch(
            facecolor=clr_1p, alpha=0.5,
            label="1P constraint"
        ),
        Patch(
            facecolor="none", hatch="//", edgecolor="black",
            label="1P design range"
        ),
        Patch(
            facecolor=clr_3p, alpha=0.5,
            label="3P constraint"
        ),
        Patch(
            facecolor="none", hatch="//", edgecolor="black",
            label="3P design range"
        ),
        Line2D(
            [0], [0], color=clr_wave_spec,
            label="Wave spectrum (JONSWAP)"
        ),
        Line2D(
            [0], [0], color=clr_wind_spec,
            label="Wind spectrum (Kaimal)"
        ),
        Line2D(
            [0], [0], color="black", linestyle="-.",
            label="Rigid-body modes"
        ),
        Line2D(
            [0], [0], color="black", linestyle="--",
            label="Tower modes"
        ),
    ]

    # One legend entry per design, using supplied colors and markers
    for design, color, marker in zip(design_labels, colors, markers):
        handles.append(
            Line2D(
                [0], [0],
                color=color,
                marker=marker,
                linestyle="none",
                label=str(design)
            )
        )

    ax.legend(
        loc="lower center",
        handles=handles,
        ncol=4,
        bbox_to_anchor=(0.5,-0.5),
    )

    fig.tight_layout()

    return fig, ax, rbm_periods, tower_periods