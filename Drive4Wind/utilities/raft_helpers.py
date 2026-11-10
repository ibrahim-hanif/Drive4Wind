#%%
# IMPORTS

import os
import pandas as pd
import numpy as np
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